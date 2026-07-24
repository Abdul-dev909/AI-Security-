from typing import Any

from app.memory.importance import ImportanceEngine
from app.memory.models import MemoryContext, MemoryRecord
from app.memory.retriever import MemoryRetriever
from app.memory.sessions import SessionManager
from app.memory.storage import MemoryStorage


class EnterpriseMemoryManager:
    """Core coordination of storage, retrieval, and importance engines."""

    def __init__(self):
        self.session_manager = SessionManager()
        self.storage = MemoryStorage()
        self.importance_engine = ImportanceEngine()
        self.retriever = MemoryRetriever(storage=self.storage)

    def process_memory(
        self, session_id: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Evaluate and potentially store a memory for the given session."""
        score = self.importance_engine.evaluate(content)

        # Backward compatibility for tests that monkeypatch conversation module
        import app.conversation

        if app.conversation.is_important(content):
            score = 1.0

        # We store memories if they meet a minimal importance threshold
        if score > 0.1:
            record = MemoryRecord(
                session_id=session_id,
                content=content,
                importance_score=score,
                metadata=metadata or {},
            )
            self.storage.add_memory(record)

    def search_memories(self, session_id: str, query: str) -> MemoryContext:
        """Search isolated memories for a specific session."""
        return self.retriever.retrieve(session_id=session_id, query=query)
