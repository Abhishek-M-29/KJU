# Ollama Setup Guide for Hybrid KG-RAG System

## What is Ollama?

Ollama is an open-source tool that allows you to run large language models locally on your machine. This eliminates the need for:
- OpenAI API keys
- Cloud-based inference costs
- Rate limiting or quota restrictions
- Network latency concerns

Perfect for the Hybrid KG-RAG system, Ollama provides free, local LLM inference for Cypher query generation.

---

## Installation

### Option 1: Direct Installation (Recommended)

**macOS:**
```bash
# Download and run the installer
https://ollama.ai/download

# Or via Homebrew
brew install ollama
```

**Linux:**
```bash
# Ubuntu/Debian
curl https://ollama.ai/install.sh | sh

# Or via package manager
# Check https://ollama.ai for your distribution
```

**Windows:**
```bash
# Download the installer from:
# https://ollama.ai/download

# Or use Windows Package Manager:
winget install Ollama.Ollama
```

### Option 2: Docker Installation

```bash
# CPU-only
docker run -d -p 11434:11434 ollama/ollama

# GPU support (NVIDIA)
docker run -d --gpus=all -p 11434:11434 ollama/ollama

# GPU support (AMD ROCm)
docker run -d --device /dev/kfd --device /dev/dri -p 11434:11434 ollama/ollama
```

---

## Verifying Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# You should see:
# {"models": []}  # Empty if no models installed yet
```

---

## Pulling Models

Once Ollama is installed and running, pull a model:

### Recommended Models

**Mistral (Recommended - Fastest)**
```bash
ollama pull mistral
# ~5GB, very fast, good quality
```

**Neural Chat (Alternative)**
```bash
ollama pull neural-chat
# ~5GB, optimized for chat/Q&A
```

**Dolphin Mixtral (Advanced)**
```bash
ollama pull dolphin-mixtral
# ~26GB, excellent reasoning, requires more resources
```

**OpenChat (Lightweight)**
```bash
ollama pull openchat
# ~3.8GB, fastest option for basic queries
```

### Verify Model Installation

```bash
curl http://localhost:11434/api/tags

# You should see:
# {"models": [{"name": "mistral:latest", ...}]}
```

---

## Starting Ollama

### Default (Auto-start on port 11434)

```bash
ollama serve
# Server running at http://localhost:11434
```

### Custom Port

```bash
OLLAMA_HOST=0.0.0.0:8000 ollama serve
# Server running at http://0.0.0.0:8000
```

### Background (macOS/Linux)

```bash
# Start as service
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

### Background (Windows)

Ollama runs as a service automatically after installation. To verify:

```powershell
# Check if service is running
Get-Service | Where-Object {$_.Name -like "*ollama*"}
```

---

## Configuring KG-RAG System for Ollama

### 1. Set Environment Variables

Create a `.env` file in your project directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 2. Update Python Code

**Quick Start:**
```python
from hybrid_kg_rag_pipeline import GraphRAGFactory

# Create pipeline with Ollama (no API keys!)
pipeline = GraphRAGFactory.create_pipeline(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="your_password",
    ollama_url="http://localhost:11434",
    ollama_model="mistral",
)

# Process query
result = pipeline.process_query("Find diabetic patients with complications")
```

**Manual Setup:**
```python
from hybrid_kg_cypher_generator import CypherGenerator
from hybrid_kg_vectorizer import KnowledgeGraphSchema

schema = KnowledgeGraphSchema(uri, user, password)

generator = CypherGenerator(
    llm_provider="ollama",
    model_name="mistral",
    ollama_url="http://localhost:11434",
    kg_schema=schema
)
```

---

## Troubleshooting

### Issue: "Connection refused" / "Cannot reach Ollama"

**Solution:**
```bash
# 1. Verify Ollama is running
curl http://localhost:11434/api/tags

# 2. If not running, start it
ollama serve

# 3. Check if running on different port
# Default: http://localhost:11434
# Update OLLAMA_URL environment variable if needed
```

### Issue: "No models found"

**Solution:**
```bash
# Pull a model
ollama pull mistral

# Verify it was pulled
ollama list
```

