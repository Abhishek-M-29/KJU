from groq import Groq
from core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        try:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

    def generate(self, messages: list, temperature: float = 0.0) -> str:
        """
        Generic generation method.
        Low temperature for code generation (Cypher).
        Higher temperature can be used for summarization if needed.
        """
        try:
            completion = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=temperature,
                stop=None
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise

    def correct_cypher(self, original_query: str, error_message: str, schema_context: str) -> str:
        """
        Specific method to handle the correction loop.
        """
        correction_messages = [
            {"role": "system", "content": f"You are a Neo4j Cypher expert. Fix the following Cypher query based on the error. \nSchema: {schema_context}"},
            {"role": "user", "content": f"Query: {original_query}\nError: {error_message}\n\nReturn ONLY the fixed Cypher query."}
        ]
        return self.generate(correction_messages, temperature=0.0)
