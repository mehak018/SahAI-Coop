import logging
from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings

logger = logging.getLogger("sahai_coop.rag_hook")


class AIRAGHook:
    """
    Integration Hook for AI/ML RAG (Retrieval-Augmented Generation) Pipeline.
    
    Prepared specifically for the AI Engine teammate (Member 3 / `ai-engine/`).
    When AI_RAG_ENABLED=True, queries are forwarded to the AI microservice.
    If disabled or if the AI engine is unreachable, the system automatically falls back
    to the MySQL `sample_responses` knowledge base.
    """

    @classmethod
    async def query_rag_engine(
        cls,
        query: str,
        language: str = "en",
        history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously queries the AI/RAG engine endpoint.
        
        Expected response format from AI service:
        {
            "answer": "Generated answer text...",
            "topic": "crop_insurance",
            "source_reference": "[{\"title\": \"PMFBY Portal\", \"url\": \"https://pmfby.gov.in\"}]",
            "confidence": 0.92
        }
        """
        if not settings.AI_RAG_ENABLED:
            return None

        try:
            async with httpx.AsyncClient(timeout=settings.AI_RAG_TIMEOUT_SECONDS) as client:
                payload: Dict[str, Any] = {
                    "query": query,
                    "language": language
                }
                if history:
                    payload["history"] = history
                response = await client.post(settings.AI_RAG_SERVICE_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "answer": data.get("answer"),
                        "topic": data.get("topic", "General Cooperative Assistance"),
                        "source_reference": data.get("source_reference", "Official Cooperative Database")
                    }
                else:
                    logger.warning(f"RAG service returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Failed to reach AI/RAG service at {settings.AI_RAG_SERVICE_URL}: {e}")

        return None
