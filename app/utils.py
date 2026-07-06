"""Small utility helpers shared across the application."""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Iterator


def current_timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""

    return datetime.now(timezone.utc).isoformat()


@contextmanager
def execution_timer() -> Iterator[Callable[[], float]]:
    """Measure how long a block of code takes to execute.

    The context manager yields a callable so the caller can ask for the elapsed
    time after the block has finished.
    """

    start_time = time.perf_counter()
    yield lambda: time.perf_counter() - start_time


def safe_json_dumps(value: Any, *, indent: int | None = None) -> str:
    """Serialize a value to JSON without raising unexpected logging errors."""

    try:
        return json.dumps(value, ensure_ascii=False, indent=indent, default=str)
    except (TypeError, ValueError):
        return json.dumps(str(value), ensure_ascii=False)


def normalize_text(value: str) -> str:
    """Trim surrounding whitespace from a string."""

    return value.strip()


def is_blank_text(value: str) -> bool:
    """Return True when a string only contains whitespace."""

    return normalize_text(value) == ""

