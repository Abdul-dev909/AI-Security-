"""Telemetry exporter interface and built-in implementations."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TelemetryExporter(ABC):
    """Abstract base class for telemetry exporters.

    Future modules can implement OTLP, Prometheus, or custom exporters
    by subclassing this interface.
    """

    @abstractmethod
    def export(self, category: str, events: list[Any]) -> None:
        """Export a batch of events for the given category."""


class JsonFileExporter(TelemetryExporter):
    """Exports telemetry events to a newline-delimited JSON file."""

    def __init__(self, output_path: str | Path = "telemetry_export.jsonl") -> None:
        self._path = Path(output_path)

    def export(self, category: str, events: list[Any]) -> None:
        try:
            with self._path.open("a", encoding="utf-8") as f:
                for event in events:
                    record = {"category": category}
                    if hasattr(event, "model_dump"):
                        record.update(event.model_dump(mode="json"))
                    else:
                        record["data"] = str(event)
                    f.write(json.dumps(record, default=str) + "\n")
        except OSError:
            logger.warning("JsonFileExporter failed to write events", exc_info=True)


class NullExporter(TelemetryExporter):
    """No-op exporter — discards all events. Useful in test environments."""

    def export(self, category: str, events: list[Any]) -> None:
        pass
