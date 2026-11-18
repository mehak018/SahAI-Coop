"""High-level RAG Retriever wrapping HybridVectorStore."""

from typing import List, Optional, Tuple
from app.rag.vector_store import HybridVectorStore, SearchHit


class RAGRetriever:
    """Retrieves top-k relevant knowledge chunks for a user query."""

    def __init__(self, store: HybridVectorStore, default_top_k: int = 4):
        self.store = store
        self.default_top_k = default_top_k

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        topic_filter: Optional[str] = None,
    ) -> Tuple[List[SearchHit], float]:
        k = top_k or self.default_top_k
        return self.store.search(query=query, top_k=k, topic_filter=topic_filter)
