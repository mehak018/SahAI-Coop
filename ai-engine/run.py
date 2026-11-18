"""
Launcher for the SahAI-Coop RAG AI Engine Microservice.
Usage:
    cd ai-engine
    python run.py
"""

import sys
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} on http://{settings.HOST}:{settings.PORT}")
    print(f"Interactive RAG Docs: http://localhost:{settings.PORT}/docs")
    print(f"Health Endpoint:      http://localhost:{settings.PORT}/api/rag/health")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
