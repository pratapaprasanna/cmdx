"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "CMS API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/cmdx_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
