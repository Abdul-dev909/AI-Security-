"""GrepTool implementation."""

from __future__ import annotations

from typing import Any

from app.tools.base import BaseTool
from app.tools.exceptions import ToolExecutionError
from app.tools.security import get_relative_sandbox_path, validate_sandbox_path


class GrepTool(BaseTool):
    """Tool to search text files safely for simple keyword matches within the sandbox."""

    @property
    def name(self) -> str:
        return "grep"

    @property
    def description(self) -> str:
        return "Searches text files within a sandbox directory for a target keyword string."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword string to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "Relative sandbox path (file or directory) to search within. Defaults to root ('.').",
                    "default": ".",
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether search should be case-sensitive. Defaults to false.",
                    "default": False,
                },
            },
            "required": ["query"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "total_matches": {"type": "integer"},
                "matches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line_number": {"type": "integer"},
                            "line_content": {"type": "string"},
                        },
                    },
                },
            },
        }

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute grep tool."""
        query = kwargs.get("query")
        if not query or not isinstance(query, str):
            raise ToolExecutionError(
                "Parameter 'query' is required and must be a non-empty string."
            )

        user_path = kwargs.get("path", ".")
        case_sensitive = bool(kwargs.get("case_sensitive", False))

        resolved_path = validate_sandbox_path(user_path)
        if not resolved_path.exists():
            raise ToolExecutionError(f"Target search path not found: '{user_path}'")

        target_files: list[Any] = []
        if resolved_path.is_file():
            target_files.append(resolved_path)
        elif resolved_path.is_dir():
            # Recursively collect all text files
            for p in resolved_path.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    target_files.append(p)

        matches: list[dict[str, Any]] = []
        search_term = query if case_sensitive else query.lower()

        for file_path in target_files:
            # Skip binary files safely
            try:
                with open(file_path, "rb") as f:
                    sample = f.read(1024)
                    if b"\x00" in sample:
                        continue
            except Exception:
                continue

            try:
                lines = file_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except Exception:
                continue

            for idx, line in enumerate(lines, start=1):
                comparison_line = line if case_sensitive else line.lower()
                if search_term in comparison_line:
                    matches.append(
                        {
                            "file": get_relative_sandbox_path(file_path),
                            "line_number": idx,
                            "line_content": line.strip(),
                        }
                    )

        return {
            "query": query,
            "total_matches": len(matches),
            "matches": matches,
        }
