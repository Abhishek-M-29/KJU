"""
KJU AI Pipeline — FastAPI Application

The main entry point for the backend server. Configures CORS,
includes routers, and sets up logging.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from models.responses import HealthResponse
from routers.diagnostics import router as diagnostics_router

# ── Logging ──

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

_fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_datefmt = "%Y-%m-%d %H:%M:%S"

# Console handler
logging.basicConfig(level=logging.INFO, format=_fmt, datefmt=_datefmt)

# File handler — 5 MB rotation, 3 backups
_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter(_fmt, datefmt=_datefmt))
logging.getLogger().addHandler(_file_handler)

logger = logging.getLogger(__name__)

# ── App ──

app = FastAPI(
    title="KJU AI Diagnostic Pipeline",
    description="Orchestrator for ML Swarm + MedGemma + Synthesis Agent pipeline",
    version="0.1.0",
)

# ── CORS (allow Vite dev server + common local ports) ──

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──

app.include_router(diagnostics_router)

# ── Health Check ──


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return HealthResponse()


# ── Startup/Shutdown Hooks ──


@app.on_event("startup")
async def on_startup():
    logger.info("=" * 60)
    logger.info("KJU AI Pipeline starting")
    logger.info("ML Swarm URL:  %s", settings.ml_swarm_url)
    logger.info("MedGemma URL:  %s", settings.medgemma_url)
    logger.info("Groq Model:    %s", settings.groq_model)
    logger.info("=" * 60)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("KJU AI Pipeline shutting down")
