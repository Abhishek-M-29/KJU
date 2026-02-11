"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date, datetime


# ============================================================================
# Auth Models
# ============================================================================

class LoginRequest(BaseModel):
    """Login request - doctor_id required, password accepted but not validated."""
    doctor_id: str = Field(..., description="Doctor's unique identifier")
    password: Optional[str] = Field(None, description="Password (not validated)")


class LoginResponse(BaseModel):
    """Login response."""
    success: bool
    message: str
    doctor_id: str


# ============================================================================
# Patient Models
# ============================================================================

class PatientCreate(BaseModel):
    """Request model for creating a new patient."""
    name: str = Field(..., min_length=1, description="Patient's full name")
    dob: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    sex: Literal["Male", "Female", "Other"] = Field(..., description="Patient's sex")


class PatientResponse(BaseModel):
    """Response model for a single patient."""
    patient_id: int
    name: str
    dob: Optional[date] = None
    sex: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PatientListResponse(BaseModel):
    """Response model for patient list."""
    patients: List[PatientResponse]
    count: int


class PatientDetailResponse(BaseModel):
    """Response model for detailed patient info."""
    patient_id: int
    basic_info: Optional[dict] = None
    medical_history: List[dict] = []
    appointments: List[dict] = []
    medications: List[dict] = []
    lab_reports: List[dict] = []
    reports: List[dict] = []


class PatientFilter(BaseModel):
    """Query parameters for filtering patients."""
    name: Optional[str] = Field(None, description="Filter by name (partial match)")
    sex: Optional[Literal["Male", "Female", "Other"]] = Field(None, description="Filter by sex")
    dob_from: Optional[date] = Field(None, description="Filter by DOB from date")
    dob_to: Optional[date] = Field(None, description="Filter by DOB to date")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")


# ============================================================================
# Document Models
# ============================================================================

class DocumentUpload(BaseModel):
    """Request model for uploading a document (stored in Report table)."""
    patient_id: int = Field(..., description="Patient ID this document belongs to")
    report_type: Literal["Radiology", "Pathology", "Clinical", "Discharge", "Consultation"] = Field(
        ..., description="Type of report"
    )
    report_date: date = Field(..., description="Date of the report")
    complete_report: str = Field(..., min_length=1, description="Full document text content")
    report_summary: Optional[str] = Field(None, description="Summary of the report")
    doctor_name: Optional[str] = Field(None, description="Name of the reporting doctor")


class DocumentResponse(BaseModel):
    """Response model for document upload."""
    success: bool
    message: str
    report_id: Optional[int] = None


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[dict]
    count: int
