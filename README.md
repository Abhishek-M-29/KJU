# Clinical Knowledge Graph RAG (KG-RAG)

## 📌 Project Overview
The **Clinical KG-RAG** is a sophisticated Retrieval-Augmented Generation system designed to query clinical patient data stored in a **Neo4j Knowledge Graph** and **MariaDB** using natural language. It leverages the **Model Context Protocol (MCP)** to abstract database interactions and uses **Groq's Llama 3** models for high-speed query generation and synthesis.

This system is designed to simulate a clinical assistant that can answer complex questions about patient history, diagnoses, treatments, medications, and risk profiles by navigating a rich graph of medical data (Synthea dataset).

## 🚀 Key Features
*   **Graph RAG Pipeline**: Converts natural language questions into executable Cypher queries.
*   **MCP Integration**: Uses a Model Context Protocol (MCP) server to handle database security and abstraction.
*   **Self-Correcting Query Engine**: Automatically retries and fixes malformed Cypher queries using error feedback loops.
*   **High-Performance Inference**: Powered by **Groq** (Llama-3.3-70b-versatile) for near-instant Cypher generation and summarization.
*   **Hybrid Data Source**: Conceptually links structured relational data (MariaDB) with graph relationships (Neo4j).
*   **Robust Error Handling**: Implements full MCP handshake (SSE) and specialized error parsers.

---

## 🏗️ System Architecture

### Components
1.  **Client Application (`main.py`)**: CLI interface for user interaction.
2.  **RAG Service (`service/rag_pipeline.py`)**: Orchestrates the flow between the user, LLM, and Database.
3.  **MCP Connector (`core/db.py`)**: Handles JSON-RPC 2.0 communication with the MCP Server over HTTP/SSE.
4.  **Prompt Domain (`domain/prompts.py`)**: Manages context-aware prompt engineering with schema injection.
5.  **LLM Client (`core/llm.py`)**: Interface for the Groq API.

### Data Flow
1.  **User Input**: "What conditions does patient X have?"
2.  **Schema Injection**: Reduced clinical schema is injected into the prompt.
3.  **Cypher Generation**: LLM generates a Cypher query (e.g., `MATCH (p:Patient)...`).
4.  **Execution (MCP)**: Query is sent via JSON-RPC to the MCP Server.
5.  **Fallback/Correction**: If execution fails (syntax error), the error is fed back to the LLM to fix the query.
6.  **Summarization**: Raw graph results are synthesized into a natural language response.

---

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Groq API Key**: You need a valid API key from [console.groq.com](https://console.groq.com).
*   **MCP Server**: A running instance of the `my-mcp-server` bridging Neo4j and MariaDB (running on `http://172.18.4.108:8069/mcp/` in this setup).
*   **Network Access**: Connectivity to the MCP server IP.

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd KG RAG
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=gsk_your_actual_api_key_here
    MCP_SERVER_URL=http://172.18.4.108:8069/mcp/
    MODEL_NAME=llama-3.3-70b-versatile
    ```

---

## 💻 Usage

### Option 1: CLI Interface (Interactive)
Run the command-line tool for quick testing:
```bash
python main.py
```

**Search Modes:**
1.  **Patient Context**: Enter an ID when prompted.
    *   **UUID** (e.g., `9184f2d3...`): Search by `synthea_id`.
    *   **Integer** (e.g., `1`, `2`): Search by `patient_no`.
2.  **Global Search**: Leave the ID blank to query the entire graph (e.g., "Count current smokers").

### Option 2: REST API
Start the FastAPI server for integration:
```bash
uvicorn api:app --reload
```
Query via HTTP POST:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"doctorId": "doc-001", "patientId": "pat-001", "message": "What is the patient'"'"'s cardiac history?"}'
```

---

## 📂 Project Structure

```text
KG RAG/
├── core/                   # Core infrastructure code
│   ├── config.py           # Settings management (Pydantic)
│   ├── db.py               # MCP Connection & Handshake logic
│   └── llm.py              # Groq Client wrapper
├── domain/                 # Domain-specific logic
│   ├── prompts.py          # Prompt templates & context building
│   └── schema.py           # Simplified graph schema for LLM
├── service/                # Business logic
│   └── rag_pipeline.py     # Main RAG orchestration & retry loop
├── tests/                  # Unit tests
│   └── test_suite.py       # Comprehensive unittests (Mocked)
├── .env                    # Environment variables (Ignored by Git)
├── main.py                 # Application entry point
├── mariadb_schema.md       # Documentation of Relational Schema
├── neo4j_schema.md         # Documentation of Graph Schema
└── requirements.txt        # Python dependencies
```

---

## 📊 Database Schemas

Detailed documentation of the underlying databases is available in the project root:

*   **[MariaDB Schema](mariadb_schema.md)**: Contains 28 tables including `Patient_Data`, `Medical_History`, and `Synthea` records.
*   **[Neo4j Schema](neo4j_schema.md)**: Documents the Knowledge Graph, including:
    *   **30+ Node Types**: `Observation`, `Condition`, `Medication`, `Encounter`, `Doctor`, `LabTrend`, etc.
    *   **Relationships**: `HAS_CONDITION`, `TREATED_BY`, `HAS_RISK_FACTOR`.

---

## 🧪 Testing

The project includes a robust test suite that mocks the MCP server and Groq API interactions to verify logic without incurring costs or network traffic.

**Run the full test suite:**
```bash
python -m unittest tests/test_suite.py
```

*Tests cover: Configuration loading, Prompt engineering, Pipeline success paths, Retry logic, and Error handling.*

---

## 🔧 Troubleshooting

### Common Issues

**1. `406 Client Error: Not Acceptable`**
*   **Cause**: The MCP server strictly requires Server-Sent Events (SSE).
*   **Fix**: Ensure `core/db.py` sends `Accept: text/event-stream` and performs the handshake (implemented in v1.1).

**2. `400 Bad Request: Invalid request parameters`**
*   **Cause**: JSON-RPC payload format mismatch.
*   **Fix**: The `ExcecuteQuery_Neo4j` tool expects the correct parameter nesting. The current implementation in `core/db.py` handles this.

**3. `400 Client Error: Model Decommissioned`**
*   **Cause**: Using an old model slug like `llama3-70b-8192`.
*   **Fix**: Update `MODEL_NAME` in `core/config.py` to `llama-3.3-70b-versatile` or another active Groq model.

**4. Connection Refused**
*   **Cause**: The MCP server IP `172.18.4.108` is unreachable.
*   **Fix**: Check your VPN or local network settings. Update `MCP_SERVER_URL` in `.env` if the server moves.
