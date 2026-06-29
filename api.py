from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from service.rag_pipeline import GraphRAGService
import logging
import uvicorn
import os
from datetime import datetime
import uuid

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title="KG-RAG API",
    description="API interface for the Clinical Knowledge Graph RAG System",
    version="1.0.0"
)

# Request Model
class QueryRequest(BaseModel):
    doctorId: str = Field(..., description="The ID of the doctor making the query")
    patientId: str = Field(..., description="The ID of the patient being queried")
    message: str = Field(..., description="The natural language query")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "doctorId": "doc-001",
            "patientId": "pat-001",
            "message": "What is the patient's cardiac history?"
        }
    })

# Response Model
class QueryResponse(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The response content")
    timestamp: str = Field(..., description="ISO 8601 timestamp of response generation")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "msg-3",
            "role": "assistant",
            "content": "Patient John Anderson has a documented history of stable angina pectoris...",
            "timestamp": "2026-02-08T10:01:12Z"
        }
    })

# Global Service Instance
rag_service = None

@app.on_event("startup")
async def startup_event():
    global rag_service
    logger.info("Initializing GraphRAGService...")
    try:
        rag_service = GraphRAGService()
        logger.info("GraphRAGService initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize GraphRAGService: {e}")

@app.post("/query", response_model=QueryResponse, responses={422: {"model": None}})
async def query_endpoint(request: QueryRequest):
    """
    Process a natural language query against the Knowledge Graph.
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG Service failed to initialize")
    
    logger.info(f"Processing query for Patient ID: {request.patientId}, Doctor ID: {request.doctorId}")
    
    try:
        # process_request is synchronous, FastAPI runs it in a threadpool automatically
        response_text = rag_service.process_request(request.message, request.patientId, request.doctorId)
        
        return QueryResponse(
            id=f"msg-{uuid.uuid4().hex[:8]}",
            role="assistant",
            content=response_text,
            timestamp=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Processing Error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service_status": "active" if rag_service else "inactive"
    }

import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be reachable; it just triggers the OS 
        # to select the correct interface for outgoing traffic.
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n--- Server starting on network IP: {local_ip} ---")
    
    import uvicorn
    # Now you can use the variable or keep '0.0.0.0' to listen on all interfaces
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)