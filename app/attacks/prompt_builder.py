"""Attack prompt builder layer."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .strategy import AttackStrategy
from .models import AttackSession


@runtime_checkable
class AttackPromptBuilder(Protocol):
    """Component for building attack prompts."""

    def build_prompt_from_strategy(self, strategy: AttackStrategy, session: AttackSession) -> str:
        """Build a prompt derived directly from the current strategy."""
        ...

    def build_prompt_from_history(self, session: AttackSession) -> str:
        """Build a prompt based on the conversation history."""
        ...

    def inject_stage_instructions(self, prompt: str, stage: str) -> str:
        """Inject stage-specific instructions into an existing prompt."""
        ...
