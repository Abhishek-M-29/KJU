"""
Kju Backend - Patient Management API
=====================================
Endpoints:
  1. Login (by doctor_id)
  2. Patients (list, get, create)
  3. File Uploads

Base URL: http://localhost:8000/api
"""

import os
import sys
import json
import uuid
import logging
import base64
import mariadb
import uvicorn
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# LOGGING
# ============================================================================
logger = logging.getLogger("PatientAPI")
logger.setLevel(logging.DEBUG)
_ch = logging.StreamHandler(sys.stdout)
_ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
logger.addHandler(_ch)

# ============================================================================
# DATABASE
# ============================================================================
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3305))


@contextmanager
def get_db():
    conn = None
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
                               database=DB_NAME, port=DB_PORT)
        yield conn
    except mariadb.Error as e:
        logger.error(f"DB error: {e}")
        raise HTTPException(500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def db_exec(query: str, params: tuple = None, fetch: bool = True) -> dict:
    """Execute a DB query. Returns dict with success, data/count or lastrowid."""
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(query, params or ())
            if fetch and query.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                # Serialise dates
                for r in rows:
                    for k, v in r.items():
                        if isinstance(v, (datetime, date)):
                            r[k] = v.isoformat()
                return {"success": True, "results": rows, "count": len(rows)}
            else:
                conn.commit()
                return {"success": True, "affected": cur.rowcount, "lastrowid": cur.lastrowid}
        except mariadb.Error as e:
            logger.error(f"Query error: {e}\nQuery: {query[:200]}")
            return {"success": False, "error": str(e)}


# ============================================================================
# OCR (Mistral)
# ============================================================================
def _extract_text_from_ocr_response(ocr_response) -> str:
    if ocr_response is None:
        return ""
    data = None
    if hasattr(ocr_response, "model_dump"):
        try:
            data = ocr_response.model_dump()
        except Exception:
            data = None
    pages = []
    if hasattr(ocr_response, "pages") and ocr_response.pages is not None:
        pages = ocr_response.pages
    elif isinstance(data, dict) and isinstance(data.get("pages"), list):
        pages = data["pages"]
    elif isinstance(ocr_response, dict) and isinstance(ocr_response.get("pages"), list):
        pages = ocr_response["pages"]
    segments = []
    for p in pages:
        if p is None:
            continue
        if isinstance(p, dict):
            seg = p.get("markdown") or p.get("text") or ""
        else:
            seg = getattr(p, "markdown", None) or getattr(p, "text", "")
        if seg:
            segments.append(seg.strip())
    return "\n\n".join(segments)


def perform_ocr(file_content: bytes, filename: str) -> str:
    logger.info(f"OCR: Starting for file '{filename}' ({len(file_content)} bytes)")
    try:
        from mistralai import Mistral
    except ImportError:
        logger.error("OCR: mistralai package not installed")
        return "OCR error: mistralai package not installed"
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_key or mistral_key == "your_mistral_api_key_here":
        logger.error("OCR: MISTRAL_API_KEY not configured")
        return "OCR not configured"
    try:
        client = Mistral(api_key=mistral_key)
        b64 = base64.b64encode(file_content).decode("utf-8")
        fl = (filename or "").lower()
        if fl.endswith(".pdf"):
            logger.info("OCR: Processing as PDF document")
            resp = client.ocr.process(model="mistral-ocr-latest",
                                      document={"type": "document_url",
                                                 "document_url": f"data:application/pdf;base64,{b64}"},
                                      include_image_base64=False)
        else:
            mime = "image/png" if fl.endswith(".png") else "image/jpeg"
            logger.info(f"OCR: Processing as image ({mime})")
            resp = client.ocr.process(model="mistral-ocr-latest",
                                      document={"type": "image_url",
                                                 "image_url": f"data:{mime};base64,{b64}"},
                                      include_image_base64=False)
        logger.debug(f"OCR: Raw response type: {type(resp).__name__}")
        if hasattr(resp, 'model_dump'):
            logger.debug(f"OCR: Response dump: {json.dumps(resp.model_dump(), default=str)[:500]}")
        text = _extract_text_from_ocr_response(resp) or "No text extracted"
        logger.info(f"OCR: Extracted {len(text)} chars from '{filename}'")
        return text
    except Exception as e:
        logger.error(f"OCR: Failed for '{filename}': {e}", exc_info=True)
        return f"OCR failed: {e}"


# ============================================================================
# DB INITIALISATION
# ============================================================================
def init_db():
    """Create helper tables if missing."""
    ddl = [
        """CREATE TABLE IF NOT EXISTS Patient_Documents (
            document_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            doctor_id INT,
            document_type VARCHAR(100) NOT NULL,
            document_name VARCHAR(255) NOT NULL,
            file_size_bytes BIGINT,
            mime_type VARCHAR(100),
            ocr_text LONGTEXT,
            ocr_status VARCHAR(20) DEFAULT 'pending',
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS Diagnostic_Jobs (
            job_id VARCHAR(50) PRIMARY KEY,
            patient_id INT NOT NULL,
            doctor_id VARCHAR(50),
            observations TEXT,
            status VARCHAR(20) DEFAULT 'queued',
            current_step VARCHAR(200) DEFAULT 'Queued',
            progress INT DEFAULT 0,
            report_data LONGTEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    ]
    try:
        with get_db() as conn:
            cur = conn.cursor()
            for q in ddl:
                cur.execute(q)
            conn.commit()
        logger.info("DB tables verified.")
    except Exception as e:
        logger.warning(f"DB init warning: {e}")


# ============================================================================
# PYDANTIC SCHEMAS  (mirrors the API spec exactly)
# ============================================================================

# --- 1. Login ---
class LoginRequest(BaseModel):
    doctorId: Optional[str] = None
    medicalLicenseId: Optional[str] = None

class DoctorProfile(BaseModel):
    id: str
    name: str
    specialty: str
    medicalLicenseId: str

class LoginResponse(BaseModel):
    success: bool
    doctor: DoctorProfile

# --- 3. Patients ---
class PatientListReq(BaseModel):
    doctorId: str
    filter: Optional[str] = "all"
    search: Optional[str] = ""

class PatientListItem(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    avatar: Optional[str] = None
    symptom: str
    riskLevel: str

class PatientListResp(BaseModel):
    patients: List[PatientListItem]

class PatientGetReq(BaseModel):
    doctorId: str
    patientId: str

class Vitals(BaseModel):
    heartRate: int
    bloodPressure: str
    oxygenSaturation: int

class LabResults(BaseModel):
    glucose: int
    cholesterol: int
    creatinine: float

class RiskPoint(BaseModel):
    date: str
    score: int

class PatientFull(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    avatar: Optional[str] = None
    symptom: str
    bloodType: Optional[str] = None
    primaryCondition: Optional[str] = None
    vitals: Vitals
    labResults: LabResults
    riskLevel: str
    riskPercentage: int
    riskHistory: List[RiskPoint]
    medications: List[str]
    allergies: List[str]
    clinicalSummary: str
    lastVisit: Optional[str] = None

class PatientCreateReq(BaseModel):
    doctorId: str
    name: str
    age: int
    sex: str
    bloodType: Optional[str] = None
    primaryCondition: Optional[str] = None
    symptom: str
    vitals: Vitals
    labResults: LabResults
    medications: List[str] = []
    allergies: List[str] = []
    clinicalSummary: str = ""

# --- 5. Uploads ---
class UploadItem(BaseModel):
    uploadId: str
    fileName: str
    fileSize: int
    mimeType: str
    status: str
    ocrText: Optional[str] = None

class UploadResp(BaseModel):
    uploads: List[UploadItem]


# ============================================================================
# HELPER: compute risk level from DB scores
# ============================================================================
def _risk(row) -> tuple:
    """Return (riskLevel, riskPercentage) from a Patient_Data row dict."""
    d = float(row.get("diabetes_risk_score") or 0)
    c = float(row.get("cardiovascular_risk_score") or 0)
    mx = max(d, c)
    pct = int(mx * 100)
    if mx > 0.7:
        return "critical", pct
    elif mx > 0.3:
        return "watch", pct
    return "low", pct


def _sex(row) -> str:
    g = str(row.get("gender") or "M").strip().upper()
    return "M" if g.startswith("M") else "F"


def _symptom(row) -> str:
    s = row.get("latest_encounter_reason") or ""
    if not s and row.get("active_conditions_list"):
        parts = str(row["active_conditions_list"]).split(",")
        s = parts[0].strip() if parts else ""
    return s[:120] or "Routine checkup"


def _split(val) -> List[str]:
    if not val:
        return []
    return [x.strip() for x in str(val).split(",") if x.strip()]


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="Kju Backend API", version="2.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def _startup():
    init_db()


# ============================================================================
# 1. LOGIN   POST /api/login
# ============================================================================
@app.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    # Accept either doctorId (numeric or "doc-N") or medicalLicenseId
    if req.doctorId:
        did = req.doctorId.replace("doc-", "")
        if did.isdigit():
            r = db_exec("SELECT doctor_id, first_name, last_name, specialization, license_number "
                        "FROM Doctor WHERE doctor_id = %s", (int(did),))
        else:
            r = db_exec("SELECT doctor_id, first_name, last_name, specialization, license_number "
                        "FROM Doctor WHERE license_number = %s", (did,))
    elif req.medicalLicenseId:
        r = db_exec("SELECT doctor_id, first_name, last_name, specialization, license_number "
                    "FROM Doctor WHERE license_number = %s", (req.medicalLicenseId,))
    else:
        raise HTTPException(400, detail={"error": "Provide doctorId or medicalLicenseId", "code": "BAD_REQUEST"})

    if r["success"] and r["count"] > 0:
        d = r["results"][0]
        return LoginResponse(
            success=True,
            doctor=DoctorProfile(
                id=f"doc-{d['doctor_id']}",
                name=f"Dr. {d['first_name']} {d['last_name']}",
                specialty=d["specialization"] or "General Practice",
                medicalLicenseId=d["license_number"],
            ),
        )
    raise HTTPException(401, detail={"error": "Doctor not found", "code": "AUTH_FAILED"})


# ============================================================================
# 3. PATIENTS
# ============================================================================

# 3.1  POST /api/patients/list
@app.post("/api/patients/list", response_model=PatientListResp)
async def patients_list(req: PatientListReq):
    where = "WHERE 1=1"
    params: list = []

    # search
    if req.search:
        where += " AND (full_name LIKE %s OR CAST(patient_data_id AS CHAR) LIKE %s)"
        params += [f"%{req.search}%", f"%{req.search}%"]

    # risk filter
    if req.filter == "critical":
        where += " AND (cardiovascular_risk_score > 0.7 OR diabetes_risk_score > 0.7)"
    elif req.filter == "watch":
        where += " AND ((cardiovascular_risk_score > 0.3 AND cardiovascular_risk_score <= 0.7) OR (diabetes_risk_score > 0.3 AND diabetes_risk_score <= 0.7))"
    elif req.filter == "low":
        where += " AND cardiovascular_risk_score <= 0.3 AND diabetes_risk_score <= 0.3"

    q = f"SELECT * FROM Patient_Data {where} ORDER BY patient_data_id LIMIT 50"
    res = db_exec(q, tuple(params) if params else None)
    pts: List[PatientListItem] = []
    if res["success"]:
        for row in res["results"]:
            rl, _ = _risk(row)
            pts.append(PatientListItem(
                id=f"pat-{row['patient_data_id']}",
                name=row["full_name"] or "Unknown",
                age=row.get("age_years") or 0,
                sex=_sex(row),
                avatar=None,
                symptom=_symptom(row),
                riskLevel=rl,
            ))
    return PatientListResp(patients=pts)


# 3.2  POST /api/patients/get
@app.post("/api/patients/get", response_model=PatientFull)
async def patients_get(req: PatientGetReq):
    pid = req.patientId.replace("pat-", "")
    if not pid.isdigit():
        raise HTTPException(404, detail={"error": "Patient not found", "code": "PATIENT_NOT_FOUND"})

    res = db_exec("SELECT * FROM Patient_Data WHERE patient_data_id = %s", (int(pid),))
    if not res["success"] or res["count"] == 0:
        raise HTTPException(404, detail={"error": "Patient not found", "code": "PATIENT_NOT_FOUND"})
    p = res["results"][0]

    rl, rpct = _risk(p)

    # Risk history from AI_Risk_Assessment
    hist_res = db_exec(
        "SELECT risk_score, assessed_at FROM AI_Risk_Assessment "
        "WHERE synthea_patient_id = %s ORDER BY assessed_at DESC LIMIT 10",
        (p.get("synthea_id") or "",),
    )
    history: List[RiskPoint] = []
    if hist_res["success"]:
        for h in hist_res["results"]:
            try:
                dt = h["assessed_at"][:10] if isinstance(h["assessed_at"], str) else str(h["assessed_at"])[:10]
                sc = int(float(h["risk_score"] or 0) * 100)
                history.append(RiskPoint(date=dt, score=sc))
            except Exception:
                pass

    vitals = Vitals(
        heartRate=p.get("heart_rate") or 78,
        bloodPressure=f"{p.get('bp_systolic') or 120}/{p.get('bp_diastolic') or 80}",
        oxygenSaturation=int(float(p.get("oxygen_saturation") or 98)),
    )
    labs = LabResults(
        glucose=p.get("glucose_fasting") or p.get("glucose") or 100,
        cholesterol=p.get("cholesterol_total") or 200,
        creatinine=float(p.get("creatinine") or 1.0),
    )

    first_cond = ""
    if p.get("active_conditions_list"):
        first_cond = str(p["active_conditions_list"]).split(",")[0].strip()

    last_visit = None
    if p.get("latest_encounter_date"):
        lv = p["latest_encounter_date"]
        last_visit = lv[:10] if isinstance(lv, str) else str(lv)[:10]

    return PatientFull(
        id=f"pat-{p['patient_data_id']}",
        name=p["full_name"] or "Unknown",
        age=p.get("age_years") or 0,
        sex=_sex(p),
        avatar=None,
        symptom=_symptom(p),
        bloodType=None,
        primaryCondition=first_cond or None,
        vitals=vitals,
        labResults=labs,
        riskLevel=rl,
        riskPercentage=rpct,
        riskHistory=history,
        medications=_split(p.get("active_medications_list")),
        allergies=_split(p.get("active_allergies_list")),
        clinicalSummary=(p.get("all_observations_list") or "No clinical summary available.")[:800],
        lastVisit=last_visit,
    )


# 3.3  POST /api/patients/create
@app.post("/api/patients/create", response_model=PatientFull, status_code=201)
async def patients_create(req: PatientCreateReq):
    gender = "Male" if req.sex.upper().startswith("M") else "Female"
    new_synthea_id = f"NEW-{uuid.uuid4().hex[:12]}"
    ins = db_exec(
        "INSERT INTO Patient_Data (synthea_id, full_name, age_years, gender, latest_encounter_reason, "
        "active_conditions_list, active_medications_list, active_allergies_list) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (new_synthea_id, req.name, req.age, gender, req.symptom,
         req.primaryCondition or "",
         ", ".join(req.medications),
         ", ".join(req.allergies)),
        fetch=False,
    )
    if not ins["success"]:
        raise HTTPException(500, detail={"error": "Failed to create patient", "code": "DB_ERROR"})

    new_id = ins["lastrowid"]
    return PatientFull(
        id=f"pat-{new_id}",
        name=req.name,
        age=req.age,
        sex=req.sex,
        avatar=None,
        symptom=req.symptom,
        bloodType=req.bloodType,
        primaryCondition=req.primaryCondition,
        vitals=req.vitals,
        labResults=req.labResults,
        riskLevel="low",
        riskPercentage=0,
        riskHistory=[],
        medications=req.medications,
        allergies=req.allergies,
        clinicalSummary=req.clinicalSummary,
        lastVisit=None,
    )


# ============================================================================
# 5. FILE UPLOADS    POST /api/patients/uploads
# ============================================================================
@app.post("/api/patients/uploads", response_model=UploadResp)
async def upload_files(
    doctorId: str = Form(...),
    patientId: str = Form(...),
    files: List[UploadFile] = File(...),
):
    pid = patientId.replace("pat-", "")
    if not pid.isdigit():
        raise HTTPException(400, detail={"error": "Invalid patientId", "code": "BAD_REQUEST"})
    doc_id_str = doctorId.replace("doc-", "")
    doc_id_int = int(doc_id_str) if doc_id_str.isdigit() else None
    items: List[UploadItem] = []
    for f in files:
        content = await f.read()
        sz = len(content)
        logger.info(f"Upload: file='{f.filename}', size={sz}, mime='{f.content_type}', patient={pid}")

        # Run OCR
        ocr_text = perform_ocr(content, f.filename)
        ocr_status = "completed" if ocr_text and not ocr_text.startswith("OCR ") and not ocr_text.startswith("No text") else "failed"
        logger.info(f"Upload: OCR status={ocr_status}, text_length={len(ocr_text)}")

        ins = db_exec(
            "INSERT INTO Patient_Documents (patient_id, doctor_id, document_type, document_name, "
            "file_size_bytes, mime_type, ocr_text, ocr_status) VALUES (%s, %s, 'Upload', %s, %s, %s, %s, %s)",
            (int(pid), doc_id_int, f.filename, sz, f.content_type, ocr_text, ocr_status),
            fetch=False,
        )
        uid = ins.get("lastrowid", 0)
        items.append(UploadItem(
            uploadId=f"upl-{uid:03d}",
            fileName=f.filename,
            fileSize=sz,
            mimeType=f.content_type or "application/octet-stream",
            status=ocr_status,
            ocrText=ocr_text,
        ))
    return UploadResp(uploads=items)


# ============================================================================
# HEALTH / ROOT
# ============================================================================
@app.get("/")
async def root():
    return {"status": "ok", "message": "Kju Backend API is running"}


@app.get("/api/health")
async def health():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print("=" * 60)
    print("  Kju Backend API Server")
    print(f"  Local:   http://localhost:8000")
    print(f"  Network: http://{local_ip}:8000")
    print(f"  Docs:    http://{local_ip}:8000/docs")
    print("=" * 60)
    uvicorn.run("patient_api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
