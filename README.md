# Project Aegis (KJU)

[![Deploy Status](https://img.shields.io/badge/Netlify-Deployed-00C7B7?style=flat-square&logo=netlify)](https://project-aegis-kju.netlify.app)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Groq](https://img.shields.io/badge/Groq-FF6F00?style=flat-square)](https://groq.com)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white)](https://ollama.com)

**Project Aegis** is a healthcare intelligence platform that combines knowledge graphs, vector search, and LLMs to power clinical decision support. It uses a hybrid KG-RAG pipeline over patient data stored in MariaDB and Neo4j, with AI risk prediction models for cardiovascular disease, diabetes, and sepsis.

> **Live demo:** [project-aegis-kju.netlify.app](https://project-aegis-kju.netlify.app)

## Features

**Hybrid KG-RAG Pipeline** — Combines semantic embeddings with multi-hop graph traversal and LLM-generated Cypher queries for context-aware retrieval over patient knowledge graphs.

**Natural Language to Cypher** — Schema-aware LLM (Groq / Ollama) converts plain English into executable Cypher queries with multiple suggestions, validation, and optimization.

**AI Risk Prediction Models** — XGBoost-based APIs for cardiovascular and diabetes risk prediction, plus a sepsis prediction model — all containerised and deployable independently.

**Disease Ontology RAG** — FAISS vector database over medical ontologies, returning cited answers via LLM on top of semantically retrieved disease knowledge.

**Patient Management API** — Full CRUD, doctor authentication, file uploads with OCR (Mistral AI), and a JSON transformation engine with natural-language field editing.

**Synthetic Data Pipeline** — End-to-end generation of realistic patient records via Synthea, loaded into MariaDB and translated into a Neo4j knowledge graph with 18 node types and 17 relationship types.

**MCP Server Support** — HTTP-based Model Context Protocol servers for AI assistant integration with hospital database tooling.

## Architecture

```
User / Frontend (Netlify)
         |
    FastAPI Backend (:8000)
         |
    +----+--------+--------+-------+
    |             |        |       |
  MariaDB       Neo4j   FAISS   AI Models
  (relational)  (graph)  (vec)   (:5002/:5003)
    |             |        |       |
    +--- Synthea Pipeline ---------+
                |
           Patient Data
```

The system layers:

- **Data layer** — MariaDB stores relational patient records; Neo4j holds the knowledge graph (Patients, Conditions, Medications, Encounters, Providers, Observations)
- **Embedding layer** — `core/hybrid_kg_vectorizer.py` converts Neo4j nodes into semantic embeddings using sentence-transformers
- **Retrieval layer** — `core/hybrid_kg_retriever.py` performs semantic search fused with multi-hop graph expansion
- **Query layer** — `core/hybrid_kg_cypher_generator.py` generates, validates, and optimises Cypher queries from natural language
- **Pipeline layer** — `core/hybrid_kg_rag_pipeline.py` orchestrates the full RAG flow with caching and execution stats
- **API layer** — `api/patient_api.py` exposes patient management, disease RAG, JSON transformation, and AI model endpoints
- **Model layer** — `AI_Models/` contains independently deployable XGBoost prediction APIs (cardio, diabetes, sepsis)
- **Frontend** — Static HTML/CSS/JS demo served via Netlify, querying the Hybrid KG-RAG pipeline

## Prerequisites

- Python 3.8+
- MariaDB (port 3305, or configure your own)
- Neo4j (local Docker or AuraDB)
- Ollama (optional, for local LLM inference)
- Java (for Synthea data generation, optional)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -r hybrid_kg_requirements.txt

# 2. Configure environment
cp .env.example .env     # Set DB, Neo4j, and Groq credentials

# 3. Verify setup
python quick_start.py

# 4. Start the API server
cd api && python patient_api.py
```

The API runs at `http://localhost:8000`. See the [docs](docs/INDEX.md) for detailed setup including Ollama, the Synthea data pipeline, and Docker deployments.

## Project Structure

```
KJU/
  api/              FastAPI backend — patient management, disease RAG, JSON transform
  core/             Hybrid KG-RAG pipeline — vectorizer, retriever, cypher generator
  AI_Models/        XGBoost prediction APIs — cardio (:5002), diabetes (:5003), sepsis
  DiseaseRag/       FAISS vector DB, medical ontology population, RAG API
  frontend/         Static demo served on Netlify
  persona_generator/  Patient persona generation package
  scripts/
    data_pipeline/     Synthea → MariaDB → Neo4j ETL
    doctor_appointments/  Doctor-patient assignment and appointment seeding
    persona_generation/   Detailed patient persona and document generators
  tests/            Connection, API, and data coherence tests
  docs/             Full documentation — architecture, schema, guides, references
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `POST /api/login` | Doctor authentication |
| `POST /api/patients/list` | List patients with filters |
| `POST /api/patients/get` | Patient details |
| `POST /api/patients/create` | Create patient record |
| `POST /api/patients/uploads` | Create upload record |
| `POST /api/patients/uploads/file` | Upload files with OCR |
| `GET /api/patients/{id}/documents` | Patient documents |
| `POST /api/rag/query` | Disease RAG query |
| `POST /api/transform` | JSON field-path transform |
| `POST /api/transform/nl` | Natural language JSON transform |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Uvicorn |
| Relational DB | MariaDB |
| Graph DB | Neo4j |
| Vector Store | FAISS |
| LLM | Groq (primary), Ollama (local) |
| Embeddings | sentence-transformers, Hugging Face |
| ML Models | XGBoost, scikit-learn |
| OCR | Mistral AI |
| Frontend | Vanilla HTML/CSS/JS |
| Infra | Docker, docker-compose |

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/INDEX.md) directory:

- [Architecture Overview](docs/COMPONENT_DATABASE_ARCHITECTURE.md)
- [Database Schema](docs/Database_Schema_README.md)
- [Knowledge Graph Schema](docs/KG_SCHEMA.md)
- [Cypher Query Guide](docs/CORRECT_CYPHER_QUERIES.md)
- [Ollama Setup Guide](docs/OLLAMA_SETUP_GUIDE.md)
- [Integration Guide](docs/INTEGRATION_GUIDE.md)
