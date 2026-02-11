# Integration Guide: Hybrid KG-RAG with Healthcare System

## Overview

This guide explains how to integrate the Hybrid KG-RAG system with your existing healthcare knowledge graph, AI models (cardiovascular, diabetes, sepsis), and data pipelines.

---

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│         Healthcare Data Pipeline                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Synthea → MariaDB → Neo4j Knowledge Graph            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│    Hybrid KG-RAG System                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Vectorizer   │  │ Retriever    │  │ Cypher Gen   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│    AI Models for Clinical Prediction                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Cardiovascular│  │ Diabetes     │  │ Sepsis       │     │
│  │ Risk Model   │  │ Risk Model   │  │ Prediction   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Query Results  │
        │  + Risk Scores  │
        │  + Reasoning    │
        └─────────────────┘
```

---

## Step 1: Connect to Your Neo4j Database

The Hybrid KG-RAG system connects directly to your existing Neo4j instance.

### Configuration

```python
# Set environment variables
import os

os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'your_password'
os.environ['OPENAI_API_KEY'] = 'your_openai_key'
```

### Verify Connection

```python
from hybrid_kg_vectorizer import KnowledgeGraphSchema

schema = KnowledgeGraphSchema(
    neo4j_uri=os.environ['NEO4J_URI'],
    neo4j_user=os.environ['NEO4J_USER'],
    neo4j_password=os.environ['NEO4J_PASSWORD']
)

# Check your schema
labels = schema.get_node_labels()
print(f"Node types: {labels}")

# Should show: Patient, Condition, Medication, LabResult, etc.
```

---

## Step 2: Initialize and Vectorize Your Graph

Generate embeddings for all nodes in your existing graph.

### First-time Setup

```python
from hybrid_kg_vectorizer import NodeVectorizer

vectorizer = NodeVectorizer(
    neo4j_uri=os.environ['NEO4J_URI'],
    neo4j_user=os.environ['NEO4J_USER'],
    neo4j_password=os.environ['NEO4J_PASSWORD'],
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)

# This will vectorize all nodes in your graph
# For large graphs (1000+ nodes), this may take time
print("Generating embeddings... (this may take 5-30 minutes)")
embeddings = vectorizer.vectorize_all_nodes(batch_size=100)

# Save embeddings
vectorizer.save_embeddings(embeddings, 'healthcare_embeddings.json')
print(f"Saved {len(embeddings)} node embeddings")
```

### Subsequent Usage

```python
# Load pre-computed embeddings
embeddings = vectorizer.load_embeddings('healthcare_embeddings.json')
print(f"Loaded {len(embeddings)} embeddings from cache")
```

### Update Embeddings When Graph Changes

```python
# After adding new patients/conditions to Neo4j:
from datetime import datetime

vectorizer = NodeVectorizer(...)

# Only vectorize new nodes (those without embeddings)
new_embeddings = vectorizer.vectorize_all_nodes()

# Merge with existing embeddings
existing_embeddings = vectorizer.load_embeddings('healthcare_embeddings.json')
all_embeddings = merge_embeddings(existing_embeddings, new_embeddings)

vectorizer.save_embeddings(all_embeddings, 'healthcare_embeddings.json')
```

---

## Step 3: Integrate with Your AI Models

### Pattern: Query Graph + Get Risk Scores

```python
from hybrid_kg_rag_pipeline import GraphRAGFactory
from AI_Models.cardio.cardiovascular_api import CardiovascularRiskModel
from AI_Models.diabetes.diabetes_api import DiabetesRiskModel

# Initialize RAG pipeline
rag_pipeline = GraphRAGFactory.create_pipeline(
    neo4j_uri=os.environ['NEO4J_URI'],
    neo4j_user=os.environ['NEO4J_USER'],
    neo4j_password=os.environ['NEO4J_PASSWORD']
)

# Initialize AI models
cardio_model = CardiovascularRiskModel()
diabetes_model = DiabetesRiskModel()

# Process query
query = "Find patients with cardiovascular risk factors"
result = rag_pipeline.process_query(query, execute_best=True)

# Extract patient data from results
patients = extract_patient_data(result)

# Get risk scores
for patient in patients:
    cardio_risk = cardio_model.predict(patient)
    diabetes_risk = diabetes_model.predict(patient)
    
    print(f"Patient {patient['id']}:")
    print(f"  Cardiovascular Risk: {cardio_risk:.2%}")
    print(f"  Diabetes Risk: {diabetes_risk:.2%}")
