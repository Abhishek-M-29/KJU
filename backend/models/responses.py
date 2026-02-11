"""
Pydantic models for API responses.
"""

from typing import Optional

from pydantic import BaseModel

from models.report import DiagnosticReport


class DiagnosticsRunResponse(BaseModel):
    jobId: str
    status: str = "processing"


class DiagnosticsStatusResponse(BaseModel):
    jobId: str
    status: str  # "processing" | "complete" | "failed"
    progress: int  # 0–100
    error: Optional[str] = None  # populated when status == "failed"


class ErrorResponse(BaseModel):
    error: str
    code: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "kju-ai-pipeline"
    version: str = "0.1.0"
