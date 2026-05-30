# Hybrid Knowledge Graph RAG System with Ollama

## Overview

This is a comprehensive implementation of a **Hybrid Knowledge Graph Retrieval-Augmented Generation (RAG)** system for healthcare data using **local LLM inference with Ollama**. It combines semantic vector search with Neo4j graph traversal and Ollama-based Cypher query generation to enable intelligent, context-aware querying of medical knowledge graphs without requiring external API keys.

### Key Features

1. **Node Vectorization**: Converts graph nodes into semantic embeddings using sentence-transformers
2. **Semantic Retrieval**: Vector similarity search across medical entities
3. **Graph Context**: Augments semantic results with graph neighbors and relationship patterns
4. **Ollama LLM Integration**: Local LLM-based Cypher query generation with schema reasoning
5. **Multi-hop Reasoning**: Sophisticated traversal strategies for complex queries
6. **Query Validation & Optimization**: Automatic Cypher validation and performance optimization
7. **Caching & Analytics**: Built-in query caching and execution statistics
8. **No API Keys Required**: All LLM inference runs locally on your machine

---

## Architecture

```
┌─────────────────────┐
│   User Query        │
│  (Natural Language) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Step 1: Semantic Retrieval     │
│  - Vector similarity search     │
│  - Node matching (top-k)        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Step 2: Context Augmentation   │
│  - Graph neighbor expansion     │
│  - Relationship discovery       │
│  - Frequency analysis           │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Step 3: Schema Reasoning       │
│  - Identify relevant labels     │
│  - Pattern suggestions          │
│  - Schema validation            │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Step 4: Cypher Generation      │
│  - LLM-based query creation     │
│  - Multiple suggestions         │
│  - Reasoning explanation        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Step 5: Validation & Execute   │
│  - Syntax validation            │
│  - Performance optimization     │
│  - Query execution              │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────┐
│   Results + Context  │
│   (with reasoning)   │
└──────────────────────┘
```

---

## Components

### 1. NodeVectorizer (`hybrid_kg_vectorizer.py`)

Converts Neo4j nodes into semantic embeddings for vector-based retrieval.

**Key Classes:**
- `NodeEmbedding`: Data class representing a vectorized node
- `NodeVectorizer`: Main vectorization engine
- `KnowledgeGraphSchema`: Schema management and caching

**Usage:**
```python
from hybrid_kg_vectorizer import NodeVectorizer

vectorizer = NodeVectorizer(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# Vectorize all nodes
embeddings = vectorizer.vectorize_all_nodes()
vectorizer.save_embeddings(embeddings, 'node_embeddings.json')

# Semantic search
matches = vectorizer.semantic_search(embeddings, "patient with heart disease", top_k=5)
```

**Features:**
- Support for both Hugging Face and OpenAI embeddings
- Batch processing of large graphs
- Change detection via hashing
- Optimized text extraction for different node types

---

### 2. HybridKGRetriever (`hybrid_kg_retriever.py`)

Combines semantic search with graph traversal for context-aware retrieval.

**Key Classes:**
- `RetrievedContext`: Data structure for retrieved context
- `HybridKGRetriever`: Main retrieval engine
- `ContextAugmenter`: Enhances context with graph insights

**Usage:**
```python
from hybrid_kg_retriever import HybridKGRetriever, ContextAugmenter

retriever = HybridKGRetriever(vectorizer, kg_schema, embeddings)

# Retrieve context
context = retriever.retrieve_context(
    query="medications for cardiovascular patients",
    top_k=5,
    expand_hops=1
)

# Augment with additional insights
augmenter = ContextAugmenter(driver)
context = augmenter.add_path_context(context)
context = augmenter.add_frequency_context(context)
```

**Context Components:**
- Semantic matches with similarity scores
- Graph neighbors at multiple hops
- Relevant relationship types
- Suggested Cypher patterns
- Schema information

---

### 3. CypherGenerator (`hybrid_kg_cypher_generator.py`)

LLM-based generation of optimized Cypher queries using local Ollama models with schema reasoning.

**Key Classes:**
- `GeneratedCypher`: Represents a generated query with metadata
- `CypherGenerator`: Main generation engine with Ollama support
- `MultiHopCypherEngine`: Specialized multi-hop traversal

