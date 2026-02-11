"""
Kju Backend — Unified API
==========================
Combines:
  • Patient Management  (login, patients CRUD, file uploads + OCR)
  • Disease RAG          (FAISS vector search + Groq/Ollama LLM answers)
  • JSON Transformer     (field-path & natural-language JSON transforms)

Single server on port 8000.
  Patient routes  →  /api/login, /api/patients/*
  RAG routes      →  /api/rag/*
  Transform routes→  /api/transform/*
  Health          →  /, /api/health
"""

import os
import re
import sys
import copy
import json
import uuid
import logging
import base64
import pickle
import asyncio
import mariadb
import uvicorn
import numpy as np
import httpx
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Any, Dict, Union
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# LOGGING  (verbose, single logger for the whole backend)
# ============================================================================
logger = logging.getLogger("KjuBackend")
logger.setLevel(logging.DEBUG)
_ch = logging.StreamHandler(sys.stdout)
_ch.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
))
logger.addHandler(_ch)

# ============================================================================
# SHARED CONFIG — Groq (primary) + Ollama (fallback)
# ============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

logger.info(f"LLM Config — Groq model: {GROQ_MODEL} | Ollama fallback: {OLLAMA_MODEL}")

# ============================================================================
# DATABASE  (MariaDB)
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
        logger.error(f"DB connection error: {e}")
        raise HTTPException(500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def db_exec(query: str, params: tuple = None, fetch: bool = True) -> dict:
    """Execute a DB query. Returns dict with success + data/lastrowid."""
    logger.debug(f"DB exec: {query[:120]}… | params={params}")
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(query, params or ())
            if fetch and query.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                for r in rows:
                    for k, v in r.items():
                        if isinstance(v, (datetime, date)):
                            r[k] = v.isoformat()
                logger.debug(f"DB returned {len(rows)} rows")
                return {"success": True, "results": rows, "count": len(rows)}
            else:
                conn.commit()
                logger.debug(f"DB affected {cur.rowcount} rows, lastrowid={cur.lastrowid}")
                return {"success": True, "affected": cur.rowcount, "lastrowid": cur.lastrowid}
        except mariadb.Error as e:
            logger.error(f"Query error: {e}\nQuery: {query[:200]}")
            return {"success": False, "error": str(e)}


# ============================================================================
# SHARED LLM HELPERS  (used by RAG + JSON Transformer)
# ============================================================================
async def _call_groq(system_prompt: str, user_prompt: str,
                     temperature: float = 0.3, max_tokens: int = 2000) -> Optional[str]:
    """Call Groq chat-completions. Returns raw content string or None on failure."""
    logger.info(f"LLM [Groq] calling model={GROQ_MODEL}, temp={temperature}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                         "Content-Type": "application/json"},
                json={"model": GROQ_MODEL,
                      "messages": [{"role": "system", "content": system_prompt},
                                   {"role": "user", "content": user_prompt}],
                      "temperature": temperature,
                      "max_tokens": max_tokens},
            )
            if resp.status_code != 200:
                logger.warning(f"LLM [Groq] HTTP {resp.status_code}: {resp.text[:300]}")
                return None
            content = resp.json()["choices"][0]["message"]["content"]
            logger.info(f"LLM [Groq] success — {len(content)} chars returned")
            return content
    except Exception as e:
        logger.error(f"LLM [Groq] exception: {e}")
        return None


async def _call_ollama(system_prompt: str, user_prompt: str,
                       temperature: float = 0.3, max_tokens: int = 2000) -> Optional[str]:
    """Call Ollama generate. Returns raw content string or None on failure."""
    logger.info(f"LLM [Ollama] calling model={OLLAMA_MODEL}, temp={temperature}")
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": full_prompt,
                      "stream": False,
                      "options": {"temperature": temperature, "num_predict": max_tokens}},
            )
            if resp.status_code != 200:
                logger.warning(f"LLM [Ollama] HTTP {resp.status_code}")
                return None
            content = resp.json().get("response", "")
            logger.info(f"LLM [Ollama] success — {len(content)} chars returned")
            return content
    except httpx.ConnectError:
        logger.error("LLM [Ollama] connection refused — is Ollama running?")
        return None
    except Exception as e:
        logger.error(f"LLM [Ollama] exception: {e}")
        return None


