"""ToolManager orchestrates tool execution, measures execution time, and
emits audit telemetry.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from app.tools.exceptions import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolSecurityError,
)
from app.tools.models import ToolAuditEvent, ToolExecutionResult
from app.tools.registry import ToolRegistry
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class ToolManager:
    """Enterprise Tool Manager orchestrating tool invocation, timing, and
    security audit telemetry.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        audit_callback: Callable[[ToolAuditEvent], None] | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()
        self.audit_callback = audit_callback
        self.audit_logs: list[ToolAuditEvent] = []

    def execute_tool(self, name: str, **kwargs: Any) -> ToolExecutionResult:
        """Execute a named tool safely and return structured ToolExecutionResult.

        Always captures timing, produces audit events, and handles exceptions cleanly.
        """
        tool_name = name.lower().strip()
        status: str = "SUCCESS"
        error_msg: str | None = None
        result_payload: Any = None
        accessed_paths: list[str] = []

        if "path" in kwargs and isinstance(kwargs["path"], str):
            accessed_paths.append(kwargs["path"])

        with execution_timer() as elapsed_seconds:
            try:
                tool = self.registry.get(tool_name)
                result_payload = tool.execute(**kwargs)
            except ToolNotFoundError as exc:
                status = "NOT_FOUND"
                error_msg = str(exc)
                logger.warning("Tool execution attempted for missing tool '%s'", name)
            except ToolSecurityError as exc:
                status = "SECURITY_VIOLATION"
                error_msg = str(exc)
                logger.warning(
                    "Security violation during tool execution of '%s': %s", name, exc
                )
            except ToolExecutionError as exc:
                status = "EXECUTION_ERROR"
                error_msg = str(exc)
                logger.error("Execution failure for tool '%s': %s", name, exc)
            except Exception as exc:
                status = "EXECUTION_ERROR"
                error_msg = f"Unexpected runtime error during tool execution: {exc}"
                logger.exception("Unexpected exception executing tool '%s'", name)

        duration_ms = round(elapsed_seconds() * 1000, 3)

        # Create security audit event
        audit_event = ToolAuditEvent(
            tool_name=tool_name,
            arguments=kwargs,
            duration_ms=duration_ms,
            status=status,  # type: ignore[arg-type]
            error_message=error_msg,
            accessed_paths=accessed_paths,
        )

        self._record_audit_event(audit_event)

        return ToolExecutionResult(
            success=(status == "SUCCESS"),
            tool=tool_name,
            execution_time_ms=duration_ms,
            result=result_payload,
            error=error_msg,
        )

    def _record_audit_event(self, event: ToolAuditEvent) -> None:
        """Record event internally and forward to optional audit callback."""
        self.audit_logs.append(event)
        if self.audit_callback:
            try:
                self.audit_callback(event)
            except Exception:
                logger.exception("Failed to send tool audit event to callback.")
