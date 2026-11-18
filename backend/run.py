"""
Convenience launcher for the SahAI-Coop FastAPI Backend Server.
Usage:
    cd backend
    python run.py
"""

import sys
from pathlib import Path
import uvicorn

# Ensure the backend directory is in the sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} on http://{settings.HOST}:{settings.PORT}")
    print(f"Interactive API Docs: http://localhost:{settings.PORT}/docs")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