async def llm_generate(system_prompt: str, user_prompt: str, *,
                       temperature: float = 0.3, max_tokens: int = 2000,
                       force_ollama: bool = False) -> str:
    """Groq-first with Ollama fallback. Always returns a string (never None)."""
    if not force_ollama:
        result = await _call_groq(system_prompt, user_prompt, temperature, max_tokens)
        if result:
            return result
        logger.warning("LLM fallback → Ollama")
    result = await _call_ollama(system_prompt, user_prompt, temperature, max_tokens)
    return result or "⚠️ Both Groq and Ollama failed to generate a response."


def _strip_llm_fences(text: str) -> str:
    """Remove markdown code fences and <think> tags from LLM output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ============================================================================
# OCR  (Mistral)
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
        if hasattr(resp, "model_dump"):
            logger.debug(f"OCR: Response dump: {json.dumps(resp.model_dump(), default=str)[:500]}")
        text = _extract_text_from_ocr_response(resp) or "No text extracted"
        logger.info(f"OCR: Extracted {len(text)} chars from '{filename}'")
        return text
    except Exception as e:
        logger.error(f"OCR: Failed for '{filename}': {e}", exc_info=True)
        return f"OCR failed: {e}"


# ============================================================================
# DISEASE RAG — Vector DB  (lazy-loaded FAISS)
# ============================================================================
VECTOR_DB_PATH = Path(__file__).parent / "DiseaseRag" / "disease_vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Lazy imports
_faiss = None
_SentenceTransformer = None


def _load_heavy_imports():
    global _faiss, _SentenceTransformer
    if _faiss is None:
        logger.info("RAG: Lazy-loading faiss…")
        import faiss as _f
        _faiss = _f
    if _SentenceTransformer is None:
        logger.info("RAG: Lazy-loading SentenceTransformer…")
        from sentence_transformers import SentenceTransformer as _ST
        _SentenceTransformer = _ST


class DiseaseVectorDB:
    """FAISS-backed vector database for disease documents."""

    def __init__(self):
        self.index = None
        self.metadata = None
        self.embeddings = None
        self.model = None
        self.is_loaded = False

    def load(self):
        if self.is_loaded:
            return
        _load_heavy_imports()
        logger.info(f"RAG: Loading vector DB from {VECTOR_DB_PATH}")
        index_path = VECTOR_DB_PATH / "faiss_index.bin"
        if not index_path.exists():
            raise FileNotFoundError(f"Vector DB not found at {VECTOR_DB_PATH}")
        self.index = _faiss.read_index(str(index_path))
        with open(VECTOR_DB_PATH / "metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)
        self.embeddings = np.load(VECTOR_DB_PATH / "embeddings.npy")
        logger.info(f"RAG: Loading embedding model: {EMBEDDING_MODEL}")
        self.model = _SentenceTransformer(EMBEDDING_MODEL)
        self.is_loaded = True
        logger.info(f"RAG: Vector DB ready — {len(self.metadata)} documents")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.is_loaded:
            self.load()
        logger.debug(f"RAG search: query='{query[:80]}…', top_k={top_k}")
        qe = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(qe.astype("float32"), top_k)
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                doc = self.metadata[idx]
                similarity = max(0, 100 * (1 - dist / 4))
                results.append({"rank": i + 1, "index": int(idx),
                                "similarity": round(similarity, 2), "document": doc})
        logger.debug(f"RAG search returned {len(results)} results")
        return results

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_loaded:
            self.load()
        for idx, doc in enumerate(self.metadata):
            if doc.get("id") == doc_id:
                return {"index": idx, "document": doc}
        return None

    @property
    def total_documents(self) -> int:
        return len(self.metadata) if self.is_loaded else 0


vector_db = DiseaseVectorDB()


# ---- RAG helper formatters ----
def _fmt(doc, key):
    v = doc.get(key, [])
    if not v:
        return ""
    if isinstance(v, list):
        return f"{key.replace('_',' ').title()}: " + ", ".join(
            s for s in v if s and not s.startswith("---"))[:500]
    return f"{key.replace('_',' ').title()}: {v}"[:500]


async def _rag_generate_answer(query: str, context_docs: List[Dict]) -> str:
    """Build context from vector search results and call LLM."""
    parts = []
    for i, result in enumerate(context_docs, 1):
        doc = result["document"]
        parts.append(f"""
