"""CapabilityResolver for determining required capabilities for incoming requests."""

from __future__ import annotations

import re

from app.agent.context import AgentContext
from app.agent.models import CapabilityResolution, ToolInvocationRequest


class CapabilityResolver:
    """Pluggable capability resolution layer for the Agent Runtime.

    Determines whether a request requires a filesystem tool, RAG, database access,
    or direct LLM completion based on intent detection.
    """

    def resolve(self, context: AgentContext) -> CapabilityResolution:
        """Analyze prompt intent and return CapabilityResolution."""
        prompt = context.user_prompt.strip().lower()

        # Heuristic 1: List directory contents (ls)
        if any(
            kw in prompt
            for kw in ["list files", "show files", "list directory", "ls ", "dir "]
        ) or prompt in ["ls", "dir"]:
            path = self._extract_path(context.user_prompt, default=".")
            return CapabilityResolution(
                capability_type="FILESYSTEM_TOOL",
                tool_request=ToolInvocationRequest(
                    tool_name="ls",
                    arguments={"path": path},
                    rationale="User requested directory contents listing.",
                ),
            )

        # Heuristic 2: Read document (cat)
        if any(
            kw in prompt
            for kw in [
                "read ",
                "show file",
                "cat ",
                "view file",
                "open file",
                "file content",
            ]
        ):
            path = self._extract_path(context.user_prompt, default="")
            if path:
                return CapabilityResolution(
                    capability_type="FILESYSTEM_TOOL",
                    tool_request=ToolInvocationRequest(
                        tool_name="cat",
                        arguments={"path": path},
                        rationale=f"User requested reading file '{path}'.",
                    ),
                )

        # Heuristic 3: Search keyword in documents (grep)
        if any(
            kw in prompt for kw in ["search ", "grep ", "find in files", "search for"]
        ):
            query = self._extract_search_query(context.user_prompt)
            if query:
                return CapabilityResolution(
                    capability_type="FILESYSTEM_TOOL",
                    tool_request=ToolInvocationRequest(
                        tool_name="grep",
                        arguments={"query": query, "path": "."},
                        rationale=f"User requested keyword search for '{query}'.",
                    ),
                )

        # Heuristic 4: Show working directory (pwd)
        if any(
            kw in prompt
            for kw in ["current directory", "pwd", "working directory", "where am i"]
        ):
            return CapabilityResolution(
                capability_type="FILESYSTEM_TOOL",
                tool_request=ToolInvocationRequest(
                    tool_name="pwd",
                    arguments={},
                    rationale="User requested current working directory.",
                ),
            )

        return CapabilityResolution(capability_type="NONE")

    def _extract_path(self, prompt: str, default: str = ".") -> str:
        """Extract path target from user prompt text."""
        # Check quoted strings first
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
        if quoted:
            return quoted[0]

        # Check for path-like tokens (e.g. engineering/architecture_spec.md)
        tokens = prompt.split()
        for token in tokens:
            clean = token.strip(".,;:?!()'\"")
            if "/" in clean or clean.endswith(
                (".md", ".txt", ".json", ".conf", ".env", ".log")
            ):
                return clean
            if clean in [
                "engineering",
                "executive",
                "finance",
                "hr",
                "it",
                "security",
                "configs",
                "credentials",
                "logs",
                "docs",
            ]:
                return clean

        return default

    def _extract_search_query(self, prompt: str) -> str:
        """Extract search query string from prompt."""
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
        if quoted:
            return quoted[0]

        lowered = prompt.lower()
        for prefix in ["search for ", "grep ", "search ", "find "]:
            if prefix in lowered:
                idx = lowered.find(prefix) + len(prefix)
                query = prompt[idx:].strip(".,;:?!()'\"")
                if query:
                    return query.split()[0] if " " in query and not quoted else query

        return prompt.strip()
