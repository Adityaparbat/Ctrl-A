import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Data paths
    data_path: str = os.path.join("data", "disability_schemes.json")
    db_dir: str = os.path.join("data", "chroma_db")
    
    # API settings
    api_title: str = "Disability Schemes Discovery System"
    api_version: str = "1.0.0"
    api_description: str = "A comprehensive API for discovering disability welfare schemes using AI-powered search"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # ChromaDB settings
    collection_name: str = "disability_schemes"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Search settings
    default_top_k: int = 5
    max_top_k: int = 50
    min_similarity_score: float = 0.0
    
    # Logging
    log_level: str = "INFO"

    # Admin/API auth
    admin_api_key: str | None = os.getenv("ADMIN_API_KEY", None)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


# Legacy constants for backward compatibility
DATA_PATH = os.path.join("data", "disability_schemes.json")
DB_DIR = os.path.join("data", "chroma_db")
