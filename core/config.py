from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GROQ_API_KEY: str
    MCP_SERVER_URL: str
    NEO4J_URI: str = "bolt://localhost:7687" # Optional now
    NEO4J_USER: str = "neo4j" # Optional now
    NEO4J_PASSWORD: str = "password" # Optional now
    MAX_RETRIES: int = 3
    MODEL_NAME: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignore extra env vars

@lru_cache()
def get_settings():
    return Settings()
