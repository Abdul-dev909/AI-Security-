"""Typed event models for the enterprise telemetry subsystem."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class RuntimeTelemetryEvent(BaseModel):
    """Captures end-to-end performance for a single agent runtime request."""

    request_id: str
    session_id: str
    user_prompt_length: int = 0
    total_latency_ms: float = 0.0
    memory_latency_ms: float = 0.0
    knowledge_latency_ms: float = 0.0
    tool_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    detection_latency_ms: float = 0.0
    prompt_tokens: int = 0
    response_tokens: int = 0
    capability_used: str | None = None
    stage_count: int = 0
    streaming: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryTelemetryEvent(BaseModel):
    """Captures a single memory operation (store or retrieval)."""

    session_id: str
    operation: Literal["store", "retrieve", "search"] = "retrieve"
    latency_ms: float = 0.0
    importance_score: float = 0.0
    result_count: int = 0
    cache_hit: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeTelemetryEvent(BaseModel):
    """Captures a knowledge retrieval operation from the RAG subsystem."""

    request_id: str
    session_id: str
    query_length: int = 0
    retrieved_chunks: int = 0
    retrieved_documents: int = 0
    retrieval_latency_ms: float = 0.0
    embedding_model: str = "unknown"
    vector_db: str = "chromadb"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToolTelemetryEvent(BaseModel):
    """Captures a single tool execution from the agent executor."""

    request_id: str
    session_id: str
    tool_name: str
    success: bool = True
    execution_time_ms: float = 0.0
    error: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DetectionTelemetryEvent(BaseModel):
    """Captures results from a detection pipeline scan."""

    request_id: str
    session_id: str
    total_detectors: int = 0
    total_detections: int = 0
    highest_severity: str | None = None
    scan_latency_ms: float = 0.0
    detector_results: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


TelemetryEvent = (
    RuntimeTelemetryEvent
    | MemoryTelemetryEvent
    | KnowledgeTelemetryEvent
    | ToolTelemetryEvent
    | DetectionTelemetryEvent
)
