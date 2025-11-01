"""
Configuration settings for the application.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str = "OCR & Document Parser API"
    VERSION: str = "0.1.0"

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

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
