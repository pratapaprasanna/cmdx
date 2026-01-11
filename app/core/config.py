"""
Application configuration settings
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    PROJECT_NAME: str = "CMS API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # CORS - expects JSON array format in .env file: ["http://localhost:3000","http://localhost:8000"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/cmdx_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )


settings = Settings()
