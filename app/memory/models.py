import datetime
import uuid
from typing import Any

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """A single persistent memory tied to a session."""

    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    content: str
    importance_score: float = 0.0
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """Tracks conversation lifecycle and metadata."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    last_accessed_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryContext(BaseModel):
    """Structured response from the retriever."""

    retrieved_memories: list[MemoryRecord] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    latency_ms: float = 0.0

    @property
    def has_memories(self) -> bool:
        return len(self.retrieved_memories) > 0


class MemoryEvent(BaseModel):
    """Telemetry generated on retrieval."""

    request_id: str
    session_id: str
    retrieved_memory_ids: list[str] = Field(default_factory=list)
    importance_scores: list[float] = Field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    retrieval_method: str = "keyword_and_importance"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
