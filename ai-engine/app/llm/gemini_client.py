"""
Google Gemini API client using the official `google-genai` SDK.
Handles both grounded chat generation and dense text embeddings with
automatic model fallback and clear error diagnostics.
"""

import logging
from typing import Dict, List, Optional

from app.config import settings

logger = logging.getLogger("sahai_coop.ai.gemini")

EMBEDDING_CANDIDATES = [
    "gemini-embedding-001",
    "text-embedding-004",
]

GENERATION_FALLBACKS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


class GeminiClient:
    """Wrapper around Google GenAI SDK for embeddings and chat generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key if api_key is not None else settings.GEMINI_API_KEY).strip()
        self._client = None
        self._active_embedding_model: Optional[str] = None
        self.active_generation_model: Optional[str] = None
        self.last_error: Optional[str] = None
        self._init_client()

    def _init_client(self) -> None:
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning(
                "GEMINI_API_KEY is not configured. Running in BM25 retrieval-only fallback mode. "
                "Add your Gemini API key in ai-engine/.env for full AI answers and vector embeddings."
            )
            self._client = None
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized Gemini client (model={settings.GEMINI_MODEL}).")
        except ImportError:
            self.last_error = "google-genai package is not installed"
            logger.error("google-genai package is not installed. Run: pip install -r requirements.txt")
            self._client = None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._client = None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def embed_texts(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
        batch_size: int = 20,
    ) -> Optional[List[List[float]]]:
        """Generate vector embeddings for a list of texts in batches."""
        if not self._client or not texts:
            return None

        from google.genai import types

        candidates: List[str] = []
        if self._active_embedding_model:
            candidates.append(self._active_embedding_model)
        if settings.GEMINI_EMBEDDING_MODEL not in candidates:
            candidates.append(settings.GEMINI_EMBEDDING_MODEL)
        for m in EMBEDDING_CANDIDATES:
            if m not in candidates:
                candidates.append(m)

        for model_name in candidates:
            try:
                all_vectors: List[List[float]] = []
                for start in range(0, len(texts), batch_size):
                    batch = texts[start:start + batch_size]
                    resp = self._client.models.embed_content(
                        model=model_name,
                        contents=batch,
                        config=types.EmbedContentConfig(task_type=task_type),
                    )
                    if not resp or not resp.embeddings:
                        raise ValueError("Empty embedding response")
                    for emb in resp.embeddings:
                        all_vectors.append(list(emb.values))
                self._active_embedding_model = model_name
                return all_vectors
            except Exception as e:
                logger.warning(f"Embedding failed with model '{model_name}': {e}")

        logger.warning("All Gemini embedding models failed; falling back to BM25 retrieval.")
        return None

    def embed_query(self, query: str) -> Optional[List[float]]:
        """Generate an embedding vector for a single search query."""
        vectors = self.embed_texts([query], task_type="RETRIEVAL_QUERY", batch_size=1)
        if vectors and len(vectors) == 1:
            return vectors[0]
        return None

    def _build_clean_contents(
        self,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]],
    ):
        """Build strictly alternating user/model turns ending with the current user prompt."""
        from google.genai import types

        turns: List[tuple[str, str]] = []
        if history:
            for msg in history[-6:]:
                sender = (msg.get("sender") or msg.get("role") or "user").lower()
                text = (msg.get("content") or "").strip()
                if not text:
                    continue
                role = "model" if sender in ("bot", "assistant", "model") else "user"
                # Must start with a 'user' turn
                if not turns and role == "model":
                    continue
                # Merge consecutive same-role messages so roles strictly alternate
                if turns and turns[-1][0] == role:
                    prev_role, prev_text = turns[-1]
                    turns[-1] = (prev_role, f"{prev_text}\n{text}")
                else:
                    turns.append((role, text))

        # Ensure history does not end on 'user' right before our new 'user' turn
        if turns and turns[-1][0] == "user":
            turns.pop()

        turns.append(("user", user_prompt))

        return [
            types.Content(role=role, parts=[types.Part.from_text(text=text)])
            for role, text in turns
        ]

    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Optional[str]:
        """Generate a grounded multilingual chatbot answer using Gemini."""
        if not self._client:
            self.last_error = "GEMINI_API_KEY not configured"
            return None

        from google.genai import types

        contents = self._build_clean_contents(user_prompt, history)

        model_candidates: List[str] = []
        if self.active_generation_model:
            model_candidates.append(self.active_generation_model)
        if settings.GEMINI_MODEL not in model_candidates:
            model_candidates.append(settings.GEMINI_MODEL)
        if settings.GEMINI_FALLBACK_MODEL not in model_candidates:
            model_candidates.append(settings.GEMINI_FALLBACK_MODEL)
        for m in GENERATION_FALLBACKS:
            if m not in model_candidates:
                model_candidates.append(m)

        last_err: Optional[str] = None
        for model_name in model_candidates:
            # Attempt 1: Standard GenerateContentConfig with system_instruction
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=settings.GEMINI_TEMPERATURE,
                        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                    ),
                )
                if response and response.text:
                    self.active_generation_model = model_name
                    self.last_error = None
                    return response.text.strip()
            except Exception as e:
                last_err = f"{model_name}: {e}"
                logger.warning(f"Gemini generation failed with model '{model_name}': {e}")

                # Attempt 2: Retry same model with system prompt folded into user text
                # (handles API versions/keys that reject system_instruction or multi-turn Content)
                try:
                    merged_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=merged_prompt,
                        config=types.GenerateContentConfig(
                            temperature=settings.GEMINI_TEMPERATURE,
                            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                        ),
                    )
                    if response and response.text:
                        self.active_generation_model = model_name
                        self.last_error = None
                        return response.text.strip()
                except Exception as e2:
                    last_err = f"{model_name}: {e2}"
                    logger.warning(f"Gemini fallback prompt failed on '{model_name}': {e2}")

        self.last_error = last_err or "Gemini returned empty response"

        # Auto-discover any available Gemini Flash model from the API as a last resort
        try:
            discovered = []
            for m in self._client.models.list():
                name = getattr(m, "name", "") or ""
                short = name.replace("models/", "")
                if "gemini" in short and "flash" in short and "embedding" not in short:
                    if short not in model_candidates:
                        discovered.append(short)
            for model_name in discovered[:4]:
                try:
                    merged_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=merged_prompt,
                        config=types.GenerateContentConfig(
                            temperature=settings.GEMINI_TEMPERATURE,
                            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                        ),
                    )
                    if response and response.text:
                        self.active_generation_model = model_name
                        self.last_error = None
                        return response.text.strip()
                except Exception as e3:
                    self.last_error = f"{model_name}: {e3}"
        except Exception:
            pass

        return None