```

### Pattern: Clinical Decision Support

```python
def clinical_decision_support(patient_id):
    """
    Integrated system providing:
    1. Patient data from graph
    2. Risk assessments from AI models
    3. Recommended interventions
    """
    
    # Query patient data
    query = f"Find all conditions and medications for patient {patient_id}"
    result = rag_pipeline.process_query(query, execute_best=True)
    
    # Extract patient information
    patient_data = result['execution_result']['records'][0]
    
    # Get risk scores
    cardio_risk = cardio_model.predict(patient_data)
    diabetes_risk = diabetes_model.predict(patient_data)
    
    # Generate recommendations
    recommendations = []
    if cardio_risk > 0.7:
        recommendations.append("Schedule cardiology consultation")
        recommendations.append("Consider ECG and stress test")
    
    if diabetes_risk > 0.6:
        recommendations.append("Order HbA1c test")
        recommendations.append("Refer to endocrinology")
    
    return {
        'patient_id': patient_id,
        'cardio_risk': cardio_risk,
        'diabetes_risk': diabetes_risk,
        'recommendations': recommendations,
        'cypher_used': result['best_query']['query'],
        'reasoning': result['best_query']['explanation']
    }

# Use it
decision = clinical_decision_support('patient_123')
print(f"Recommendations for {decision['patient_id']}:")
for rec in decision['recommendations']:
    print(f"  - {rec}")
```

---

## Step 4: Build Custom Query Patterns

Define healthcare-specific query patterns that your system should support.

### Pattern: Risk Stratification

```python
def find_high_risk_patients():
    """Find patients with multiple risk factors"""
    
    query = """
    What patients have:
    - Age > 60
    - Any cardiovascular condition
    - Take multiple medications (> 5)
    """
    
    result = rag_pipeline.process_query(query, execute_best=True)
    return result['execution_result']['records']
```

### Pattern: Medication Interaction Check

```python
def check_medication_interactions(medications):
    """Check for dangerous medication interactions"""
    
    med_list = ", ".join(medications)
    query = f"""
    Do these medications interact dangerously:
    {med_list}
    """
    
    result = rag_pipeline.process_query(query, execute_best=True)
    return result
```

### Pattern: Treatment Pathway

```python
def get_treatment_pathway(condition):
    """Get recommended treatment pathway for a condition"""
    
    query = f"""
    What is the standard treatment pathway for {condition}?
    Include all medications and typical follow-up tests.
    """
    
    result = rag_pipeline.process_query(query, execute_best=True)
    return result
```

---

## Step 5: Integrate with Your Data Pipelines

### Auto-Sync with Synthea Pipeline

```python
import schedule
import time
from synthea_to_neo4j import SyntheaPipeline

def sync_and_vectorize():
    """
    Scheduled job to:
    1. Sync new Synthea data to Neo4j
    2. Vectorize new nodes
    """
    
    # Sync Synthea data
    pipeline = SyntheaPipeline()
    new_patient_count = pipeline.run()
    
    if new_patient_count > 0:
        print(f"Added {new_patient_count} new patients")
        
        # Vectorize new nodes
        vectorizer = NodeVectorizer(...)
        embeddings = vectorizer.vectorize_all_nodes()
        vectorizer.save_embeddings(embeddings, 'healthcare_embeddings.json')
        
        print(f"Updated embeddings for {len(embeddings)} nodes")

# Schedule sync
schedule.every().day.at("02:00").do(sync_and_vectorize)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Batch Process Patient Cohorts

```python
def batch_analyze_cohort(cohort_query, batch_size=100):
    """
    Analyze a cohort of patients:
    1. Query graph for matching patients
    2. Calculate risk scores
    3. Export results
    """
    
    # Get patient list
    result = rag_pipeline.process_query(cohort_query, execute_best=True)
    patients = result['execution_result']['records']
    
    results = []
    for i in range(0, len(patients), batch_size):
        batch = patients[i:i+batch_size]
        
        for patient in batch:
            risk_data = {
                'patient_id': patient['id'],
                'cardio_risk': cardio_model.predict(patient),
                'diabetes_risk': diabetes_model.predict(patient),
            }
            results.append(risk_data)
        
        print(f"Processed {min(i+batch_size, len(patients))}/{len(patients)}")
    
    return results
```

---

## Step 6: Expose via API

### FastAPI Wrapper

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Clinical Decision Support")

class QueryRequest(BaseModel):
    query: str
    execute_best: bool = True

class RiskAssessmentRequest(BaseModel):
    patient_id: str

