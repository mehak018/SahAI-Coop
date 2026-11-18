"""Central configuration for the SahAI-Coop RAG AI Engine."""

from pathlib import Path
from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "SahAI-Coop RAG AI Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Google Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_FALLBACK_MODEL: str = "gemini-3.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_OUTPUT_TOKENS: int = 1024

    # Knowledge Base & RAG Configuration
    KNOWLEDGE_BASE_DIR: str = str(AI_ENGINE_DIR / "app" / "knowledge_base")
    VECTOR_INDEX_PATH: str = str(AI_ENGINE_DIR / "data" / "vector_index.json")
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 4
    MIN_CONFIDENCE_THRESHOLD: float = 0.12

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(AI_ENGINE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
