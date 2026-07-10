import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    APP_NAME: str = "Scraper Hub"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./scraper_hub.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT_MS: int = 45000
    WEBHOOK_SIGNING_SECRET: str = "change-me"
    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_REQUEST_TIMEOUT: int = 30
    DEFAULT_TIMEZONE: str = "Africa/Harare"
    GEMINI_API_KEY: str = "AIzaSyANqI_aWF854Wu-IDlk7dhtb6_7Dd74S_s"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()