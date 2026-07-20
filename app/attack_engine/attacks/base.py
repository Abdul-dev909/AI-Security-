"""Base class for all attack definitions in the Attack Library.

Provides a reusable dataclass that every attack module inherits from.
Each attack carries structured metadata and multiple prompt variants,
and can convert itself into the engine-compatible ``Attack`` Pydantic models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from app.attack_engine.models import Attack

if TYPE_CHECKING:
    from app.attack_engine.registry import AttackRegistry

# Allowed difficulty levels for type safety.
Difficulty = Literal["Easy", "Medium", "Hard"]


@dataclass(frozen=True, slots=True)
class BaseAttack:
    """Reusable base for every attack definition.

    Attributes:
        name: Human-readable name of the attack.
        category: High-level category (e.g. ``Prompt Injection``, ``Jailbreak``).
        difficulty: One of ``Easy``, ``Medium``, or ``Hard``.
        description: What this attack attempts to achieve.
        expected_behavior: How a properly defended model should respond.
        prompts: A list of adversarial prompt variants.
    """

    name: str
    category: str
    difficulty: Difficulty
    description: str
    expected_behavior: str
    prompts: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def to_attack_models(self, *, severity: str | None = None) -> list[Attack]:
        """Convert every prompt variant into an engine-compatible ``Attack``.

        Each prompt is mapped to the engine's Pydantic ``Attack`` model so
        that the existing ``AttackRegistry`` can consume them without any
        engine modifications.

        Args:
            severity: Optional override for the severity field.  When
                ``None`` the difficulty is mapped automatically
                (``Easy`` → ``low``, ``Medium`` → ``medium``,
                ``Hard`` → ``high``).

        Returns:
            A list of ``Attack`` instances ready for registry registration.
        """
        severity_map: dict[str, str] = {
            "Easy": "low",
            "Medium": "medium",
            "Hard": "high",
        }
        resolved_severity = severity or severity_map.get(self.difficulty, "medium")

        attacks: list[Attack] = []
        for idx, prompt in enumerate(self.prompts, start=1):
            attack_id = f"{self._slug()}-{idx:02d}"
            attacks.append(
                Attack(
                    id=attack_id,
                    name=f"{self.name} #{idx}",
                    category=self.category,
                    description=self.description,
                    prompt=prompt,
                    severity=resolved_severity,
                )
            )
        return attacks

    def register_all(
        self,
        registry: AttackRegistry,
        *,
        severity: str | None = None,
    ) -> list[Attack]:
        """Create engine ``Attack`` instances and register them.

        This is a convenience wrapper that calls :meth:`to_attack_models`
        and feeds each result into the registry.

        Args:
            registry: The ``AttackRegistry`` to populate.
            severity: Optional severity override (see :meth:`to_attack_models`).

        Returns:
            The list of ``Attack`` instances that were registered.
        """
        models = self.to_attack_models(severity=severity)
        for model in models:
            registry.register(model)
        return models

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _slug(self) -> str:
        """Generate a URL-safe slug from the attack name."""
        return self.name.lower().replace(" ", "-").replace("_", "-")
