"""
Pydantic models for incoming API request bodies.

The DiagnosticsRunRequest accepts flexible input — the data can be structured
JSON, raw free-text, or any mix. An LLM-powered Separator will triage it into
numeric vs text paths. Only patientId and doctorId are truly required; everything
else is passed through to the Separator LLM as-is.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class DiagnosticsRunRequest(BaseModel):
    """
    Request body for POST /api/diagnostics/run.

    Accepts ANY shape of patient data. The only hard requirements are
    patientId and doctorId. Everything else (vitals, labs, notes, raw text)
    is passed as-is to the LLM Separator for intelligent triage.

    Examples of valid payloads:

    1. Structured:
       {"patientId": "p-1", "doctorId": "d-1", "age": 71, "vitals": {...}}

    2. Raw text:
       {"patientId": "p-1", "doctorId": "d-1", "data": "71yo male, BP 165/105..."}

    3. Mixed:
       {"patientId": "p-1", "doctorId": "d-1", "age": 71, "notes": "Patient presents with..."}
    """

    patientId: str
    doctorId: str

    # Everything else is optional and flexible — captured by model_config extra="allow"
    # Common fields the frontend might send (all optional):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    bloodType: Optional[str] = None
    primaryCondition: Optional[str] = None
    symptom: Optional[str] = None
    vitals: Optional[dict[str, Any]] = None
    labResults: Optional[dict[str, Any]] = None
    medications: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
    clinicalSummary: Optional[str] = None

    # Catch-all for raw text or any other data shape
    data: Optional[str] = None

    model_config = {"extra": "allow"}

    def to_raw_string(self) -> str:
        """
        Serialize the entire request payload into a single string for the
        LLM Separator. Includes ALL fields — structured and unstructured.
        """
        import json

        dump = self.model_dump(exclude_none=True, exclude={"doctorId"})
        return json.dumps(dump, indent=2, default=str)


class DiagnosticsStatusRequest(BaseModel):
    """Request body for POST /api/diagnostics/status"""

    jobId: str


class DiagnosticsReportRequest(BaseModel):
    """Request body for POST /api/diagnostics/report"""

    jobId: str
