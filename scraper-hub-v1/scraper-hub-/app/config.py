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

    # Email & 12-Hour Reporting Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "reports@omnis-signal.com"
    REPORT_RECIPIENTS: list = ["dennis@rubiem.com", "takuechakanyuka@gmail.com", "arthur@rubiem.com"]

    # Free LLM & Price Extraction Models (DeepSeek, Qwen, OpenRouter, Groq, Gemini, Ollama)
    LLM_PROVIDER: str = "auto"  # auto | deepseek | qwen | openrouter | groq | gemini | ollama
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    QWEN_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "deepseek/deepseek-r1:free"  # or qwen/qwen-2.5-72b-instruct:free
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "qwen-2.5-32b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()