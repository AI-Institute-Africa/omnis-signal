import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ai_research_intelligence"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@airesearchintel.com"
    EMAIL_ENABLED: bool = False
    
    # Gemini API
    GEMINI_API_KEY: str = "AIzaSyANqI_aWF854Wu-IDlk7dhtb6_7Dd74S_s"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # OpenAI API
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Anthropic API
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini | openai | anthropic | litellm
    
    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "ai_research"
    
    # Processing Configuration
    BATCH_SIZE: int = 50
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    REQUEST_TIMEOUT: int = 30
    
    # Scheduler Configuration
    DIGEST_SCHEDULE_HOURS: int = 4
    CRAWLER_SCHEDULE_MINUTES: int = 15
    DEDUPLICATION_SCHEDULE_MINUTES: int = 30
    TREND_ANALYSIS_SCHEDULE_MINUTES: int = 60
    
    # Alert Thresholds
    HIGH_PRIORITY_SCORE_THRESHOLD: float = 85.0
    MEDIUM_PRIORITY_SCORE_THRESHOLD: float = 65.0
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Environment
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Default export
settings = get_settings()
