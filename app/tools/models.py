"""Structured data models for tool inputs, outputs, and audit events."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ToolExecutionResult(BaseModel):
    """Structured response object returned by ToolManager for all tool executions."""

    success: bool = Field(
        description="Whether the tool completed execution successfully."
    )
    tool: str = Field(description="Unique name of the executed tool.")
    execution_time_ms: float = Field(description="Execution duration in milliseconds.")
    result: Any | None = Field(
        default=None, description="Structured result data produced by the tool."
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed."
    )


class ToolAuditEvent(BaseModel):
    """Security audit event captured for every tool invocation."""

    event_id: str = Field(
        default_factory=lambda: f"evt-{uuid4().hex[:12]}",
        description="Unique identifier for the audit event.",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when execution occurred.",
    )
    tool_name: str = Field(description="Name of the tool requested.")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Raw arguments passed to the tool."
    )
    duration_ms: float = Field(description="Execution duration in milliseconds.")
    status: Literal["SUCCESS", "SECURITY_VIOLATION", "EXECUTION_ERROR", "NOT_FOUND"] = (
        Field(description="Outcome status of the tool invocation.")
    )
    error_message: str | None = Field(
        default=None, description="Detailed error description if failed."
    )
    accessed_paths: list[str] = Field(
        default_factory=list,
        description="Sandbox relative paths accessed during execution.",
    )
