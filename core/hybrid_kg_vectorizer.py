"""
Hybrid Knowledge Graph Vector Embedding Module
Vectorizes Neo4j nodes for semantic search and retrieval.
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
from datetime import datetime
from neo4j import GraphDatabase, Session
import logging

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class NodeEmbedding:
    """Represents a vectorized node in the KG"""
    node_id: str
    node_label: str
    node_properties: Dict[str, Any]
    embedding: List[float]
    embedding_model: str
    text_content: str
    embedding_timestamp: str
    hash_value: str


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):  # Handle neo4j DateTime
            return obj.isoformat()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        try:
            return super().default(obj)
        except TypeError:
            # For unknown types, convert to string
            return str(obj)


class NodeVectorizer:
    """Vectorizes healthcare knowledge graph nodes using embeddings"""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_openai: bool = False,
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize the node vectorizer
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            embedding_model: Hugging Face model or OpenAI model
            use_openai: Whether to use OpenAI embeddings
            openai_api_key: OpenAI API key if using OpenAI
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.embedding_model_name = embedding_model
        self.use_openai = use_openai
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Initialize embedding model
        if use_openai:
            if not HAS_OPENAI:
                raise ImportError("openai package not installed. Install with: pip install openai")
            openai.api_key = openai_api_key
            self.embedding_model = None
            self.embedding_dim = 1536  # OpenAI embedding dimension
        else:
            if not HAS_SENTENCE_TRANSFORMERS:
                raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        logger.info(f"Initialized NodeVectorizer with model: {embedding_model}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")

    def _extract_node_text(self, node_label: str, node_properties: Dict) -> str:
        """Extract meaningful text from node properties for vectorization"""
        text_parts = []
        
        # Priority properties by node type
        priority_props = {
            "Patient": ["full_name", "name"],
            "Condition": ["condition_name", "name", "description"],
            "Medication": ["medication_name", "name", "dosage"],
            "LabResult": ["test_name", "name", "result_value"],
            "Appointment": ["appointment_type", "name", "description"],
            "Symptom": ["symptom_name", "name", "severity"],
            "MedicalHistory": ["condition_name", "name", "description"],
            "LabReport": ["report_type", "name", "description"],
            "Encounter": ["encounter_type", "name", "description"],
        }
        
        # Add node label
        text_parts.append(f"[{node_label}]")
        
        # Add priority properties (with DateTime handling)
        for prop in priority_props.get(node_label, []):
            if prop in node_properties and node_properties[prop]:
                val = node_properties[prop]
                # Convert DateTime to string
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                text_parts.append(str(val))
        
        # Add other meaningful properties (skip DateTime fields)
        skip_props = {"patient_id", "node_type", "entity_type", "created_at", "last_updated", "graph_center"}
        for key, value in node_properties.items():
            if key not in skip_props and key not in priority_props.get(node_label, []):
                # Convert DateTime to string, skip other complex types
                if isinstance(value, (str, int, float, bool)):
                    text_parts.append(f"{key}: {value}")
                elif hasattr(value, 'isoformat'):  # DateTime object
                    text_parts.append(f"{key}: {value.isoformat()}")
        
        return " ".join(text_parts)

    def _clean_properties(self, props: Dict) -> Dict:
        """Clean node properties for JSON serialization"""
        cleaned = {}
        for key, value in props.items():
            try:
                # Try JSON serializing to check if it's safe
                json.dumps(value, cls=DateTimeEncoder)
                cleaned[key] = value
            except (TypeError, ValueError):
                # Convert unsupported types to string
                if hasattr(value, 'isoformat'):
                    cleaned[key] = value.isoformat()
                else:
                    cleaned[key] = str(value)
        return cleaned

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        if self.use_openai:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response['data'][0]['embedding'])
        else:
            return self.embedding_model.encode(text, convert_to_numpy=True)

    def _compute_hash(self, node_id: str, text_content: str) -> str:
        """Compute hash for change detection"""
        content = f"{node_id}:{text_content}"
        return hashlib.sha256(content.encode()).hexdigest()

    def vectorize_node(self, node_id: str, node_label: str, node_properties: Dict) -> NodeEmbedding:
        """Vectorize a single node"""
        text_content = self._extract_node_text(node_label, node_properties)
        embedding = self._get_embedding(text_content)
        hash_value = self._compute_hash(node_id, text_content)
        
        # Clean properties for JSON serialization
        cleaned_props = self._clean_properties(node_properties)
        
        return NodeEmbedding(
            node_id=node_id,
            node_label=node_label,
            node_properties=cleaned_props,
            embedding=embedding.tolist(),
            embedding_model=self.embedding_model_name,
            text_content=text_content,
            embedding_timestamp=datetime.utcnow().isoformat(),
            hash_value=hash_value,
        )

    def vectorize_all_nodes(self, batch_size: int = 100) -> List[NodeEmbedding]:
        """
        Vectorize all nodes in the Neo4j database
        
        Args:
            batch_size: Number of nodes to process at once
            
        Returns:
            List of NodeEmbedding objects
        """
        embeddings = []
        
        with self.driver.session() as session:
            # Get all nodes
            result = session.run("""
                MATCH (n)
                RETURN id(n) as node_id, labels(n) as labels, properties(n) as props
                LIMIT 10000
            """)
            
            nodes = result.data()
            logger.info(f"Found {len(nodes)} nodes to vectorize")
            
            for i, node in enumerate(nodes):
                if i % batch_size == 0:
                    logger.info(f"Processing node {i}/{len(nodes)}")
                
                node_id = str(node['node_id'])
                node_label = node['labels'][0] if node['labels'] else "Unknown"
                node_properties = node['props']
                
                embedding = self.vectorize_node(node_id, node_label, node_properties)
                embeddings.append(embedding)
        
        logger.info(f"Successfully vectorized {len(embeddings)} nodes")
        return embeddings

    def save_embeddings(self, embeddings: List[NodeEmbedding], filepath: str) -> None:
        """Save embeddings to JSON file with custom encoder"""
        data = [asdict(e) for e in embeddings]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, cls=DateTimeEncoder)
        logger.info(f"Saved {len(embeddings)} embeddings to {filepath}")

    def load_embeddings(self, filepath: str) -> List[NodeEmbedding]:
        """Load embeddings from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        embeddings = [
            NodeEmbedding(
                node_id=e['node_id'],
                node_label=e['node_label'],
                node_properties=e['node_properties'],
                embedding=e['embedding'],
                embedding_model=e['embedding_model'],
                text_content=e['text_content'],
                embedding_timestamp=e['embedding_timestamp'],
                hash_value=e['hash_value'],
            )
            for e in data
        ]
        
        logger.info(f"Loaded {len(embeddings)} embeddings from {filepath}")
        return embeddings

    def semantic_search(
        self,
        embeddings: List[NodeEmbedding],
        query: str,
        top_k: int = 5
    ) -> List[Tuple[NodeEmbedding, float]]:
        """
        Semantic search across vectorized nodes
        
        Args:
            embeddings: List of node embeddings
            query: Search query
            top_k: Number of top results
            
        Returns:
            List of (NodeEmbedding, similarity_score) tuples
        """
        query_embedding = self._get_embedding(query)
        
        # Calculate cosine similarity
        similarities = []
        for embedding in embeddings:
            emb_array = np.array(embedding.embedding)
            similarity = np.dot(query_embedding, emb_array) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb_array) + 1e-10
            )
            similarities.append((embedding, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def close(self):
        """Close Neo4j driver connection"""
        self.driver.close()


class KnowledgeGraphSchema:
    """Manages and caches the KG schema for reasoning"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self._schema_cache = None
        self._relationships_cache = None

    def get_node_labels(self) -> List[str]:
        """Get all node labels in the graph"""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.labels()
                YIELD label
                RETURN label
            """)
            return [record['label'] for record in result]

    def get_relationships(self) -> List[str]:
        """Get all relationship types in the graph"""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.relationshipTypes()
                YIELD relationshipType
                RETURN relationshipType
            """)
            return [record['relationshipType'] for record in result]

    def get_schema(self) -> Dict:
        """Get complete schema including node properties"""
        if self._schema_cache is None:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)
                    UNWIND labels(n) as label
                    RETURN DISTINCT label, keys(n) as properties
                """)
                
                schema = {}
                for record in result:
                    label = record['label']
                    if label not in schema:
                        schema[label] = {
                            'properties': set(record['properties']),
                            'sample_relationships': []
                        }
                    else:
                        schema[label]['properties'].update(record['properties'])
                
                # Get relationships for each label
                for label in schema:
                    result = session.run(f"""
                        MATCH (n:{label})-[r]->()
                        UNWIND [type(r)] as rel_type
                        RETURN DISTINCT rel_type
                        LIMIT 10
                    """)
                    schema[label]['sample_relationships'] = [r['rel_type'] for r in result]
                
                self._schema_cache = schema
        
        return self._schema_cache

    def get_relationship_pattern(self, relationship_type: str) -> str:
        """Get the pattern of a relationship (start label -> end label)"""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (start)-[r:{relationship_type}]->(end)
                RETURN DISTINCT labels(start)[0] as start_label, labels(end)[0] as end_label
                LIMIT 1
            """)
            
            record = result.single()
            if record:
                return f"{record['start_label']}-[{relationship_type}]->{record['end_label']}"
            return f"?-[{relationship_type}]->?"

    def close(self):
        """Close connection"""
        self.driver.close()
