"""
MediMax Backend API

FastAPI server for patient management, authentication, and document handling.
Connects to MariaDB database using the same credentials as the main KJU project.

Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path to access shared modules if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes import auth, patients, documents
from database import check_connection

# Create FastAPI app
app = FastAPI(
    title="MediMax Backend API",
    description="Backend API for patient management, authentication, and document handling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(documents.router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API info."""
    return {
        "name": "MediMax Backend API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth/login",
            "patients": "/patients",
            "documents": "/documents"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Verifies MCP server connectivity.
    """
    db_status = check_connection()
    
    return {
        "status": "healthy" if db_status.get("status") == "connected" else "degraded",
        "database": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
