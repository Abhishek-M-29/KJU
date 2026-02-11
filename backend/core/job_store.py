"""
In-memory job store for tracking async diagnostic pipeline runs.
Thread-safe via asyncio.Lock.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from models.report import DiagnosticReport


class JobStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class JobState(BaseModel):
    jobId: str
    patientId: str
    status: JobStatus = JobStatus.PROCESSING
    progress: int = 0
    report: Optional[DiagnosticReport] = None
    error: Optional[str] = None
    createdAt: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z"
    )


class JobStore:
    """Simple in-memory store. Jobs are lost on restart."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}
        self._lock = asyncio.Lock()

    async def create_job(self, patient_id: str) -> JobState:
        job_id = f"diag-{uuid.uuid4().hex[:8]}"
        job = JobState(jobId=job_id, patientId=patient_id)
        async with self._lock:
            self._jobs[job_id] = job
        return job

    async def update_job(
        self,
        job_id: str,
        *,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        report: Optional[DiagnosticReport] = None,
        error: Optional[str] = None,
    ) -> Optional[JobState]:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            if status is not None:
                job.status = status
            if progress is not None:
                job.progress = progress
            if report is not None:
                job.report = report
            if error is not None:
                job.error = error
            return job

    async def get_job(self, job_id: str) -> Optional[JobState]:
        async with self._lock:
            return self._jobs.get(job_id)


# Singleton instance
job_store = JobStore()
