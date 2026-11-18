"""
End-to-End RAG Orchestration Service for SahAI-Coop.

Pipeline:
1. Detect/normalize language (en / hi / mr).
2. Handle greetings warmly without unnecessary API calls.
3. Contextualize short follow-up queries using recent conversation history.
4. Retrieve top-k knowledge chunks via Hybrid Vector + BM25 search.
5. Generate a grounded multilingual answer via Gemini API (with safe fallback if key is unset).
6. Return structured JSON matching Backend `AIRAGHook` contract + clickable frontend citations.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.llm.gemini_client import GeminiClient
from app.llm.prompts import GREETING_RESPONSES, SYSTEM_PROMPT, build_rag_user_prompt
from app.multilingual.language_utils import (
    detect_query_language,
    is_simple_greeting,
)
from app.rag.retriever import RAGRetriever
from app.rag.vector_store import HybridVectorStore, SearchHit

logger = logging.getLogger("sahai_coop.ai.rag_service")


class RAGService:
    """Coordinates retrieval, prompt assembly, LLM generation, and citation formatting."""

    def __init__(self):
        self.gemini = GeminiClient()
        self.store = HybridVectorStore(
            kb_dir=Path(settings.KNOWLEDGE_BASE_DIR),
            index_path=Path(settings.VECTOR_INDEX_PATH),
            gemini_client=self.gemini,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.retriever = RAGRetriever(self.store, default_top_k=settings.TOP_K)
        self._initialized = False

    def initialize(self, force_rebuild: bool = False) -> Dict[str, Any]:
        stats = self.store.initialize(force_rebuild=force_rebuild)
        self._initialized = True
        return stats

    def _contextualize_query(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]],
    ) -> str:
        """
        If the user asks a short follow-up (e.g., 'what documents?' or 'in Marathi'),
        append the previous user message so retrieval stays on-topic.
        """
        if not history or len(query.split()) > 8:
            return query

        last_user_msgs = [
            (m.get("content") or "").strip()
            for m in history
            if (m.get("sender") or m.get("role") or "").lower() == "user"
            and (m.get("content") or "").strip()
        ]
        if not last_user_msgs:
            return query

        prev_q = last_user_msgs[-1]
        if prev_q.lower() == query.strip().lower():
            return query
        return f"{prev_q} {query}"

    def _format_sources(self, hits: List[SearchHit]) -> str:
        """
        Format deduplicated source citations as a JSON array string
        `[{"title": "...", "url": "..."}]` which `frontend/chat.html` renders as clickable links.
        """
        seen = set()
        sources: List[Dict[str, str]] = []
        for hit in hits:
            title = hit.chunk.source_title
            url = hit.chunk.source_url
            key = (title, url)
            if key in seen:
                continue
            seen.add(key)
            sources.append({"title": title, "url": url})
            if len(sources) >= 3:
                break

        if not sources:
            sources.append(
                {
                    "title": "Ministry of Cooperation, Govt. of India",
                    "url": "https://cooperation.gov.in",
                }
            )
        return json.dumps(sources, ensure_ascii=False)

    def _build_retrieval_only_fallback(
        self,
        hits: List[SearchHit],
        language: str,
    ) -> str:
        """
        Safe fallback when Gemini generation is unavailable: returns the best retrieved
        knowledge snippet cleanly with an accurate diagnostic note.
        """
        if not hits:
            return GREETING_RESPONSES.get(language, GREETING_RESPONSES["en"])

        top = hits[0].chunk
        # Strip the internal "[Title | Section]\n" prefix for cleaner display
        body = top.content
        if body.startswith("[") and "]\n" in body:
            body = body.split("]\n", 1)[1]

        if not self.gemini.is_configured:
            notice = {
                "en": "\n\n(Note: Running in local Knowledge-Base mode. Add GEMINI_API_KEY in ai-engine/.env for full AI answers.)",
                "hi": "\n\n(नोट: वर्तमान में स्थानीय ज्ञान-आधार मोड सक्रिय है। पूर्ण AI उत्तरों के लिए ai-engine/.env में GEMINI_API_KEY जोड़ें।)",
                "mr": "\n\n(टीप: सध्या स्थानिक ज्ञान-साठा मोड सुरू आहे. पूर्ण AI उत्तरांसाठी ai-engine/.env मध्ये GEMINI_API_KEY जोडा.)",
            }
            return f"{body.strip()}{notice.get(language, notice['en'])}"

        # Key IS configured, but the Gemini API call returned an error (quota/model/network)
        err_hint = (self.gemini.last_error or "API temporarily unavailable")[:140]
        return f"{body.strip()}\n\n(Note: Shown directly from verified Knowledge Base — Gemini generation error: {err_hint})"

    def answer_query(
        self,
        query: str,
        language: str = "en",
        history: Optional[List[Dict[str, str]]] = None,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run the full RAG pipeline and return backend-compatible response dict."""
        if not self._initialized:
            self.initialize()

        cleaned_query = query.strip()
        target_lang = detect_query_language(cleaned_query, requested_language=language)

        # Fast path for simple greetings
        if is_simple_greeting(cleaned_query):
            return {
                "answer": GREETING_RESPONSES.get(target_lang, GREETING_RESPONSES["en"]),
                "topic": "government_schemes",
                "source_reference": json.dumps(
                    [
                        {
                            "title": "Ministry of Cooperation, Govt. of India",
                            "url": "https://cooperation.gov.in",
                        }
                    ]
                ),
                "confidence": 1.0,
                "language": target_lang,
                "mode": "greeting",
                "retrieved_chunks": [],
            }

        # 1. Contextualize & Retrieve
        search_query = self._contextualize_query(cleaned_query, history)
        hits, confidence = self.retriever.retrieve(
            query=search_query,
            top_k=top_k or settings.TOP_K,
        )

        # Keep hits above minimal relevance floor
        relevant_hits = [h for h in hits if h.score > 0 or h.vector_score >= 0.38]
        context_blocks = [h.chunk.content for h in relevant_hits]

        # 2. Generate grounded answer via Gemini
        answer_text: Optional[str] = None
        mode = "rag_gemini"

        if self.gemini.is_configured:
            user_prompt = build_rag_user_prompt(
                query=cleaned_query,
                language=target_lang,
                context_blocks=context_blocks,
            )
            answer_text = self.gemini.generate_answer(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                history=history,
            )

        if not answer_text:
            mode = "retrieval_fallback"
            answer_text = self._build_retrieval_only_fallback(relevant_hits, target_lang)

        # 3. Topic & Sources
        primary_topic = relevant_hits[0].chunk.topic if relevant_hits else "government_schemes"
        source_reference = self._format_sources(relevant_hits)

        return {
            "answer": answer_text,
            "topic": primary_topic,
            "source_reference": source_reference,
            "confidence": confidence,
            "language": target_lang,
            "mode": mode,
            "retrieved_chunks": [
                {
                    "chunk_id": h.chunk.chunk_id,
                    "file": h.chunk.file_name,
                    "section": h.chunk.section,
                    "topic": h.chunk.topic,
                    "score": h.score,
                    "vector_score": h.vector_score,
                    "bm25_score": h.bm25_score,
                }
                for h in relevant_hits
            ],
        }


# Singleton service instance
rag_service = RAGService()
