"""
Disease RAG API
Retrieval-Augmented Generation API for medical information queries.
Returns answers with traceable citations linked to the vector database.
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Lazy imports for heavy modules
faiss = None
SentenceTransformer = None

def load_heavy_imports():
    """Lazy load heavy imports."""
    global faiss, SentenceTransformer
    if faiss is None:
        import faiss as _faiss
        faiss = _faiss
    if SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as _ST
        SentenceTransformer = _ST

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import asyncio

# Load environment variables
load_dotenv()

# Configuration
VECTOR_DB_PATH = Path(__file__).parent / "disease_vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Groq Configuration (Primary)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "qwen/qwen3-32b"

# Ollama Configuration (Fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "qwen2.5:7b-instruct"

# Default model setting
DEFAULT_MODEL = GROQ_MODEL

# FastAPI app
app = FastAPI(
    title="Disease RAG API",
    description="Medical information retrieval with AI-powered answers and traceable citations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Data Models ====================

class Citation(BaseModel):
    """A citation linking back to the vector database source."""
    id: str = Field(..., description="Unique identifier in the vector database")
    name: str = Field(..., description="Name of the disease/condition")
    source: str = Field(..., description="Original source of the information")
    relevance_score: float = Field(..., description="Similarity score (0-100%)")
    excerpt: str = Field(..., description="Relevant excerpt from the document")
    full_citations: Optional[List[str]] = Field(None, description="Academic citations if available")
    category: Optional[str] = Field(None, description="Medical category")


class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str = Field(..., description="The medical question or text to analyze")
    top_k: int = Field(5, description="Number of relevant documents to retrieve", ge=1, le=20)
    include_answer: bool = Field(True, description="Whether to generate an AI answer")
    model: str = Field(DEFAULT_MODEL, description="LLM model to use for answer generation")


class RAGResponse(BaseModel):
    """Response model with answer and citations."""
    query: str = Field(..., description="Original query")
    answer: Optional[str] = Field(None, description="AI-generated answer based on retrieved context")
    citations: List[Citation] = Field(..., description="List of traceable citations from vector DB")
    total_documents_searched: int = Field(..., description="Total documents in the database")
    retrieval_method: str = Field("semantic_similarity", description="Method used for retrieval")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_db_loaded: bool
    total_documents: int
    embedding_model: str


# ==================== Vector Database Manager ====================

class DiseaseVectorDB:
    """Manager for the disease vector database."""
    
    def __init__(self):
        self.index = None
        self.metadata = None
        self.embeddings = None
        self.model = None
        self.is_loaded = False
    
    def load(self):
        """Load the vector database and embedding model."""
        if self.is_loaded:
            return
        
        # Load heavy imports first
        load_heavy_imports()
        
        print("Loading vector database...")
        
        # Load FAISS index
        index_path = VECTOR_DB_PATH / "faiss_index.bin"
        if not index_path.exists():
            raise FileNotFoundError(f"Vector database not found at {VECTOR_DB_PATH}")
        
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(VECTOR_DB_PATH / "metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)
        
        # Load embeddings
        self.embeddings = np.load(VECTOR_DB_PATH / "embeddings.npy")
        
        # Load embedding model
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        self.is_loaded = True
        print(f"✅ Vector database loaded with {len(self.metadata)} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the vector database for relevant documents."""
        if not self.is_loaded:
            self.load()
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                doc = self.metadata[idx]
                # Convert L2 distance to similarity percentage
                similarity = max(0, 100 * (1 - dist / 4))  # Normalize to 0-100%
                
                results.append({
                    "rank": i + 1,
                    "index": int(idx),
                    "similarity": round(similarity, 2),
                    "document": doc
                })
        
        return results
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by its ID."""
        if not self.is_loaded:
            self.load()
        
        for idx, doc in enumerate(self.metadata):
            if doc.get("id") == doc_id:
                return {"index": idx, "document": doc}
        return None
    
    @property
    def total_documents(self) -> int:
        """Get total number of documents in the database."""
        if not self.is_loaded:
            return 0
        return len(self.metadata)


# Global vector database instance
vector_db = DiseaseVectorDB()


# ==================== LLM Integration ====================

async def generate_answer_groq(query: str, context: str, system_prompt: str, user_prompt: str) -> str:
    """Generate answer using Groq API (Primary)."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"Groq API error: {response.status_code} - {error_text}")
                return None  # Signal to try fallback
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    except Exception as e:
        print(f"Groq error: {str(e)}")
        return None  # Signal to try fallback


