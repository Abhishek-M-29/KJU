"""
Example Usage of Hybrid KG-RAG System
Demonstrates how to use the hybrid knowledge graph with vectorization and Cypher generation.
"""

import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Basic example: Create pipeline and process a query"""
    
    from hybrid_kg_rag_pipeline import GraphRAGFactory
    
    logger.info("=== Basic Usage Example ===")
    
    # Create pipeline
    pipeline = GraphRAGFactory.create_pipeline(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        ollama_url="http://localhost:11434",
        ollama_model="qwen2.5:7b-instruct",
    )
    
    # Process a healthcare query
    query = "What medications are prescribed for patients with cardiovascular conditions?"
    
    logger.info(f"Processing query: {query}")
    result = pipeline.process_query(
        user_query=query,
        top_k=5,
        expand_hops=1,
        num_cypher_suggestions=3,
        execute_best=True,
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"Query: {result['user_query']}")
    print(f"Processing Time: {result['elapsed_time']:.2f}s")
    print("\nRetrieved Context:")
    print(f"  - Nodes Found: {result['retrieved_context']['node_count']}")
    print(f"  - Node Types: {', '.join(result['retrieved_context']['node_labels'])}")
    print(f"  - Relationships: {', '.join(result['retrieved_context']['relationships'])}")
    
    print("\nGenerated Cypher Queries:")
    for i, suggestion in enumerate(result['cypher_suggestions'], 1):
        print(f"\n  Suggestion {i}:")
        print(f"    - Confidence: {suggestion['confidence']:.1%}")
        print(f"    - Valid: {suggestion['is_valid']}")
        print(f"    - Multi-hop: {suggestion['multi_hop']}")
        print(f"    - Query:\n{suggestion['query'][:200]}...")
    
    if result['execution_result'] and result['execution_result']['success']:
        print(f"\nExecution Result:")
        print(f"  - Records Found: {result['execution_result']['record_count']}")
        print(f"  - Sample Records: {len(result['execution_result']['records'])} returned")
    
    # Get and display statistics
    stats = pipeline.get_statistics()
    print("\nPipeline Statistics:")
    print(f"  - Total Queries: {stats['total_queries_processed']}")
    print(f"  - Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
    print(f"  - Avg Execution Time: {stats['average_execution_time']:.2f}s")
    
    pipeline.close()
    print("\n" + "="*80 + "\n")


def example_batch_processing():
    """Example: Process multiple queries in batch"""
    
    from hybrid_kg_rag_pipeline import GraphRAGFactory
    
    logger.info("=== Batch Processing Example ===")
    
    pipeline = GraphRAGFactory.create_pipeline(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
    )
    
    queries = [
        "Find high-risk diabetic patients",
        "Which medications interact with each other?",
        "Show all encounters for patient X in the last month",
        "What are the common symptoms for cardiovascular diseases?",
    ]
    
    logger.info(f"Processing {len(queries)} queries in batch")
    results = pipeline.batch_process_queries(queries, batch_size=2)
    
    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = f"batch_results_{timestamp}.json"
    pipeline.export_results(results, export_file)
    
    logger.info(f"Batch processing complete. Results exported to {export_file}")
    
    # Print summary
    print(f"\nProcessed {len(results)} queries")
    for result in results:
        print(f"  - {result['user_query']}: {result['retrieved_context']['node_count']} nodes retrieved")
    
    pipeline.close()


def example_semantic_search():
    """Example: Semantic search without Cypher generation"""
    
    from hybrid_kg_vectorizer import NodeVectorizer
    from hybrid_kg_retriever import HybridKGRetriever
    
    logger.info("=== Semantic Search Example ===")
    
    # Initialize vectorizer and retriever
    vectorizer = NodeVectorizer(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
    )
    
    # Load embeddings
    embeddings = vectorizer.load_embeddings('node_embeddings.json')
    
    # Semantic search
    query = "patient with heart disease taking medication"
    matches = vectorizer.semantic_search(embeddings, query, top_k=10)
    
    print(f"\nSemantic search results for: '{query}'")
    print(f"Found {len(matches)} matches:")
    
    for i, (embedding, score) in enumerate(matches, 1):
        print(f"\n  {i}. {embedding.node_label} (score: {score:.3f})")
        print(f"     Text: {embedding.text_content[:100]}...")
        print(f"     Properties: {embedding.node_properties}")
    
    vectorizer.close()


def example_multi_hop_reasoning():
    """Example: Multi-hop reasoning across the graph"""
    
    from hybrid_kg_cypher_generator import MultiHopCypherEngine
    from hybrid_kg_cypher_generator import CypherGenerator
    from neo4j import GraphDatabase
    
    logger.info("=== Multi-hop Reasoning Example ===")
    
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "your_password")
    )
    
    cypher_gen = CypherGenerator()
    multi_hop_engine = MultiHopCypherEngine(cypher_gen, driver)
    
    # Generate multi-hop queries with different strategies
    strategies = ['shortest_path', 'breadth_first', 'depth_first']
    
    for strategy in strategies:
        query = multi_hop_engine.generate_multi_hop_query(
            start_entity="Patient",
            target_entity="Condition",
            hops=2,
            strategy=strategy,
        )
        
        print(f"\nStrategy: {strategy}")
        print(f"Query:\n{query.cypher_query}")
        print(f"Confidence: {query.confidence:.1%}")
    
    driver.close()


def example_query_reasoning_explanation():
    """Example: Get detailed reasoning explanation for queries"""
    
    from hybrid_kg_rag_pipeline import GraphRAGFactory
    
    logger.info("=== Query Reasoning Explanation Example ===")
    
    pipeline = GraphRAGFactory.create_pipeline(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
    )
    
    query = "What are the risk factors for patients with diabetes?"
    result = pipeline.process_query(query)
    
    # Get detailed explanation
    explanation = pipeline.explain_query_reasoning(result)
    print(explanation)
    
    pipeline.close()


def example_schema_exploration():
    """Example: Explore the graph schema"""
    
    from hybrid_kg_vectorizer import KnowledgeGraphSchema
    
    logger.info("=== Schema Exploration Example ===")
    
    schema = KnowledgeGraphSchema(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="your_password",
    )
    
    # Get node labels
    labels = schema.get_node_labels()
    print(f"\nNode Labels in Graph: {', '.join(labels)}")
    
    # Get relationships
    relationships = schema.get_relationships()
    print(f"\nRelationship Types: {', '.join(relationships[:10])}")
    
    # Get full schema
    full_schema = schema.get_schema()
    print(f"\nSchema Information:")
    for label, info in list(full_schema.items())[:5]:
        print(f"\n  {label}:")
        print(f"    Properties: {', '.join(list(info['properties'])[:5])}")
        print(f"    Sample Relationships: {', '.join(info['sample_relationships'])}")
    
    schema.close()


def example_custom_configuration():
    """Example: Create pipeline with custom configuration"""
    
    from hybrid_kg_rag_pipeline import HybridGraphRAG
    from hybrid_kg_vectorizer import NodeVectorizer, KnowledgeGraphSchema
    from hybrid_kg_retriever import HybridKGRetriever
    from hybrid_kg_cypher_generator import CypherGenerator
    from neo4j import GraphDatabase
    
    logger.info("=== Custom Configuration Example ===")
    
    # Custom configuration
    config = {
        'neo4j_uri': "bolt://localhost:7687",
        'neo4j_user': "neo4j",
        'neo4j_password': "your_password",
        'embedding_model': "sentence-transformers/paraphrase-MiniLM-L6-v2",
        'llm_provider': "openai",
        'llm_model': "gpt-4-turbo",
        'use_cache': True,
    }
    
    # Initialize components manually
    driver = GraphDatabase.driver(
        config['neo4j_uri'],
        auth=(config['neo4j_user'], config['neo4j_password'])
    )
    
    vectorizer = NodeVectorizer(
        neo4j_uri=config['neo4j_uri'],
        neo4j_user=config['neo4j_user'],
        neo4j_password=config['neo4j_password'],
        embedding_model=config['embedding_model'],
    )
    
    schema = KnowledgeGraphSchema(
        config['neo4j_uri'],
        config['neo4j_user'],
        config['neo4j_password'],
    )
    
    embeddings = vectorizer.load_embeddings('node_embeddings.json')
    
    retriever = HybridKGRetriever(vectorizer, schema, embeddings)
    
    cypher_generator = CypherGenerator(
        llm_provider=config['llm_provider'],
        model_name=config['llm_model'],
        kg_schema=schema,
    )
    
    pipeline = HybridGraphRAG(
        vectorizer=vectorizer,
        retriever=retriever,
        cypher_generator=cypher_generator,
        driver=driver,
        cache_enabled=config['use_cache'],
    )
    
    print(f"Custom pipeline created with config:")
    for key, value in config.items():
        if 'password' not in key:
            print(f"  {key}: {value}")
    
    # Use pipeline...
    query = "Show me all test results for patients with high cardiovascular risk"
    result = pipeline.process_query(query, execute_best=True)
    
    print(f"\nProcessed query: {result['user_query']}")
    print(f"Execution time: {result['elapsed_time']:.2f}s")
    
    pipeline.close()


if __name__ == "__main__":
    """Run examples"""
    
    print("\n" + "="*80)
    print("HYBRID KNOWLEDGE GRAPH RAG SYSTEM - EXAMPLES")
    print("="*80 + "\n")
    
    # Uncomment to run specific examples
    try:
        # example_basic_usage()
        # example_batch_processing()
        # example_semantic_search()
        # example_multi_hop_reasoning()
        # example_query_reasoning_explanation()
        # example_schema_exploration()
        # example_custom_configuration()
        
        print("""
Available examples:
1. example_basic_usage() - Basic query processing
2. example_batch_processing() - Process multiple queries
3. example_semantic_search() - Semantic search across nodes
4. example_multi_hop_reasoning() - Multi-hop graph traversal
5. example_query_reasoning_explanation() - Get detailed explanations
6. example_schema_exploration() - Explore graph schema
7. example_custom_configuration() - Custom setup

To run an example, uncomment it in the __main__ section.
        """)
    
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
