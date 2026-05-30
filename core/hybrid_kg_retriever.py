"""
Hybrid Knowledge Graph Retriever
Combines semantic search with graph structure for context-aware retrieval.
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
import json
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


@dataclass
class RetrievedContext:
    """Represents retrieved context for Cypher generation"""
    query: str
    retrieved_nodes: List[Dict]  # Nodes matching semantic query
    node_labels: List[str]  # Relevant node labels
    relationships: List[str]  # Relevant relationship types
    suggested_patterns: List[str]  # Suggested cypher patterns
    schema_info: Dict  # Relevant schema information
    connecting_paths: Optional[List[Dict]] = None  # Connecting paths between nodes
    relationship_frequencies: Optional[Dict] = None  # Frequency info


class HybridKGRetriever:
    """Combines vector similarity and graph structure for intelligent retrieval"""

    def __init__(
        self,
        node_vectorizer,
        kg_schema,
        embeddings: List,
    ):
        """
        Initialize the hybrid retriever
        
        Args:
            node_vectorizer: NodeVectorizer instance
            kg_schema: KnowledgeGraphSchema instance
            embeddings: Pre-loaded node embeddings
        """
        self.vectorizer = node_vectorizer
        self.schema = kg_schema
        self.embeddings = embeddings
        self.driver = node_vectorizer.driver

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        expand_hops: int = 1,
    ) -> RetrievedContext:
        """
        Retrieve context combining semantic and structural information
        
        Args:
            query: Natural language query
            top_k: Number of top semantic matches
            expand_hops: Number of hops to expand from matched nodes
            
        Returns:
            RetrievedContext with all relevant information
        """
        
        # Step 1: Semantic search
        semantic_matches = self.vectorizer.semantic_search(self.embeddings, query, top_k=top_k)
        logger.info(f"Found {len(semantic_matches)} semantic matches for query: {query}")
        
        retrieved_nodes = []
        matched_node_ids = set()
        matched_labels = set()
        
        for embedding, score in semantic_matches:
            retrieved_nodes.append({
                'node_id': embedding.node_id,
                'label': embedding.node_label,
                'properties': embedding.node_properties,
                'text': embedding.text_content,
                'similarity_score': float(score),
            })
            matched_node_ids.add(embedding.node_id)
            matched_labels.add(embedding.node_label)
        
        # Step 2: Expand with graph neighbors
        neighbor_context = self._expand_with_neighbors(matched_node_ids, expand_hops)
        retrieved_nodes.extend(neighbor_context['nodes'])
        
        # Step 3: Extract relevant relationships
        all_labels = matched_labels.union(set(neighbor_context['labels']))
        relationships = self._get_relevant_relationships(all_labels)
        
        # Step 4: Suggest Cypher patterns
        suggested_patterns = self._suggest_cypher_patterns(
            query, all_labels, relationships, neighbor_context
        )
        
        # Step 5: Get schema info
        schema_info = self._get_schema_info(all_labels, relationships)
        
        return RetrievedContext(
            query=query,
            retrieved_nodes=retrieved_nodes,
            node_labels=list(all_labels),
            relationships=relationships,
            suggested_patterns=suggested_patterns,
            schema_info=schema_info,
        )

    def _expand_with_neighbors(
        self,
        node_ids: Set[str],
        hops: int,
    ) -> Dict[str, Any]:
        """Expand semantic matches with graph neighbors"""
        
        neighbor_nodes = []
        neighbor_labels = set()
        
        with self.driver.session() as session:
            for node_id in node_ids:
                for hop in range(1, hops + 1):
                    # Build match pattern
                    rel_pattern = "-".join(["[r]" for _ in range(hop)])
                    match_query = f"""
                        MATCH (start)-{rel_pattern}-(neighbor)
                        WHERE id(start) = $node_id
                        RETURN DISTINCT neighbor, labels(neighbor) as labels, 
                               [r IN relationships($node_id, neighbor) | type(r)] as rel_types
                        LIMIT 10
                    """
                    
                    try:
                        result = session.run(match_query, node_id=int(node_id))
                        for record in result:
                            neighbor = record['neighbor']
                            labels = record['labels']
                            neighbor_labels.update(labels)
                            neighbor_nodes.append({
                                'label': labels[0] if labels else 'Unknown',
                                'properties': dict(neighbor),
                                'hop_distance': hop,
                            })
                    except Exception as e:
                        logger.debug(f"Could not expand node {node_id}: {e}")
        
        return {
            'nodes': neighbor_nodes,
            'labels': neighbor_labels,
        }

    def _get_relevant_relationships(self, node_labels: Set[str]) -> List[str]:
        """Get relationships that connect the relevant node labels"""
        
        relationships = set()
        with self.driver.session() as session:
            for label in node_labels:
                # Find relationships from this label
                result = session.run(f"""
                    MATCH (n:{label})-[r]->()
                    RETURN DISTINCT type(r) as rel_type
                """)
                relationships.update([r['rel_type'] for r in result])
                
                # Find relationships to this label
                result = session.run(f"""
                    MATCH ()-[r]->(n:{label})
                    RETURN DISTINCT type(r) as rel_type
                """)
                relationships.update([r['rel_type'] for r in result])
        
        return list(relationships)

    def _suggest_cypher_patterns(
        self,
        query: str,
        labels: Set[str],
        relationships: List[str],
        neighbor_context: Dict,
    ) -> List[str]:
        """Suggest Cypher query patterns based on context"""
        
        patterns = []
        labels_list = list(labels)
        
        # Pattern 1: Direct relationships between matched labels
        for i, label1 in enumerate(labels_list):
            for label2 in labels_list[i+1:]:
                for rel in relationships:
                    patterns.append(f"(:{label1})-[:{rel}]->(:{label2})")
        
        # Pattern 2: Multi-hop patterns
        if len(labels_list) >= 2:
            patterns.append(f"(:{labels_list[0]})-[*1..2]->(:{labels_list[-1]})")
        
        # Pattern 3: Hub-and-spoke (patient-centric)
        if "Patient" in labels:
            for label in labels_list:
                if label != "Patient":
                    patterns.append(f"(:Patient)-[]->(:{label})")
        
        return patterns[:10]  # Limit suggestions

    def _get_schema_info(self, labels: Set[str], relationships: List[str]) -> Dict:
        """Get schema information for the relevant labels and relationships"""
        
        schema_info = {
            'node_schemas': {},
            'relationship_descriptions': {},
        }
        
        full_schema = self.schema.get_schema()
        
        for label in labels:
            if label in full_schema:
                schema_info['node_schemas'][label] = {
                    'properties': list(full_schema[label]['properties']),
                    'sample_relationships': full_schema[label]['sample_relationships'],
                }
        
        for rel in relationships:
            pattern = self.schema.get_relationship_pattern(rel)
            schema_info['relationship_descriptions'][rel] = pattern
        
        return schema_info

    def filter_by_query_intent(
        self,
        context: RetrievedContext,
        intent: str,
    ) -> RetrievedContext:
        """Filter context based on detected query intent"""
        
        # Detect intent
        if any(word in intent.lower() for word in ['risk', 'predict', 'severity', 'danger']):
            # Filter to include only condition and risk-related nodes
            context.node_labels = [
                l for l in context.node_labels
                if l in ['Condition', 'Symptom', 'Patient', 'MedicalHistory', 'Risk']
            ]
        
        elif any(word in intent.lower() for word in ['medication', 'drug', 'treatment', 'prescri']):
            context.node_labels = [
                l for l in context.node_labels
                if l in ['Medication', 'Treatment', 'Condition', 'Patient']
            ]
        
        elif any(word in intent.lower() for word in ['appointment', 'visit', 'encounter', 'schedule']):
            context.node_labels = [
                l for l in context.node_labels
                if l in ['Appointment', 'Encounter', 'Patient', 'Provider']
            ]
        
        elif any(word in intent.lower() for word in ['lab', 'result', 'test', 'finding']):
            context.node_labels = [
                l for l in context.node_labels
                if l in ['LabResult', 'LabReport', 'TestResult', 'LabFinding', 'Patient']
            ]
        
        return context


class ContextAugmenter:
    """Augments retrieved context with additional graph insights"""

    def __init__(self, driver):
        self.driver = driver

    def add_path_context(self, context: RetrievedContext) -> RetrievedContext:
        """Find connecting paths between retrieved nodes"""
        
        with self.driver.session() as session:
            if len(context.retrieved_nodes) >= 2:
                # Find shortest paths between first and last retrieved nodes
                node1_id = context.retrieved_nodes[0]['node_id']
                node2_id = context.retrieved_nodes[-1]['node_id']
                
                result = session.run("""
                    MATCH path = shortestPath((n1)-[*1..3]-(n2))
                    WHERE id(n1) = $n1 AND id(n2) = $n2
                    RETURN [r IN relationships(path) | type(r)] as path_types,
                           [nodes IN nodes(path) | labels(nodes)[0]] as node_path
                    LIMIT 5
                """, n1=int(node1_id), n2=int(node2_id))
                
                paths = []
                for record in result:
                    paths.append({
                        'node_path': record['node_path'],
                        'relationship_path': record['path_types'],
                    })
                
                if context.connecting_paths is None:
                    context.connecting_paths = []
                context.connecting_paths.extend(paths)
        
        return context

    def add_frequency_context(self, context: RetrievedContext) -> RetrievedContext:
        """Add frequency information for common patterns"""
        
        with self.driver.session() as session:
            for rel_type in context.relationships:
                result = session.run(f"""
                    MATCH ()-[r:{rel_type}]->()
                    RETURN count(r) as count
                """)
                
                record = result.single()
                if record:
                    if context.relationship_frequencies is None:
                        context.relationship_frequencies = {}
                    context.relationship_frequencies[rel_type] = record['count']
        
        return context
