"""Read-only configuration service.

Wraps ``app.config.settings`` and masks any credential-adjacent field names
before exposing them through administrative APIs.
"""

from __future__ import annotations

import re
from typing import Any

from app.config import settings

# Fields matching this pattern will have their values replaced with "***"
_SENSITIVE_PATTERN = re.compile(
    r"(KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL|APIKEY)",
    re.IGNORECASE,
)


class ConfigurationService:
    """Provides a sanitized read-only view of the application configuration."""

    # Fields to expose (allowlist keeps the snapshot predictable)
    _EXPOSED_FIELDS = (
        "OLLAMA_URL",
        "MODEL_NAME",
        "MAX_HISTORY",
        "ENABLE_MEMORY",
        "MEMORY_LIMIT",
        "REQUEST_TIMEOUT",
        "LOG_LEVEL",
        "DEBUG_MODE",
        "TELEMETRY_ENABLED",
        "TELEMETRY_BUFFER_SIZE",
        "DEBUG_STORE_SIZE",
        "FALLBACK_MODEL_NAMES",
        "API_TITLE",
        "API_VERSION",
    )

    def get_snapshot(self) -> dict[str, Any]:
        """Return a sanitized configuration dict safe for API exposure."""
        snapshot: dict[str, Any] = {}
        for field in self._EXPOSED_FIELDS:
            value = getattr(settings, field, None)
            if value is None:
                continue
            if _SENSITIVE_PATTERN.search(field):
                snapshot[field] = "***"
            else:
                snapshot[field] = value
        return snapshot

    def is_debug_mode(self) -> bool:
        return bool(settings.DEBUG_MODE)

    def is_telemetry_enabled(self) -> bool:
        return bool(settings.TELEMETRY_ENABLED)
