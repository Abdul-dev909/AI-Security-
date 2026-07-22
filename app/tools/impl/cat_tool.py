"""CatTool implementation."""

from __future__ import annotations

from typing import Any

from app.tools.base import BaseTool
from app.tools.exceptions import ToolExecutionError
from app.tools.security import (
    get_relative_sandbox_path,
    validate_sandbox_path,
    validate_text_file,
)


class CatTool(BaseTool):
    """Tool to read text file contents cleanly within the enterprise sandbox."""

    @property
    def name(self) -> str:
        return "cat"

    @property
    def description(self) -> str:
        return "Reads and returns text file content within the sandbox directory."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative sandbox file path to read.",
                }
            },
            "required": ["path"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "size_bytes": {"type": "integer"},
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute cat tool."""
        user_path = kwargs.get("path")
        if not user_path or not isinstance(user_path, str):
            raise ToolExecutionError(
                "Parameter 'path' is required and must be a non-empty string."
            )

        resolved_path = validate_sandbox_path(user_path)
        validate_text_file(resolved_path)

        try:
            content = resolved_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ToolExecutionError(
                f"Failed to read file '{user_path}': {exc}"
            ) from exc

        return {
            "path": get_relative_sandbox_path(resolved_path),
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
        }
