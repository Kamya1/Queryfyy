from __future__ import annotations

import hashlib
from functools import lru_cache
from math import sqrt
from typing import List


class EmbeddingService:
    """Reusable embedding service with caching support."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_dimension = 384

    def _load_model(self):
        if self.model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except Exception:
            return
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as exc:
            print(f"Embedding model failed to load: {exc}")
            self.model = None

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @lru_cache(maxsize=1024)
    def _cached_encode(self, text_hash: str, text: str):
        self._load_model()
        if self.model is None:
            # Deterministic fallback keeps the app usable when sentence-transformers
            # is unavailable, while making the missing dependency obvious in logs.
            vector = [0.0] * self.embedding_dimension
            for token in text.lower().split():
                idx = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.embedding_dimension
                vector[idx] += 1.0
            norm = sqrt(sum(value * value for value in vector))
            return [value / norm for value in vector] if norm else vector
        vector = self.model.encode(text, normalize_embeddings=True)
        if hasattr(vector, "tolist"):
            return vector.tolist()
        return list(vector)

    def encode_text(self, text: str):
        text_hash = self._hash_text(text)
        return self._cached_encode(text_hash, text)

    def encode_texts(self, texts: List[str]) -> List:
        return [self.encode_text(text) for text in texts]

    @staticmethod
    def cosine_similarity(a, b) -> float:
        a_values = a.tolist() if hasattr(a, "tolist") else list(a)
        b_values = b.tolist() if hasattr(b, "tolist") else list(b)
        denom = sqrt(sum(value * value for value in a_values)) * sqrt(sum(value * value for value in b_values))
        if denom == 0:
            return 0.0
        return float(sum(x * y for x, y in zip(a_values, b_values)) / denom)
