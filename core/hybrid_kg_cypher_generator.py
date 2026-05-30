"""
LLM-based Cypher Query Generator with Schema Reasoning
Converts natural language to optimized Cypher queries.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class GeneratedCypher:
    """Represents a generated Cypher query"""
    cypher_query: str
    natural_language: str
    explanation: str
    reasoning: str
    schema_used: List[str]
    confidence: float
    multi_hop: bool
    optimizations: List[str]


class CypherGenerator:
    """Generates optimized Cypher queries from natural language with schema reasoning"""

    def __init__(
        self,
        llm_provider: str = "ollama",
        model_name: str = "qwen2.5:7b-instruct",
        ollama_url: str = "http://localhost:11434",
        kg_schema=None,
    ):
        """
        Initialize Cypher generator with Ollama
        
        Args:
            llm_provider: 'ollama' (local LLM)
            model_name: Ollama model name (e.g., 'qwen2.5:7b-instruct', 'mistral', 'neural-chat')
            ollama_url: URL to Ollama server (default: http://localhost:11434)
            kg_schema: KnowledgeGraphSchema instance for context
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.kg_schema = kg_schema
        self.llm = self._initialize_llm()
        self.schema_context = ""
        self._initialize_schema_context()

    def _initialize_llm(self):
        """Initialize the Ollama LLM"""
        if self.llm_provider != "ollama":
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}. Only 'ollama' is supported.")
        
        if not HAS_REQUESTS:
            raise ImportError("requests not installed. Install with: pip install requests")
        
        # Test Ollama connection
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama at {self.ollama_url}")
                models = response.json().get('models', [])
                model_names = [m['name'].split(':')[0] for m in models]
                logger.info(f"Available models: {model_names}")
            else:
                raise ConnectionError(f"Ollama server returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama at {self.ollama_url}: {e}")
            logger.warning("Make sure Ollama is running: ollama serve")
        
        return self.ollama_url

    def _initialize_schema_context(self):
        """Initialize schema context for the LLM"""
        if self.kg_schema is None:
            return
        
        schema = self.kg_schema.get_schema()
        relationships = self.kg_schema.get_relationships()
        
        schema_text = "# Healthcare Knowledge Graph Schema\n\n"
        
        schema_text += "## Node Labels:\n"
        for label, info in schema.items():
            schema_text += f"- {label}: properties = {', '.join(list(info['properties'])[:5])}\n"
        
        schema_text += "\n## Relationship Types:\n"
        for rel in relationships[:15]:
            pattern = self.kg_schema.get_relationship_pattern(rel)
            schema_text += f"- {pattern}\n"
        
        self.schema_context = schema_text
        logger.info("Schema context initialized")

    def generate_from_context(
        self,
        retrieved_context,
        user_query: str,
        num_suggestions: int = 3,
    ) -> List[GeneratedCypher]:
        """
        Generate Cypher queries from retrieved context
        
        Args:
            retrieved_context: RetrievedContext from HybridKGRetriever
            user_query: Original user query
            num_suggestions: Number of query suggestions to generate
            
        Returns:
            List of GeneratedCypher objects
        """
        
        # Prepare context for LLM
        context_str = self._format_context(retrieved_context)
        
        # Generate multiple Cypher queries
        queries = []
        for i in range(num_suggestions):
            query = self._generate_single_cypher(
                user_query=user_query,
                context_str=context_str,
                suggestion_number=i + 1,
                total_suggestions=num_suggestions,
            )
            if query:
                queries.append(query)
        
        return queries

    def generate_fallback_queries(self, retrieved_context, user_query: str) -> List[GeneratedCypher]:
        """Generate deterministic fallback queries when LLM output is invalid"""
        queries: List[GeneratedCypher] = []

        if not self.kg_schema:
            return queries

        query_lc = user_query.lower()
        wants_medication = any(k in query_lc for k in ["medication", "medicine", "drug", "meds"]) and "patient" in query_lc

        if wants_medication:
            relationships = self.kg_schema.get_relationships()

            # If user specifies a name, try a name-based query first
            name_match = re.search(r"\bname\s+([A-Za-z]+)\b|\bnamed\s+([A-Za-z]+)\b", user_query, re.IGNORECASE)
            if name_match:
                name_value = next((g for g in name_match.groups() if g), "").strip()
                if name_value:
                    for rel in relationships:
                        pattern = self.kg_schema.get_relationship_pattern(rel)
                        if "-" not in pattern or "->" not in pattern:
                            continue
                        start_label, rest = pattern.split("-[", 1)
                        rel_type, end_label = rest.split("]->", 1)
                        start_label = start_label.strip()
                        end_label = end_label.strip()
                        if any(x in start_label.lower() for x in ["patient", "person"]) and any(x in end_label.lower() for x in ["medication", "drug"]):
                            cypher = (
                                f"// Patient by name and their medications\n"
                                f"MATCH (p:{start_label})-[:{rel_type}]->(m:{end_label})\n"
                                f"WHERE toLower(p.name) = toLower('{name_value}')\n"
                                f"RETURN p, collect(m) AS meds LIMIT 1"
                            )
                            queries.append(
                                GeneratedCypher(
                                    cypher_query=cypher,
                                    natural_language=user_query,
                                    explanation="Return medications for the specified patient name",
                                    reasoning="Schema-based fallback using Patient/Medication relationship and name filter",
                                    schema_used=[start_label, end_label, rel_type],
                                    confidence=0.6,
                                    multi_hop=False,
                                    optimizations=["LIMIT 1"],
                                )
                            )
                            return queries

            def parse_pattern(rel_name: str):
                pattern = self.kg_schema.get_relationship_pattern(rel_name)
                if "-" not in pattern or "->" not in pattern:
                    return None
                start_label, rest = pattern.split("-[", 1)
                rel_type, end_label = rest.split("]->", 1)
                return start_label.strip(), rel_type.strip(), end_label.strip()

            rel_patterns = [parse_pattern(r) for r in relationships]
            rel_patterns = [p for p in rel_patterns if p]

            # Prefer direct Patient/Person -> Medication/Drug
            direct = next(
                (p for p in rel_patterns
                 if any(x in p[0].lower() for x in ["patient", "person"]) and any(x in p[2].lower() for x in ["medication", "drug"])),
                None,
            )

            if direct:
                start_label, rel_type, end_label = direct
                cypher = (
                    f"// Random patient and their medications\n"
                    f"MATCH (p:{start_label})-[:{rel_type}]->(m:{end_label})\n"
                    f"WITH p, collect(m) AS meds ORDER BY rand() LIMIT 1\n"
                    f"RETURN p, meds LIMIT 1"
                )
                queries.append(
                    GeneratedCypher(
                        cypher_query=cypher,
                        natural_language=user_query,
                        explanation="Select a random patient and return medications",
                        reasoning="Schema-based fallback using direct Patient/Medication relationship",
                        schema_used=[start_label, end_label, rel_type],
                        confidence=0.55,
                        multi_hop=False,
                        optimizations=["LIMIT 1", "ORDER BY rand()"],
                    )
                )
                return queries

            # Try Patient/Person -> Encounter -> Medication
            person_to_enc = next(
                (p for p in rel_patterns if any(x in p[0].lower() for x in ["patient", "person"]) and "encounter" in p[2].lower()),
                None,
            )
            enc_to_med = next(
                (p for p in rel_patterns if "encounter" in p[0].lower() and any(x in p[2].lower() for x in ["medication", "drug"])),
                None,
            )
            if person_to_enc and enc_to_med:
                p_lbl, p_rel, e_lbl = person_to_enc
                e2_lbl, e2_rel, m_lbl = enc_to_med
                cypher = (
                    f"// Random patient and medications via encounters\n"
                    f"MATCH (p:{p_lbl})-[:{p_rel}]->(e:{e_lbl})-[:{e2_rel}]->(m:{m_lbl})\n"
                    f"WITH p, collect(distinct m) AS meds ORDER BY rand() LIMIT 1\n"
                    f"RETURN p, meds LIMIT 1"
                )
                queries.append(
                    GeneratedCypher(
                        cypher_query=cypher,
                        natural_language=user_query,
                        explanation="Select a random patient and medications via encounters",
                        reasoning="Schema-based fallback using Encounter bridge",
                        schema_used=[p_lbl, e_lbl, m_lbl, p_rel, e2_rel],
                        confidence=0.5,
                        multi_hop=True,
                        optimizations=["LIMIT 1", "ORDER BY rand()"],
                    )
                )
                return queries

            # Try Patient/Person -> Condition -> Medication
            person_to_cond = next(
                (p for p in rel_patterns if any(x in p[0].lower() for x in ["patient", "person"]) and "condition" in p[2].lower()),
                None,
            )
            cond_to_med = next(
                (p for p in rel_patterns if "condition" in p[0].lower() and any(x in p[2].lower() for x in ["medication", "drug"])),
                None,
            )
            if person_to_cond and cond_to_med:
                p_lbl, p_rel, c_lbl = person_to_cond
                c2_lbl, c2_rel, m_lbl = cond_to_med
                cypher = (
                    f"// Random patient and medications via conditions\n"
                    f"MATCH (p:{p_lbl})-[:{p_rel}]->(c:{c_lbl})-[:{c2_rel}]->(m:{m_lbl})\n"
                    f"WITH p, collect(distinct m) AS meds ORDER BY rand() LIMIT 1\n"
                    f"RETURN p, meds LIMIT 1"
                )
                queries.append(
                    GeneratedCypher(
                        cypher_query=cypher,
                        natural_language=user_query,
                        explanation="Select a random patient and medications via conditions",
                        reasoning="Schema-based fallback using Condition bridge",
                        schema_used=[p_lbl, c_lbl, m_lbl, p_rel, c2_rel],
                        confidence=0.5,
                        multi_hop=True,
                        optimizations=["LIMIT 1", "ORDER BY rand()"],
                    )
                )

        return queries

    def _format_context(self, retrieved_context) -> str:
        """Format retrieved context for LLM"""
        # Simplified context to reduce token count
        sample_node = "None"
        if retrieved_context.retrieved_nodes:
            first_node = retrieved_context.retrieved_nodes[0]
            sample_node = first_node.get('label', first_node.get('node_label', 'Unknown'))
        
        context = f"""Query: {retrieved_context.query}
    Nodes: {', '.join(retrieved_context.node_labels[:5])}
    Relationships: {', '.join(retrieved_context.relationships[:5])}
    Patterns: {', '.join(retrieved_context.suggested_patterns[:3])}"""
        return context

    def _generate_single_cypher(
        self,
        user_query: str,
        context_str: str,
        suggestion_number: int,
        total_suggestions: int,
    ) -> Optional[GeneratedCypher]:
        """Generate a single Cypher query using Ollama"""
        
        prompt = self._build_prompt(
            user_query=user_query,
            context_str=context_str,
            suggestion_number=suggestion_number,
            total_suggestions=total_suggestions,
        )
        
        try:
            full_prompt = f"{self._get_system_prompt()}\n\n{prompt}"
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
                timeout=180,  # Increased to 3 minutes for larger models
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            response_text = response.json().get('response', '')
            
            # Parse response
            return self._parse_cypher_response(response_text, user_query)
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_url}")
            logger.error("Make sure Ollama is running: ollama serve")
            return None
        except Exception as e:
            logger.error(f"Error generating Cypher query: {e}")
            return None

    def _get_system_prompt(self) -> str:
        """Get system prompt for Cypher generation"""
        # Simplified prompt to reduce tokens
        return f"""Generate Neo4j Cypher query for healthcare data.

Schema:
{self.schema_context}

Rules:
- Use MATCH/WHERE/RETURN
- Patient/Person is central node when relevant
- Do NOT hardcode names/IDs unless explicitly in the user query
- Add LIMIT to avoid large scans
"""

    def _build_prompt(
        self,
        user_query: str,
        context_str: str,
        suggestion_number: int,
        total_suggestions: int,
    ) -> str:
        """Build the prompt for Cypher generation"""
        
        return f"""Query: {user_query}
{context_str}

Generate Neo4j Cypher. Format:
```cypher
MATCH ... RETURN ... LIMIT 20
```"""

    def is_query_too_specific(self, cypher_query: str, user_query: str) -> bool:
        """Reject queries that hardcode names/ids not mentioned by the user"""
        if not user_query:
            return False
        user_lc = user_query.lower()
        for match in re.findall(r"name\s*:\s*'([^']+)'", cypher_query, flags=re.IGNORECASE):
            if match.lower() not in user_lc:
                return True
        for match in re.findall(r"\bid\s*:\s*'([^']+)'", cypher_query, flags=re.IGNORECASE):
            if match.lower() not in user_lc:
                return True
        return False

    def _parse_cypher_response(self, response_text: str, user_query: str) -> Optional[GeneratedCypher]:
        """Parse LLM response into GeneratedCypher object"""
        
        try:
            # Extract Cypher query
            cypher_match = re.search(r'```cypher\s*(.*?)\s*```', response_text, re.DOTALL)
            if not cypher_match:
                cypher_match = re.search(r'```\s*(MATCH.*?)(?:\n\n|$)', response_text, re.DOTALL)
            
            if not cypher_match:
                logger.warning("Could not extract Cypher query from response")
                return None
            
            cypher_query = cypher_match.group(1).strip()
            
            # Extract explanation
            explanation = ""
            if "//" in cypher_query:
                lines = cypher_query.split('\n')
                explanation = '\n'.join([l for l in lines if l.strip().startswith('//')])
            
            # Extract reasoning
            reasoning_match = re.search(r'reasoning[:\s]*(.*?)(?:\n|Confidence)', response_text, re.IGNORECASE | re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
            
            # Extract confidence
            confidence_match = re.search(r'confidence[:\s]*(\d+\.?\d*)', response_text, re.IGNORECASE)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.7
            confidence = min(1.0, max(0.0, confidence))
            
            # Detect multi-hop
            multi_hop = len(re.findall(r'-\[.*?\]-', cypher_query)) > 1
            
            # Extract optimizations
            opt_match = re.search(r'optimizations?[:\s]*(.*?)(?:\n\n|$)', response_text, re.IGNORECASE | re.DOTALL)
            optimizations = []
            if opt_match:
                opt_text = opt_match.group(1)
                optimizations = [o.strip() for o in re.split(r'[,;\n]', opt_text) if o.strip()]
            
            return GeneratedCypher(
                cypher_query=cypher_query,
                natural_language=user_query,
                explanation=explanation,
                reasoning=reasoning,
                schema_used=self._extract_schema_elements(cypher_query),
                confidence=confidence,
                multi_hop=multi_hop,
                optimizations=optimizations[:3],
            )
        
        except Exception as e:
            logger.error(f"Error parsing Cypher response: {e}")
            return None

    def _extract_schema_elements(self, cypher_query: str) -> List[str]:
        """Extract node labels and relationships from generated Cypher"""
        
        elements = []
        
        # Extract node labels
        label_matches = re.findall(r':\w+', cypher_query)
        elements.extend(set(label_matches))
        
        # Extract relationships
        rel_matches = re.findall(r':\w+\s*\|', cypher_query)
        elements.extend(set(rel_matches))
        
        return list(set(elements))

    def validate_cypher(self, cypher_query: str, driver) -> Tuple[bool, str]:
        """Validate Cypher query syntax"""
        
        try:
            with driver.session() as session:
                # Add LIMIT 1 to avoid heavy computation
                limited_query = re.sub(r'RETURN\s+', 'RETURN ', cypher_query)
                if 'LIMIT' not in limited_query:
                    limited_query += ' LIMIT 1'
                
                session.run(limited_query)
            return True, "Query is valid"
        
        except Exception as e:
            return False, str(e)

    def optimize_cypher(self, cypher_query: str) -> str:
        """Optimize Cypher query"""
        
        optimized = cypher_query
        
        # Optimization 1: Add LIMIT if missing
        if 'LIMIT' not in optimized and 'RETURN' in optimized:
            optimized += '\nLIMIT 100'
        
        # Optimization 2: Use properties efficiently
        optimized = re.sub(r'\((\w+)\)', lambda m: f'({m.group(1)})' if len(m.group(1)) > 1 else m.group(0), optimized)
        
        # Optimization 3: Index hints (comment-based for now)
        if 'WHERE' in optimized:
            optimized = re.sub(r'WHERE\s+', '// Consider indexing properties used in WHERE\nWHERE ', optimized)
        
        return optimized


class MultiHopCypherEngine:
    """Specialized engine for multi-hop queries"""

    def __init__(self, cypher_generator: CypherGenerator, driver):
        self.generator = cypher_generator
        self.driver = driver
        self.hop_strategies = self._initialize_hop_strategies()

    def _initialize_hop_strategies(self) -> Dict:
        """Initialize different strategies for multi-hop traversal"""
        
        return {
            'breadth_first': {
                'description': 'Explore all nodes at each hop level',
                'pattern': '(start)-[*1..{hops}]-(target)',
            },
            'depth_first': {
                'description': 'Follow specific paths deeply',
                'pattern': '(start)-[r1]->(mid)-[r2]->(target)',
            },
            'shortest_path': {
                'description': 'Find shortest path between nodes',
                'pattern': 'shortestPath((start)-[*1..{hops}]-(target))',
            },
            'all_paths': {
                'description': 'Find all paths (limited for performance)',
                'pattern': 'allShortestPaths((start)-[*1..{hops}]-(target))',
            },
        }

    def generate_multi_hop_query(
        self,
        start_entity: str,
        target_entity: str,
        hops: int = 2,
        strategy: str = 'shortest_path',
    ) -> GeneratedCypher:
        """Generate a multi-hop query"""
        
        if strategy not in self.hop_strategies:
            strategy = 'shortest_path'
        
        pattern = self.hop_strategies[strategy]['pattern'].format(hops=hops)
        
        cypher_query = f"""
// {self.hop_strategies[strategy]['description']}
// Finding paths from {start_entity} to {target_entity}
MATCH path = {pattern}
WHERE ({start_entity})-[:*]->({target_entity})
RETURN path, length(path) as hop_count
LIMIT 20
"""
        
        return GeneratedCypher(
            cypher_query=cypher_query,
            natural_language=f"Find {hops}-hop paths from {start_entity} to {target_entity}",
            explanation=self.hop_strategies[strategy]['description'],
            reasoning=f"Using {strategy} strategy for {hops} hops",
            schema_used=[start_entity, target_entity],
            confidence=0.85,
            multi_hop=True,
            optimizations=["LIMIT 20 to prevent performance issues"],
        )

    def execute_with_reasoning(
        self,
        cypher_query: str,
        reasoning_context: str,
    ) -> Dict:
        """Execute query and provide reasoning about results"""
        
        with self.driver.session() as session:
            result = session.run(cypher_query)
            records = result.data()
        
        return {
            'query': cypher_query,
            'record_count': len(records),
            'samples': records[:3],
            'reasoning': reasoning_context,
        }
