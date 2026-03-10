from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Use environment variable for production
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./carfirstaid.db")
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "fallback-secret-key-for-development-only")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File upload
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # AI Model
    ai_model_url: str = os.getenv("AI_MODEL_URL", "http://localhost:8001")
    
    # YouTube API
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    
    # Development Settings
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS settings
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",
        "exp://localhost:19000",
        "*"  # Allow all origins for mobile app
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

def get_database_url():
    """Get the appropriate database URL based on environment"""
    return settings.database_url