async def generate_answer_ollama(query: str, context: str, system_prompt: str, user_prompt: str) -> str:
    """Generate answer using Ollama API (Fallback)."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2000
                    }
                }
            )
            
            if response.status_code != 200:
                return f"⚠️ Ollama API error: {response.status_code}. Showing retrieved documents only."
            
            data = response.json()
            return data.get("response", "No response generated")
            
    except httpx.ConnectError:
        return "⚠️ Could not connect to Ollama fallback. Showing retrieved documents only."
    except Exception as e:
        return f"⚠️ Error generating answer: {str(e)}. Showing retrieved documents only."


async def generate_answer(query: str, context_docs: List[Dict], model: str = DEFAULT_MODEL) -> str:
    """Generate an answer using Groq (primary) with Ollama fallback."""
    
    # Build context from retrieved documents
    context_parts = []
    for i, result in enumerate(context_docs, 1):
        doc = result["document"]
        context_parts.append(f"""
--- Document {i}: {doc.get('name', 'Unknown')} ---
ID: {doc.get('id', 'N/A')}
Source: {doc.get('source', 'Disease Ontology Database')}

Description: {doc.get('description', 'No description available')}

{_format_symptoms(doc)}
{_format_treatments(doc)}
{_format_diagnostics(doc)}
{_format_risk_factors(doc)}
""")
    
    context = "\n".join(context_parts)
    
    system_prompt = """You are a medical information assistant. Your role is to provide accurate, helpful information based ONLY on the provided context documents.

IMPORTANT GUIDELINES:
1. Base your answer ONLY on the information provided in the context documents
2. Always cite which document(s) support each part of your answer using [Document X] format
3. If the context doesn't contain enough information to fully answer the question, clearly state what is missing
4. Use clear, accessible language while maintaining medical accuracy
5. Include relevant warnings, contraindications, or when to seek medical attention
6. DO NOT make up information not present in the context
7. Structure your answer with clear sections if appropriate

Remember: This is for informational purposes only and does not constitute medical advice."""

    user_prompt = f"""Based on the following medical reference documents, please answer this question:

QUESTION: {query}

CONTEXT DOCUMENTS:
{context}

