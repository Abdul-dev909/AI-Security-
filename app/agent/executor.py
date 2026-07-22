"""AgentExecutor for executing resolved capability requests."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.models import ToolInvocationRequest, ToolInvocationResult
from app.tools.manager import ToolManager
from app.tools.models import ToolExecutionResult


class AgentExecutor:
    """Executes capability tool requests via ToolManager and formats output for prompt context."""

    def __init__(self, tool_manager: ToolManager | None = None) -> None:
        self.tool_manager = tool_manager or ToolManager()

    def execute_capability(
        self, context: AgentContext, tool_request: ToolInvocationRequest
    ) -> ToolInvocationResult:
        """Execute the capability tool and format the result."""
        res: ToolExecutionResult = self.tool_manager.execute_tool(
            tool_request.tool_name, **tool_request.arguments
        )

        formatted_text = self._format_result_text(res)

        return ToolInvocationResult(
            success=res.success,
            tool_name=res.tool,
            execution_time_ms=res.execution_time_ms,
            raw_result=res.result,
            formatted_output=formatted_text,
            error_message=res.error,
        )

    def _format_result_text(self, res: ToolExecutionResult) -> str:
        """Format raw result dictionary into structured markdown for context injection."""
        if not res.success:
            return f"Tool '{res.tool}' Execution Error: {res.error}"

        payload = res.result
        if not payload or not isinstance(payload, dict):
            return str(payload)

        # Format cat output
        if res.tool == "cat":
            path = payload.get("path", "")
            content = payload.get("content", "")
            return f"--- START FILE CONTEXT: {path} ---\n{content}\n--- END FILE CONTEXT ---"

        # Format ls output
        if res.tool == "ls":
            path = payload.get("path", ".")
            entries = payload.get("entries", [])
            lines = []
            for e in entries:
                size_str = (
                    "DIR" if e.get("is_dir") else f"{e.get('size_bytes', 0)} bytes"
                )
                lines.append(f"- {e.get('name')} ({size_str})")
            return f"Directory Listing for '{path}':\n" + "\n".join(lines)

        # Format grep output
        if res.tool == "grep":
            query = payload.get("query", "")
            matches = payload.get("matches", [])
            if not matches:
                return f"No keyword matches found for query '{query}'."
            lines = [
                f"File: {m['file']} (Line {m['line_number']}): {m['line_content']}"
                for m in matches
            ]
            return f"Search results for '{query}':\n" + "\n".join(lines)

        # Format pwd output
        if res.tool == "pwd":
            return f"Current working directory: {payload.get('cwd', 'sandbox/')}"

        return str(payload)
