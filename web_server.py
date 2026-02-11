"""
Simple FastAPI server to demo Hybrid KG-RAG with Ollama.
"""

import os
import time
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from hybrid_kg_rag_pipeline import GraphRAGFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_server")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    expand_hops: int = 1
    num_suggestions: int = 2
    execute_best: bool = True


class QueryResponse(BaseModel):
    query: str
    elapsed_ms: int
    cypher_suggestions: Any
    result: Any
    retrieved_context: Any


app = FastAPI(title="Hybrid KG-RAG Demo")


def build_pipeline():
    """Initialize the pipeline once for the server."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

    logger.info("Initializing HybridGraphRAG pipeline for web server...")
    return GraphRAGFactory.create_pipeline(
        neo4j_uri=uri,
        neo4j_user=user,
        neo4j_password=password,
        ollama_url=ollama_url,
        ollama_model=ollama_model,
    )


PIPELINE = build_pipeline()


@app.get("/api/status")
def status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct"),
    }


@app.post("/api/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start = time.time()
    try:
        result = PIPELINE.process_query(
            user_query=payload.query,
            top_k=payload.top_k,
            expand_hops=payload.expand_hops,
            num_cypher_suggestions=payload.num_suggestions,
            execute_best=payload.execute_best,
        )
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed_ms = int((time.time() - start) * 1000)
    return QueryResponse(
        query=payload.query,
        elapsed_ms=elapsed_ms,
        cypher_suggestions=result.get("cypher_suggestions", []),
        result=result.get("execution_result"),
        retrieved_context=result.get("retrieved_context"),
    )


app.mount("/static", StaticFiles(directory="frontend", html=False), name="static")


@app.get("/")
def index():
    return FileResponse("frontend/index.html")
