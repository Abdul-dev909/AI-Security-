"""Memory management module for storing and retrieving memories.

DEPRECATED: This module is retained only for backward compatibility.
Please use app.memory.EnterpriseMemoryManager for new development.
"""

import datetime
import warnings
from typing import Any

from app.memory.manager import EnterpriseMemoryManager
from app.memory.models import MemoryRecord


class MemoryManager:
    """Manage memory storage and retrieval.

    DEPRECATED: This class acts as a thin adapter to EnterpriseMemoryManager
    to maintain backward compatibility with legacy code and tests.
    """

    def __init__(self) -> None:
        warnings.warn(
            "MemoryManager is deprecated and will be removed in Module 2. "
            "Use EnterpriseMemoryManager instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.enterprise = EnterpriseMemoryManager()
        self.legacy_session_id = "legacy_adapter_session"
        # Map memory_id -> updated_at for tracking update timestamps
        self._updated_at: dict[str, datetime.datetime] = {}

    def save_memory(self, memory: str) -> str:
        """Save a new memory to the database using the enterprise storage.

        Args:
            memory: The memory text to save. Must not be empty or None.

        Returns:
            str: The UUID of the newly inserted memory record.

        Raises:
            ValueError: If memory is None or an empty string.
        """
        # Reject None and empty string; whitespace-only strings are allowed.
        if memory is None or not isinstance(memory, str) or memory == "":
            raise ValueError("Memory must be a non-empty string")

        record = MemoryRecord(
            session_id=self.legacy_session_id,
            content=memory,
            importance_score=1.0,
        )
        self.enterprise.storage.add_memory(record)
        self._updated_at[record.memory_id] = record.created_at
        return record.memory_id

    def list_memories(self) -> list[dict[str, Any]]:
        """Retrieve all memories for the legacy session in ascending order."""
        records = self.enterprise.storage.get_memories_by_session(
            self.legacy_session_id, limit=500
        )
        # Storage returns DESC by importance/created; reverse for ascending
        return [self._to_dict(r) for r in reversed(records)]

    def load_memories(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Retrieve memories with optional limit (most recent first)."""
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValueError("Limit must be a positive integer")

        records = self.enterprise.storage.get_memories_by_session(
            self.legacy_session_id, limit=limit or 500
        )
        return [self._to_dict(r) for r in records]

    def search_memories(self, query: str) -> list[dict[str, Any]]:
        """Search memories using case-insensitive keyword matching."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        records = self.enterprise.storage.get_memories_by_session(
            self.legacy_session_id, limit=500
        )
        query_lower = query.lower()
        matches = [r for r in records if query_lower in r.content.lower()]
        # Return in ascending order (storage returns DESC)
        return [self._to_dict(r) for r in reversed(matches)]

    def update_memory(self, memory_id: str, new_memory: str) -> bool:
        """Update the text of an existing memory.

        Since MemoryStorage does not natively support in-place updates,
        this adapter performs a delete-and-reinsert using the same memory_id.
        The updated_at timestamp is set to the current time.
        """
        if not isinstance(memory_id, str) or not memory_id:
            raise ValueError("Memory ID must be a non-empty string")
        if not new_memory or not isinstance(new_memory, str):
            raise ValueError("New memory must be a non-empty string")

        if self.enterprise.storage.delete_memory_by_id(memory_id):
            now = datetime.datetime.now(datetime.timezone.utc)
            record = MemoryRecord(
                memory_id=memory_id,
                session_id=self.legacy_session_id,
                content=new_memory,
                importance_score=1.0,
                created_at=self._updated_at.get(memory_id, now),
            )
            self.enterprise.storage.add_memory(record)
            self._updated_at[memory_id] = now
            return True
        return False

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        if not isinstance(memory_id, str) or not memory_id:
            raise ValueError("Memory ID must be a non-empty string")

        deleted = self.enterprise.storage.delete_memory_by_id(memory_id)
        if deleted:
            self._updated_at.pop(memory_id, None)
        return deleted

    def _to_dict(self, record: MemoryRecord) -> dict[str, Any]:
        """Convert a MemoryRecord to the legacy dictionary format."""
        updated_at = self._updated_at.get(record.memory_id, record.created_at)
        return {
            "id": record.memory_id,
            "memory": record.content,
            "created_at": record.created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        }
