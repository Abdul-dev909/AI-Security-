"""Pydantic response models for the administrative API layer.

Designed to be consumed directly by the Module 10 Dashboard.
All models carry timestamps and structured component health so the
dashboard can poll without an adapter layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status of a single platform subsystem."""

    name: str
    status: Literal["healthy", "degraded", "unavailable"]
    latency_ms: float | None = None
    last_checked: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    details: dict[str, Any] = Field(default_factory=dict)


class RuntimeStatus(BaseModel):
    """Current operational status of the Agent Runtime."""

    uptime_seconds: float
    active_sessions: int
    total_requests_served: int
    stage_timing_averages: dict[str, float] = Field(default_factory=dict)
    components: list[ComponentHealth] = Field(default_factory=list)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RuntimeMetrics(BaseModel):
    """Computed performance metrics derived from the telemetry buffer."""

    total_events: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    avg_memory_latency_ms: float = 0.0
    avg_llm_latency_ms: float = 0.0
    avg_knowledge_latency_ms: float = 0.0
    tool_executions: int = 0
    detection_scans: int = 0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class MemoryAdminRecord(BaseModel):
    """Serialized memory record for administrative inspection."""

    memory_id: str
    session_id: str
    content: str
    importance_score: float
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryMetrics(BaseModel):
    """Aggregated statistics for the enterprise memory subsystem."""

    total_memories: int = 0
    total_sessions: int = 0
    avg_importance_score: float = 0.0
    memories_by_session: dict[str, int] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class KnowledgeMetrics(BaseModel):
    """Statistics and health for the RAG knowledge subsystem."""

    total_documents: int = 0
    total_chunks: int = 0
    vector_count: int = 0
    indexed_at: str | None = None
    embedding_model: str = "unknown"
    index_version: str | None = None
    vector_db_status: Literal["healthy", "degraded", "unavailable"] = "unavailable"
    index_available: bool = False
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class KnowledgeDocumentSummary(BaseModel):
    """Lightweight document summary for listing endpoints."""

    document_id: str
    source_path: str
    department: str
    classification: str
    asset_type: str
    contains_honeytoken: bool = False
    contains_prompt_injection: bool = False


class KnowledgeChunkSummary(BaseModel):
    """Lightweight chunk summary for listing endpoints."""

    chunk_id: str
    document_id: str
    source_path: str
    text_preview: str  # First 120 chars
    classification: str


class ToolMetrics(BaseModel):
    """Metrics for the tool registry and execution subsystem."""

    registered_tools: list[dict[str, Any]] = Field(default_factory=list)
    total_registered: int = 0
    total_executions: int = 0
    executions_by_tool: dict[str, int] = Field(default_factory=dict)
    success_rate: float = 0.0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DetectionMetrics(BaseModel):
    """Aggregated detection statistics from the telemetry buffer."""

    total_scans: int = 0
    total_detections: int = 0
    detections_by_severity: dict[str, int] = Field(default_factory=dict)
    avg_scan_latency_ms: float = 0.0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DiagnosticsReport(BaseModel):
    """Comprehensive runtime diagnostics snapshot."""

    uptime_seconds: float
    active_sessions: int
    total_requests_served: int
    vector_count: int = 0
    indexed_documents: int = 0
    tool_executions_total: int = 0
    stage_timing_averages: dict[str, float] = Field(default_factory=dict)
    subsystems: dict[str, ComponentHealth] = Field(default_factory=dict)
    telemetry_buffer_stats: dict[str, dict[str, int]] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DebugRequestSnapshot(BaseModel):
    """Per-request debug snapshot exposed only when DEBUG_MODE=true."""

    request_id: str
    session_id: str
    user_prompt: str
    generated_prompt: list[dict[str, str]] = Field(default_factory=list)
    retrieved_memories: list[str] = Field(default_factory=list)
    retrieved_knowledge_chunks: int = 0
    selected_capability: str | None = None
    executed_tool: str | None = None
    tool_output: str | None = None
    model_response: str | None = None
    stage_timings: dict[str, float] = Field(default_factory=dict)
    total_duration_ms: float = 0.0
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SessionSummary(BaseModel):
    """Summary of a single tracked session."""

    session_id: str
    created_at: str
    last_active: str
    metadata: dict[str, Any] = Field(default_factory=dict)
