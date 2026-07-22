"""Unified AgentContext container flowing through the runtime pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.agent.models import (
    CapabilityResolution,
    StageExecutionMetadata,
    ToolInvocationResult,
)


@dataclass
class AgentContext:
    """Unified context object containing state across all pipeline stages."""

    request_id: str
    session_id: str
    user_prompt: str
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    memories: list[str] = field(default_factory=list)
    available_tools: list[dict[str, str]] = field(default_factory=list)
    capability_resolution: CapabilityResolution | None = None
    tool_result: ToolInvocationResult | None = None
    formatted_messages: list[dict[str, str]] = field(default_factory=list)
    raw_ai_response: str | None = None
    detection_report: Any | None = None
    stage_telemetry: list[StageExecutionMetadata] = field(default_factory=list)
    start_timestamp: float = field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )

    def record_stage(
        self,
        stage_name: str,
        duration_ms: float,
        status: str = "SUCCESS",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record telemetry metadata for a completed pipeline stage."""
        now_iso = datetime.now(timezone.utc).isoformat()
        metadata = StageExecutionMetadata(
            stage_name=stage_name,
            end_time=now_iso,
            duration_ms=round(duration_ms, 3),
            status=status,  # type: ignore[arg-type]
            details=details or {},
        )
        self.stage_telemetry.append(metadata)
