import sqlite3
import uuid
from datetime import datetime


class EpisodicStore:
    def __init__(self, db_path: str = "memory_bus.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id         TEXT PRIMARY KEY,
                content    TEXT NOT NULL,
                source     TEXT DEFAULT 'unknown',
                confidence REAL DEFAULT 1.0,
                tags       TEXT DEFAULT '',
                written_at TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_written_at ON episodic_memory(written_at)"
        )
        self._conn.commit()

    def write(self, content: str, source: str = "unknown", confidence: float = 1.0, tags=None) -> str:
        if tags is None:
            tags = []
        memory_id = f"ep_{uuid.uuid4().hex[:8]}"
        written_at = datetime.utcnow().isoformat()
        tags_str = ",".join(tags) if isinstance(tags, list) else str(tags)
        self._conn.execute(
            """
            INSERT INTO episodic_memory (id, content, source, confidence, tags, written_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (memory_id, content, source, confidence, tags_str, written_at),
        )
        self._conn.commit()
        return memory_id

    def recall_by_range(self, since: str, until: str) -> list:
        cursor = self._conn.execute(
            """
            SELECT id, content, source, confidence, tags, written_at
            FROM episodic_memory
            WHERE written_at BETWEEN ? AND ?
            ORDER BY written_at ASC
            """,
            (since, until),
        )
        return [dict(row) for row in cursor.fetchall()]

    def forget(self, memory_id: str) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM episodic_memory WHERE id = ?", (memory_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0