@app.post("/query")
async def process_query(request: QueryRequest):
    """Process natural language query against knowledge graph"""
    try:
        result = rag_pipeline.process_query(
            user_query=request.query,
            execute_best=request.execute_best
        )
        return {
            "success": True,
            "query": request.query,
            "nodes_found": result['retrieved_context']['node_count'],
            "best_confidence": result['best_query']['confidence'] if result['best_query'] else 0,
            "cypher": result['best_query']['query'] if result['best_query'] else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/risk-assessment")
async def get_risk_assessment(request: RiskAssessmentRequest):
    """Get risk assessment for patient"""
    try:
        decision = clinical_decision_support(request.patient_id)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check system health"""
    return {
        "status": "healthy",
        "graph_nodes": len(embeddings),
        "cache_size": len(rag_pipeline.query_cache)
    }

# Run with: uvicorn api:app --reload
```

---

## Step 7: Monitoring and Optimization

### Performance Monitoring

```python
def monitor_pipeline_performance():
    """Track pipeline performance metrics"""
    
    stats = rag_pipeline.get_statistics()
    
    print(f"Pipeline Statistics:")
    print(f"  Total Queries: {stats['total_queries_processed']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
    print(f"  Avg Time: {stats['average_execution_time']:.2f}s")
    print(f"  Min/Max Time: {stats['min_execution_time']:.2f}s / {stats['max_execution_time']:.2f}s")
    
    # Alert if performance degrades
    if stats['average_execution_time'] > 5.0:
        print("⚠️  WARNING: Average query time exceeds 5 seconds")
        # Trigger optimization
```

### Query Optimization

```python
def optimize_slow_queries():
    """Identify and optimize slow queries"""
    
    # Check slow queries from cache
    slow_queries = [
        (q, t) for q, t in zip(
            rag_pipeline.query_cache.keys(),
            rag_pipeline.execution_stats['execution_times']
        )
        if t > 2.0
    ]
    
    for query, exec_time in slow_queries:
        print(f"Slow query ({exec_time:.2f}s): {query}")
        # Suggest optimization or add indexes
```

---

## Step 8: Testing Integration

### Unit Tests

```python
import pytest

def test_rag_pipeline_creation():
    pipeline = GraphRAGFactory.create_pipeline(...)
    assert pipeline is not None
    stats = pipeline.get_statistics()
    assert 'total_queries_processed' in stats

def test_semantic_search():
    matches = vectorizer.semantic_search(embeddings, "heart disease", top_k=5)
    assert len(matches) > 0
    assert all(score >= 0 and score <= 1 for _, score in matches)

def test_cypher_generation():
    result = rag_pipeline.process_query("Find diabetic patients")
    assert len(result['cypher_suggestions']) > 0
    for suggestion in result['cypher_suggestions']:
        assert 'cypher_query' in suggestion
        assert 'confidence' in suggestion
```

### Integration Tests

```python
def test_end_to_end_query_and_risk():
    """Test complete flow: query + risk assessment"""
    
    # Process query
    query = "Find patients with cardiovascular risk factors"
    result = rag_pipeline.process_query(query, execute_best=True)
    
    # Verify results
    assert result['execution_result']['success']
    patients = result['execution_result']['records']
    
    # Get risk scores
    for patient in patients[:3]:
        risk = cardio_model.predict(patient)
        assert 0 <= risk <= 1
```

---

## Best Practices

1. **Cache Embeddings**: Regenerate embeddings only when Neo4j data changes significantly
2. **Monitor Performance**: Track query times and optimize indexes on frequently queried properties
3. **Version Control**: Keep embeddings and configurations in git (exclude sensitive data)
4. **Error Handling**: Gracefully handle Neo4j connection failures
5. **Rate Limiting**: Implement rate limiting if exposing via API
6. **Audit Logging**: Log all clinical queries for compliance
7. **Regular Updates**: Retrain embeddings monthly as new patient data accumulates

---

## Troubleshooting

### Slow Vectorization

```python
# Use smaller embedding model
vectorizer = NodeVectorizer(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # Smaller/faster
)

# Or use GPU
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### Poor Query Results

```python
# Debug: Check what nodes are being retrieved
matches = vectorizer.semantic_search(embeddings, query, top_k=20)
for emb, score in matches[:5]:
    print(f"{emb.node_label}: {score:.3f} - {emb.text_content[:100]}")
```

### Neo4j Memory Issues

```python
# Add LIMIT to queries
# Reduce batch size for vectorization
embeddings = vectorizer.vectorize_all_nodes(batch_size=10)  # Smaller batches
```

---

## Support

For questions on integration:
1. Check example files in `example_usage.py`
2. Review your existing system docs
3. Test components individually
4. Enable DEBUG logging for detailed error messages

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
