from core.db import MCPConnection
from core.llm import GroqClient
from core.config import get_settings
from domain.prompts import PromptBuilder
from domain.schema import CLINICAL_SCHEMA
import logging
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class GraphRAGService:
    def __init__(self):
        self.db = MCPConnection()
        self.llm = GroqClient()

    def _sanitize_cypher(self, cypher: str) -> str:
        # Remove markdown code blocks if present
        cleaned = re.sub(r"```cypher", "", cypher, flags=re.IGNORECASE)
        cleaned = re.sub(r"```", "", cleaned)
        return cleaned.strip()

    def process_request(self, query: str, patient_id: str = None, doctor_id: str = None) -> str:
        logger.info(f"Processing query: {query} (Patient: {patient_id}, Doctor: {doctor_id})")

        # 1. Build Initial Prompt
        messages = PromptBuilder.get_cypher_gen_messages(query, patient_id, doctor_id)
        
        # 2. Generate Cypher
        cypher_query = self.llm.generate(messages)
        cleaned_cypher = self._sanitize_cypher(cypher_query)
        logger.info(f"Generated Cypher: {cleaned_cypher}")

        results = None
        
        # 3. Execution Loop with Auto-Correction
        for attempt in range(settings.MAX_RETRIES):
            try:
                results = self.db.query(cleaned_cypher)
                
                # Unwrap standardized MCP result format if present
                # Expected format: {"results": [...], "count": N}
                if isinstance(results, dict):
                    # Check for soft errors returned as data
                    if "error" in results:
                        raise Exception(f"Database Error: {results['error']}")
                    
                    if "results" in results:
                        results = results["results"]
                
                break # Success!
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                
                if attempt < settings.MAX_RETRIES - 1:
                    logger.info("Attempting auto-correction...")
                    cleaned_cypher = self.llm.correct_cypher(cleaned_cypher, error_msg, CLINICAL_SCHEMA)
                    cleaned_cypher = self._sanitize_cypher(cleaned_cypher)
                    logger.info(f"Corrected Cypher: {cleaned_cypher}")
                else:
                    return f"I'm sorry, I couldn't generate a valid query after {settings.MAX_RETRIES} attempts. Error: {error_msg}"

        # 4. Synthesize Answer
        if not results:
            return "No records found matching your query."
            
        summary = self.llm.generate(
            PromptBuilder.get_summarization_messages(query, results)
        )
        
        return summary
