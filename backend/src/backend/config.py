"""
Configuration settings for the application.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "Speed-Run AML Platform"
    VERSION: str = "1.0.0"

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging settings
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, AUDIT
    LOG_FILE: str = ""  # Optional: path to log file

    # Database settings (PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://speedrun:speedrun@localhost:5432/speedrun_aml"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False  # Set to True for SQL query logging
    TESTING: bool = False  # Set to True in test environment

    # Redis settings (Cache)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 3600  # 1 hour default

    # Cache TTLs (in seconds)
    CACHE_TTL_DOCUMENT_PARSING: int = 86400  # 24 hours
    CACHE_TTL_OCR: int = 172800  # 48 hours
    CACHE_TTL_IMAGE_ANALYSIS: int = 86400  # 24 hours
    CACHE_TTL_VALIDATION: int = 43200  # 12 hours

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".docx"]

    # OCR settings
    OCR_ENGINE: str = "docling"  # Using Docling for OCR and document parsing
    OCR_LANGUAGE: str = "en"  # All documents assumed to be in English

    # Temporary file storage
    UPLOAD_DIR: str = "/tmp/uploads"

    # Corroboration settings
    AUDIT_LOG_PATH: str = "/tmp/corroboration_audit"
    ENABLE_REVERSE_IMAGE_SEARCH: bool = False  # Set to True when API keys are configured
    ENABLE_ADVANCED_FORENSICS: bool = True

    # External API keys (optional - add to .env file)
    GOOGLE_VISION_API_KEY: str = ""
    TINEYE_API_KEY: str = ""
    TINEYE_API_SECRET: str = ""
    BING_VISUAL_SEARCH_KEY: str = ""
    HIVE_AI_API_TOKEN: str = ""
    SIGHTENGINE_API_USER: str = ""
    SIGHTENGINE_API_SECRET: str = ""

    # Risk scoring thresholds
    RISK_THRESHOLD_LOW: float = 25.0
    RISK_THRESHOLD_MEDIUM: float = 50.0
    RISK_THRESHOLD_HIGH: float = 75.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
