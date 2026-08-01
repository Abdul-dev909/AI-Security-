"""Attack plugin interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AttackDefinition
from .planner import AttackPlanner
from .strategy import AttackStrategy
from .prompt_builder import AttackPromptBuilder
from .analyzer import AttackResponseAnalyzer

@runtime_checkable
class AttackPlugin(Protocol):
    """Interface for dynamically loadable attack plugins."""

    @property
    def definition(self) -> AttackDefinition:
        """The structural definition and metadata for this attack."""
        ...

    def get_planner(self) -> AttackPlanner:
        """Returns the planner for this attack."""
        ...

    def get_strategy(self) -> AttackStrategy:
        """Returns the strategy for this attack."""
        ...

    def get_prompt_builder(self) -> AttackPromptBuilder:
        """Returns the prompt builder for this attack."""
        ...

    def get_analyzer(self) -> AttackResponseAnalyzer:
        """Returns the response analyzer for this attack."""
        ...
