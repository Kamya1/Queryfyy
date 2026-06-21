from __future__ import annotations

import os
import re
import tempfile
from typing import Dict, List, Optional

from services.embeddingService import EmbeddingService


class VectorStore:
    """Semantic vector store with ChromaDB persistence and in-memory fallback."""

    def __init__(self, embedding_service: EmbeddingService, persist_directory: Optional[str] = None, collection_name: str = "queryfy_chunks"):
        self.embedding_service = embedding_service
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_PERSIST_DIR",
            os.path.join(tempfile.gettempdir(), "queryfy_chroma") if os.getenv("VERCEL") else "vectorstore/chroma",
        )
        self.documents: List[Dict] = []
        self.chunk_embeddings: List = []
        self.collection = None
        self._init_chroma(collection_name)

    def _init_chroma(self, collection_name: str):
        try:
            import chromadb
        except Exception:
            return
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = client.get_or_create_collection(name=collection_name)
        except Exception as exc:
            print(f"ChromaDB disabled, using in-memory vector store: {exc}")
            self.collection = None

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\u00a0", " ", text or "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
        if not text:
            return []

        chunk_size = max(100, int(chunk_size))
        overlap = max(0, min(int(overlap), chunk_size // 2))
        text = cls.clean_text(text)
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        sentences = []
        for paragraph in paragraphs:
            sentences.extend([s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()])
        if not sentences:
            sentences = [text]

        chunks = []
        current_words: List[str] = []
        for sentence in sentences:
            words = sentence.split()
            if current_words and len(current_words) + len(words) > chunk_size:
                chunks.append(" ".join(current_words))
                current_words = current_words[-overlap:] if overlap else []
            current_words.extend(words)

            while len(current_words) >= chunk_size:
                chunks.append(" ".join(current_words[:chunk_size]))
                current_words = current_words[chunk_size - overlap:] if overlap else []

        if current_words:
            chunks.append(" ".join(current_words))
        return [chunk for chunk in chunks if len(chunk.split()) >= 20] or chunks

    def add_document(self, doc_id: str, filename: str, text: str, metadata: Optional[Dict] = None, chunk_size: int = 500, overlap: int = 80) -> List[Dict]:
        metadata = metadata or {}
        chunks = self.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        stored_chunks = []
        for idx, chunk in enumerate(chunks):
            vector = self.embedding_service.encode_text(chunk)
            chunk_doc = {
                "id": f"{doc_id}::{idx}",
                "document_id": doc_id,
                "filename": filename,
                "chunk_index": idx,
                "text": chunk,
                "metadata": metadata,
            }
            self.documents.append(chunk_doc)
            self.chunk_embeddings.append(vector)
            stored_chunks.append(chunk_doc)

            if self.collection is not None:
                try:
                    chroma_metadata = {
                        "document_id": doc_id,
                        "filename": filename,
                        "chunk_index": idx,
                        **{k: str(v) for k, v in metadata.items()},
                    }
                    self.collection.upsert(
                        ids=[chunk_doc["id"]],
                        documents=[chunk],
                        embeddings=[vector.tolist() if hasattr(vector, "tolist") else list(vector)],
                        metadatas=[chroma_metadata],
                    )
                except Exception as exc:
                    print(f"ChromaDB upsert failed: {exc}")
                    self.collection = None
        return stored_chunks

    def query(self, query_text: str, top_k: int = 5, where: Optional[Dict] = None):
        query_vector = self.embedding_service.encode_text(query_text)
        if self.collection is not None:
            try:
                results = self.collection.query(
                    query_embeddings=[query_vector.tolist() if hasattr(query_vector, "tolist") else list(query_vector)],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"],
                )
                ids = results.get("ids", [[]])[0]
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                ranked = []
                for idx, chunk_id in enumerate(ids):
                    metadata = metadatas[idx] or {}
                    similarity = 1.0 - float(distances[idx] or 0.0)
                    ranked.append((similarity, {
                        "id": chunk_id,
                        "document_id": metadata.get("document_id"),
                        "filename": metadata.get("filename"),
                        "chunk_index": metadata.get("chunk_index"),
                        "text": documents[idx],
                        "metadata": metadata,
                    }))
                return ranked
            except Exception as exc:
                print(f"ChromaDB query failed, using in-memory search: {exc}")

        if not self.documents:
            return []
        scores = []
        for idx, doc in enumerate(self.documents):
            sim = self.embedding_service.cosine_similarity(query_vector, self.chunk_embeddings[idx])
            if where and any(doc.get(key) != value and doc.get("metadata", {}).get(key) != value for key, value in where.items()):
                continue
            scores.append((sim, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]

    def count(self) -> int:
        return len(self.documents)

    def get_all_chunks(self) -> List[Dict]:
        return self.documents