Please provide a comprehensive answer with citations to the relevant documents."""

    # Try Groq first (primary)
    print(f"🔄 Attempting Groq API with model: {GROQ_MODEL}")
    answer = await generate_answer_groq(query, context, system_prompt, user_prompt)
    
    if answer:
        print("✅ Groq API succeeded")
        return answer
    
    # Fallback to Ollama
    print(f"⚠️ Groq failed, falling back to Ollama with model: {OLLAMA_MODEL}")
    return await generate_answer_ollama(query, context, system_prompt, user_prompt)


def _format_symptoms(doc: Dict) -> str:
    """Format symptoms from document."""
    symptoms = doc.get("symptoms", [])
    if not symptoms:
        return ""
    if isinstance(symptoms, list):
        return "Symptoms: " + ", ".join([s for s in symptoms if s and not s.startswith("---")])[:500]
    return f"Symptoms: {symptoms}"[:500]


def _format_treatments(doc: Dict) -> str:
    """Format treatments from document."""
    treatments = doc.get("treatments", [])
    if not treatments:
        return ""
    if isinstance(treatments, list):
        return "Treatments: " + ", ".join([t for t in treatments if t and not t.startswith("---")])[:500]
    return f"Treatments: {treatments}"[:500]


def _format_diagnostics(doc: Dict) -> str:
    """Format diagnostics from document."""
    diagnostics = doc.get("diagnostics", [])
    if not diagnostics:
        return ""
    if isinstance(diagnostics, list):
        return "Diagnostics: " + ", ".join([d for d in diagnostics if d])[:500]
    return f"Diagnostics: {diagnostics}"[:500]


def _format_risk_factors(doc: Dict) -> str:
    """Format risk factors from document."""
    risk_factors = doc.get("risk_factors", [])
    if not risk_factors:
        return ""
    if isinstance(risk_factors, list):
        return "Risk Factors: " + ", ".join([r for r in risk_factors if r])[:500]
    return f"Risk Factors: {risk_factors}"[:500]


# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup_event():
    """Load vector database on startup."""
    try:
        vector_db.load()
    except Exception as e:
        print(f"⚠️ Warning: Could not load vector database on startup: {e}")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        vector_db_loaded=vector_db.is_loaded,
        total_documents=vector_db.total_documents,
        embedding_model=EMBEDDING_MODEL
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return await root()


@app.post("/query", response_model=RAGResponse)
async def query_rag(request: QueryRequest):
    """
    Query the Disease RAG system.
    
    Takes a medical question or text and returns:
    1. An AI-generated answer based on retrieved context
    2. A list of citations traceable to the vector database
    """
    
    # Ensure vector DB is loaded
    if not vector_db.is_loaded:
        try:
            vector_db.load()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load vector database: {str(e)}")
    
    # Search for relevant documents
    results = vector_db.search(request.query, request.top_k)
    
    if not results:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    
    # Build citations
    citations = []
    for result in results:
        doc = result["document"]
        
        # Get excerpt (use description or text field)
        excerpt = doc.get("description", doc.get("text", ""))[:300]
        if len(doc.get("description", doc.get("text", ""))) > 300:
            excerpt += "..."
        
        citation = Citation(
            id=doc.get("id", f"IDX:{result['index']}"),
            name=doc.get("name", "Unknown Disease/Condition"),
            source=doc.get("source", doc.get("citations", ["Disease Ontology Database"])[0] if doc.get("citations") else "Disease Ontology Database"),
            relevance_score=result["similarity"],
            excerpt=excerpt,
            full_citations=doc.get("citations"),
            category=doc.get("category")
        )
        citations.append(citation)
    
    # Generate answer if requested
    answer = None
    if request.include_answer:
        answer = await generate_answer(request.query, results, request.model)
    
    return RAGResponse(
        query=request.query,
        answer=answer,
        citations=citations,
        total_documents_searched=vector_db.total_documents,
        retrieval_method="semantic_similarity"
    )


@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """
    Retrieve a specific document by its ID.
    
    This allows tracing citations back to their full source.
    """
    if not vector_db.is_loaded:
        try:
            vector_db.load()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load vector database: {str(e)}")
    
    result = vector_db.get_document_by_id(doc_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
    
    return {
        "id": doc_id,
        "database_index": result["index"],
        "document": result["document"],
        "retrieval_url": f"/document/{doc_id}"
    }


@app.get("/search")
async def search_diseases(
    q: str,
    top_k: int = 5
):
    """
    Simple search endpoint for disease lookup.
    
    Returns matching documents without AI-generated answer.
    """
    if not vector_db.is_loaded:
        try:
            vector_db.load()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load vector database: {str(e)}")
    
    results = vector_db.search(q, top_k)
    
    formatted_results = []
    for r in results:
        doc = r["document"]
        doc_id = doc.get("id") or f"IDX:{r['index']}"
        formatted_results.append({
            "rank": int(r["rank"]),
            "id": doc_id,
            "name": doc.get("name", "Unknown"),
            "similarity": float(r["similarity"]),
            "description": doc.get("description", "")[:200],
            "source": doc.get("source", "Disease Ontology Database"),
            "document_url": f"/document/{doc_id}"
        })
    
    return {
        "query": q,
        "results": formatted_results,
        "total_in_database": vector_db.total_documents
    }


@app.get("/citations/{doc_id}")
async def get_citations(doc_id: str):
    """
    Get full citation information for a document.
    
    Returns academic citations and source information for verification.
    """
    if not vector_db.is_loaded:
        try:
            vector_db.load()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load vector database: {str(e)}")
    
    result = vector_db.get_document_by_id(doc_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Document with ID '{doc_id}' not found")
    
    doc = result["document"]
    
    return {
        "id": doc_id,
        "name": doc.get("name", "Unknown"),
        "primary_source": doc.get("source", "Disease Ontology Database"),
        "academic_citations": doc.get("citations", []),
        "category": doc.get("category"),
        "synonyms": doc.get("synonyms", []),
        "related_terms": doc.get("related_synonyms", []),
        "verification_note": "Citations link to peer-reviewed medical literature and clinical guidelines."
    }


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║           Disease RAG API - Medical Information           ║
║         with Traceable Citations from Vector DB           ║
╠═══════════════════════════════════════════════════════════╣
║  Endpoints:                                               ║
║    POST /query     - Query with AI answer + citations     ║
║    GET  /search    - Simple document search               ║
║    GET  /document/{id} - Get full document by ID          ║
║    GET  /citations/{id} - Get citation details            ║
║    GET  /health    - Health check                         ║
╠═══════════════════════════════════════════════════════════╣
║  Primary LLM: Groq API (qwen/qwen3-32b)                   ║
║  Fallback:    Ollama (qwen2.5:7b-instruct)                ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
