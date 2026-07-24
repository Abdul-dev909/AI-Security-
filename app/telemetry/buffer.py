"""Thread-safe, bounded ring buffers for telemetry event categories."""

from __future__ import annotations

import threading
from collections import deque
from typing import Any

# Default per-category event capacity
DEFAULT_BUFFER_SIZE = 500


class TelemetryBuffer:
    """A single bounded ring-buffer for one event category.

    Thread-safe: all mutations are guarded by a lock.
    When full, the oldest event is automatically evicted (FIFO).
    """

    def __init__(self, max_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self._max_size = max_size
        self._events: deque[Any] = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._total_pushed = 0

    def push(self, event: Any) -> None:
        """Append an event. Silently evicts oldest when full."""
        with self._lock:
            self._events.append(event)
            self._total_pushed += 1

    def get_recent(self, limit: int = 50) -> list[Any]:
        """Return up to *limit* most-recent events (newest last)."""
        with self._lock:
            items = list(self._events)
        return items[-limit:] if limit < len(items) else items

    def clear(self) -> None:
        """Remove all buffered events."""
        with self._lock:
            self._events.clear()

    def stats(self) -> dict[str, int]:
        """Return buffer statistics."""
        with self._lock:
            current = len(self._events)
        return {
            "current_size": current,
            "max_size": self._max_size,
            "total_pushed": self._total_pushed,
        }


class TelemetryBufferSet:
    """A collection of named TelemetryBuffers, one per event category."""

    CATEGORIES = ("runtime", "memory", "knowledge", "tools", "detection")

    def __init__(self, max_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self._buffers: dict[str, TelemetryBuffer] = {
            category: TelemetryBuffer(max_size=max_size) for category in self.CATEGORIES
        }

    def buffer(self, category: str) -> TelemetryBuffer:
        """Return the buffer for the given category."""
        if category not in self._buffers:
            raise KeyError(f"Unknown telemetry category: {category!r}")
        return self._buffers[category]

    def all_stats(self) -> dict[str, dict[str, int]]:
        """Return stats for every category."""
        return {cat: buf.stats() for cat, buf in self._buffers.items()}
