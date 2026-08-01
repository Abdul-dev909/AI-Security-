"""Decision engine interface for orchestrating attack flow."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AttackSession
from .strategy import AttackStrategy


@runtime_checkable
class DecisionEngine(Protocol):
    """Engine responsible for orchestrator decision-making."""

    def choose_next_action(self, session: AttackSession, strategy: AttackStrategy) -> str:
        """Decide the next action based on current state."""
        ...

    def decide_retry(self, session: AttackSession, strategy: AttackStrategy) -> bool:
        """Decide whether to retry after a failed attempt."""
        ...

    def decide_escalation(self, session: AttackSession, strategy: AttackStrategy) -> bool:
        """Decide whether to escalate the attack."""
        ...

    def choose_next_stage(self, session: AttackSession, strategy: AttackStrategy) -> str:
        """Choose the next stage to transition to."""
        ...

    def should_terminate(self, session: AttackSession, strategy: AttackStrategy) -> bool:
        """Decide whether the attack should be terminated."""
        ...
