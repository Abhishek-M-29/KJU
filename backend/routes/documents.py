"""
Document routes - Upload documents.
"""

from fastapi import APIRouter, HTTPException
from database import upload_document, get_patient
from models import DocumentUpload, DocumentResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
def upload_doc(document: DocumentUpload):
    """
    Upload a document for a patient.
    
    Documents are stored via the external API.
    
    Args:
        document: Document data
        
    Returns:
        DocumentResponse: Success status with report_id
    """
    # Call the external API to upload
    result = upload_document(
        patient_id=document.patient_id,
        report_type=document.report_type,
        report_date=str(document.report_date),
        complete_report=document.complete_report,
        report_summary=document.report_summary,
        doctor_name=document.doctor_name
    )
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to upload document")
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Patient {document.patient_id} not found")
        raise HTTPException(status_code=500, detail=error_msg)
    
    return DocumentResponse(
        success=True,
        message="Document uploaded successfully",
        report_id=result.get("report_id")
    )


@router.get("/{patient_id}")
def list_patient_documents(patient_id: int):
    """
    List all documents for a specific patient.
    
    Gets documents from the patient details endpoint.
    """
    result = get_patient(patient_id)
    
    if not result.get("success"):
        error_msg = result.get("error", "Failed to fetch patient")
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        raise HTTPException(status_code=500, detail=error_msg)
    
    patient = result.get("patient", {})
    documents = patient.get("reports", [])
    
    return {"documents": documents, "count": len(documents)}
