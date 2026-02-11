"""
The Orchestrator — the pipeline coordinator.

This is the entry point (API Gateway logic). It:
1. Receives raw patient data (structured, unstructured, or mixed).
2. Passes the ENTIRE raw context as-is to ML Swarm (it has its own filtering).
3. Uses an LLM to extract medical details from the context, appends a diagnosis
   prompt, and sends that to MedGemma.
4. Both branches run in parallel.
5. Feeds all outputs into the Synthesis Agent to produce the final report.
6. Updates the job store with progress throughout.
"""

from __future__ import annotations

import asyncio
import logging
import traceback

from core.job_store import JobStatus, job_store
from models.requests import DiagnosticsRunRequest
from models.report import DiagnosticReport
from services import ml_swarm, medgemma, synthesis
from services.separator import extract_medical_details
from services.ml_swarm import SwarmResponse
from services.medgemma import MedGemmaResponse

logger = logging.getLogger(__name__)


# ── Pipeline Execution ──


async def run_pipeline(job_id: str, request: DiagnosticsRunRequest) -> None:
    """
    Execute the full diagnostic pipeline as a background task.

    Progress milestones:
      10 — Job started, preparing data
      20 — Medical details extracted for MedGemma
      50 — Both ML Swarm and MedGemma complete
      80 — Synthesis Agent generating report
      90 — Report validated
     100 — Complete
    """
    try:
        # ── Step 1: Prepare raw context ──
        await job_store.update_job(job_id, progress=10)
        logger.info("[%s] Pipeline started", job_id)

        # Serialize the entire request into a raw string
        raw_data = request.to_raw_string()
        logger.info("[%s] Raw context (%d chars): %.200s...", job_id, len(raw_data), raw_data)

        # ── Step 2: Extract medical details for MedGemma (LLM call) ──
        # This runs BEFORE the parallel branch so MedGemma gets a clean query.
        # ML Swarm gets raw_data directly — no pre-processing needed.
        logger.info("[%s] Extracting medical details for MedGemma", job_id)
        medgemma_query = await extract_medical_details(raw_data)

        await job_store.update_job(job_id, progress=20)
        logger.info("[%s] MedGemma query ready: %.150s...", job_id, medgemma_query)

        # ── Step 3: Parallel Branch Execution ──
        logger.info("[%s] Firing ML Swarm (full context) + MedGemma (filtered) in parallel", job_id)

        # ML Swarm: gets the entire raw context as-is
        swarm_task = _safe_call("ML Swarm", ml_swarm.analyze(raw_data))
        # MedGemma: gets LLM-filtered medical details + diagnosis prompt
        medgemma_task = _safe_call("MedGemma", medgemma.analyze(medgemma_query))

        results = await asyncio.gather(swarm_task, medgemma_task)
        swarm_result: SwarmResponse | None = results[0]
        medgemma_result: MedGemmaResponse | None = results[1]

        await job_store.update_job(job_id, progress=50)
        logger.info(
            "[%s] Branches complete — Swarm: %s, MedGemma: %s",
            job_id,
            "OK" if swarm_result else "FAILED",
            "OK" if medgemma_result else "FAILED",
        )

        # At least one branch must succeed
        if swarm_result is None and medgemma_result is None:
            raise RuntimeError("Both ML Swarm and MedGemma failed — cannot generate report")

        # ── Step 4: Synthesis ──
        await job_store.update_job(job_id, progress=80)
        logger.info("[%s] Running Synthesis Agent", job_id)

        # Build a minimal patient context from the request for the synthesiser
        patient_context = request.model_dump(exclude_none=True, exclude={"doctorId"})

        report: DiagnosticReport = await synthesis.generate_report(
            job_id=job_id,
            patient_id=request.patientId,
            patient_context=patient_context,
            swarm_result=swarm_result,
            medgemma_result=medgemma_result,
        )

        # ── Step 5: Validation & Storage ──
        await job_store.update_job(job_id, progress=90)
        logger.info("[%s] Report generated — riskScore=%d", job_id, report.riskScore)

        # Validate by re-serializing (Pydantic will catch schema issues)
        _ = report.model_dump()

        await job_store.update_job(
            job_id, status=JobStatus.COMPLETE, progress=100, report=report
        )
        logger.info("[%s] Pipeline COMPLETE", job_id)

    except Exception as exc:
        logger.error("[%s] Pipeline FAILED: %s", job_id, exc)
        logger.error(traceback.format_exc())
        await job_store.update_job(
            job_id, status=JobStatus.FAILED, error=str(exc)
        )


async def _safe_call(name: str, coro) -> any:
    """Run an async call, returning None on failure instead of raising."""
    try:
        return await coro
    except Exception as exc:
        logger.warning("%s call failed (non-fatal): %s", name, exc)
        return None
