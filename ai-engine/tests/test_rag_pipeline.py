"""Automated unit & integration tests for the SahAI-Coop RAG AI Engine."""

from pathlib import Path
import sys

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AI_ENGINE_DIR))

from fastapi.testclient import TestClient

from app.main import app
from app.multilingual.language_utils import (
    detect_query_language,
    expand_query_for_bm25,
    is_simple_greeting,
)
from app.rag.loader import load_knowledge_base


def test_knowledge_base_loads_documents():
    kb_dir = AI_ENGINE_DIR / "app" / "knowledge_base"
    chunks, docs = load_knowledge_base(kb_dir)
    assert len(docs) >= 6
    assert len(chunks) >= 12
    topics = {d["topic"] for d in docs}
    assert "crop_insurance" in topics
    assert "pacs" in topics
    assert "documents" in topics
    assert "grievance" in topics
    assert "cooperative_rules" in topics
    assert "government_schemes" in topics


def test_multilingual_detection_and_expansion():
    assert detect_query_language("How do I apply for PMFBY?", "en") == "en"
    assert detect_query_language("पीक विम्यासाठी अर्ज कसा करावा?", "en") == "mr"
    assert detect_query_language("फसल बीमा के लिए कैसे आवेदन करें?", "en") == "hi"
    assert is_simple_greeting("Namaste!") is True
    assert is_simple_greeting("What is PMFBY?") is False
    expanded = expand_query_for_bm25("पीक विमा नुकसान")
    assert "insurance" in expanded and "pmfby" in expanded


def test_rag_api_health_and_query():
    with TestClient(app) as client:
        health = client.get("/api/rag/health")
        assert health.status_code == 200
        hdata = health.json()
        assert hdata["status"] == "ok"
        assert hdata["chunks_indexed"] > 0

        # Greeting test
        greet = client.post("/api/rag/query", json={"query": "Hello", "language": "en"})
        assert greet.status_code == 200
        assert greet.json()["mode"] == "greeting"

        # Domain retrieval test (works even without API key via BM25 fallback)
        res = client.post(
            "/api/rag/query",
            json={"query": "What is the 72 hour rule in PMFBY crop insurance?", "language": "en"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["topic"] == "crop_insurance"
        assert "72" in body["answer"] or "PMFBY" in body["answer"]
        assert body["confidence"] > 0
        assert "pmfby.gov.in" in body["source_reference"]

        # Marathi query test
        mr_res = client.post(
            "/api/rag/query",
            json={"query": "सातबारा आणि कागदपत्रे कोणती लागतात?", "language": "mr"},
        )
        assert mr_res.status_code == 200
        assert mr_res.json()["topic"] == "documents"
