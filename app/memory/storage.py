import contextlib
import json
import logging
import sqlite3

from app.config import settings
from app.memory.models import MemoryRecord

logger = logging.getLogger(__name__)


class MemoryStorage:
    """Manages persistent memory records in SQLite, strictly partitioned by
    session_id.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = str(db_path or getattr(settings, "MEMORY_DB_PATH", "memory.db"))
        self._memory_conn = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(self.db_path)
            self._memory_conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database and create tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS enterprise_memories (
                    memory_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
                """
            )
            # Create an index on session_id for fast isolated retrieval
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_id "
                "ON enterprise_memories (session_id)"
            )
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        if self._memory_conn:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_memory(self, record: MemoryRecord) -> None:
        """Add a new memory record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO enterprise_memories
                (memory_id, session_id, content, importance_score, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.memory_id,
                    record.session_id,
                    record.content,
                    record.importance_score,
                    record.created_at.isoformat(),
                    json.dumps(record.metadata),
                ),
            )
            conn.commit()
            logger.info(
                "Stored memory %s for session %s", record.memory_id, record.session_id
            )

    def get_memories_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[MemoryRecord]:
        """Retrieve memories isolated to a specific session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM enterprise_memories
                WHERE session_id = ?
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()

        records = []
        for row in rows:
            meta = {}
            with contextlib.suppress(Exception):
                meta = json.loads(row["metadata"])

            records.append(
                MemoryRecord(
                    memory_id=row["memory_id"],
                    session_id=row["session_id"],
                    content=row["content"],
                    importance_score=row["importance_score"],
                    created_at=row["created_at"],
                    metadata=meta,
                )
            )
        return records

    def delete_memories_for_session(self, session_id: str) -> None:
        """Delete all memories for a specific session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM enterprise_memories WHERE session_id = ?", (session_id,)
            )
            conn.commit()
            logger.info("Deleted all memories for session %s", session_id)

    def delete_memory_by_id(self, memory_id: str) -> bool:
        """Delete a single memory record by ID. Returns True if found and deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM enterprise_memories WHERE memory_id = ?", (memory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_all_memories(self, limit: int = 500, offset: int = 0) -> list[MemoryRecord]:
        """Retrieve all memories across sessions (for admin inspection)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM enterprise_memories
                ORDER BY importance_score DESC, created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()

        records = []
        for row in rows:
            meta = {}
            with contextlib.suppress(Exception):
                meta = json.loads(row["metadata"])
            records.append(
                MemoryRecord(
                    memory_id=row["memory_id"],
                    session_id=row["session_id"],
                    content=row["content"],
                    importance_score=row["importance_score"],
                    created_at=row["created_at"],
                    metadata=meta,
                )
            )
        return records

    def delete_all_memories(self) -> int:
        """Delete every memory record. Returns count of deleted rows."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM enterprise_memories")
            conn.commit()
            deleted = cursor.rowcount
            logger.info("Deleted all %d memories", deleted)
            return deleted

    def count_memories(self) -> int:
        """Return total memory record count."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM enterprise_memories")
            return cursor.fetchone()[0]

    def count_by_session(self) -> dict[str, int]:
        """Return memory count grouped by session_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, COUNT(*) as cnt FROM enterprise_memories "
                "GROUP BY session_id"
            )
            return {row["session_id"]: row["cnt"] for row in cursor.fetchall()}
