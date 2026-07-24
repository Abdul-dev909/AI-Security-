import datetime
import uuid
from typing import Any

from pydantic import BaseModel, Field


class EnterpriseMetadata(BaseModel):
    """Rich enterprise metadata preserved across documents and chunks."""

    source_path: str
    department: str = "Unknown"
    owner: str = "Unknown"
    classification: str = "Unclassified"
    asset_type: str = "Document"
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
    contains_honeytoken: bool = False
    contains_prompt_injection: bool = False
    synthetic_dataset: str | None = None
    version: str = "1.0"


class KnowledgeDocument(BaseModel):
    """Represents a full document ingested from the enterprise sandbox."""

    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    metadata: EnterpriseMetadata


class Chunk(BaseModel):
    """Represents a discrete chunk of text derived from a KnowledgeDocument."""

    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    text: str
    metadata: EnterpriseMetadata


class KnowledgeRetrievalEvent(BaseModel):
    """Telemetry event generated on every knowledge retrieval."""

    request_id: str
    session_id: str
    retrieved_document_ids: list[str] = Field(default_factory=list)
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    similarity_scores: list[float] = Field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    retrieval_method: str = "similarity_search"
    embedding_model: str
    vector_database: str = "chromadb"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class KnowledgeContext(BaseModel):
    """Rich structured object encapsulating retrieved knowledge."""

    retrieved_chunks: list[Chunk] = Field(default_factory=list)
    similarity_scores: list[float] = Field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    retrieval_method: str = "similarity_search"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_database: str = "chromadb"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    security_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def has_knowledge(self) -> bool:
        """Returns True if any chunks were retrieved."""
        return len(self.retrieved_chunks) > 0

    def to_telemetry_event(
        self, request_id: str, session_id: str
    ) -> KnowledgeRetrievalEvent:
        """Converts the context into a telemetry event for the detection engine."""
        return KnowledgeRetrievalEvent(
            request_id=request_id,
            session_id=session_id,
            retrieved_document_ids=list({c.document_id for c in self.retrieved_chunks}),
            retrieved_chunk_ids=[c.chunk_id for c in self.retrieved_chunks],
            similarity_scores=self.similarity_scores,
            retrieval_latency_ms=self.retrieval_latency_ms,
            retrieval_method=self.retrieval_method,
            embedding_model=self.embedding_model,
            vector_database=self.vector_database,
            timestamp=self.timestamp,
        )
