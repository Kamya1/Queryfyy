import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseManager:
    """SQLite-backed storage for documents, questions, and analytics."""

    def __init__(self, db_path: str = "queryfy.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_value(row, key):
        return row[key]

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT,
                    uploaded_at TEXT NOT NULL,
                    text_length INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    difficulty TEXT,
                    question_text TEXT NOT NULL,
                    answer TEXT,
                    explanation TEXT,
                    source_chunk TEXT,
                    relevance_score REAL,
                    context_coverage REAL,
                    difficulty_score REAL,
                    confidence_score REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def store_document(self, doc_id: str, filename: str, file_type: str, text_length: int, chunk_count: int, metadata: Optional[Dict] = None):
        metadata = metadata or {}
        conn = self._get_connection()
        try:
            values = (
                doc_id,
                filename,
                file_type,
                datetime.utcnow().isoformat(),
                text_length,
                chunk_count,
                json.dumps(metadata),
            )
            conn.execute(
                "INSERT OR REPLACE INTO documents (id, filename, file_type, uploaded_at, text_length, chunk_count, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                values,
            )
            conn.commit()
        finally:
            conn.close()

    def store_question(self, document_id: str, question_type: str, difficulty: str, question_text: str, answer: str, explanation: str, source_chunk: str, metrics: Dict):
        conn = self._get_connection()
        try:
            values = (
                document_id,
                question_type,
                difficulty,
                question_text,
                answer,
                explanation,
                source_chunk,
                metrics.get("relevance_score", 0),
                metrics.get("context_coverage", 0),
                metrics.get("difficulty_score", 0),
                metrics.get("confidence_score", 0),
                datetime.utcnow().isoformat(),
            )
            conn.execute(
                """
                INSERT INTO questions (
                    document_id, question_type, difficulty, question_text, answer, explanation,
                    source_chunk, relevance_score, context_coverage, difficulty_score, confidence_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            conn.commit()
        finally:
            conn.close()

    def get_analytics(self) -> Dict:
        conn = self._get_connection()
        try:
            doc_count = self._row_value(conn.execute("SELECT COUNT(*) AS count FROM documents").fetchone(), "count")
            question_count = self._row_value(conn.execute("SELECT COUNT(*) AS count FROM questions").fetchone(), "count")
            difficulty_rows = conn.execute(
                "SELECT difficulty, COUNT(*) AS count FROM questions GROUP BY difficulty"
            ).fetchall()
            difficulty_distribution = {self._row_value(row, "difficulty") or "Unknown": self._row_value(row, "count") for row in difficulty_rows}
            question_type_rows = conn.execute(
                "SELECT question_type, COUNT(*) AS count FROM questions GROUP BY question_type"
            ).fetchall()
            topic_distribution = {self._row_value(row, "question_type"): self._row_value(row, "count") for row in question_type_rows}
            return {
                "documents_processed": doc_count,
                "questions_generated": question_count,
                "difficulty_distribution": difficulty_distribution,
                "topic_coverage": topic_distribution,
            }
        finally:
            conn.close()
