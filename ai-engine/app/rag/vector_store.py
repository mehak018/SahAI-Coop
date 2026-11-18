"""
Lightweight Hybrid Vector + BM25 Knowledge Store.

Combines:
1. Dense Vector Search (Gemini API Embeddings + NumPy cosine similarity, persisted to disk JSON)
2. Lexical BM25Okapi Search (pure Python, Unicode/Devanagari-aware with cross-lingual expansion)
3. Reciprocal Rank Fusion (RRF) for high-recall, high-precision retrieval without heavy ML dependencies.
"""

from collections import Counter
from dataclasses import dataclass
import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.llm.gemini_client import GeminiClient
from app.multilingual.language_utils import expand_query_for_bm25, tokenize_multilingual
from app.rag.loader import DocumentChunk, compute_kb_fingerprint, load_knowledge_base

logger = logging.getLogger("sahai_coop.ai.vector_store")


@dataclass
class SearchHit:
    chunk: DocumentChunk
    score: float
    bm25_score: float
    vector_score: float


class BM25Index:
    """Lightweight, Unicode-friendly BM25Okapi implementation in pure Python."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: Dict[str, int] = {}
        self.doc_lens: List[int] = []
        self.term_freqs: List[Counter] = []
        self.avg_dl: float = 0.0
        self.num_docs: int = 0

    def build(self, documents: List[str]) -> None:
        self.doc_freqs = {}
        self.doc_lens = []
        self.term_freqs = []
        self.num_docs = len(documents)

        total_len = 0
        for doc in documents:
            tokens = tokenize_multilingual(doc, remove_stopwords=True)
            tf = Counter(tokens)
            self.term_freqs.append(tf)
            self.doc_lens.append(len(tokens))
            total_len += len(tokens)
            for term in tf.keys():
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_dl = (total_len / self.num_docs) if self.num_docs > 0 else 1.0

    def score(self, query: str) -> List[float]:
        if self.num_docs == 0:
            return []
        expanded = expand_query_for_bm25(query)
        q_tokens = tokenize_multilingual(expanded, remove_stopwords=True)
        if not q_tokens:
            return [0.0] * self.num_docs

        scores = [0.0] * self.num_docs
        for term in q_tokens:
            df = self.doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))
            for idx in range(self.num_docs):
                tf = self.term_freqs[idx].get(term, 0)
                if tf == 0:
                    continue
                dl = self.doc_lens[idx]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_dl))
                scores[idx] += idf * ((tf * (self.k1 + 1.0)) / denom)
        return scores


class HybridVectorStore:
    """
    Hybrid Vector (Gemini Embeddings + NumPy) + BM25 retriever with disk caching.
    """

    def __init__(
        self,
        kb_dir: Path,
        index_path: Path,
        gemini_client: GeminiClient,
        chunk_size: int = 900,
        chunk_overlap: int = 150,
    ):
        self.kb_dir = Path(kb_dir)
        self.index_path = Path(index_path)
        self.gemini_client = gemini_client
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.chunks: List[DocumentChunk] = []
        self.documents: List[Dict[str, str]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.bm25 = BM25Index()
        self.kb_fingerprint: str = ""
        self.vector_enabled: bool = False

    def initialize(self, force_rebuild: bool = False) -> Dict[str, object]:
        """Load cached index if unchanged, otherwise chunk & embed the knowledge base."""
        current_fp = compute_kb_fingerprint(self.kb_dir)

        if not force_rebuild and self._try_load_cache(current_fp):
            # If cache had no vectors, try upgrading it if Gemini API key is now available
            if not self.vector_enabled and self.gemini_client.is_configured and self.chunks:
                logger.info("Gemini API key detected; computing embeddings to upgrade cached index...")
                self._compute_and_save_embeddings(current_fp)
            return self.get_stats()

        logger.info("Building hybrid RAG index from knowledge base...")
        self.chunks, self.documents = load_knowledge_base(
            self.kb_dir,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        self.kb_fingerprint = current_fp
        self._build_bm25()
        self._compute_and_save_embeddings(current_fp)
        return self.get_stats()

    def _build_bm25(self) -> None:
        corpus = [
            f"{c.topic} {c.section} {c.keywords} {c.content}"
            for c in self.chunks
        ]
        self.bm25.build(corpus)

    def _compute_and_save_embeddings(self, fingerprint: str) -> None:
        self.embeddings = None
        self.vector_enabled = False

        if self.chunks and self.gemini_client.is_configured:
            texts = [
                f"Topic: {c.topic}\nSection: {c.section}\nKeywords: {c.keywords}\n{c.content}"
                for c in self.chunks
            ]
            vectors = self.gemini_client.embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
            if vectors and len(vectors) == len(self.chunks):
                mat = np.array(vectors, dtype=np.float32)
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                self.embeddings = mat / norms
                self.vector_enabled = True
                logger.info(f"Generated Gemini embeddings: shape={self.embeddings.shape}")

        self._save_cache(fingerprint)

    def _save_cache(self, fingerprint: str) -> None:
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "fingerprint": fingerprint,
                "documents": self.documents,
                "chunks": [c.to_dict() for c in self.chunks],
                "embeddings": self.embeddings.tolist() if self.embeddings is not None else None,
            }
            self.index_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            logger.info(f"Saved RAG index cache to {self.index_path}")
        except Exception as e:
            logger.warning(f"Could not save RAG cache: {e}")

    def _try_load_cache(self, expected_fingerprint: str) -> bool:
        if not self.index_path.exists():
            return False
        try:
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            if data.get("fingerprint") != expected_fingerprint:
                return False

            self.chunks = [DocumentChunk.from_dict(c) for c in data.get("chunks", [])]
            self.documents = data.get("documents", [])
            self.kb_fingerprint = expected_fingerprint
            self._build_bm25()

            raw_emb = data.get("embeddings")
            if raw_emb and len(raw_emb) == len(self.chunks):
                self.embeddings = np.array(raw_emb, dtype=np.float32)
                self.vector_enabled = True
            else:
                self.embeddings = None
                self.vector_enabled = False

            logger.info(
                f"Loaded cached RAG index ({len(self.chunks)} chunks, vector_enabled={self.vector_enabled})."
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to load RAG cache, rebuilding: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 4,
        topic_filter: Optional[str] = None,
    ) -> Tuple[List[SearchHit], float]:
        """
        Execute Hybrid Vector + BM25 search with Reciprocal Rank Fusion (RRF).
        Returns (hits, overall_confidence in [0.0, 1.0]).
        """
        if not self.chunks or not query.strip():
            return [], 0.0

        n = len(self.chunks)
        bm25_scores = self.bm25.score(query)
        vector_scores = [0.0] * n
        used_vector = False

        if self.vector_enabled and self.embeddings is not None:
            q_vec = self.gemini_client.embed_query(query)
            if q_vec is not None:
                qv = np.array(q_vec, dtype=np.float32)
                q_norm = np.linalg.norm(qv)
                if q_norm > 0 and qv.shape[0] == self.embeddings.shape[1]:
                    qv = qv / q_norm
                    sims = self.embeddings @ qv
                    vector_scores = [float(s) for s in sims]
                    used_vector = True

        # Candidate indices (with optional topic filter)
        indices = [
            i for i in range(n)
            if not topic_filter or self.chunks[i].topic == topic_filter
        ]
        if not indices:
            indices = list(range(n))

        # Rank lists for RRF
        bm25_ranked = sorted(indices, key=lambda i: bm25_scores[i], reverse=True)
        vec_ranked = sorted(indices, key=lambda i: vector_scores[i], reverse=True) if used_vector else []

        rrf_k = 40.0
        combined: Dict[int, float] = {i: 0.0 for i in indices}

        max_bm25 = max((bm25_scores[i] for i in indices), default=0.0)
        for rank, idx in enumerate(bm25_ranked, start=1):
            if bm25_scores[idx] > 0:
                weight = 0.45 if used_vector else 1.0
                combined[idx] += weight * (1.0 / (rrf_k + rank))

        if used_vector:
            for rank, idx in enumerate(vec_ranked, start=1):
                if vector_scores[idx] > 0.25:
                    combined[idx] += 0.55 * (1.0 / (rrf_k + rank))

        # Sort by hybrid score (tie-break by vector then bm25)
        ranked_final = sorted(
            indices,
            key=lambda i: (combined[i], vector_scores[i], bm25_scores[i]),
            reverse=True,
        )

        hits: List[SearchHit] = []
        for idx in ranked_final[:top_k]:
            if combined[idx] <= 0 and vector_scores[idx] < 0.35:
                continue
            hits.append(
                SearchHit(
                    chunk=self.chunks[idx],
                    score=round(combined[idx], 5),
                    bm25_score=round(bm25_scores[idx], 4),
                    vector_score=round(vector_scores[idx], 4),
                )
            )

        # Estimate intuitive confidence score in [0.0, 1.0]
        if not hits:
            confidence = 0.0
        elif used_vector:
            top_vec = max(0.0, min(1.0, hits[0].vector_score))
            bm25_boost = min(0.18, (hits[0].bm25_score / (max_bm25 + 1e-6)) * 0.18) if max_bm25 > 0 else 0.0
            confidence = round(min(0.98, max(top_vec, top_vec * 0.85 + bm25_boost)), 2)
        else:
            # BM25-only heuristic confidence
            confidence = round(min(0.90, 0.35 + min(hits[0].bm25_score, 8.0) / 14.0), 2)

        return hits, confidence

    def get_stats(self) -> Dict[str, object]:
        return {
            "documents_indexed": len(self.documents),
            "chunks_indexed": len(self.chunks),
            "vector_embeddings_active": self.vector_enabled,
            "retrieval_mode": "hybrid_vector_bm25" if self.vector_enabled else "bm25_lexical",
        }
