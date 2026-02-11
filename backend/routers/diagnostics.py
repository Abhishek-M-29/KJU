"""
Diagnostics router — the three endpoints for the async diagnostic pipeline.

POST /api/diagnostics/run     → Kick off pipeline, return jobId (202)
POST /api/diagnostics/status  → Poll job progress
POST /api/diagnostics/report  → Fetch completed report
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from core.job_store import JobStatus, job_store
from models.requests import (
    DiagnosticsReportRequest,
    DiagnosticsRunRequest,
    DiagnosticsStatusRequest,
)
from models.responses import DiagnosticsRunResponse, DiagnosticsStatusResponse
from services.orchestrator import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.post("/run", response_model=DiagnosticsRunResponse, status_code=202)
async def diagnostics_run(
    request: DiagnosticsRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Start an async diagnostic pipeline run.

    Creates a job entry, kicks off the orchestrator in the background,
    and immediately returns the jobId for polling.
    """
    job = await job_store.create_job(patient_id=request.patientId)
    logger.info(
        "Diagnostics run started: jobId=%s, patientId=%s", job.jobId, request.patientId
    )

    # Fire the pipeline as a background task
    background_tasks.add_task(run_pipeline, job.jobId, request)

    return DiagnosticsRunResponse(jobId=job.jobId, status="processing")


@router.post("/status", response_model=DiagnosticsStatusResponse)
async def diagnostics_status(request: DiagnosticsStatusRequest):
    """
    Poll the status of a diagnostic pipeline job.

    Returns the current status and progress percentage.
    """
    job = await job_store.get_job(request.jobId)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Job {request.jobId} not found", "code": "JOB_NOT_FOUND"},
        )

    return DiagnosticsStatusResponse(
        jobId=job.jobId,
        status=job.status.value,
        progress=job.progress,
        error=job.error,
    )


@router.post("/report")
async def diagnostics_report(request: DiagnosticsReportRequest):
    """
    Fetch the completed diagnostic report for a job.

    Returns 409 if the job is still processing, 404 if not found,
    or the full report JSON if complete.
    """
    job = await job_store.get_job(request.jobId)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Job {request.jobId} not found", "code": "JOB_NOT_FOUND"},
        )

    if job.status == JobStatus.PROCESSING:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Report not ready yet — job is still processing",
                "code": "JOB_PROCESSING",
            },
        )

    if job.status == JobStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Pipeline failed: {job.error}",
                "code": "PIPELINE_FAILED",
            },
        )

    # Status is COMPLETE — return the report
    if job.report is None:
        raise HTTPException(
            status_code=500,
            detail={"error": "Job complete but report is missing", "code": "REPORT_MISSING"},
        )

    return job.report.model_dump()