--- Document {i}: {doc.get('name','Unknown')} ---
ID: {doc.get('id','N/A')}
Source: {doc.get('source','Disease Ontology Database')}
Description: {doc.get('description','N/A')}
{_fmt(doc,'symptoms')}
{_fmt(doc,'treatments')}
{_fmt(doc,'diagnostics')}
{_fmt(doc,'risk_factors')}
""")
    context = "\n".join(parts)
    system = (
        "You are a medical information assistant. Provide accurate answers based ONLY on the "
        "provided context documents. Cite sources as [Document X]. If the context is insufficient, "
        "say so. This is informational only, not medical advice."
    )
    user = f"QUESTION: {query}\n\nCONTEXT DOCUMENTS:\n{context}\n\nProvide a comprehensive answer with citations."
    return await llm_generate(system, user)


# ============================================================================
# JSON TRANSFORMER — helpers
# ============================================================================
def get_nested_value(data: dict, path: str) -> Any:
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
            current = current[key]
        elif isinstance(current, list):
            idx = int(key)
            if idx < 0 or idx >= len(current):
                raise IndexError(f"Index {idx} out of range for path '{path}'")
            current = current[idx]
        else:
            raise TypeError(f"Cannot navigate into {type(current).__name__} at '{path}'")
    return current


def set_nested_value(data: dict, path: str, value: Any) -> Any:
    keys = path.split(".")
    current = data
    for key in keys[:-1]:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            raise TypeError(f"Cannot navigate at '{path}'")
    final = keys[-1]
    if isinstance(current, dict):
        old = current[final]
        current[final] = value
        return old
    elif isinstance(current, list):
        idx = int(final)
        old = current[idx]
        current[idx] = value
        return old
    raise TypeError(f"Cannot set at '{path}'")


def apply_transformations(data: dict, instructions) -> tuple:
    result = copy.deepcopy(data)
    changes = []
    for t in instructions.transformations:
        try:
            old = set_nested_value(result, t.field_path, t.new_value)
            changes.append(f"{t.field_path}: {old} -> {t.new_value}")
        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise HTTPException(400, detail=f"Transform failed at '{t.field_path}': {e}")
    return result, changes


def compute_changes(original: dict, transformed: dict, prefix: str = "") -> List[str]:
    changes = []
    for key in original:
        cp = f"{prefix}{key}" if prefix else key
        if key not in transformed:
            continue
        ov, nv = original[key], transformed[key]
        if isinstance(ov, dict) and isinstance(nv, dict):
            changes.extend(compute_changes(ov, nv, f"{cp}."))
        elif isinstance(ov, list) and isinstance(nv, list):
            for i, (a, b) in enumerate(zip(ov, nv)):
                if isinstance(a, dict) and isinstance(b, dict):
                    changes.extend(compute_changes(a, b, f"{cp}.{i}."))
                elif a != b:
                    changes.append(f"{cp}.{i}: {a} -> {b}")
        elif ov != nv:
            changes.append(f"{cp}: {ov} -> {nv}")
    return changes


def _json_transform_prompts(original: dict, instructions: str):
    system = """You are a JSON transformation assistant. Modify JSON per instructions.
