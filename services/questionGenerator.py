import json
import os
import re
from typing import Dict, List, Optional

from services.embeddingService import EmbeddingService
from services.evaluationService import EvaluationService


class QuestionGenerator:
    """Generates context-aware questions with explanations and metadata."""

    def __init__(self, embedding_service: EmbeddingService, evaluation_service: EvaluationService, llm_client):
        self.embedding_service = embedding_service
        self.evaluation_service = evaluation_service
        self.llm_client = llm_client

    def _build_prompt(self, question_type: str, num_questions: int, difficulty: str, context_chunks: List[str], existing_questions: List[str] = None, attempt: int = 1) -> str:
        context = "\n\n".join(
    f"Chunk {i+1}: {chunk[:500]}"
    for i, chunk in enumerate(context_chunks[:3])
)
        existing_questions = existing_questions or []
        avoid_block = "\n".join(f"- {question}" for question in existing_questions[-50:])
        avoid_instruction = f"\nAlready generated questions to avoid:\n{avoid_block}\n" if avoid_block else ""
        return f"""
You are an expert assessment designer. Use ONLY the provided context.
Do NOT invent facts. Do NOT mention the source document directly.
Create exactly {num_questions} {question_type} questions for {difficulty} difficulty.
This is generation attempt {attempt}. Produce new questions that test different concepts from prior attempts.
Maintain topic diversity across the provided chunks and keep the requested difficulty level.
Use Bloom's Taxonomy:
- Easy: remember, define, identify, recall, recognize
- Medium: explain, apply, compare, classify, summarize
- Hard: analyze, evaluate, justify, design, synthesize
Return valid JSON only in this shape:
{{"questions": [
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer": "...",
    "explanation": "...",
    "difficulty": "{difficulty}",
    "source_excerpt": "short supporting excerpt copied or paraphrased from one chunk"
  }}
]}}
Each item must contain:
- question
- options (array for MCQ, empty array for others)
- answer
- explanation
- difficulty
- source_excerpt

Context:
{context}
{avoid_instruction}
"""

    def _parse_response(self, response_text: str) -> List[Dict]:
        cleaned = response_text.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "")
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.S)
        if match:
            cleaned = match.group(1)
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("questions"), list):
                return data["questions"]
        except Exception:
            pass

        # Fallback parser for numbered lists
        items = []
        pattern = r"\d+\.\s*(.*?)(?=\n\d+\.|\n\*\*Answer|$)"
        matches = re.findall(pattern, cleaned, flags=re.S)
        for match in matches:
            text = match.strip()
            if text:
                items.append({
                    "question": text,
                    "options": [],
                    "answer": "",
                    "explanation": "",
                    "difficulty": "Medium",
                    "source_excerpt": ""
                })
        return items

    def _dedupe_questions(self, questions: List[Dict], threshold: float = 0.88) -> List[Dict]:
        unique = []
        for question in questions:
            question_text = question.get("question", "")
            q_embedding = self.embedding_service.encode_text(question_text)
            is_duplicate = False
            for existing in unique:
                existing_text = existing.get("question", "")
                existing_embedding = self.embedding_service.encode_text(existing_text)
                similarity = self.embedding_service.cosine_similarity(q_embedding, existing_embedding)
                if similarity >= threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique.append(question)
        return unique

    def _is_duplicate_against(self, question_text: str, existing: List[Dict], threshold: float = 0.88) -> bool:
        if not question_text:
            return True
        normalized = re.sub(r"\s+", " ", question_text.strip().lower())
        for item in existing:
            existing_text = item.get("question", "")
            existing_normalized = re.sub(r"\s+", " ", existing_text.strip().lower())
            if normalized == existing_normalized:
                return True

        q_embedding = self.embedding_service.encode_text(question_text)
        for item in existing:
            existing_embedding = self.embedding_service.encode_text(item.get("question", ""))
            similarity = self.embedding_service.cosine_similarity(q_embedding, existing_embedding)
            if similarity >= threshold:
                return True
        return False

    def _score_items(self, items: List[Dict], context_chunks: List[str], difficulty: str) -> List[Dict]:
        valid = []
        for item in items:
            question = (item.get("question") or "").strip()
            if not question:
                continue
            item["question"] = question
            item["difficulty"] = item.get("difficulty") or difficulty
            score = self.evaluation_service.evaluate_question(
                question,
                item.get("answer", ""),
                item.get("explanation", ""),
                context_chunks
            )
            if not item.get("source_excerpt"):
                item["source_excerpt"] = context_chunks[0][:500]
            item.update(score)
            valid.append(item)
        return valid

    @staticmethod
    def _rotate_context(context_chunks: List[str], attempt: int) -> List[str]:
        if not context_chunks:
            return []

        offset = (attempt - 1) % len(context_chunks)
        return context_chunks[offset:] + context_chunks[:offset]

    def generate(
        self,
        context_chunks: List[str],
        question_type: str,
        num_questions: int,
        difficulty: str = "Medium"
    ) -> List[Dict]:

        if not context_chunks:
            return []

        collected: List[Dict] = []
        hosted_runtime = bool(os.getenv("VERCEL") or os.getenv("RENDER"))
        default_attempts = "2" if hosted_runtime else str(max(4, min(10, num_questions + 2)))
        max_attempts = int(os.getenv("QUESTION_MAX_ATTEMPTS", default_attempts))

        for attempt in range(1, max_attempts + 1):

            missing = num_questions - len(collected)

            if missing <= 0:
                break

            request_count = min(
                num_questions,
                max(missing + 3, int(missing * 1.5))
            )

            attempt_context = self._rotate_context(
                context_chunks,
                attempt
            )

            # Prevent Groq token overflow
            attempt_context = attempt_context[:3]
            attempt_context = [
                chunk[:500]
                for chunk in attempt_context
            ]

            prompt = self._build_prompt(
                question_type,
                request_count,
                difficulty,
                attempt_context,
                existing_questions=[
                    item.get("question", "")
                    for item in collected
                ],
                attempt=attempt,
            )

            print("CHUNKS SENT:", len(attempt_context))
            print("PROMPT LENGTH:", len(prompt))

            response = self.llm_client(prompt)

            if not response:
                continue

            parsed = self._parse_response(response)

            scored = self._score_items(
                parsed,
                attempt_context,
                difficulty
            )

            for item in self._dedupe_questions(scored):

                if len(collected) >= num_questions:
                    break

                if self._is_duplicate_against(
                    item.get("question", ""),
                    collected
                ):
                    continue

                collected.append(item)

        return collected[:num_questions]
