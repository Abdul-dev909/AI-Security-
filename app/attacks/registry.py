"""Central registry for structured attack definitions."""

from __future__ import annotations

from collections.abc import Iterable

from app.attack_engine.models import Attack as LegacyAttack

from .metadata import AttackCategory, AttackTechnique
from .models import AttackDefinition
from .validation import (
    normalize_category,
    normalize_technique,
    validate_attack_definition,
)


class AttackRegistry:
    """Central attack registry with structured lookup helpers."""

    def __init__(self) -> None:
        self._definitions: dict[str, AttackDefinition] = {}

    def register(self, attack: AttackDefinition) -> None:
        attack = validate_attack_definition(attack)
        if attack.attack_id in self._definitions:
            raise ValueError(
                f"Attack with ID '{attack.attack_id}' is already registered."
            )
        self._definitions[attack.attack_id] = attack

    def load(self, attacks: Iterable[AttackDefinition]) -> list[AttackDefinition]:
        loaded: list[AttackDefinition] = []
        for attack in attacks:
            self.register(attack)
            loaded.append(attack)
        return loaded

    def get(self, attack_id: str) -> AttackDefinition | None:
        return self._definitions.get(attack_id)

    def get_by_category(self, category: str | AttackCategory) -> list[AttackDefinition]:
        target = normalize_category(category)
        return [attack for attack in self._definitions.values() if attack.category == target]

    def get_by_technique(self, technique: str | AttackTechnique) -> list[AttackDefinition]:
        target = normalize_technique(technique)
        return [attack for attack in self._definitions.values() if attack.technique == target]

    def list_available(self) -> list[AttackDefinition]:
        return list(self._definitions.values())

    def list_attacks(self) -> list[LegacyAttack]:
        attacks: list[LegacyAttack] = []
        for definition in self._definitions.values():
            attacks.extend(definition.to_legacy_attacks())
        return attacks

    def list(self) -> list[LegacyAttack]:
        """Legacy alias retained for compatibility with the existing API."""

        return self.list_attacks()

    def clear(self) -> None:
        self._definitions.clear()
