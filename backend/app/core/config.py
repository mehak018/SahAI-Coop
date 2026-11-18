import json
from typing import List, Union
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables and .env file.
    """
    # Application Info
    APP_NAME: str = "SahAI-Coop API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MySQL Database Connection String
    # Format: mysql+pymysql://username:password@localhost:3306/sahai_coop_db
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/sahai_coop_db"

    # JWT Authentication & Cryptography
    SECRET_KEY: str = "sahai_coop_super_secret_jwt_key_sih26088_production_change_this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS Allowed Origins
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "*"
    ]

    # AI / RAG Module Integration Parameters
    AI_RAG_ENABLED: bool = False
    AI_RAG_SERVICE_URL: str = "http://localhost:8001/api/rag/query"
    AI_RAG_TIMEOUT_SECONDS: int = 10

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
