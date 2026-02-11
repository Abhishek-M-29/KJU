"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # External API endpoints (from .env)
    ml_swarm_url: str
    medgemma_url: str

    # Groq (Synthesis Agent)
    groq_api_key: str
    groq_model: str

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
