"""
Configuration settings for the EcoDrive API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_TITLE: str = "EcoDrive Query API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for processing EcoDrive customer queries"

    # External API
    RAG_API_BASE_URL: str
    RAG_API_KEY: str

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL_CLASSIFIER: str = "gpt-3.5-turbo-0125"
    OPENAI_MODEL_CHAT: str = "gpt-3.5-turbo"
    OPENAI_MODEL_RAG: str = "o3-mini"
    OPENAI_TEMPERATURE: float = 0.7

    # Cohere Configuration
    COHERE_API_KEY: Optional[str] = None
    COHERE_RERANK_MODEL: str = "rerank-english-v3.0"

    # Knowledge Base Dataset IDs
    DATASET_IDS: str = ""

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Redis (optional, for caching)
    REDIS_URL: Optional[str] = None

    # Retry Configuration
    HTTP_MAX_RETRIES: int = 3
    HTTP_RETRY_INTERVAL: int = 100  # milliseconds

    # Timeout Configuration
    HTTP_CONNECT_TIMEOUT: int = 30
    HTTP_READ_TIMEOUT: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
