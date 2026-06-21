import math
import re
from typing import Dict, List

from services.embeddingService import EmbeddingService


class EvaluationService:
    """Heuristic quality evaluation for generated questions."""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def evaluate_question(self, question: str, answer: str, explanation: str, context_chunks: List[str]) -> Dict[str, float]:
        context_text = " ".join(context_chunks)
        question_embedding = self.embedding_service.encode_text(question)
        context_embedding = self.embedding_service.encode_text(context_text)
        relevance = self.embedding_service.cosine_similarity(question_embedding, context_embedding)

        question_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", question.lower()))
        context_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", context_text.lower()))
        overlap = len(question_words & context_words)
        coverage = min(1.0, overlap / max(1, len(question_words)))

        bloom_weights = {
            "define": 0.25, "identify": 0.25, "recall": 0.25, "list": 0.25,
            "explain": 0.55, "apply": 0.55, "compare": 0.6, "classify": 0.55,
            "analyze": 0.85, "evaluate": 0.9, "justify": 0.9, "design": 0.95, "synthesize": 0.95,
        }
        lower_question = question.lower()
        difficulty_score = min(1.0, 0.25 + min(0.45, len(question.split()) / 50.0))
        for term, weight in bloom_weights.items():
            if term in lower_question:
                difficulty_score = max(difficulty_score, weight)

        confidence = min(1.0, 0.5 * relevance + 0.3 * coverage + 0.2 * (1.0 if answer.strip() else 0.0))

        return {
            "relevance_score": round(float(relevance), 3),
            "context_coverage": round(float(coverage), 3),
            "difficulty_score": round(float(difficulty_score), 3),
            "confidence_score": round(float(confidence), 3),
        }
