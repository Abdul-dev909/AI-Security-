"""Tool registry for registering and discovering available enterprise tools."""

from __future__ import annotations

import logging
from collections.abc import Iterator

from app.tools.base import BaseTool
from app.tools.exceptions import ToolNotFoundError
from app.tools.impl.cat_tool import CatTool
from app.tools.impl.grep_tool import GrepTool
from app.tools.impl.ls_tool import LsTool
from app.tools.impl.pwd_tool import PwdTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry mapping tool names to BaseTool instances.

    Supports dynamic registration of initial builtin tools (pwd, ls, cat, grep)
    and allows future modules to extend the registry with additional enterprise tools.
    """

    def __init__(self, auto_register_builtins: bool = True) -> None:
        self._tools: dict[str, BaseTool] = {}
        if auto_register_builtins:
            self.register_builtins()

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        if not isinstance(tool, BaseTool):
            raise TypeError("Only instances of BaseTool can be registered.")
        name = tool.name.lower().strip()
        if not name:
            raise ValueError("Tool name must not be empty.")
        self._tools[name] = tool
        logger.debug("Registered tool '%s'", name)

    def register_builtins(self) -> None:
        """Register default sandbox tools (pwd, ls, cat, grep)."""
        self.register(PwdTool())
        self.register(LsTool())
        self.register(CatTool())
        self.register(GrepTool())

    def get(self, name: str) -> BaseTool:
        """Fetch a registered tool by name."""
        key = name.lower().strip()
        if key not in self._tools:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered in the tool registry."
            )
        return self._tools[key]

    def has(self, name: str) -> bool:
        """Check whether a tool exists in the registry."""
        return name.lower().strip() in self._tools

    def list_tools(self) -> list[dict[str, str]]:
        """Return metadata declarations for all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]

    def __iter__(self) -> Iterator[BaseTool]:
        return iter(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)
