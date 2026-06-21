from typing import Dict, List, Optional

from vectorstore.vector_store import VectorStore


class RetrievalService:
    """Retrieves relevant chunks for context-aware generation."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(self, query_text: str, top_k: int = 5, document_id: Optional[str] = None) -> List[str]:
        where = {"document_id": document_id} if document_id else None
        results = self.vector_store.query(query_text, top_k=top_k, where=where)
        return [item[1]["text"] for item in results if item[1].get("text")]

    def retrieve_with_metadata(self, query_text: str, top_k: int = 5, document_id: Optional[str] = None) -> List[Dict]:
        where = {"document_id": document_id} if document_id else None
        return [
            {"score": round(float(score), 3), **doc}
            for score, doc in self.vector_store.query(query_text, top_k=top_k, where=where)
            if doc.get("text")
        ]