**Usage:**
```python
from hybrid_kg_cypher_generator import CypherGenerator

# Initialize with Ollama (no API keys needed!)
generator = CypherGenerator(
    llm_provider="ollama",
    model_name="mistral",
    ollama_url="http://localhost:11434",
    kg_schema=schema
)

# Generate from context
queries = generator.generate_from_context(
    retrieved_context=context,
    user_query="What medications treat cardiovascular conditions?",
    num_suggestions=3
)

# Validate
is_valid, message = generator.validate_cypher(query.cypher_query, driver)

# Optimize
optimized = generator.optimize_cypher(query.cypher_query)
```

**Features:**
- Multiple query suggestions per question
- Confidence scoring
- Multi-hop detection
- Automatic optimization hints
- Schema validation
- Reasoning explanations
- **Local inference - no API keys required**

**Supported Ollama Models:**
- `mistral` - Fast, high-quality inference
- `neural-chat` - Optimized for dialogue
- `dolphin-mixtral` - Advanced reasoning
- `openchat` - Lightweight option
- Any other Ollama model you have installed

---

### 4. HybridGraphRAG (`hybrid_kg_rag_pipeline.py`)

Unified end-to-end pipeline orchestrating all components.

**Key Classes:**
- `HybridGraphRAG`: Main pipeline
- `GraphRAGFactory`: Factory for creating configured instances

**Usage:**
```python
from hybrid_kg_rag_pipeline import GraphRAGFactory

# Create pipeline
pipeline = GraphRAGFactory.create_pipeline(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    llm_provider="openai",
    llm_model="gpt-4",
    llm_api_key="your-api-key"
)

# Process query
result = pipeline.process_query(
    user_query="Find high-risk diabetic patients",
    execute_best=True
)

# Get statistics
stats = pipeline.get_statistics()

# Batch processing
results = pipeline.batch_process_queries(queries, batch_size=5)

# Export results
pipeline.export_results(results, "results.json")
```

---

## Installation

### Prerequisites

```bash
pip install neo4j sentence-transformers numpy openai langchain
```

### Optional Dependencies

For using OpenAI embeddings:
```bash
pip install openai
```

For using Anthropic models:
```bash
pip install anthropic
```

---

## Configuration

### Neo4j Setup

Ensure Neo4j is running:
```bash
docker run -d \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### Environment Variables

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export OPENAI_API_KEY="your-api-key"
```

---

## Usage Examples

### Basic Query Processing

```python
from hybrid_kg_rag_pipeline import GraphRAGFactory

pipeline = GraphRAGFactory.create_pipeline(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

result = pipeline.process_query(
    user_query="What are the side effects of metformin?"
)

print(f"Found {result['retrieved_context']['node_count']} relevant nodes")
print(f"Generated {len(result['cypher_suggestions'])} query suggestions")
print(f"Best query confidence: {result['best_query']['confidence']:.1%}")
```

### Semantic Search

```python
vectorizer.semantic_search(
    embeddings,
    "patient with high blood pressure",
    top_k=10
)
```

### Multi-hop Reasoning

```python
from hybrid_kg_cypher_generator import MultiHopCypherEngine

engine = MultiHopCypherEngine(generator, driver)

query = engine.generate_multi_hop_query(
    start_entity="Patient",
    target_entity="LabResult",
    hops=3,
    strategy="shortest_path"
)
```

### Batch Processing

```python
queries = [
    "Find diabetic patients with complications",
    "What medications interact with aspirin?",
    "Show recent lab results for high-risk patients"
]

results = pipeline.batch_process_queries(queries, batch_size=2)
pipeline.export_results(results, "batch_results.json")
```

---

## Query Reasoning Flow

The system generates detailed reasoning for each query:

1. **Semantic Matching**: Identifies relevant entities using vector similarity
2. **Graph Exploration**: Discovers related nodes and relationships
3. **Schema Analysis**: Validates node labels and relationship types
4. **Pattern Recognition**: Suggests traversal patterns based on context
5. **Cypher Generation**: Creates optimized queries with explanations
6. **Validation**: Checks syntax and execution feasibility
7. **Optimization**: Applies performance enhancements

---

## Performance Optimization

### Query Caching

```python
pipeline = GraphRAGFactory.create_pipeline(..., use_cache=True)

# First call: generates and caches
result1 = pipeline.process_query("Find diabetic patients")

# Second call: cache hit (instant)
result2 = pipeline.process_query("Find diabetic patients")

stats = pipeline.get_statistics()
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
```

### Batch Processing