### Issue: Slow responses / High memory usage

**Solutions:**
1. Use lighter model: `ollama pull openchat` (smaller, faster)
2. Reduce model loading time: Ollama caches loaded models
3. Check available system resources
4. Try quantized versions (already included)

### Issue: GPU not being used

**Verify GPU support:**
```bash
# Check Ollama logs
ollama version
# Look for GPU information

# For NVIDIA:
ollama list  # Shows GPU info if available

# For AMD ROCm (Docker):
docker run -d --device /dev/kfd --device /dev/dri -p 11434:11434 ollama/ollama
```

---

## Performance Tips

### 1. Model Selection by Use Case

| Model | Speed | Quality | Memory | Best For |
|-------|-------|---------|--------|----------|
| openchat | ⚡⚡⚡ | ⭐⭐ | 3.8GB | Quick answers |
| mistral | ⚡⚡ | ⭐⭐⭐ | 5GB | **Recommended** |
| neural-chat | ⚡⚡ | ⭐⭐⭐ | 5GB | Dialogue-based queries |
| dolphin-mixtral | ⚡ | ⭐⭐⭐⭐⭐ | 26GB | Complex reasoning |

### 2. System Requirements

**Minimum:**
- 8GB RAM (for smaller models)
- CPU: Modern processor (2+ cores)
- 10GB free disk space

**Recommended:**
- 16GB+ RAM
- GPU (NVIDIA/AMD) for faster inference
- SSD storage

**For Advanced Models:**
- 32GB+ RAM
- GPU strongly recommended
- 40GB+ disk space

### 3. Optimization Techniques

```python
# Batch multiple queries for efficiency
queries = [
    "Find patients with heart disease",
    "List medications for diabetes",
    "Show cardiovascular risk factors"
]

for query in queries:
    result = pipeline.process_query(query)
    # Model stays loaded, faster subsequent queries
```

---

## Model Comparison for KG-RAG

| Aspect | Mistral | Neural Chat | Dolphin Mixtral | OpenChat |
|--------|---------|-------------|-----------------|----------|
| Cypher Generation | Excellent | Good | Excellent | Good |
| Schema Understanding | Excellent | Good | Excellent | Fair |
| Speed | Fast | Medium | Slow | Very Fast |
| Memory | 5GB | 5GB | 26GB | 3.8GB |
| Inference Time | 2-5s | 2-5s | 5-10s | 1-3s |
| Recommended | ✅ | ✅ | For Complex | For Demo |

**Recommendation:** Start with **Mistral** for the best balance of speed and quality.

---

## Advanced Configuration

### Using Different Ollama Instances

```python
# Multi-instance setup
from hybrid_kg_cypher_generator import CypherGenerator

# Different models on different machines
generator1 = CypherGenerator(
    model_name="mistral",
    ollama_url="http://machine1:11434"
)

generator2 = CypherGenerator(
    model_name="dolphin-mixtral",
    ollama_url="http://machine2:11434"
)
```

### Custom Model Parameters

```python
# Modify generation parameters in code
# (Advanced - requires modifying hybrid_kg_cypher_generator.py)

# In the requests.post call, adjust:
json={
    "model": self.model_name,
    "prompt": full_prompt,
    "stream": False,
    "temperature": 0.3,      # Adjust creativity (0-1)
    "top_p": 0.9,            # Adjust diversity
    "top_k": 40,             # Top-k sampling
    "num_predict": 1000,     # Max tokens
}
```

---

## Next Steps

1. **Install Ollama:** Follow installation steps above
2. **Pull a model:** `ollama pull mistral`
3. **Start Ollama:** `ollama serve`
4. **Run quick_start.py:** `python quick_start.py`
5. **Try examples:** See [HYBRID_KG_RAG_README.md](HYBRID_KG_RAG_README.md)

---

## Resources

- **Ollama Official:** https://ollama.ai
- **Model Library:** https://ollama.ai/library
- **GitHub:** https://github.com/jmorganca/ollama
- **Discord Community:** https://discord.gg/ollama

---

## License

This guide is part of the Hybrid KG-RAG system. Ollama is open-source and MIT licensed.
