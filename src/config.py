"""Configuration settings for the RAG system."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Endee Configuration
    endee_url: str = "http://localhost:8080"
    endee_auth_token: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: str = "your-openai-api-key-here"
    openai_model: str = "text-embedding-3-small"
    
    # Document Processing
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Application
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
def get_settings():
    """Get settings instance with error handling."""
    try:
        return Settings()
    except Exception as e:
        print(f"⚠️  Configuration error: {e}")
        print("Using default settings...")
        return Settings(
            openai_api_key="your-openai-api-key-here",
            endee_url="http://localhost:8080"
        )

settings = get_settings()