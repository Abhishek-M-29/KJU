"""
Authentication routes.
"""

from fastapi import APIRouter, HTTPException
from models import LoginRequest, LoginResponse
from database import login

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def do_login(request: LoginRequest):
    """
    Doctor login endpoint.
    
    Accepts doctor_id (required) and password (optional, not validated).
    Returns success if doctor_id is provided.
    """
    if not request.doctor_id or not request.doctor_id.strip():
        raise HTTPException(status_code=400, detail="Doctor ID is required")
    
    # Call the external API
    result = login(request.doctor_id, request.password)
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Login failed"))
    
    return LoginResponse(
        success=True,
        message="Login successful",
        doctor_id=request.doctor_id
    )
