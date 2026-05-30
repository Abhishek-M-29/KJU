"""
FastAPI server for Patient Management API with MariaDB backend.
Provides endpoints for doctor authentication, patient management, and document uploads.
"""

import mariadb
import os
import logging
import sys
import os
import sys
import logging
import mariadb
import uvicorn
import base64
import json
import uuid
import random
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List, Any, Dict, Union
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add DiseaseRag to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DiseaseRag'))

try:
    from DiseaseRag.disease_rag_api import vector_db, generate_answer, DiseaseVectorDB
except ImportError:
    # If import fails (e.g. dependencies missing), define mock class
    class DiseaseVectorDB:
        def search(self, query, top_k=5): return []
        @property 
        def is_loaded(self): return False
    vector_db = DiseaseVectorDB()
    async def generate_answer(*args, **kwargs): return "RAG System Unavailable"

# Load environment variables
load_dotenv()

# =============================================================================
# LOGGING CONFIGURATION - VERBOSE
# =============================================================================

# Create logger
logger = logging.getLogger("PatientAPI")
logger.setLevel(logging.DEBUG)

# Create console handler with detailed formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create file handler for detailed logs
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patient_api.log')
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create formatters - verbose
console_format = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_format = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)-25s | Line:%(lineno)-4d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Also configure uvicorn logging to be verbose
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)

logger.info("=" * 70)
logger.info("Patient API Server - Initializing")
logger.info("=" * 70)

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

logger.info(f"Database Config: host={DB_HOST}, port={DB_PORT}, database={DB_NAME}, user={DB_USER}")

# =============================================================================
# DATABASE CONNECTION MANAGEMENT
# =============================================================================