RULES: preserve structure, only change values mentioned, return ONLY raw JSON (no markdown/code fences).
TEMPERATURE: tempc is Celsius (30-45). If value >45, convert from Fahrenheit: C=(F-32)*5/9.
RELATIVE: "increase by X"=add X, "decrease by X"=subtract X, "set to X"=replace."""
    user = f"Original JSON:\n{json.dumps(original, indent=2)}\n\nInstructions: {instructions}\n\nReturn modified JSON:"
    return system, user


async def _transform_with_llm(original: dict, instructions: str, force_ollama: bool = False):
    """Use LLM for NL JSON transform. Returns (dict|None, model_name)."""
    system, user = _json_transform_prompts(original, instructions)
    raw = await llm_generate(system, user, temperature=0.1, force_ollama=force_ollama)
    if raw.startswith("⚠️"):
        return None, raw
    cleaned = _strip_llm_fences(raw)
    try:
        return json.loads(cleaned), (OLLAMA_MODEL if force_ollama else GROQ_MODEL)
    except json.JSONDecodeError as e:
        logger.error(f"Transform LLM JSON parse error: {e}\nRaw: {cleaned[:500]}")
        return None, f"JSON parse error: {e}"


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
# PYDANTIC SCHEMAS — Patient
# ============================================================================

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

class PatientListReq(BaseModel):
    doctorId: str
    filter: Optional[str] = "all"
    search: Optional[str] = ""

class PatientListItem(BaseModel):
    id: str; name: str; age: int; sex: str
    avatar: Optional[str] = None; symptom: str; riskLevel: str

class PatientListResp(BaseModel):
    patients: List[PatientListItem]

class PatientGetReq(BaseModel):
    doctorId: str; patientId: str

class Vitals(BaseModel):
    heartRate: int; bloodPressure: str; oxygenSaturation: int

class LabResults(BaseModel):
    glucose: int; cholesterol: int; creatinine: float

class RiskPoint(BaseModel):
    date: str; score: int

class PatientFull(BaseModel):
    id: str; name: str; age: int; sex: str
    avatar: Optional[str] = None; symptom: str
    bloodType: Optional[str] = None; primaryCondition: Optional[str] = None
    vitals: Vitals; labResults: LabResults
    riskLevel: str; riskPercentage: int; riskHistory: List[RiskPoint]
    medications: List[str]; allergies: List[str]
    clinicalSummary: str; lastVisit: Optional[str] = None

class PatientCreateReq(BaseModel):
    doctorId: str; name: str; age: int; sex: str
    bloodType: Optional[str] = None; primaryCondition: Optional[str] = None
    symptom: str; vitals: Vitals; labResults: LabResults
    medications: List[str] = []; allergies: List[str] = []
    clinicalSummary: str = ""

class UploadReq(BaseModel):
    patient_id: int

class UploadItem(BaseModel):
    uploadId: str; fileName: str; fileSize: int; mimeType: str
    status: str; ocrText: Optional[str] = None

class UploadResp(BaseModel):
    uploads: List[UploadItem]


# ============================================================================
# PYDANTIC SCHEMAS — RAG
# ============================================================================

class RagCitation(BaseModel):
    id: str; name: str; source: str; relevance_score: float; excerpt: str

class RagQueryRequest(BaseModel):
    query: str

class RagResponse(BaseModel):
    answer: str
    citations: List[RagCitation]


# ============================================================================
# PYDANTIC SCHEMAS — JSON Transformer
# ============================================================================

class FieldTransformation(BaseModel):
    field_path: str; new_value: Any

class TransformationInstruction(BaseModel):
    transformations: List[FieldTransformation] = []

class TxObservation(BaseModel):
    heartrate: float = Field(..., ge=0, le=300)
    sysbp: float = Field(..., ge=0, le=300)
    diasbp: float = Field(..., ge=0, le=200)
    meanbp: float = Field(..., ge=0, le=250)
    resprate: float = Field(..., ge=0, le=100)
    tempc: float = Field(..., ge=30, le=45)
    spo2: float = Field(..., ge=0, le=100)
    glucose: float = Field(..., ge=0, le=1000)
    age: float = Field(..., ge=0, le=150)
    gender: int = Field(..., ge=0, le=1)

class TxPatientData(BaseModel):
    patient_id: str
    observations: List[TxObservation] = Field(..., min_length=1)

class TransformRequest(BaseModel):
    original_data: TxPatientData
    instructions: TransformationInstruction

class TransformResponse(BaseModel):
    success: bool; transformed_data: Dict[str, Any]
    changes_applied: List[str] = []; timestamp: str
    model_used: Optional[str] = None

class NLTransformRequest(BaseModel):
    original_data: TxPatientData
    instructions: str
    use_ollama: bool = False


# ============================================================================
# PATIENT HELPERS
# ============================================================================
def _risk(row) -> tuple:
    d = float(row.get("diabetes_risk_score") or 0)
    c = float(row.get("cardiovascular_risk_score") or 0)
    mx = max(d, c); pct = int(mx * 100)
    if mx > 0.7: return "critical", pct
    elif mx > 0.3: return "watch", pct
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
    if not val: return []
    return [x.strip() for x in str(val).split(",") if x.strip()]


# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="Kju Unified Backend", version="3.0.0",
              description="Patient Management + Disease RAG + JSON Transformer",
              docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def _startup():
    logger.info("=== Kju Unified Backend starting ===")
    init_db()
    # Pre-load vector DB (non-blocking — log warning if missing)
    try:
        vector_db.load()
    except Exception as e:
        logger.warning(f"RAG vector DB not loaded on startup (will lazy-load): {e}")
    logger.info("=== Startup complete ===")


# ===================== PATIENT ROUTES =======================================

@app.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    logger.info(f"LOGIN: doctorId={req.doctorId}, licenseId={req.medicalLicenseId}")
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
        logger.info(f"LOGIN: success for doctor_id={d['doctor_id']}")
        return LoginResponse(
            success=True,
            doctor=DoctorProfile(
                id=f"doc-{d['doctor_id']}",
                name=f"Dr. {d['first_name']} {d['last_name']}",
                specialty=d["specialization"] or "General Practice",
                medicalLicenseId=d["license_number"],
            ),
        )
    logger.warning("LOGIN: doctor not found")
    raise HTTPException(401, detail={"error": "Doctor not found", "code": "AUTH_FAILED"})


@app.post("/api/patients/list", response_model=PatientListResp)
async def patients_list(req: PatientListReq):
    logger.info(f"PATIENTS LIST: doctor={req.doctorId}, filter={req.filter}, search='{req.search}'")
    where = "WHERE 1=1"
    params: list = []
    if req.search:
        where += " AND (full_name LIKE %s OR CAST(patient_data_id AS CHAR) LIKE %s)"
        params += [f"%{req.search}%", f"%{req.search}%"]
    if req.filter == "critical":
        where += " AND (cardiovascular_risk_score > 0.7 OR diabetes_risk_score > 0.7)"
    elif req.filter == "watch":
        where += (" AND ((cardiovascular_risk_score > 0.3 AND cardiovascular_risk_score <= 0.7) "
                   "OR (diabetes_risk_score > 0.3 AND diabetes_risk_score <= 0.7))")
    elif req.filter == "low":
        where += " AND cardiovascular_risk_score <= 0.3 AND diabetes_risk_score <= 0.3"
    q = f"SELECT * FROM Patient_Data {where} ORDER BY patient_data_id LIMIT 50"
    res = db_exec(q, tuple(params) if params else None)
    pts: List[PatientListItem] = []
    if res["success"]:
        for row in res["results"]:
            rl, _ = _risk(row)
            pts.append(PatientListItem(
                id=f"pat-{row['patient_data_id']}", name=row["full_name"] or "Unknown",
                age=row.get("age_years") or 0, sex=_sex(row), avatar=None,
                symptom=_symptom(row), riskLevel=rl))
    logger.info(f"PATIENTS LIST: returning {len(pts)} patients")
    return PatientListResp(patients=pts)


@app.post("/api/patients/get", response_model=PatientFull)
async def patients_get(req: PatientGetReq):
    pid = req.patientId.replace("pat-", "")
    logger.info(f"PATIENT GET: id={pid}")
    if not pid.isdigit():
        raise HTTPException(404, detail={"error": "Patient not found", "code": "PATIENT_NOT_FOUND"})
    res = db_exec("SELECT * FROM Patient_Data WHERE patient_data_id = %s", (int(pid),))
    if not res["success"] or res["count"] == 0:
        raise HTTPException(404, detail={"error": "Patient not found", "code": "PATIENT_NOT_FOUND"})
    p = res["results"][0]
    rl, rpct = _risk(p)
    hist_res = db_exec(
        "SELECT risk_score, assessed_at FROM AI_Risk_Assessment "
        "WHERE synthea_patient_id = %s ORDER BY assessed_at DESC LIMIT 10",
        (p.get("synthea_id") or "",))
    history: List[RiskPoint] = []
    if hist_res["success"]:
        for h in hist_res["results"]:
            try:
                dt = h["assessed_at"][:10] if isinstance(h["assessed_at"], str) else str(h["assessed_at"])[:10]
                sc = int(float(h["risk_score"] or 0) * 100)
                history.append(RiskPoint(date=dt, score=sc))
            except Exception:
                pass
    vitals = Vitals(heartRate=p.get("heart_rate") or 78,
                    bloodPressure=f"{p.get('bp_systolic') or 120}/{p.get('bp_diastolic') or 80}",
                    oxygenSaturation=int(float(p.get("oxygen_saturation") or 98)))
    labs = LabResults(glucose=p.get("glucose_fasting") or p.get("glucose") or 100,
                      cholesterol=p.get("cholesterol_total") or 200,
                      creatinine=float(p.get("creatinine") or 1.0))
    first_cond = ""
    if p.get("active_conditions_list"):
        first_cond = str(p["active_conditions_list"]).split(",")[0].strip()
    last_visit = None
    if p.get("latest_encounter_date"):
        lv = p["latest_encounter_date"]
        last_visit = lv[:10] if isinstance(lv, str) else str(lv)[:10]
    logger.info(f"PATIENT GET: returning patient {pid}, risk={rl}")
    return PatientFull(
        id=f"pat-{p['patient_data_id']}", name=p["full_name"] or "Unknown",
        age=p.get("age_years") or 0, sex=_sex(p), avatar=None, symptom=_symptom(p),
        bloodType=None, primaryCondition=first_cond or None, vitals=vitals, labResults=labs,
        riskLevel=rl, riskPercentage=rpct, riskHistory=history,
        medications=_split(p.get("active_medications_list")),
        allergies=_split(p.get("active_allergies_list")),
        clinicalSummary=(p.get("all_observations_list") or "No clinical summary available.")[:800],
        lastVisit=last_visit)


@app.post("/api/patients/create", response_model=PatientFull, status_code=201)
async def patients_create(req: PatientCreateReq):
    logger.info(f"PATIENT CREATE: name={req.name}, age={req.age}")
    gender = "Male" if req.sex.upper().startswith("M") else "Female"
    new_synthea_id = f"NEW-{uuid.uuid4().hex[:12]}"
    ins = db_exec(
        "INSERT INTO Patient_Data (synthea_id, full_name, age_years, gender, latest_encounter_reason, "
        "active_conditions_list, active_medications_list, active_allergies_list) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (new_synthea_id, req.name, req.age, gender, req.symptom,
         req.primaryCondition or "", ", ".join(req.medications), ", ".join(req.allergies)),
        fetch=False)
    if not ins["success"]:
        raise HTTPException(500, detail={"error": "Failed to create patient", "code": "DB_ERROR"})
    new_id = ins["lastrowid"]
    logger.info(f"PATIENT CREATE: success, new id={new_id}")
    return PatientFull(
        id=f"pat-{new_id}", name=req.name, age=req.age, sex=req.sex, avatar=None,
        symptom=req.symptom, bloodType=req.bloodType, primaryCondition=req.primaryCondition,
        vitals=req.vitals, labResults=req.labResults, riskLevel="low", riskPercentage=0,
        riskHistory=[], medications=req.medications, allergies=req.allergies,
        clinicalSummary=req.clinicalSummary, lastVisit=None)


@app.post("/api/patients/uploads", response_model=UploadResp)
async def upload_files(req: UploadReq):
    logger.info(f"UPLOAD: patient={req.patient_id} (no files — record only)")
    ins = db_exec(
        "INSERT INTO Patient_Documents (patient_id, document_type, document_name, "
        "file_size_bytes, mime_type, ocr_status) VALUES (%s,'Upload','no_file',0,'application/octet-stream','pending')",
        (req.patient_id,), fetch=False)
    uid = ins.get("lastrowid", 0)
    return UploadResp(uploads=[UploadItem(
        uploadId=f"upl-{uid:03d}", fileName="no_file", fileSize=0,
        mimeType="application/octet-stream", status="pending", ocrText=None)])


@app.post("/api/patients/uploads/file", response_model=UploadResp)
async def upload_files_with_file(
    patient_id: int = Form(...),
    files: List[UploadFile] = File(...),
):
    logger.info(f"UPLOAD FILE: patient={patient_id}, files={len(files)}")
    items: List[UploadItem] = []
    for f in files:
        content = await f.read()
        sz = len(content)
        logger.info(f"UPLOAD FILE: file='{f.filename}', size={sz}, mime='{f.content_type}'")
        ocr_text = perform_ocr(content, f.filename)
        ocr_status = ("completed" if ocr_text and not ocr_text.startswith("OCR ")
                      and not ocr_text.startswith("No text") else "failed")
        logger.info(f"UPLOAD FILE: OCR status={ocr_status}, text_len={len(ocr_text)}")
        ins = db_exec(
            "INSERT INTO Patient_Documents (patient_id, document_type, document_name, "
            "file_size_bytes, mime_type, ocr_text, ocr_status) VALUES (%s,'Upload',%s,%s,%s,%s,%s)",
            (patient_id, f.filename, sz, f.content_type, ocr_text, ocr_status),
            fetch=False)
        uid = ins.get("lastrowid", 0)
        items.append(UploadItem(
            uploadId=f"upl-{uid:03d}", fileName=f.filename, fileSize=sz,
            mimeType=f.content_type or "application/octet-stream",
            status=ocr_status, ocrText=ocr_text))
    return UploadResp(uploads=items)


@app.get("/api/patients/{patient_id}/documents")
async def get_patient_documents(patient_id: int):
    logger.info(f"GET DOCUMENTS: patient={patient_id}")
    res = db_exec(
        "SELECT * FROM Patient_Documents WHERE patient_id = %s ORDER BY created_at DESC",
        (patient_id,))
    if not res["success"]:
        raise HTTPException(500, detail="Failed to fetch documents")
    logger.info(f"GET DOCUMENTS: returning {res['count']} documents for patient {patient_id}")
    return {"patient_id": patient_id, "documents": res["results"]}


# ===================== RAG ROUTES ===========================================

@app.post("/api/rag/query", response_model=RagResponse)
async def rag_query(req: RagQueryRequest):
    logger.info(f"RAG QUERY: '{req.query[:80]}…'")
    if not vector_db.is_loaded:
        try:
            vector_db.load()
        except Exception as e:
            raise HTTPException(500, detail=f"Failed to load vector DB: {e}")
    results = vector_db.search(req.query, 5)
    if not results:
        raise HTTPException(404, detail="No relevant documents found")
    citations = []
    for r in results:
        doc = r["document"]
        excerpt = doc.get("description", doc.get("text", ""))[:300]
        if len(doc.get("description", doc.get("text", ""))) > 300:
            excerpt += "..."
        citations.append(RagCitation(
            id=doc.get("id", f"IDX:{r['index']}"),
            name=doc.get("name", "Unknown"),
            source=doc.get("source", "Disease Ontology DB"),
            relevance_score=r["similarity"], excerpt=excerpt))
    answer = await _rag_generate_answer(req.query, results)
    logger.info(f"RAG QUERY: returning {len(citations)} citations")
    return RagResponse(answer=answer, citations=citations)


# ===================== TRANSFORM ROUTES =====================================

@app.post("/api/transform", response_model=TransformResponse)
async def transform_patient_data(request: TransformRequest):
    logger.info(f"TRANSFORM: {len(request.instructions.transformations)} field transforms")
    data_dict = request.original_data.model_dump()
    transformed, changes = apply_transformations(data_dict, request.instructions)
    try:
        validated = TxPatientData(**transformed)
    except Exception as e:
        raise HTTPException(400, detail=f"Transformed data invalid: {e}")
    logger.info(f"TRANSFORM: {len(changes)} changes applied")
    return TransformResponse(success=True, transformed_data=validated.model_dump(),
                             changes_applied=changes, timestamp=datetime.now().isoformat())


@app.post("/api/transform/nl", response_model=TransformResponse)
async def transform_nl(request: NLTransformRequest):
    logger.info(f"TRANSFORM NL: instructions='{request.instructions[:80]}…'")
    data_dict = request.original_data.model_dump()
    transformed, model_used = await _transform_with_llm(data_dict, request.instructions,
                                                        force_ollama=request.use_ollama)
    if transformed is None:
        raise HTTPException(500, detail=f"LLM failed: {model_used}")
    try:
        validated = TxPatientData(**transformed)
    except Exception as e:
        raise HTTPException(400, detail=f"LLM output invalid: {e}")
    changes = compute_changes(data_dict, validated.model_dump())
    logger.info(f"TRANSFORM NL: {len(changes)} changes via {model_used}")
    return TransformResponse(success=True, transformed_data=validated.model_dump(),
                             changes_applied=changes, timestamp=datetime.now().isoformat(),
                             model_used=model_used)


# ===================== HEALTH / ROOT ========================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Kju Unified Backend",
        "version": "3.0.0",
        "modules": {
            "patients": "/api/patients/*",
            "rag": "/api/rag/*",
            "transform": "/api/transform/*",
        },
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    db_ok = False
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        db_ok = True
    except Exception:
        pass
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "rag_loaded": vector_db.is_loaded,
        "rag_documents": vector_db.total_documents,
        "llm_primary": GROQ_MODEL,
        "llm_fallback": OLLAMA_MODEL,
    }


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