```python
# Process in batches to optimize throughput
results = pipeline.batch_process_queries(
    queries=large_query_list,
    batch_size=10
)
```

### Index Creation

For optimal Neo4j performance:

```cypher
CREATE INDEX ON :Patient(patient_id);
CREATE INDEX ON :Condition(condition_name);
CREATE INDEX ON :Medication(medication_name);
```

---

## API Reference

### NodeVectorizer

```python
vectorizer.vectorize_node(node_id, node_label, properties) -> NodeEmbedding
vectorizer.vectorize_all_nodes(batch_size=100) -> List[NodeEmbedding]
vectorizer.semantic_search(embeddings, query, top_k=5) -> List[(NodeEmbedding, float)]
vectorizer.save_embeddings(embeddings, filepath)
vectorizer.load_embeddings(filepath) -> List[NodeEmbedding]
```

### HybridKGRetriever

```python
retriever.retrieve_context(query, top_k=5, expand_hops=1) -> RetrievedContext
retriever.filter_by_query_intent(context, intent) -> RetrievedContext
```

### CypherGenerator

```python
generator.generate_from_context(context, user_query, num_suggestions=3) -> List[GeneratedCypher]
generator.validate_cypher(query, driver) -> (bool, str)
generator.optimize_cypher(query) -> str
```

### HybridGraphRAG

```python
pipeline.process_query(user_query, top_k=5, expand_hops=1, execute_best=True) -> Dict
pipeline.batch_process_queries(queries, batch_size=5) -> List[Dict]
pipeline.get_statistics() -> Dict
pipeline.explain_query_reasoning(result) -> str
pipeline.export_results(results, filepath)
```

---

## Troubleshooting

### Embedding Generation is Slow

- Use a smaller model: `"sentence-transformers/all-MiniLM-L6-v2"`
- Enable GPU: `CUDA_VISIBLE_DEVICES=0`
- Cache embeddings: `vectorizer.save_embeddings()`

### LLM API Rate Limiting

- Implement exponential backoff
- Use batch processing with delays
- Cache query results

### Neo4j Connection Issues

- Check Neo4j is running: `curl http://localhost:7474`
- Verify credentials
- Adjust timeout: `neo4j_driver(..., connection_timeout=30)`

### Poor Semantic Results

- Try different embedding models
- Ensure sufficient graph data
- Verify node properties are populated

---

## Advanced Topics

### Custom Embedding Models

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectorizer = NodeVectorizer(..., embedding_model=model)
```

### Custom LLM Providers

Extend `CypherGenerator` to support additional LLM providers:

```python
class CustomLLMGenerator(CypherGenerator):
    def _initialize_llm(self, api_key):
        # Custom LLM initialization
        pass
```

### Schema-Driven Query Generation

```python
schema = KnowledgeGraphSchema(neo4j_uri, user, password)
schema_info = schema.get_schema()

# Use schema info for guided generation
for label, info in schema_info.items():
    print(f"{label}: {info['properties']}")
```

---

## Healthcare Domain Specifics

The system is optimized for healthcare knowledge graphs with:

- **Patient-centric architecture**: All data contextualized around patients
- **Medical relationships**: HAS_CONDITION, TAKES_MEDICATION, HAS_LAB_RESULT, etc.
- **Temporal data**: Encounter dates, medication start/end dates
- **Risk assessment**: Supports multi-factor risk scoring
- **Lab result hierarchies**: Report → Study → Result structure

### Example Healthcare Queries

1. "Find patients with cardiovascular risk factors"
2. "What are the contraindications for this medication?"
3. "Show lab result trends for diabetic patients"
4. "Which conditions are most common in this demographic?"
5. "What's the treatment pathway for sepsis patients?"

---

## Contributing

To extend the system:

1. Implement custom embedding models in `NodeVectorizer`
2. Add new retrieval strategies in `HybridKGRetriever`
3. Extend `CypherGenerator` for additional LLM providers
4. Create domain-specific retrieval filters

---

## License

MIT License

---

## References

- Neo4j Documentation: https://neo4j.com/docs/
- Sentence-Transformers: https://www.sbert.net/
- OpenAI API: https://platform.openai.com/docs/
- RAG Pattern: https://arxiv.org/abs/2005.11401

---

## Support

For issues and questions:
1. Check the examples in `example_usage.py`
2. Review logs (set logging level to DEBUG)
3. Verify Neo4j connection and data
4. Test components individually
