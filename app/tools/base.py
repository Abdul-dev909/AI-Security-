"""Abstract BaseTool class for all enterprise tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract Base Class that every tool in the framework must implement.

    Subclasses must define:
    - name: Unique identifier for the tool (e.g. 'cat', 'ls')
    - description: Human-readable explanation of what the tool does
    - parameters_schema: Dict describing expected keyword parameters
    - output_schema: Dict describing expected output structure
    - execute(**kwargs): Core logic of the tool
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique string name of the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Clear description of the tool functionality."""

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """JSON-schema style parameter dictionary for LLM tool selection."""
        return {}

    @property
    def output_schema(self) -> dict[str, Any]:
        """JSON-schema style output dictionary."""
        return {}

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool logic with keyword parameters.

        Raises:
            ToolSecurityError: If path/permission security rules are violated.
            ToolExecutionError: If tool fails operational checks.
        """
