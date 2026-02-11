"""
Database helper that calls the external Patient API.
No direct database credentials needed - calls the API server.
"""

import httpx
from typing import Optional, Dict, Any

# External API URL
API_BASE_URL = "http://172.18.4.108:8000"


def call_api(endpoint: str, data: Dict[str, Any] = None, method: str = "POST") -> Dict[str, Any]:
    """
    Call the external API.
    
    Args:
        endpoint: API endpoint (e.g., "/api/patients/list")
        data: Request body as dictionary
        method: HTTP method (GET or POST)
        
    Returns:
        dict: API response or error
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        with httpx.Client(timeout=30.0) as client:
            if method == "GET":
                response = client.get(url)
            else:
                response = client.post(url, json=data or {})
            
            response.raise_for_status()
            return response.json()
            
    except httpx.ConnectError:
        return {"success": False, "error": f"Cannot connect to API at {API_BASE_URL}"}
    except httpx.TimeoutException:
        return {"success": False, "error": "API request timeout"}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"API error: {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"API call failed: {str(e)}"}


def list_patients(limit: int = 100) -> Dict[str, Any]:
    """List all patients."""
    return call_api("/api/patients/list", {"limit": limit})


def filter_patients(name: str = None, sex: str = None, dob_from: str = None, dob_to: str = None, limit: int = 100) -> Dict[str, Any]:
    """Filter patients by criteria."""
    data = {"limit": limit}
    if name:
        data["name"] = name
    if sex:
        data["sex"] = sex
    if dob_from:
        data["dob_from"] = dob_from
    if dob_to:
        data["dob_to"] = dob_to
    return call_api("/api/patients/filter", data)


def get_patient(patient_id: int) -> Dict[str, Any]:
    """Get patient by ID with full details."""
    return call_api("/api/patients/get", {"patient_id": patient_id})


def create_patient(name: str, dob: str, sex: str) -> Dict[str, Any]:
    """Create a new patient."""
    return call_api("/api/patients/create", {
        "name": name,
        "dob": dob,
        "sex": sex
    })


def upload_document(patient_id: int, report_type: str, report_date: str, 
                    complete_report: str, report_summary: str = None, 
                    doctor_name: str = None) -> Dict[str, Any]:
    """Upload a document for a patient."""
    return call_api("/api/patients/uploads", {
        "patient_id": patient_id,
        "report_type": report_type,
        "report_date": report_date,
        "complete_report": complete_report,
        "report_summary": report_summary,
        "doctor_name": doctor_name
    })


def login(doctor_id: str, password: str = None) -> Dict[str, Any]:
    """Doctor login."""
    return call_api("/api/login", {
        "doctor_id": doctor_id,
        "password": password or ""
    })


def check_connection() -> Dict[str, Any]:
    """Check if API is reachable."""
    result = call_api("/api/health", method="GET")
    if result.get("success") or "error" not in result:
        return {"status": "connected", "server": API_BASE_URL}
    return {"status": "error", "message": result.get("error", "Unknown error")}
