import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.database.session import engine, get_db
from app.database.base import Base
# Import models to ensure they are registered with Base.metadata
import app.models  # noqa: F401
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.api.routes import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sahai_coop")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    Ensures database tables are created automatically on startup.
    """
    logger.info("Initializing SahAI-Coop Backend Application...")
    try:
        # Create all tables if they do not already exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verification and table creation complete.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down SahAI-Coop Backend Application...")


def create_application() -> FastAPI:
    """Application factory for SahAI-Coop FastAPI Backend."""
    app = FastAPI(
        title="SahAI-Coop API",
        description=(
            "Multilingual Cooperative Governance & Legal Assistance Chatbot Backend (SIH26088). "
            "Provides authentication, session-based chat management, topic categorizations, "
            "and AI RAG hook integrations for farmers and cooperative members in English, Hindi, and Marathi."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Setup Middleware
    setup_cors(app)
    setup_error_handlers(app)

    # Mount API Routes
    app.include_router(api_router)

    # Root Endpoint
    @app.get(
        "/",
        tags=["System"],
        summary="API Root",
        status_code=status.HTTP_200_OK
    )
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "online",
            "docs_url": "/docs",
            "health_check": "/api/health"
        }

    # Health Check Endpoint
    @app.get(
        "/api/health",
        tags=["System"],
        summary="Service Health Check",
        status_code=status.HTTP_200_OK
    )
    def health_check(db: Session = Depends(get_db)):
        db_status = "connected"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        return {
            "status": "healthy" if "unhealthy" not in db_status else "degraded",
            "database": db_status,
            "environment": settings.ENVIRONMENT,
            "ai_rag_hook_enabled": settings.AI_RAG_ENABLED
        }

    return app


app = create_application()
