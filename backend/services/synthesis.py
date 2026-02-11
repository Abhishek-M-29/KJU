"""
Synthesis Agent — the Narrator.

Uses a Groq-hosted LLM to combine outputs from the ML Swarm and MedGemma into
a coherent, clinician-readable diagnostic report in the exact JSON schema
specified in AI/ai.md.

This is the ONLY general-purpose LLM in the stack. It acts as a technical
writer, NOT a diagnostician.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from groq import AsyncGroq

from core.config import settings
from models.report import (
    DiagnosticReport,
    HeatmapEntry,
    QualitativeFactors,
    ShapFeature,
)
from services.ml_swarm import SwarmResponse
from services.medgemma import MedGemmaResponse

logger = logging.getLogger(__name__)

# ── System prompt ──

SYSTEM_PROMPT = """\
You are a medical technical writer for an AI-powered clinical decision support system.
Your role is to synthesize quantitative ML analysis and qualitative text analysis into
a clear, actionable diagnostic report. You are NOT a diagnostician — you summarize and
narrate findings produced by upstream models.

RULES:
1. Write a comprehensive executiveSummary (2-4 sentences) that integrates both the
   numeric risk analysis and the text-based findings. Be specific about values and
   conditions. Use clinical language appropriate for a physician audience.
2. The riskScore is an integer 0-100 derived from the ML Swarm output. If the ML Swarm
   provided a risk score, use it. Otherwise, estimate based on the available data.
3. shapFeatures come from the ML Swarm. Include them exactly as provided. If null or
   missing, generate reasonable features from the available clinical data.
4. featureHeatmap entries come from the ML Swarm. Include them as provided. If null,
   generate categories with appropriate intensity values (0.0-1.0).
5. qualitativeFactors should merge insights from both the ML Swarm and MedGemma outputs.
   - riskFactors: conditions/findings that increase risk
   - protectiveFactors: conditions/findings that reduce risk
   - recommendations: actionable clinical next steps
6. Output ONLY valid JSON matching the exact schema. No markdown, no code fences.

OUTPUT JSON SCHEMA:
{
  "executiveSummary": "<string>",
  "riskScore": <int 0-100>,
  "shapFeatures": [{"name": "<string>", "impact": <float>, "direction": "positive|negative"}],
  "featureHeatmap": [{"name": "<string>", "value": <float 0.0-1.0>}],
  "qualitativeFactors": {
    "riskFactors": ["<string>"],
    "protectiveFactors": ["<string>"],
    "recommendations": ["<string>"]
  }
}
"""


def _build_user_prompt(
    patient_context: dict[str, Any],
    swarm_result: Optional[SwarmResponse],
    medgemma_result: Optional[MedGemmaResponse],
) -> str:
    """Build the user message with all available upstream data."""
    sections: list[str] = []

    # Patient context
    sections.append("=== PATIENT CONTEXT ===")
    sections.append(json.dumps(patient_context, indent=2))

    # ML Swarm results
    sections.append("\n=== ML SWARM ANALYSIS (Numeric Branch) ===")
    if swarm_result:
        sections.append(json.dumps(swarm_result.raw, indent=2, default=str))
    else:
        sections.append("ML Swarm data unavailable. Generate analysis from patient context only.")

    # MedGemma results
    sections.append("\n=== MEDGEMMA ANALYSIS (Text Branch) ===")
    if medgemma_result:
        sections.append(f"Answer:\n{medgemma_result.answer}")
        if medgemma_result.citations:
            sections.append(f"Citations: {json.dumps(medgemma_result.citations)}")
    else:
        sections.append("MedGemma data unavailable. Generate analysis from patient context only.")

    sections.append(
        "\n=== INSTRUCTIONS ===\n"
        "Synthesize ALL the above into the diagnostic report JSON. "
        "Include every SHAP feature and heatmap entry from the ML Swarm if available. "
        "Merge qualitative findings from both sources. "
        "Output ONLY the JSON object, nothing else."
    )

    return "\n".join(sections)


async def generate_report(
    job_id: str,
    patient_id: str,
    patient_context: dict[str, Any],
    swarm_result: Optional[SwarmResponse],
    medgemma_result: Optional[MedGemmaResponse],
) -> DiagnosticReport:
    """
    Call the Groq LLM to synthesize all pipeline outputs into the final report.

    Args:
        job_id: The diagnostic job identifier.
        patient_id: Patient identifier.
        patient_context: Dict with patient demographics + clinical info.
        swarm_result: ML Swarm output (may be None if the call failed).
        medgemma_result: MedGemma output (may be None if the call failed).

    Returns:
        DiagnosticReport: Validated final report object.
    """
    client = AsyncGroq(api_key=settings.groq_api_key)

    user_prompt = _build_user_prompt(patient_context, swarm_result, medgemma_result)

    logger.info("Synthesis Agent: calling Groq (%s)", settings.groq_model)

    chat_completion = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )

    raw_content = chat_completion.choices[0].message.content
    logger.info("Synthesis Agent: received %d chars from Groq", len(raw_content or ""))

    # Parse the LLM JSON response
    try:
        llm_output = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("Synthesis Agent: failed to parse LLM JSON: %s", exc)
        logger.error("Raw content: %s", raw_content[:500])
        raise ValueError(f"Synthesis Agent produced invalid JSON: {exc}") from exc

    # Build the report with the fixed fields + LLM-generated content
    report = DiagnosticReport(
        jobId=job_id,
        patientId=patient_id,
        generatedAt=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        status="draft",
        executiveSummary=llm_output.get("executiveSummary", ""),
        riskScore=_clamp(llm_output.get("riskScore", 50), 0, 100),
        shapFeatures=[
            ShapFeature(**f) for f in llm_output.get("shapFeatures", []) if _valid_shap(f)
        ],
        featureHeatmap=[
            HeatmapEntry(**h) for h in llm_output.get("featureHeatmap", []) if _valid_heatmap(h)
        ],
        qualitativeFactors=QualitativeFactors(
            riskFactors=llm_output.get("qualitativeFactors", {}).get("riskFactors", []),
            protectiveFactors=llm_output.get("qualitativeFactors", {}).get("protectiveFactors", []),
            recommendations=llm_output.get("qualitativeFactors", {}).get("recommendations", []),
        ),
    )

    logger.info(
        "Synthesis Agent: report generated — riskScore=%d, shapFeatures=%d, heatmap=%d",
        report.riskScore,
        len(report.shapFeatures),
        len(report.featureHeatmap),
    )

    return report


def _clamp(value: Any, lo: int, hi: int) -> int:
    """Clamp a value to [lo, hi], defaulting to midpoint if not numeric."""
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return (lo + hi) // 2


def _valid_shap(f: Any) -> bool:
    """Check that a SHAP feature dict has the required keys."""
    return isinstance(f, dict) and "name" in f and "impact" in f and "direction" in f


def _valid_heatmap(h: Any) -> bool:
    """Check that a heatmap entry dict has the required keys."""
    return isinstance(h, dict) and "name" in h and "value" in h
