import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration and environment variables."""

    # Application settings
    APP_NAME: str = "EMS Assistant Backend"
    APP_ENV: str = "development"  # 'development', 'staging', 'production', 'test'
    DEBUG: bool = False
    DEBUG_RAG: bool = True  # Logs detailed RAG analysis for observability
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Timezone configuration for authoritative date & time calculations
    EMS_TIMEZONE: str = "Asia/Kolkata"

    # API & CORS
    API_PREFIX: str = "/api"
    ALLOWED_WIDGET_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Google Gemini AI configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GOOGLE_EMBEDDING_MODEL: str = "text-embedding-004"

    # Supabase / PostgreSQL configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    USE_IN_MEMORY_FALLBACK: bool = True  # Allows offline/local dev and testing without Supabase connection

    # EMS Public Source configuration
    EMS_PUBLIC_BASE_URL: str = "https://ems.mlritcie.in"
    EMS_PUBLIC_API_URL: str = "https://ems.mlritcie.in/api/public/events"

    # Guardrails & Precision RAG settings
    OUT_OF_SCOPE_COOLDOWN_SECONDS: int = 10
    MAX_CONVERSATION_HISTORY_MESSAGES: int = 6
    MAX_MESSAGE_CHAR_LENGTH: int = 1000
    MAX_RETRIEVAL_CHUNKS: int = 6
    MIN_SIMILARITY_THRESHOLD: float = 0.35
    MIN_PRECISION_SCORE: float = 0.50

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 40

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
