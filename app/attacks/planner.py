"""Attack planner interface and models."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from dataclasses import dataclass

from .models import AttackObjective, AttackDefinition


@dataclass(frozen=True, slots=True)
class AttackPlan:
    """The generated plan for executing an attack."""
    
    planned_stages: list[str]
    estimated_turns: int
    objectives: list[AttackObjective]
    success_criteria: list[str]
    retry_limits: int
    fallback_strategy: str | None


@runtime_checkable
class AttackPlanner(Protocol):
    """Component that generates an AttackPlan before execution begins."""

    def generate_plan(self, definition: AttackDefinition, metadata: dict | None = None) -> AttackPlan:
        """Generate a plan for the given attack definition."""
        ...
