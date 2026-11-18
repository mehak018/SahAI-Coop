"""
SahAI-Coop RAG AI Engine Microservice (Port 8001).
Integrates directly with backend/app/services/rag_hook.py.
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.services.rag_service import rag_service

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sahai_coop.ai.main")


# =============================================================================
# Request / Response Schemas
# =============================================================================

class ChatTurn(BaseModel):
    sender: str = Field(..., description="'user' or 'bot'")
    content: str = Field(..., description="Message text")


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User question")
    language: str = Field(default="en", description="Target language: en, hi, or mr")
    history: Optional[List[ChatTurn]] = Field(
        default=None,
        description="Optional recent conversation turns for multi-turn context",
    )
    top_k: Optional[int] = Field(default=None, ge=1, le=10)


class RAGQueryResponse(BaseModel):
    answer: str
    topic: str
    source_reference: str
    confidence: float
    language: str
    mode: str
    retrieved_chunks: List[Dict[str, Any]] = []


# =============================================================================
# Application Lifespan & Factory
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SahAI-Coop RAG AI Engine...")
    stats = rag_service.initialize(force_rebuild=False)
    logger.info(
        f"RAG Engine Ready | gemini_configured={rag_service.gemini.is_configured} | {stats}"
    )
    yield
    logger.info("Shutting down SahAI-Coop RAG AI Engine...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Hybrid Vector + BM25 Retrieval-Augmented Generation (RAG) Engine powered by "
        "Google Gemini API for SahAI-Coop (SIH26088)."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/", tags=["System"])
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/rag/health",
    }


@app.get("/api/rag/health", tags=["System"])
def health():
    stats = rag_service.store.get_stats()
    return {
        "status": "ok",
        "gemini_configured": rag_service.gemini.is_configured,
        "gemini_model": rag_service.gemini.active_generation_model or settings.GEMINI_MODEL,
        "last_gemini_error": rag_service.gemini.last_error,
        **stats,
    }


@app.get("/api/rag/test-gemini", tags=["System"])
def test_gemini():
    """Quick live test of Gemini text generation."""
    reply = rag_service.gemini.generate_answer(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say hello in one short sentence.",
    )
    return {
        "ok": reply is not None,
        "model_used": rag_service.gemini.active_generation_model,
        "reply": reply,
        "error": rag_service.gemini.last_error,
    }


@app.post("/api/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
def query_rag(payload: RAGQueryRequest):
    """
    Main RAG endpoint invoked by the SahAI-Coop backend (`AIRAGHook`).
    """
    history_dicts = (
        [{"sender": turn.sender, "content": turn.content} for turn in payload.history]
        if payload.history
        else None
    )
    result = rag_service.answer_query(
        query=payload.query,
        language=payload.language,
        history=history_dicts,
        top_k=payload.top_k,
    )
    return RAGQueryResponse(**result)


@app.get("/api/rag/documents", tags=["Knowledge Base"])
def list_documents():
    """Return all currently indexed knowledge base documents."""
    return {
        "total_documents": len(rag_service.store.documents),
        "total_chunks": len(rag_service.store.chunks),
        "documents": rag_service.store.documents,
    }


@app.post("/api/rag/reindex", tags=["Knowledge Base"])
def reindex_knowledge_base():
    """Force reload & re-embed all files in app/knowledge_base/."""
    stats = rag_service.initialize(force_rebuild=True)
    return {"status": "reindexed", **stats}


@app.post("/api/rag/upload", tags=["Knowledge Base"])
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="government_schemes"),
):
    """
    Upload a new .md, .txt, or .pdf knowledge document into app/knowledge_base/<category>/
    and immediately reindex the vector store.
    """
    allowed_ext = {".md", ".txt", ".pdf"}
    filename = Path(file.filename or "uploaded.txt").name
    ext = Path(filename).suffix.lower()
    if ext not in allowed_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: .md, .txt, .pdf",
        )

    safe_category = "".join(c for c in category.lower() if c.isalnum() or c == "_") or "government_schemes"
    target_dir = Path(settings.KNOWLEDGE_BASE_DIR) / safe_category
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    content = await file.read()
    target_path.write_bytes(content)

    stats = rag_service.initialize(force_rebuild=True)
    return {
        "status": "uploaded_and_reindexed",
        "saved_to": str(target_path.relative_to(Path(settings.KNOWLEDGE_BASE_DIR))),
        **stats,
    }
