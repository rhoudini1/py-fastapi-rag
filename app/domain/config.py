# Configuration for loading .env files
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory (parent of 'app' directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    DATABASE_URL: str = "sqlite+aiosqlite:///./documents.db"

    google_api_key: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

# Set GOOGLE_API_KEY environment variable for Google Generative AI SDK
os.environ["GOOGLE_API_KEY"] = settings.google_api_key