@contextmanager
def get_db_connection():
    """Context manager for database connections with verbose logging."""
    conn = None
    try:
        logger.debug(f"Opening database connection to {DB_HOST}:{DB_PORT}/{DB_NAME}")
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        logger.debug("Database connection established successfully")
        yield conn
    except mariadb.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def execute_query(query: str, params: tuple = None, fetch: bool = True) -> dict:
    """Execute a database query with verbose logging."""
    logger.debug(f"Executing query: {query[:200]}{'...' if len(query) > 200 else ''}")
    if params:
        logger.debug(f"Query parameters: {params}")
    
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch and query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                # Convert date/datetime objects to strings for JSON serialization
                for row in results:
                    for key, value in row.items():
                        if isinstance(value, (datetime, date)):
                            row[key] = value.isoformat()
                logger.debug(f"Query returned {len(results)} rows")
                return {"success": True, "data": results, "count": len(results)}
            else:
                conn.commit()
                logger.debug(f"Query executed, {cursor.rowcount} rows affected, lastrowid={cursor.lastrowid}")
                return {"success": True, "affected_rows": cursor.rowcount, "lastrowid": cursor.lastrowid}
                
        except mariadb.Error as e:
            logger.error(f"Query execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# =============================================================================
# CREATE PATIENT_DOCUMENTS TABLE
# =============================================================================

def create_patient_documents_table():
    """Create the Patient_Documents table if it doesn't exist."""
    logger.info("Checking/Creating Patient_Documents table...")
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Patient_Documents (
        document_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        doctor_id INT,
        document_type VARCHAR(100) NOT NULL COMMENT 'e.g., Lab Report, Prescription, Imaging, Clinical Notes',
        document_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500),
        file_size_bytes BIGINT,
        mime_type VARCHAR(100),
        ocr_text LONGTEXT COMMENT 'OCR extracted text from the document',
        ocr_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
        ocr_processed_at TIMESTAMP NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        is_verified TINYINT DEFAULT 0 COMMENT '1 if document has been verified by doctor',
        verified_by INT COMMENT 'doctor_id who verified',
        verified_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES Patient_Data(patient_data_id) ON DELETE CASCADE,
        INDEX idx_patient (patient_id),
        INDEX idx_doctor (doctor_id),
        INDEX idx_document_type (document_type),
        INDEX idx_ocr_status (ocr_status),
        INDEX idx_upload_date (upload_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("✅ Patient_Documents table ready")
    except mariadb.Error as e:
        logger.error(f"Failed to create Patient_Documents table: {e}")
        raise


# =============================================================================
# DTO & SCHEMAS (Based on API Requirements)
# =============================================================================

# --- 1. Login ---
class LoginRequest(BaseModel):
    medicalLicenseId: str
    password: str

class DoctorProfile(BaseModel):
    id: str
    name: str
    specialty: str
    medicalLicenseId: str

class LoginResponse(BaseModel):
    success: bool
    doctor: DoctorProfile

# --- 2. Notifications ---
class NotificationRequest(BaseModel):
    doctorId: str

class NotificationItem(BaseModel):
    id: str
    type: str # urgent, info, warning
    message: str
    patientId: str
    timestamp: str

class NotificationResponse(BaseModel):
    notifications: List[NotificationItem]

# --- 3. Patients ---
class PatientCodeFilterRequest(BaseModel):
    doctorId: str
    filter: Optional[str] = "all"
    search: Optional[str] = ""

class PatientListItem(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    avatar: Optional[str]
    symptom: str
    riskLevel: str

class PatientListResponse(BaseModel):
    patients: List[PatientListItem]

class PatientDetailRequest(BaseModel):
    doctorId: str
    patientId: str

class PatientVitals(BaseModel):
    heartRate: int
    bloodPressure: str
    oxygenSaturation: int

class PatientLabs(BaseModel):
    glucose: int
    cholesterol: int
    creatinine: float

class RiskHistoryPoint(BaseModel):
    date: str
    score: int

class PatientDetailResponse(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    avatar: Optional[str]
    symptom: str
    bloodType: Optional[str]
    primaryCondition: Optional[str]
    vitals: PatientVitals
    labResults: PatientLabs
    riskLevel: str
    riskPercentage: int
    riskHistory: List[RiskHistoryPoint]
    medications: List[str]
    allergies: List[str]
    clinicalSummary: str
    lastVisit: Optional[str]

class PatientCreateRequest(BaseModel):
    doctorId: str
    name: str
    age: int
    sex: str
    bloodType: Optional[str]
    primaryCondition: Optional[str]
    symptom: str
    vitals: PatientVitals
    labResults: PatientLabs
    medications: List[str]
    allergies: List[str]
    clinicalSummary: str

# --- 4. Chat ---
class ChatHistoryRequest(BaseModel):
    doctorId: str
    patientId: str

class ChatMessage(BaseModel):
    id: str
    role: str # user, assistant
    content: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]

class ChatQueryRequest(BaseModel):
    doctorId: str
    patientId: str
    message: str

# --- 5. Uploads (Handled via Form Data, response model below) ---
class UploadItem(BaseModel):
    uploadId: str
    fileName: str
    fileSize: int
    mimeType: str
    status: str

class UploadResponse(BaseModel):
    uploads: List[UploadItem]

# --- 6. Diagnostics ---
class DiagnosticsRunRequest(BaseModel):
    doctorId: str
    patientId: str
    observations: str
    uploadIds: List[str]

class DiagnosticsRunResponse(BaseModel):
    jobId: str
    patientId: str
    status: str
    startedAt: str

class DiagnosticsStatusRequest(BaseModel):
    jobId: str

class DiagnosticsStatusResponse(BaseModel):
    jobId: str
    status: str
    progress: int
    currentStep: str
    startedAt: str
    completedAt: Optional[str] = None
    error: Optional[str] = None

# --- 7. Reports ---
class ReportRequest(BaseModel):
    jobId: str

class ShapFeature(BaseModel):
    name: str
    impact: float
    direction: str

class FeatureHeatmapItem(BaseModel):
    name: str
    value: float

class QualitativeFactors(BaseModel):
    riskFactors: List[str]
    protectiveFactors: List[str]
    recommendations: List[str]

class ReportResponse(BaseModel):
    jobId: str
    patientId: str
    generatedAt: str
    status: str
    executiveSummary: str
    riskScore: int
    shapFeatures: List[ShapFeature]
    featureHeatmap: List[FeatureHeatmapItem]
    qualitativeFactors: QualitativeFactors

class RebuildReportRequest(BaseModel):
    jobId: str
    doctorId: str
    doctorNotes: str

class FinalizeReportRequest(BaseModel):
    jobId: str
    doctorId: str

class FinalizeReportResponse(BaseModel):
    jobId: str
    status: str
    finalizedAt: str
    finalizedBy: str

class ExportReportRequest(BaseModel):
    jobId: str
    format: str = "pdf"
    type: str = "draft"

class CommitReportRequest(BaseModel):
    jobId: str
    doctorId: str

class CommitReportResponse(BaseModel):
    success: bool
    recordId: str
    patientId: str
    committedAt: str
    committedBy: str


# =============================================================================
# OCR FUNCTIONS (Mistral API)
# =============================================================================

def _extract_text_from_ocr_response(ocr_response) -> str:
    """
    Normalize different possible OCR response shapes to plain text.
    Supports SDK pydantic model objects or raw dict replies.
    """
    if ocr_response is None:
        return ""
    
    # If pydantic model, prefer model_dump() if available
    data = None
    if hasattr(ocr_response, "model_dump"):
        try:
            data = ocr_response.model_dump()
        except Exception:
            data = None

    pages = []
    # Priority: direct attribute .pages
    if hasattr(ocr_response, "pages") and ocr_response.pages is not None:
        pages = ocr_response.pages
    elif isinstance(data, dict) and isinstance(data.get("pages"), list):
        pages = data.get("pages")
    elif isinstance(ocr_response, dict) and isinstance(ocr_response.get("pages"), list):
        pages = ocr_response.get("pages")

    segments = []
    for p in pages:
        if p is None:
            continue
        if isinstance(p, dict):
            seg = p.get("markdown") or p.get("text") or ""
        else:  # object with attributes
            seg = getattr(p, "markdown", None) or getattr(p, "text", "")
        if seg:
            segments.append(seg.strip())
    
    return "\n\n".join(segments)


def perform_ocr(file_content: bytes, filename: str) -> str:
    """
    Perform OCR on uploaded file using Mistral AI OCR API.
    Supports images (JPEG, PNG) and PDF files.
    
    Args:
        file_content: The binary content of the uploaded file
        filename: The name of the uploaded file
        
    Returns:
        str: Extracted text from the document
    """
    import base64
    from mistralai import Mistral
    
    logger.info(f"OCR processing file: {filename}, size: {len(file_content)} bytes")
    
    # Get Mistral API key
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key or mistral_api_key == "your_mistral_api_key_here":
        logger.warning("MISTRAL_API_KEY not configured - returning placeholder")
        return "OCR not configured - please set MISTRAL_API_KEY in .env"
    
    try:
        client = Mistral(api_key=mistral_api_key)
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Determine file type based on extension
        filename_lower = filename.lower() if filename else ""
        
        if filename_lower.endswith('.pdf'):
            # PDF document
            logger.debug("Processing as PDF document")
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_content}"
                },
                include_image_base64=False
            )
        else:
            # Image file (JPEG, PNG, etc.)
            # Determine MIME type
            if filename_lower.endswith('.png'):
                mime_type = "image/png"
            elif filename_lower.endswith('.gif'):
                mime_type = "image/gif"
            elif filename_lower.endswith('.webp'):
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"  # Default to JPEG
            
            logger.debug(f"Processing as image with MIME type: {mime_type}")
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{base64_content}"
                },
                include_image_base64=False
            )
        
        # Extract text from response
        extracted_text = _extract_text_from_ocr_response(ocr_response)
        
        if extracted_text:
            logger.info(f"OCR completed successfully, extracted {len(extracted_text)} characters")
            return extracted_text
        else:
            logger.warning("OCR completed but no text was extracted")
            return "No text could be extracted from the document"
            
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        return f"OCR processing failed: {str(e)}"


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Patient Management API",
    description="API for managing patients, authentication, and clinical document uploads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    logger.info("=" * 70)
    logger.info("FastAPI Application Starting")
    logger.info("=" * 70)
    
    try:
        create_patient_documents_table()
        logger.info("✅ Database initialization complete")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    logger.debug("Root endpoint accessed")
    return {"status": "ok", "message": "Patient Management API is running"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


# -----------------------------------------------------------------------------
# AUTHENTICATION
# -----------------------------------------------------------------------------

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Doctor authentication endpoint.
    Authenticates doctor by doctor_id only (no password required).
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "doctor_id": 1  // Required: Integer - The doctor's ID
    }
    ```
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/login" \
         -H "Content-Type: application/json" \
         -d '{"doctor_id": 1}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "message": "Login successful",
        "doctor_id": 1,
        "doctor_name": "Dr. Robert Jones",
        "specialization": "Pulmonology"
    }
    ```
    
    **Error Response (401):**
    ```json
    {
        "detail": "Doctor not found or not available"
    }
    ```
    """
    logger.info(f"Login attempt for doctor_id: {request.doctor_id}")
    
    query = """
    SELECT doctor_id, first_name, last_name, specialization 
    FROM Doctor 
    WHERE doctor_id = %s AND is_available = 1
    """
    
    result = execute_query(query, (request.doctor_id,))
    
    if result["success"] and result["count"] > 0:
        doctor = result["data"][0]
        doctor_name = f"Dr. {doctor['first_name']} {doctor['last_name']}"
        logger.info(f"Login successful for doctor: {doctor_name}")
        return LoginResponse(
            success=True,
            message="Login successful",
            doctor_id=doctor["doctor_id"],
            doctor_name=doctor_name,
            specialization=doctor.get("specialization")
        )
    else:
        logger.warning(f"Login failed for doctor_id: {request.doctor_id} - Doctor not found or not available")
        raise HTTPException(status_code=401, detail="Doctor not found or not available")


# -----------------------------------------------------------------------------
# PATIENT MANAGEMENT
# -----------------------------------------------------------------------------

@app.post("/api/patients/list", response_model=PatientListResponse)
async def list_patients(request: PatientListRequest):
    """
    List all patients with pagination (no filters).
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "limit": 100,   // Optional: Integer - Max results (default: 100)
        "offset": 0     // Optional: Integer - Pagination offset (default: 0)
    }
    ```
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/patients/list" \
         -H "Content-Type: application/json" \
         -d '{"limit": 10, "offset": 0}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "patients": [
            {
                "patient_id": 1,
                "name": "Barbara Rodriguez",
                "dob": "1985-03-15",
                "sex": "Female",
                "age": 40,
                "created_at": "2026-01-15T10:30:00",
                "updated_at": "2026-01-15T10:30:00"
            }
        ],
        "total_count": 1
    }
    ```
    """
    logger.info(f"Listing all patients with pagination: limit={request.limit}, offset={request.offset}")
    
    # Get total count
    count_query = "SELECT COUNT(*) as total FROM Patient_Data"
    count_result = execute_query(count_query)
    total_count = count_result["data"][0]["total"] if count_result["success"] else 0
    
    # Get patients with pagination
    query = """
    SELECT p.patient_data_id as patient_id, p.full_name as name, p.birthdate as dob, p.gender as sex, p.created_at, p.updated_at,
           TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) as age
    FROM Patient_Data p
    ORDER BY p.patient_data_id
    LIMIT %s OFFSET %s
    """
    
    result = execute_query(query, (request.limit, request.offset))
    
    if result["success"]:
        logger.info(f"Found {result['count']} patients (total: {total_count})")
        return PatientListResponse(
            success=True,
            patients=result["data"],
            total_count=total_count
        )
    else:
        logger.error("Failed to list patients")
        raise HTTPException(status_code=500, detail="Failed to retrieve patients")


@app.post("/api/patients/filter", response_model=PatientListResponse)
async def filter_patients(request: PatientFilterRequest):
    """
    Filter patients with various criteria.
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "doctor_id": 1,           // Optional: Integer - Filter by assigned doctor
        "name_filter": "John",    // Optional: String - Partial name match (case-insensitive)
        "sex": "Male",            // Optional: String - "Male", "Female", or "Other"
        "min_age": 18,            // Optional: Integer - Minimum age
        "max_age": 65,            // Optional: Integer - Maximum age
        "limit": 100,             // Optional: Integer - Max results (default: 100)
        "offset": 0               // Optional: Integer - Pagination offset (default: 0)
    }
    ```
    
    **Example Requests:**
    
    Filter by name:
    ```bash
    curl -X POST "http://localhost:8000/api/patients/filter" \
         -H "Content-Type: application/json" \
         -d '{"name_filter": "Barbara"}'
    ```
    
    Filter by sex and age range:
    ```bash
    curl -X POST "http://localhost:8000/api/patients/filter" \
         -H "Content-Type: application/json" \
         -d '{"sex": "Female", "min_age": 30, "max_age": 50}'
    ```
    
    Filter by doctor:
    ```bash
    curl -X POST "http://localhost:8000/api/patients/filter" \
         -H "Content-Type: application/json" \
         -d '{"doctor_id": 1}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "patients": [
            {
                "patient_id": 1,
                "name": "Barbara Rodriguez",
                "dob": "1985-03-15",
                "sex": "Female",
                "age": 40,
                "created_at": "2026-01-15T10:30:00",
                "updated_at": "2026-01-15T10:30:00"
            }
        ],
        "total_count": 1
    }
    ```
    """
    logger.info(f"Filtering patients with: {request.dict()}")
    
    # Build dynamic query based on filters
    conditions = []
    params = []
    
    base_query = """
    SELECT p.patient_data_id as patient_id, p.full_name as name, p.birthdate as dob, p.gender as sex, p.created_at, p.updated_at,
           TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) as age
    FROM Patient_Data p
    """
    
    # Add join for doctor filter
    if request.doctor_id:
        base_query += " LEFT JOIN Patient_Doctor pd ON p.patient_data_id = pd.patient_id"
        conditions.append("pd.doctor_id = %s")
        params.append(request.doctor_id)
    
    if request.name_filter:
        conditions.append("p.full_name LIKE %s")
        params.append(f"%{request.name_filter}%")
    
    if request.sex:
        conditions.append("p.gender = %s")
        params.append(request.sex)
    
    if request.min_age is not None:
        conditions.append("TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) >= %s")
        params.append(request.min_age)
    
    if request.max_age is not None:
        conditions.append("TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) <= %s")
        params.append(request.max_age)
    
    # Build WHERE clause
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    # Get total count first
    count_query = f"SELECT COUNT(*) as total FROM ({base_query}) as subquery"
    count_result = execute_query(count_query, tuple(params) if params else None)
    total_count = count_result["data"][0]["total"] if count_result["success"] else 0
    
    # Add pagination
    base_query += " ORDER BY p.patient_data_id LIMIT %s OFFSET %s"
    params.extend([request.limit, request.offset])
    
    result = execute_query(base_query, tuple(params))
    
    if result["success"]:
        logger.info(f"Found {result['count']} patients matching filters (total: {total_count})")
        return PatientListResponse(
            success=True,
            patients=result["data"],
            total_count=total_count
        )
    else:
        logger.error("Failed to filter patients")
        raise HTTPException(status_code=500, detail="Failed to filter patients")


@app.post("/api/patients/get", response_model=PatientGetResponse)
async def get_patient(request: PatientGetRequest):
    """
    Get detailed information for a single patient including medical history,
    appointments, medications, and documents.
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "patient_id": 1  // Required: Integer - The patient's ID
    }
    ```
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/patients/get" \
         -H "Content-Type: application/json" \
         -d '{"patient_id": 1}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "patient": {
            "patient_id": 1,
            "name": "Barbara Rodriguez",
            "dob": "1985-03-15",
            "sex": "Female",
            "age": 40,
            "doctors": [{"doctor_id": 1, "first_name": "Robert", "last_name": "Jones"}],
            "medical_history": [...],
            "recent_appointments": [...],
            "medications": [...],
            "documents": [...]
        },
        "message": "Patient found"
    }
    ```
    
    **Not Found Response (200 with success=false):**
    ```json
    {
        "success": false,
        "patient": null,
        "message": "Patient not found"
    }
    ```
    """
    logger.info(f"Getting patient details for patient_id: {request.patient_id}")
    
    # Get basic patient info (mapped from Patient_Data)
    patient_query = """
    SELECT p.patient_data_id as patient_id, p.full_name as name, p.birthdate as dob, p.gender as sex, p.created_at, p.updated_at,
           TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) as age
    FROM Patient_Data p
    WHERE p.patient_data_id = %s
    """
    
    result = execute_query(patient_query, (request.patient_id,))
    
    if not result["success"] or result["count"] == 0:
        logger.warning(f"Patient not found: {request.patient_id}")
        return PatientGetResponse(
            success=False,
            patient=None,
            message="Patient not found"
        )
    
    patient = result["data"][0]
    
    # Get assigned doctors
    doctors_query = """
    SELECT d.doctor_id, d.first_name, d.last_name, d.specialization, pd.is_primary_doctor
    FROM Doctor d
    JOIN Patient_Doctor pd ON d.doctor_id = pd.doctor_id
    WHERE pd.patient_id = %s
    """
    doctors_result = execute_query(doctors_query, (request.patient_id,))
    patient["doctors"] = doctors_result["data"] if doctors_result["success"] else []
    
    # Get medical history
    history_query = """
    SELECT history_id, history_type, history_item, history_details, history_date, severity, is_active
    FROM Medical_History
    WHERE patient_id = %s
    ORDER BY history_date DESC
    """
    history_result = execute_query(history_query, (request.patient_id,))
    patient["medical_history"] = history_result["data"] if history_result["success"] else []
    
    # Get appointments
    appointments_query = """
    SELECT appointment_id, appointment_date, appointment_time, status, appointment_type, doctor_name, notes
    FROM Appointment
    WHERE patient_id = %s
    ORDER BY appointment_date DESC
    LIMIT 10
    """
    appointments_result = execute_query(appointments_query, (request.patient_id,))
    patient["recent_appointments"] = appointments_result["data"] if appointments_result["success"] else []
    
    # Get medications
    medications_query = """
    SELECT medication_id, medicine_name, dosage, frequency, prescribed_date, is_continued
    FROM Medication
    WHERE patient_id = %s
    ORDER BY prescribed_date DESC
    """
    medications_result = execute_query(medications_query, (request.patient_id,))
    patient["medications"] = medications_result["data"] if medications_result["success"] else []
    
    # Get documents
    documents_query = """
    SELECT document_id, document_type, document_name, upload_date, ocr_status, is_verified
    FROM Patient_Documents
    WHERE patient_id = %s
    ORDER BY upload_date DESC
    """
    documents_result = execute_query(documents_query, (request.patient_id,))
    patient["documents"] = documents_result["data"] if documents_result["success"] else []
    
    logger.info(f"Successfully retrieved patient details for: {patient['name']}")
    return PatientGetResponse(
        success=True,
        patient=patient,
        message="Patient found"
    )


@app.post("/api/patients/create", response_model=PatientCreateResponse)
async def create_patient(request: PatientCreateRequest):
    """
    Create a new patient record.
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "name": "John Doe",       // Required: String - Full name of the patient
        "dob": "1990-05-15",      // Optional: String - Date of birth (YYYY-MM-DD format)
        "sex": "Male",            // Optional: String - "Male", "Female", or "Other"
        "doctor_id": 1            // Optional: Integer - Assign a primary doctor
    }
    ```
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/patients/create" \
         -H "Content-Type: application/json" \
         -d '{"name": "John Doe", "dob": "1990-05-15", "sex": "Male", "doctor_id": 1}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "message": "Patient created successfully",
        "patient_id": 3
    }
    ```
    
    **Error Response (400 - Invalid sex value):**
    ```json
    {
        "detail": "Sex must be 'Male', 'Female', or 'Other'"
    }
    ```
    """
    logger.info(f"Creating new patient: {request.name}")
    
    # Validate sex if provided
    if request.sex and request.sex not in ['Male', 'Female', 'Other']:
        logger.warning(f"Invalid sex value: {request.sex}")
        raise HTTPException(status_code=400, detail="Sex must be 'Male', 'Female', or 'Other'")
    
    # Build insert query
    columns = ["name"]
    values = [request.name]
    placeholders = ["%s"]
    
    if request.dob:
        columns.append("dob")
        values.append(request.dob)
        placeholders.append("%s")
    
    if request.sex:
        columns.append("sex")
        values.append(request.sex)
        placeholders.append("%s")
    
    insert_query = f"""
    INSERT INTO Patient ({', '.join(columns)})
    VALUES ({', '.join(placeholders)})
    """
    
    result = execute_query(insert_query, tuple(values), fetch=False)
    
    if result["success"] and result["lastrowid"]:
        patient_id = result["lastrowid"]
        logger.info(f"Created patient with ID: {patient_id}")
        
        # If doctor_id provided, create Patient_Doctor relationship
        if request.doctor_id:
            assign_query = """
            INSERT INTO Patient_Doctor (patient_id, doctor_id, is_primary_doctor)
            VALUES (%s, %s, 1)
            """
            try:
                execute_query(assign_query, (patient_id, request.doctor_id), fetch=False)
                logger.info(f"Assigned doctor {request.doctor_id} to patient {patient_id}")
            except Exception as e:
                logger.warning(f"Failed to assign doctor: {e}")
        
        return PatientCreateResponse(
            success=True,
            message="Patient created successfully",
            patient_id=patient_id
        )
    else:
        logger.error("Failed to create patient")
        raise HTTPException(status_code=500, detail="Failed to create patient")


# -----------------------------------------------------------------------------
# DOCUMENT MANAGEMENT
# -----------------------------------------------------------------------------

@app.post("/api/documents/list", response_model=DocumentListResponse)
async def list_patient_documents(request: DocumentListRequest):
    """
    Get all documents for a specific patient.
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "patient_id": 1,              // Required: Integer - The patient's ID
        "document_type": "Lab Report", // Optional: String - Filter by document type
        "limit": 100,                  // Optional: Integer - Max results (default: 100)
        "offset": 0                    // Optional: Integer - Pagination offset (default: 0)
    }
    ```
    
    **Example Requests:**
    
    Get all documents for a patient:
    ```bash
    curl -X POST "http://localhost:8000/api/documents/list" \
         -H "Content-Type: application/json" \
         -d '{"patient_id": 1}'
    ```
    
    Get only Lab Reports:
    ```bash
    curl -X POST "http://localhost:8000/api/documents/list" \
         -H "Content-Type: application/json" \
         -d '{"patient_id": 1, "document_type": "Lab Report"}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "documents": [
            {
                "document_id": 1,
                "document_type": "Lab Report",
                "document_name": "blood_test.pdf",
                "upload_date": "2026-02-10T14:30:00",
                "ocr_status": "completed",
                "ocr_text": "Patient Name: John Doe...",
                "is_verified": 1,
                "notes": "Annual checkup results"
            }
        ],
        "total_count": 1,
        "patient_id": 1
    }
    ```
    """
    logger.info(f"Listing documents for patient_id: {request.patient_id}")
    
    # Verify patient exists
    check_query = "SELECT patient_data_id as patient_id, full_name as name FROM Patient_Data WHERE patient_data_id = %s"
    check_result = execute_query(check_query, (request.patient_id,))
    if not check_result["success"] or check_result["count"] == 0:
        logger.warning(f"Patient not found: {request.patient_id}")
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Build query with optional document_type filter
    conditions = ["patient_id = %s"]
    params = [request.patient_id]
    
    if request.document_type:
        conditions.append("document_type = %s")
        params.append(request.document_type)
    
    where_clause = " AND ".join(conditions)
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM Patient_Documents WHERE {where_clause}"
    count_result = execute_query(count_query, tuple(params))
    total_count = count_result["data"][0]["total"] if count_result["success"] else 0
    
    # Get documents with pagination
    query = f"""
    SELECT document_id, patient_id, doctor_id, document_type, document_name, 
           file_path, file_size_bytes, mime_type, ocr_text, ocr_status, 
           ocr_processed_at, upload_date, notes, is_verified, verified_by, 
           verified_at, created_at, updated_at
    FROM Patient_Documents
    WHERE {where_clause}
    ORDER BY upload_date DESC
    LIMIT %s OFFSET %s
    """
    params.extend([request.limit, request.offset])
    
    result = execute_query(query, tuple(params))
    
    if result["success"]:
        logger.info(f"Found {result['count']} documents for patient {request.patient_id} (total: {total_count})")
        return DocumentListResponse(
            success=True,
            documents=result["data"],
            total_count=total_count,
            patient_id=request.patient_id
        )
    else:
        logger.error("Failed to list documents")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")


@app.post("/api/documents/get", response_model=DocumentGetResponse)
async def get_document(request: DocumentGetRequest):
    """
    Get a specific document by document_id.
    
    **Request Format:** JSON
    
    **Content-Type:** application/json
    
    **Request Body:**
    ```json
    {
        "document_id": 1  // Required: Integer - The document's ID
    }
    ```
    
    **Example Request:**
    ```bash
    curl -X POST "http://localhost:8000/api/documents/get" \
         -H "Content-Type: application/json" \
         -d '{"document_id": 1}'
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "document": {
            "document_id": 1,
            "patient_id": 1,
            "patient_name": "John Doe",
            "doctor_id": 1,
            "document_type": "Lab Report",
            "document_name": "blood_test.pdf",
            "ocr_text": "Full OCR extracted text...",
            "ocr_status": "completed",
            "upload_date": "2026-02-10T14:30:00",
            "is_verified": 1,
            "notes": "Annual checkup results"
        },
        "message": "Document found"
    }
    ```
    
    **Not Found Response (200 with success=false):**
    ```json
    {
        "success": false,
        "document": null,
        "message": "Document not found"
    }
    ```
    """
    logger.info(f"Getting document details for document_id: {request.document_id}")
    
    query = """
    SELECT d.document_id, d.patient_id, p.full_name as patient_name, d.doctor_id, 
           d.document_type, d.document_name, d.file_path, d.file_size_bytes, 
           d.mime_type, d.ocr_text, d.ocr_status, d.ocr_processed_at, 
           d.upload_date, d.notes, d.is_verified, d.verified_by, d.verified_at,
           d.created_at, d.updated_at
    FROM Patient_Documents d
    JOIN Patient_Data p ON d.patient_id = p.patient_data_id
    WHERE d.document_id = %s
    """
    
    result = execute_query(query, (request.document_id,))
    
    if result["success"] and result["count"] > 0:
        logger.info(f"Found document: {result['data'][0]['document_name']}")
        return DocumentGetResponse(
            success=True,
            document=result["data"][0],
            message="Document found"
        )
    else:
        logger.warning(f"Document not found: {request.document_id}")
        return DocumentGetResponse(
            success=False,
            document=None,
            message="Document not found"
        )


# -----------------------------------------------------------------------------
# DOCUMENT UPLOAD
# -----------------------------------------------------------------------------

@app.post("/api/patients/uploads", response_model=DocumentUploadResponse)
async def upload_document(
    patient_id: int = Form(..., description="Patient ID"),
    doctor_id: Optional[int] = Form(None, description="Doctor ID who uploads"),
    document_type: str = Form(..., description="Type of document (e.g., Lab Report, Prescription)"),
    notes: Optional[str] = Form(None, description="Additional notes"),
    file: UploadFile = File(..., description="Clinical document file")
):
    """
    Upload a clinical document for a patient.
    Performs OCR (placeholder - returns 'Done' for now).
    
    **Request Format:** multipart/form-data
    
    **Content-Type:** multipart/form-data
    
    **Form Fields:**
    - `patient_id` (Required): Integer - The patient's ID
    - `doctor_id` (Optional): Integer - The uploading doctor's ID
    - `document_type` (Required): String - Type of document
      - Examples: "Lab Report", "Prescription", "Imaging", "Clinical Notes", "Discharge Summary"
    - `notes` (Optional): String - Additional notes about the document
    - `file` (Required): File - The clinical document file (PDF, image, etc.)
    
    **Example Request (curl):**
    ```bash
    curl -X POST "http://localhost:8000/api/patients/uploads" \
         -F "patient_id=1" \
         -F "doctor_id=1" \
         -F "document_type=Lab Report" \
         -F "notes=Blood test results from 2026-02-10" \
         -F "file=@/path/to/document.pdf"
    ```
    
    **Example Request (JavaScript/Fetch):**
    ```javascript
    const formData = new FormData();
    formData.append('patient_id', '1');
    formData.append('doctor_id', '1');
    formData.append('document_type', 'Lab Report');
    formData.append('notes', 'Blood test results');
    formData.append('file', fileInput.files[0]);
    
    fetch('http://localhost:8000/api/patients/uploads', {
        method: 'POST',
        body: formData
    });
    ```
    
    **Success Response (200):**
    ```json
    {
        "success": true,
        "message": "Document uploaded and processed successfully",
        "document_id": 1,
        "ocr_result": "Done"
    }
    ```
    
    **Error Response (404 - Patient not found):**
    ```json
    {
        "detail": "Patient not found"
    }
    ```
    """
    logger.info(f"Document upload for patient_id: {patient_id}, file: {file.filename}")
    logger.debug(f"Document type: {document_type}, doctor_id: {doctor_id}")
    
    # Verify patient exists
    check_query = "SELECT patient_data_id as patient_id, full_name as name FROM Patient_Data WHERE patient_data_id = %s"
    check_result = execute_query(check_query, (patient_id,))
    if not check_result["success"] or check_result["count"] == 0:
        logger.warning(f"Patient not found: {patient_id}")
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
        logger.debug(f"File read successfully, size: {file_size} bytes, content_type: {file.content_type}")
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")
    
    # Perform OCR (placeholder)
    ocr_result = perform_ocr(file_content, file.filename)
    logger.info(f"OCR result: {ocr_result}")
    
    # Store document record in database
    insert_query = """
    INSERT INTO Patient_Documents 
    (patient_id, doctor_id, document_type, document_name, file_size_bytes, mime_type, 
     ocr_text, ocr_status, ocr_processed_at, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', NOW(), %s)
    """
    
    params = (
        patient_id,
        doctor_id,
        document_type,
        file.filename,
        file_size,
        file.content_type,
        ocr_result,
        notes
    )
    
    result = execute_query(insert_query, params, fetch=False)
    
    if result["success"] and result["lastrowid"]:
        document_id = result["lastrowid"]
        logger.info(f"Document stored with ID: {document_id}")
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded and processed successfully",
            document_id=document_id,
            ocr_result=ocr_result
        )
    else:
        logger.error("Failed to store document record")
        raise HTTPException(status_code=500, detail="Failed to store document")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def get_local_ip():
    """Get the local network IP address."""
    import socket
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    import uvicorn
    
    local_ip = get_local_ip()
    
    logger.info("=" * 70)
    logger.info("Starting Patient API Server")
    logger.info("=" * 70)
    logger.info(f"Local:   http://localhost:8000")
    logger.info(f"Network: http://{local_ip}:8000")
    logger.info("=" * 70)
    logger.info("API Documentation:")
    logger.info(f"  - http://localhost:8000/docs")
    logger.info(f"  - http://{local_ip}:8000/docs")
    logger.info("=" * 70)
    
    print("\n" + "=" * 70)
    print("🚀 Patient API Server Starting")
    print("=" * 70)
    print(f"  Local:   http://localhost:8000")
    print(f"  Network: http://{local_ip}:8000")
    print("=" * 70)
    print(f"  API Docs: http://{local_ip}:8000/docs")
    print("=" * 70 + "\n")
    
    uvicorn.run(
        "patient_api:app",
        host="0.0.0.0",  # Accessible from network
        port=8000,
        reload=True,
        log_level="debug",  # Verbose logging
        access_log=True
    )
