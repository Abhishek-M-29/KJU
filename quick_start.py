"""
Quick Start Guide for Hybrid KG-RAG System

Run this script to set up and test the hybrid knowledge graph RAG system.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required packages are installed"""
    
    required_packages = {
        'neo4j': 'neo4j',
        'sentence_transformers': 'sentence-transformers',
        'numpy': 'numpy',
        'requests': 'requests',
    }
    
    logger.info("Checking dependencies...")
    
    missing_required = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            logger.info(f"✓ {package_name} installed")
        except ImportError:
            missing_required.append(package_name)
            logger.warning(f"✗ {package_name} NOT installed")
    
    if missing_required:
        logger.error(f"Missing required packages: {', '.join(missing_required)}")
        logger.error(f"Install with: pip install {' '.join(missing_required)}")
        return False
    
    return True


def check_neo4j_connection():
    """Check if Neo4j is accessible"""
    
    logger.info("Checking Neo4j connection...")
    
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        
        if not password:
            logger.warning("NEO4J_PASSWORD not set. Using empty password.")
            password = ""
        
        driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=5)
        driver.verify_connectivity()
        
        logger.info(f"✓ Connected to Neo4j at {uri}")
        driver.close()
        return True
    
    except Exception as e:
        logger.error(f"✗ Could not connect to Neo4j: {e}")
        logger.error("Make sure Neo4j is running. You can start it with:")
        logger.error("  docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
        return False


def check_embeddings_file():
    """Check if embeddings file exists"""
    
    logger.info("Checking embeddings cache...")
    
    embeddings_path = Path("node_embeddings.json")
    
    if embeddings_path.exists():
        logger.info(f"✓ Embeddings file exists: {embeddings_path}")
        return True
    else:
        logger.warning(f"⚠ Embeddings file not found: {embeddings_path}")
        logger.warning("  Embeddings will be generated on first run (may take time)")
        return False


def verify_api_keys():
    """Verify Ollama connection"""
    
    logger.info("Checking Ollama connection...")
    
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    try:
        import requests
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("✓ Ollama connection successful")
            models = response.json().get('models', [])
            if models:
                logger.info(f"✓ Available Ollama models: {[m['name'].split(':')[0] for m in models]}")
            else:
                logger.warning("⚠ No Ollama models found. Pull a model with: ollama pull mistral")
            return True
        else:
            logger.error(f"✗ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Could not connect to Ollama at {ollama_url}")
        logger.error(f"  Error: {e}")
        logger.info("  Start Ollama with: ollama serve")
        logger.info("  Pull a model with: ollama pull mistral")
        return False


def test_basic_pipeline():
    """Test basic pipeline functionality"""
    
    logger.info("\nTesting basic pipeline...")
    
    try:
        from hybrid_kg_vectorizer import NodeVectorizer, KnowledgeGraphSchema
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        
        # Test vectorizer
        logger.info("Initializing vectorizer...")
        vectorizer = NodeVectorizer(
            neo4j_uri=uri,
            neo4j_user=user,
            neo4j_password=password,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Test schema
        logger.info("Initializing schema...")
        schema = KnowledgeGraphSchema(uri, user, password)
        labels = schema.get_node_labels()
        logger.info(f"✓ Found {len(labels)} node labels: {', '.join(labels[:5])}...")
        
        vectorizer.close()
        schema.close()
        
        logger.info("✓ Basic pipeline test passed")
        return True
    
    except Exception as e:
        logger.error(f"✗ Basic pipeline test failed: {e}")
        return False


def generate_embeddings():
    """Generate embeddings for the first time"""
    
    logger.info("\nGenerating embeddings...")
    
    try:
        from hybrid_kg_vectorizer import NodeVectorizer
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        
        vectorizer = NodeVectorizer(
            neo4j_uri=uri,
            neo4j_user=user,
            neo4j_password=password,
        )
        
        logger.info("This may take a few minutes...")
        embeddings = vectorizer.vectorize_all_nodes(batch_size=50)
        
        vectorizer.save_embeddings(embeddings, 'node_embeddings.json')
        logger.info(f"✓ Generated and saved {len(embeddings)} embeddings")
        
        vectorizer.close()
        return True
    
    except Exception as e:
        logger.error(f"✗ Failed to generate embeddings: {e}")
        return False


def run_example_query():
    """Run an example query"""
    
    logger.info("\nRunning example query...")
    
    try:
        from hybrid_kg_rag_pipeline import GraphRAGFactory
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        
        logger.info("Creating pipeline with Ollama...")
        pipeline = GraphRAGFactory.create_pipeline(
            neo4j_uri=uri,
            neo4j_user=user,
            neo4j_password=password,
            ollama_url=ollama_url,
            ollama_model=ollama_model,
        )
        
        query = "Show me all conditions for patients"
        logger.info(f"Processing query: '{query}'")
        
        result = pipeline.process_query(query, execute_best=False)
        
        logger.info(f"✓ Query processed successfully")
        logger.info(f"  - Found {result['retrieved_context']['node_count']} relevant nodes")
        logger.info(f"  - Generated {len(result['cypher_suggestions'])} query suggestions")
        
        if result['cypher_suggestions']:
            best = result['cypher_suggestions'][0]
            logger.info(f"  - Best query confidence: {best['confidence']:.1%}")
        
        stats = pipeline.get_statistics()
        logger.info(f"  - Execution time: {result['elapsed_time']:.2f}s")
        
        pipeline.close()
        return True
    
    except Exception as e:
        logger.error(f"✗ Example query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks and setup"""
    
    print("\n" + "="*80)
    print("HYBRID KG-RAG SYSTEM - QUICK START")
    print("="*80 + "\n")
    
    checks = {
        "Dependencies": check_dependencies,
        "Neo4j Connection": check_neo4j_connection,
        "Embeddings Cache": check_embeddings_file,
        "API Keys": verify_api_keys,
        "Basic Pipeline": test_basic_pipeline,
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            logger.error(f"Error in {check_name}: {e}")
            results[check_name] = False
    
    print("\n" + "="*80)
    print("SETUP SUMMARY")
    print("="*80)
    
    for check_name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    # Suggest next steps
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80 + "\n")
    
    if not results["Embeddings Cache"]:
        print("1. Generate embeddings:")
        print("   python quick_start.py --generate-embeddings")
    
    if results["Dependencies"] and results["Neo4j Connection"]:
        print("2. Run example query:")
        print("   python quick_start.py --run-example")
    
    print("3. Explore examples:")
    print("   python example_usage.py")
    
    print("4. Read documentation:")
    print("   See HYBRID_KG_RAG_README.md\n")
    
    return all(results.values())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate-embeddings":
            logger.info("Generating embeddings...")
            success = generate_embeddings()
            sys.exit(0 if success else 1)
        
        elif sys.argv[1] == "--run-example":
            logger.info("Running example query...")
            success = run_example_query()
            sys.exit(0 if success else 1)
    
    success = main()
    sys.exit(0 if success else 1)
