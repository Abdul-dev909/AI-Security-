"""TelemetryManager — facade over all per-category ring buffers."""

from __future__ import annotations

import logging

from app.telemetry.buffer import TelemetryBufferSet
from app.telemetry.models import (
    DetectionTelemetryEvent,
    KnowledgeTelemetryEvent,
    MemoryTelemetryEvent,
    RuntimeTelemetryEvent,
    ToolTelemetryEvent,
)

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Central entry-point for recording and querying telemetry events.

    Designed to be instantiated once and stored on ``app.state``.
    All push methods are fire-and-forget: exceptions are swallowed so that
    telemetry failures never degrade the request path.
    """

    def __init__(self, buffer_size: int = 500) -> None:
        self._buffers = TelemetryBufferSet(max_size=buffer_size)

    # --- Push helpers ---

    def record_runtime(self, event: RuntimeTelemetryEvent) -> None:
        self._safe_push("runtime", event)

    def record_memory(self, event: MemoryTelemetryEvent) -> None:
        self._safe_push("memory", event)

    def record_knowledge(self, event: KnowledgeTelemetryEvent) -> None:
        self._safe_push("knowledge", event)

    def record_tool(self, event: ToolTelemetryEvent) -> None:
        self._safe_push("tools", event)

    def record_detection(self, event: DetectionTelemetryEvent) -> None:
        self._safe_push("detection", event)

    # --- Query helpers ---

    def get_runtime_events(self, limit: int = 50) -> list[RuntimeTelemetryEvent]:
        return self._buffers.buffer("runtime").get_recent(limit)

    def get_memory_events(self, limit: int = 50) -> list[MemoryTelemetryEvent]:
        return self._buffers.buffer("memory").get_recent(limit)

    def get_knowledge_events(self, limit: int = 50) -> list[KnowledgeTelemetryEvent]:
        return self._buffers.buffer("knowledge").get_recent(limit)

    def get_tool_events(self, limit: int = 50) -> list[ToolTelemetryEvent]:
        return self._buffers.buffer("tools").get_recent(limit)

    def get_detection_events(self, limit: int = 50) -> list[DetectionTelemetryEvent]:
        return self._buffers.buffer("detection").get_recent(limit)

    def get_all_stats(self) -> dict[str, dict[str, int]]:
        """Return buffer fill stats per category."""
        return self._buffers.all_stats()

    def clear_category(self, category: str) -> None:
        self._buffers.buffer(category).clear()

    # --- Internal ---

    def _safe_push(self, category: str, event: object) -> None:
        try:
            self._buffers.buffer(category).push(event)
        except Exception:
            logger.debug(
                "Telemetry push failed for category %r", category, exc_info=True
            )
