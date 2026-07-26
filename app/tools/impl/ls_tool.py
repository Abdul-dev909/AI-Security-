"""LsTool implementation."""

from __future__ import annotations

from typing import Any

from app.tools.base import BaseTool
from app.tools.exceptions import ToolExecutionError
from app.tools.security import get_relative_sandbox_path, validate_sandbox_path


class LsTool(BaseTool):
    """Tool to list directory contents safely within the enterprise sandbox."""

    @property
    def name(self) -> str:
        return "ls"

    @property
    def description(self) -> str:
        return "Lists files and subdirectories within a specified sandbox path."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Relative sandbox directory path to list. Defaults "
                        "to root ('.')."
                    ),
                    "default": ".",
                }
            },
            "required": [],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "is_dir": {"type": "boolean"},
                            "size_bytes": {"type": "integer"},
                        },
                    },
                },
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute ls tool."""
        user_path = kwargs.get("path", ".")
        resolved_path = validate_sandbox_path(user_path)

        if not resolved_path.exists():
            raise ToolExecutionError(f"Directory not found: '{user_path}'")

        if not resolved_path.is_dir():
            raise ToolExecutionError(f"Path is not a directory: '{user_path}'")

        entries: list[dict[str, Any]] = []
        try:
            for item in sorted(resolved_path.iterdir(), key=lambda p: p.name):
                entries.append(
                    {
                        "name": item.name,
                        "is_dir": item.is_dir(),
                        "size_bytes": item.stat().st_size if item.is_file() else 0,
                    }
                )
        except Exception as exc:
            raise ToolExecutionError(
                f"Failed to list directory '{user_path}': {exc}"
            ) from exc

        return {
            "path": get_relative_sandbox_path(resolved_path) or ".",
            "entries": entries,
        }
