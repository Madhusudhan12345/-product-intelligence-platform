import json
import os
import sqlite3
import threading
import time
from typing import List, Optional

from app.config import settings


class MemoryStore:
    """
    Long-term memory: persists past Q&A pairs plus distilled 'insights'
    (short factual statements the analyst agent has already derived),
    so future queries don't have to re-derive the same conclusions from scratch.
    """

    def __init__(self):
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        with self._lock:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS query_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    answer TEXT,
                    agent_trace TEXT,
                    evidence_source_ids TEXT,
                    created_at REAL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT,
                    source_question TEXT,
                    created_at REAL
                )
                """
            )
            self.conn.commit()

    def log_query(self, question: str, answer: str, agent_trace: list, evidence_source_ids: list):
        with self._lock:
            self.conn.execute(
                "INSERT INTO query_log (question, answer, agent_trace, evidence_source_ids, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (question, answer, json.dumps(agent_trace), json.dumps(evidence_source_ids), time.time()),
            )
            self.conn.commit()

    def add_insight(self, statement: str, source_question: str):
        with self._lock:
            self.conn.execute(
                "INSERT INTO insights (statement, source_question, created_at) VALUES (?, ?, ?)",
                (statement, source_question, time.time()),
            )
            self.conn.commit()

    def get_relevant_insights(self, keywords: List[str], limit: int = 5) -> List[str]:
        """Naive keyword match over stored insights. Swap for embedding search if needed."""
        if not keywords:
            return []
        with self._lock:
            cur = self.conn.execute("SELECT statement FROM insights ORDER BY created_at DESC LIMIT 200")
            rows = [r[0] for r in cur.fetchall()]
        matched = [r for r in rows if any(k.lower() in r.lower() for k in keywords)]
        return matched[:limit]

    def recent_queries(self, limit: int = 20) -> List[dict]:
        with self._lock:
            cur = self.conn.execute(
                "SELECT question, answer, created_at FROM query_log ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            return [{"question": q, "answer": a, "created_at": t} for q, a, t in cur.fetchall()]


memory_store = MemoryStore()
