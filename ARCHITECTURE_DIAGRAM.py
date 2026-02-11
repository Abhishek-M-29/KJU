"""
Hybrid Knowledge Graph RAG System - Architecture Overview
"""

# =============================================================================
# SYSTEM ARCHITECTURE DIAGRAM
# =============================================================================

ARCHITECTURE = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                    HYBRID KG-RAG SYSTEM ARCHITECTURE                        ║
╚═════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ INPUT LAYER                                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Natural Language│  │  Patient Query   │  │  Clinical Query  │          │
│  │  Questions       │  │  (SQL-like)      │  │  (Knowledge)     │          │
│  └──────────┬───────┘  └────────┬─────────┘  └────────┬─────────┘          │
│             └──────────────────┬──────────────────────┘                     │
└─────────────────────────────────┼────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ VECTORIZATION LAYER                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Input Query ──► Text Processing ──► Embedding Model                        │
│                                            │                                │
│                                      ┌─────┴─────┐                         │
│                                      ▼           ▼                         │
│                              SentenceTransformers OpenAI API                │
│                                            │                                │
│                                    Query Embedding Vector                   │
│                                    (768-1536 dimensions)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SEMANTIC RETRIEVAL LAYER                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────┐                          │
│  │  Node Embedding Cache (Pre-computed)         │                          │
│  │  - Patient nodes (embeddings)                │                          │
│  │  - Condition nodes (embeddings)              │                          │
│  │  - Medication nodes (embeddings)             │                          │
│  │  - Lab Result nodes (embeddings)             │                          │
│  │  - ... (all node types)                      │                          │
│  └──────────────────────────────────────────────┘                          │
│                 │                                                           │
│  Cosine Similarity Calculation                                             │
│  Scores = Query_Embedding • Node_Embeddings / (||Q|| • ||N||)            │
│                 │                                                           │
│  Top-K Selection (e.g., top 5 matches)                                    │
│                                                                              │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐             │
│  │ Patient 42   │ Condition 15 │ Medication 8 │ LabResult 23 │  ...       │
│  │ (Score: 0.89)│ (Score: 0.87)│ (Score: 0.82)│ (Score: 0.78)│            │
│  └──────────────┴──────────────┴──────────────┴──────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GRAPH CONTEXT AUGMENTATION LAYER                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  For Each Retrieved Node:                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ 1. Expand Neighbors (N hops in graph)                             │    │
│  │    Query: (node)-[*1..N]-(neighbor)                               │    │
│  │                                                                    │    │
│  │ 2. Find Connecting Paths                                          │    │
│  │    Query: shortestPath((start)-[*1..3]-(end))                    │    │
│  │                                                                    │    │
│  │ 3. Extract Relationship Types                                     │    │
│  │    Query: MATCH (n:Label)-[r]->() RETURN type(r)                │    │
│  │                                                                    │    │
│  │ 4. Frequency Analysis                                             │    │
│  │    Query: MATCH ()-[r:TYPE]->() RETURN count(r)                 │    │
│  │                                                                    │    │
│  │ 5. Schema Validation                                              │    │
│  │    Extract available properties for each node label               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Result: RetrievedContext Object                                           │
│  {                                                                           │
│    retrieved_nodes: [nodes with similarity],                              │
│    neighboring_nodes: [expanded context],                                │
│    node_labels: [Patient, Condition, ...],                              │
│    relationships: [HAS_CONDITION, TAKES_MEDICATION, ...],               │
│    suggested_patterns: ["(p:Patient)-[r]->(c:Condition)", ...],        │
│    schema_info: {Patient: {...}, Condition: {...}, ...}                 │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SCHEMA REASONING LAYER                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────┐                       │
│  │ Schema Knowledge Base                           │                       │
│  │ - Node Labels: 18 types                         │                       │
│  │ - Relationships: 17 types                       │                       │
│  │ - Properties per label: {...}                   │                       │
│  │ - Typical patterns: {...}                       │                       │
│  └─────────────────────────────────────────────────┘                       │
│                          │                                                  │
│  Reasoning:                                                                 │
│  1. Identify Intent: "Find high-risk patients" → Risk-related entities     │
│  2. Select Relevant Labels: [Patient, Condition, LabResult]               │
│  3. Find Connecting Paths: PATIENT -[*]-> CONDITION -[*]-> LABRESULT    │
│  4. Filter Relationships: HAS_CONDITION, HAS_LAB_RESULT                   │
│                                                                              │
│  Output: Pattern Suggestions                                                │
│  [                                                                           │
│    "(p:Patient)-[h:HAS_CONDITION]->(c:Condition)",                        │
│    "(p:Patient)-[*1..2]->(lr:LabResult)",                                 │
│    "shortestPath((p:Patient)-[*1..3]-(high_risk:Condition))"              │
│  ]                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ CYPHER GENERATION LAYER (LLM-based)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │ LLM Prompt Engineering                               │                  │
│  │                                                      │                  │
│  │ System Prompt:                                       │                  │
│  │ "You are a Neo4j Cypher expert for healthcare graphs"│                  │
│  │ [Full schema documentation]                         │                  │
│  │ [Example queries]                                   │                  │
│  │                                                      │                  │
│  │ User Prompt:                                         │                  │
│  │ "Generate Cypher for: [user_query]                  │                  │
│  │  Context: [retrieved_context]                       │                  │
│  │  Patterns: [suggested_patterns]"                    │                  │
│  └──────────────────────────────────────────────────────┘                  │
│                          │                                                  │
│              ┌───────────┴───────────┐                                     │
│              ▼                       ▼                                     │
│          OpenAI API           Anthropic API                               │
│          (GPT-4)              (Claude-3)                                  │
│              │                       │                                     │
│              └───────────┬───────────┘                                     │
│                          ▼                                                  │
│  LLM Response Parsing:                                                      │
│  Extract:                                                                    │
│  1. Cypher Query                                                            │
│  2. Explanation/Comments                                                   │
│  3. Reasoning (why this query)                                             │
│  4. Confidence Score                                                       │
│  5. Optimizations Applied                                                  │
│  6. Multi-hop Detection                                                    │
│                                                                              │
│  Generate Multiple Suggestions: 3-5 variants                              │
│                                                                              │
│  Suggestion 1 (Breadth-first):                                            │
│    MATCH (p:Patient)-[r]->(c:Condition)                                 │
│    RETURN p, c LIMIT 100                                                  │
│    Confidence: 0.92                                                        │
│                                                                              │
│  Suggestion 2 (Depth-first):                                              │
│    MATCH (p:Patient)-[r1]->(c:Condition)-[r2]->(t:Treatment)            │
│    RETURN p, c, t LIMIT 50                                                │
│    Confidence: 0.87                                                        │
│                                                                              │
│  Suggestion 3 (Aggregation):                                               │
│    MATCH (p:Patient)-[r:HAS_CONDITION]->(c:Condition)                   │
│    WITH p, COUNT(c) as condition_count                                    │
│    WHERE condition_count > 5                                               │
│    RETURN p, condition_count LIMIT 100                                    │
│    Confidence: 0.85                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ VALIDATION & OPTIMIZATION LAYER                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  For Each Generated Query:                                                  │
│                                                                              │
│  1. Syntax Validation                                                       │
│     Try: driver.session().run(query)                                       │
│     Result: ✓ Valid or ✗ Error                                            │
│                                                                              │
│  2. Performance Analysis                                                    │
│     - Detects missing LIMIT clauses                                        │
│     - Suggests index usage                                                 │
│     - Flags expensive operations                                           │
│                                                                              │
│  3. Query Optimization                                                      │
│     Original:  MATCH (p:Patient) RETURN p                                │
│     Optimized: MATCH (p:Patient) RETURN p LIMIT 100                      │
│                                                                              │
│  4. Ranking                                                                 │
│     - Sort by confidence                                                   │
│     - Filter valid queries only                                            │
│     - Select best query                                                    │
│                                                                              │
│  Output: Validated & Ranked Queries                                       │
│  [                                                                           │
│    {query: "...", confidence: 0.92, valid: true, optimizations: [...]},   │
│    {query: "...", confidence: 0.87, valid: true, optimizations: [...]},   │
│    {query: "...", confidence: 0.85, valid: false, error: "..."},          │
│  ]                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ EXECUTION LAYER                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Execute Best Query (highest confidence):                                  │
│                                                                              │
│  driver.session().run(best_query)                                          │
│                                                                              │
│  Results:                                                                    │
│  ┌─────────────────────────────────────────────────┐                       │
│  │ Record 1: {patient: {...}, conditions: [...]}   │                       │
│  │ Record 2: {patient: {...}, conditions: [...]}   │                       │
│  │ Record 3: {patient: {...}, conditions: [...]}   │                       │
│  │ ...                                              │                       │
│  │ (Up to LIMIT, e.g., 100 records)                │                       │
│  └─────────────────────────────────────────────────┘                       │
│                                                                              │
│  Metrics:                                                                    │
│  - Execution Time: 0.234s                                                   │
│  - Records Returned: 42                                                     │
│  - Relationship Traversals: 156                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT LAYER                                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HybridGraphRAG Response:                                                  │
│  {                                                                           │
│    "user_query": "Find diabetic patients with complications",             │
│    "elapsed_time": 1.23,                                                  │
│    "retrieved_context": {                                                  │
│      "node_count": 87,                                                     │
│      "node_labels": ["Patient", "Condition", "LabResult"],               │
│      "relationships": ["HAS_CONDITION", "HAS_LAB_RESULT"],               │
│      "suggested_patterns": [...]                                          │
│    },                                                                       │
│    "cypher_suggestions": [                                                │
│      {                                                                      │
│        "query": "...",                                                     │
│        "explanation": "...",                                              │
│        "confidence": 0.92,                                                │
│        "multi_hop": true,                                                │
│        "is_valid": true                                                   │
│      },                                                                     │
│      ...                                                                    │
│    ],                                                                       │
│    "best_query": {                                                         │
│      "query": "MATCH (p:Patient)-[h:HAS_CONDITION]-(c:Condition)...",  │
│      "confidence": 0.92                                                   │
│    },                                                                       │
│    "execution_result": {                                                   │
│      "success": true,                                                      │
│      "record_count": 42,                                                   │
│      "records": [...]                                                      │
│    }                                                                         │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌─────────────┐ ┌──────────┐ ┌───────────┐
            │ Web API     │ │Dashboard │ │ Analytics │
            │ Endpoint    │ │ Display  │ │ Export    │
            └─────────────┘ └──────────┘ └───────────┘


╔═════════════════════════════════════════════════════════════════════════════╗
║                           COMPONENT INTERACTIONS                            ║
╚═════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        HybridGraphRAG (Orchestrator)                        │
│                                │                                             │
│                ┌───────────────┼───────────────┐                            │
│                ▼               ▼               ▼                            │
│           Vectorizer      Retriever       CypherGenerator                  │
│              │                │                 │                          │
│              └────────────────┼─────────────────┘                          │
│                               │                                             │
│                       Neo4j Graph Database                                 │
│                               │                                             │
│                  ┌────────────┴────────────┐                              │
│                  ▼                         ▼                              │
│            Patient Data            Medical Knowledge                     │
│            (Nodes & Edges)         (Schema & Relationships)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


╔═════════════════════════════════════════════════════════════════════════════╗
║                          DATA FLOW EXAMPLE                                  ║
╚═════════════════════════════════════════════════════════════════════════════╝

Input:
  "What medications should be prescribed for diabetic patients with hypertension?"

Step 1: Vectorization
  Query Embedding: [0.23, -0.45, 0.78, ..., 0.12] (768-dim)

Step 2: Semantic Search
  Top Matches:
  - Diabetes (0.94)
  - Hypertension (0.91)
  - Medication (0.87)
  - Treatment (0.85)
  - Patient (0.82)

Step 3: Graph Augmentation
  Retrieved Nodes:
  - 42 Diabetes condition records
  - 38 Hypertension condition records
  - 156 Medication records
  - 89 Patient-condition relationships

Step 4: Schema Reasoning
  Relevant Patterns:
  - (Patient)-[HAS_CONDITION]-(Condition)
  - (Medication)-[TREATS]-(Condition)
  - (Patient)-[TAKES_MEDICATION]-(Medication)

Step 5: LLM Cypher Generation
  Generated Queries:
  1. MATCH (p:Patient)-[h:HAS_CONDITION]-(c:Condition)
     WHERE c.name IN ['Diabetes', 'Hypertension']
     MATCH (m:Medication)-[t:TREATS]-(c)
     RETURN DISTINCT m, c
     LIMIT 50
     [Confidence: 0.93]

  2. MATCH (p:Patient)-[hc:HAS_CONDITION]-(c:Condition)
     WHERE c.name IN ['Diabetes', 'Hypertension']
     MATCH (p)-[tm:TAKES_MEDICATION]-(m:Medication)
     WITH m, COUNT(p) as patient_count
     RETURN m, patient_count
     ORDER BY patient_count DESC
     LIMIT 50
     [Confidence: 0.87]

Step 6: Validation & Optimization
  ✓ Query 1: Valid, optimized, confidence 0.93 (SELECTED)
  ✓ Query 2: Valid, optimized, confidence 0.87

Step 7: Execution
  Results:
  - Metformin treats Diabetes
  - Lisinopril treats Hypertension
  - Amlodipine treats Hypertension
  - ... (48 more)

Output:
  {
    "user_query": "...",
    "results": [Metformin, Lisinopril, ...],
    "cypher_used": "...",
    "confidence": 0.93,
    "execution_time": 0.342s
  }
"""

# Print architecture
if __name__ == "__main__":
    print(ARCHITECTURE)
    
    # Save to file
    with open("ARCHITECTURE_DIAGRAM.txt", "w") as f:
        f.write(ARCHITECTURE)
    
    print("\n✓ Architecture diagram saved to ARCHITECTURE_DIAGRAM.txt")
