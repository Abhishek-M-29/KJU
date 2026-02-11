"""
Patient routes - CRUD operations for patients.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date

from database import list_patients, filter_patients, get_patient, create_patient
from models import (
    PatientCreate, 
    PatientResponse, 
    PatientListResponse,
    PatientDetailResponse
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=PatientListResponse)
def get_patients(limit: int = Query(100, ge=1, le=1000, description="Maximum patients to return")):
    """
    List all patients.
    
    Returns:
        PatientListResponse: List of patients with count
    """
    result = list_patients(limit)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch patients"))
    
    patients = []
    for row in result.get("patients", []):
        patients.append(PatientResponse(
            patient_id=row["patient_id"],
            name=row["name"],
            dob=row.get("dob"),
            sex=row.get("sex"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        ))
    
    return PatientListResponse(patients=patients, count=len(patients))


@router.get("/filter", response_model=PatientListResponse)
def get_filtered_patients(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    sex: Optional[str] = Query(None, description="Filter by sex (Male/Female/Other)"),
    dob_from: Optional[date] = Query(None, description="Filter by DOB from date"),
    dob_to: Optional[date] = Query(None, description="Filter by DOB to date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """
    Filter patients by various criteria.
    """
    result = filter_patients(
        name=name,
        sex=sex,
        dob_from=str(dob_from) if dob_from else None,
        dob_to=str(dob_to) if dob_to else None,
        limit=limit
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to filter patients"))
    
    patients = []
    for row in result.get("patients", []):
        patients.append(PatientResponse(
            patient_id=row["patient_id"],
            name=row["name"],
            dob=row.get("dob"),
            sex=row.get("sex"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        ))
    
    return PatientListResponse(patients=patients, count=len(patients))


@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient_by_id(patient_id: int):
    """
    Get comprehensive details for a specific patient.
    """
    result = get_patient(patient_id)
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to fetch patient")
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        raise HTTPException(status_code=500, detail=error_msg)
    
    patient = result.get("patient", {})
    
    return PatientDetailResponse(
        patient_id=patient_id,
        basic_info={
            "patient_id": patient.get("patient_id"),
            "name": patient.get("name"),
            "dob": patient.get("dob"),
            "sex": patient.get("sex"),
            "age": patient.get("age"),
            "created_at": patient.get("created_at"),
            "updated_at": patient.get("updated_at")
        },
        medical_history=patient.get("medical_history", []),
        appointments=patient.get("recent_appointments", []),
        medications=patient.get("medications", []),
        lab_reports=patient.get("lab_reports", []),
        reports=patient.get("reports", [])
    )


@router.post("", response_model=PatientResponse, status_code=201)
def create_new_patient(patient: PatientCreate):
    """
    Create a new patient.
    """
    result = create_patient(
        name=patient.name,
        dob=str(patient.dob),
        sex=patient.sex
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to create patient"))
    
    created = result.get("patient", {})
    return PatientResponse(
        patient_id=created.get("patient_id"),
        name=created.get("name"),
        dob=created.get("dob"),
        sex=created.get("sex"),
        created_at=created.get("created_at"),
        updated_at=created.get("updated_at")
    )
