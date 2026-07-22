"""PwdTool implementation."""

from __future__ import annotations

from typing import Any

from app.tools.base import BaseTool
from app.tools.security import get_relative_sandbox_path, get_sandbox_root


class PwdTool(BaseTool):
    """Tool to return the current working directory relative to sandbox root."""

    @property
    def name(self) -> str:
        return "pwd"

    @property
    def description(self) -> str:
        return "Returns the current enterprise sandbox working directory root."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cwd": {"type": "string", "description": "Current sandbox path"}
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, str]:
        """Execute pwd tool."""
        root = get_sandbox_root()
        rel_path = get_relative_sandbox_path(root)
        display_path = f"sandbox/{rel_path}".rstrip("/")
        return {"cwd": display_path}
