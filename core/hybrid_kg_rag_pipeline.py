"""
Unified Hybrid Knowledge Graph RAG Pipeline
Combines vectorization, retrieval, and Cypher generation for end-to-end querying.
"""

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import asdict
import time

logger = logging.getLogger(__name__)


class HybridGraphRAG:
    """Unified pipeline combining hybrid KG retrieval and Cypher generation"""

    def __init__(
        self,
        vectorizer,
        retriever,
        cypher_generator,
        driver,
        cache_enabled: bool = True,
    ):
        """
        Initialize the GraphRAG pipeline
        
        Args:
            vectorizer: NodeVectorizer instance
            retriever: HybridKGRetriever instance
            cypher_generator: CypherGenerator instance
            driver: Neo4j driver
            cache_enabled: Enable query caching
        """
        self.vectorizer = vectorizer
        self.retriever = retriever
        self.cypher_generator = cypher_generator
        self.driver = driver
        self.cache_enabled = cache_enabled
        self.query_cache = {}
        self.execution_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'execution_times': [],
        }

    def process_query(
        self,
        user_query: str,
        top_k: int = 5,
        expand_hops: int = 1,
        num_cypher_suggestions: int = 3,
        execute_best: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end
        
        Args:
            user_query: Natural language query
            top_k: Top-k semantic matches
            expand_hops: Graph expansion hops
            num_cypher_suggestions: Number of Cypher suggestions
            execute_best: Execute the best query and return results
            
        Returns:
            Dictionary with retrieved context, generated Cypher, and results
        """
        
        start_time = time.time()
        
        # Check cache
        if self.cache_enabled and user_query in self.query_cache:
            logger.info(f"Cache hit for query: {user_query}")
            self.execution_stats['cache_hits'] += 1
            return self.query_cache[user_query]
        
        self.execution_stats['total_queries'] += 1
        
        # Step 1: Retrieve context
        logger.info(f"Step 1: Retrieving context for query: {user_query}")
        retrieved_context = self.retriever.retrieve_context(
            query=user_query,
            top_k=top_k,
            expand_hops=expand_hops,
        )
        
        # Step 2: Augment context
        logger.info("Step 2: Augmenting retrieved context")
        from hybrid_kg_retriever import ContextAugmenter
        augmenter = ContextAugmenter(self.driver)
        retrieved_context = augmenter.add_path_context(retrieved_context)
        retrieved_context = augmenter.add_frequency_context(retrieved_context)
        
        # Step 3: Generate Cypher queries
        logger.info(f"Step 3: Generating {num_cypher_suggestions} Cypher suggestions")
        cypher_suggestions = self.cypher_generator.generate_from_context(
            retrieved_context=retrieved_context,
            user_query=user_query,
            num_suggestions=num_cypher_suggestions,
        )
        
        # Step 4: Validate and optimize
        logger.info("Step 4: Validating and optimizing queries")
        validated_queries = []
        for suggestion in cypher_suggestions:
            if self.cypher_generator.is_query_too_specific(suggestion.cypher_query, user_query):
                logger.info("Skipping overly specific query not mentioned by user")
                validated_queries.append((suggestion, False, "Hardcoded value not in user query"))
                continue
            is_valid, message = self.cypher_generator.validate_cypher(
                suggestion.cypher_query, self.driver
            )
            
            if is_valid:
                optimized = self.cypher_generator.optimize_cypher(suggestion.cypher_query)
                suggestion.cypher_query = optimized
                validated_queries.append((suggestion, is_valid, message))
            else:
                validated_queries.append((suggestion, is_valid, message))

        # Fallback: generate deterministic queries if none are valid
        if not [q for q, is_valid, _ in validated_queries if is_valid]:
            logger.info("No valid LLM queries. Generating fallback query.")
            fallback_queries = self.cypher_generator.generate_fallback_queries(
                retrieved_context=retrieved_context,
                user_query=user_query,
            )
            for suggestion in fallback_queries:
                is_valid, message = self.cypher_generator.validate_cypher(
                    suggestion.cypher_query, self.driver
                )
                if is_valid:
                    optimized = self.cypher_generator.optimize_cypher(suggestion.cypher_query)
                    suggestion.cypher_query = optimized
                validated_queries.append((suggestion, is_valid, message))
        
        # Step 5: Execute best query if requested
        execution_result = None
        best_query = None
        if execute_best and validated_queries:
            # Find best valid query
            valid_queries = [(q, m) for q, is_valid, m in validated_queries if is_valid]
            if valid_queries:
                best_query = max(valid_queries, key=lambda x: x[0].confidence)[0]
                logger.info(f"Executing best query (confidence: {best_query.confidence})")
                execution_result = self._execute_cypher(best_query.cypher_query)

        # If execution returned no records, try fallback queries
        if execute_best and (execution_result is None or execution_result.get('record_count', 0) == 0):
            fallback_queries = self.cypher_generator.generate_fallback_queries(
                retrieved_context=retrieved_context,
                user_query=user_query,
            )
            for fb in fallback_queries:
                is_valid, message = self.cypher_generator.validate_cypher(fb.cypher_query, self.driver)
                if not is_valid:
                    continue
                logger.info("Executing fallback query")
                execution_result = self._execute_cypher(fb.cypher_query)
                best_query = fb
                validated_queries.append((fb, True, message))
                if execution_result.get('record_count', 0) > 0:
                    break
        
        # Step 6: Prepare response
        elapsed_time = time.time() - start_time
        self.execution_stats['execution_times'].append(elapsed_time)
        
        response = {
            'user_query': user_query,
            'elapsed_time': elapsed_time,
            'retrieved_context': {
                'node_count': len(retrieved_context.retrieved_nodes),
                'node_labels': retrieved_context.node_labels,
                'relationships': retrieved_context.relationships,
                'suggested_patterns': retrieved_context.suggested_patterns,
            },
            'cypher_suggestions': [
                {
                    'query': q.cypher_query,
                    'explanation': q.explanation,
                    'reasoning': q.reasoning,
                    'confidence': q.confidence,
                    'multi_hop': q.multi_hop,
                    'optimizations': q.optimizations,
                    'is_valid': is_valid,
                    'validation_message': msg,
                }
                for q, is_valid, msg in validated_queries
            ],
            'best_query': {
                'query': best_query.cypher_query if best_query else None,
                'confidence': best_query.confidence if best_query else None,
                'explanation': best_query.explanation if best_query else None,
            } if best_query else None,
            'execution_result': execution_result,
        }
        
        # Cache result
        if self.cache_enabled:
            self.query_cache[user_query] = response
        
        return response

    def _execute_cypher(self, cypher_query: str) -> Dict[str, Any]:
        """Execute Cypher query and format results"""
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query)
                records = result.data()
                
                return {
                    'success': True,
                    'record_count': len(records),
                    'records': records[:20],  # Return first 20
                    'execution_time': result.consume().result_available_after,
                }
        
        except Exception as e:
            logger.error(f"Error executing Cypher: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_count': 0,
                'records': [],
            }

    def batch_process_queries(
        self,
        queries: List[str],
        batch_size: int = 5,
    ) -> List[Dict[str, Any]]:
        """Process multiple queries in batches"""
        
        results = []
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} queries)")
            
            for query in batch:
                result = self.process_query(query)
                results.append(result)
        
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        
        avg_time = (
            sum(self.execution_stats['execution_times'])
            / len(self.execution_stats['execution_times'])
            if self.execution_stats['execution_times']
            else 0
        )
        
        return {
            'total_queries_processed': self.execution_stats['total_queries'],
            'cache_hits': self.execution_stats['cache_hits'],
            'cache_hit_rate': (
                self.execution_stats['cache_hits'] / self.execution_stats['total_queries']
                if self.execution_stats['total_queries'] > 0
                else 0
            ),
            'average_execution_time': avg_time,
            'min_execution_time': min(self.execution_stats['execution_times']) if self.execution_stats['execution_times'] else 0,
            'max_execution_time': max(self.execution_stats['execution_times']) if self.execution_stats['execution_times'] else 0,
            'cache_size': len(self.query_cache),
        }

    def explain_query_reasoning(self, query_result: Dict[str, Any]) -> str:
        """Generate human-readable explanation of query reasoning"""
        
        explanation = f"""
## Query Analysis: {query_result['user_query']}

### Processing Time: {query_result['elapsed_time']:.2f}s

### Context Retrieved:
- Relevant Nodes: {query_result['retrieved_context']['node_count']}
- Node Types: {', '.join(query_result['retrieved_context']['node_labels'])}
- Relationships: {', '.join(query_result['retrieved_context']['relationships'])}

### Generated Queries:
"""
        
        for i, suggestion in enumerate(query_result['cypher_suggestions'], 1):
            explanation += f"""
#### Suggestion {i}:
- Confidence: {suggestion['confidence']:.2%}
- Multi-hop: {suggestion['multi_hop']}
- Valid: {suggestion['is_valid']}
- Reasoning: {suggestion['reasoning']}
- Optimizations: {', '.join(suggestion['optimizations'])}

Query:
```cypher
{suggestion['query']}
```
"""
        
        if query_result['execution_result'] and query_result['execution_result']['success']:
            explanation += f"""

### Execution Results:
- Records Found: {query_result['execution_result']['record_count']}
- Execution Time: {query_result['execution_result']['execution_time']}ms
"""
        
        return explanation

    def export_results(self, query_results: List[Dict], filepath: str) -> None:
        """Export query results to JSON file"""
        
        export_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': self.get_statistics(),
            'queries': query_results,
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Exported results to {filepath}")

    def close(self):
        """Close all connections"""
        if hasattr(self.vectorizer, 'close'):
            self.vectorizer.close()
        if hasattr(self.cypher_generator, 'driver'):
            self.cypher_generator.driver.close()
        self.driver.close()


class GraphRAGFactory:
    """Factory for creating fully configured GraphRAG instances"""

    @staticmethod
    def create_pipeline(
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "qwen2.5:7b-instruct",
        use_cache: bool = True,
    ) -> HybridGraphRAG:
        """
        Create a fully configured GraphRAG pipeline with Ollama
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            embedding_model: Embedding model name
            ollama_url: Ollama server URL
            ollama_model: Ollama model name (e.g., 'mistral', 'neural-chat')
            use_cache: Enable query caching
            
        Returns:
            Configured HybridGraphRAG instance
        """
        
        logger.info("Creating HybridGraphRAG pipeline with Ollama...")
        
        # Initialize components
        from hybrid_kg_vectorizer import NodeVectorizer, KnowledgeGraphSchema
        from hybrid_kg_retriever import HybridKGRetriever
        from hybrid_kg_cypher_generator import CypherGenerator
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Create vectorizer
        logger.info("Initializing vectorizer...")
        vectorizer = NodeVectorizer(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            embedding_model=embedding_model,
        )
        
        # Create schema
        logger.info("Initializing schema...")
        kg_schema = KnowledgeGraphSchema(neo4j_uri, neo4j_user, neo4j_password)
        
        # Load or generate embeddings
        try:
            logger.info("Loading embeddings...")
            embeddings = vectorizer.load_embeddings('node_embeddings.json')
        except FileNotFoundError:
            logger.info("Generating embeddings...")
            embeddings = vectorizer.vectorize_all_nodes()
            vectorizer.save_embeddings(embeddings, 'node_embeddings.json')
        
        # Create retriever
        logger.info("Initializing retriever...")
        retriever = HybridKGRetriever(vectorizer, kg_schema, embeddings)
        
        # Create Cypher generator with Ollama
        logger.info(f"Initializing Cypher generator with Ollama ({ollama_model})...")
        cypher_generator = CypherGenerator(
            llm_provider="ollama",
            model_name=ollama_model,
            ollama_url=ollama_url,
            kg_schema=kg_schema,
        )
        
        # Create pipeline
        pipeline = HybridGraphRAG(
            vectorizer=vectorizer,
            retriever=retriever,
            cypher_generator=cypher_generator,
            driver=driver,
            cache_enabled=use_cache,
        )
        
        logger.info("HybridGraphRAG pipeline created successfully")
        return pipeline
