"""Validation helpers for attack definitions."""

from __future__ import annotations

from collections.abc import Iterable

from .metadata import AttackCategory, AttackSeverity, AttackTechnique
from .models import AttackDefinition, AttackVariant
from .metadata import ExecutionMode


def _ensure_unique(values: list[str], *, label: str, attack_id: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label} values found for attack {attack_id!r}.")


def validate_attack_variant(variant: AttackVariant) -> AttackVariant:
    """Validate a single attack variant."""

    if not variant.variant_id.strip():
        raise ValueError("variant_id must not be empty")
    if not variant.name.strip():
        raise ValueError("variant.name must not be empty")
    if not variant.prompt.strip():
        raise ValueError("variant.prompt must not be empty")
    return variant


def validate_attack_definition(definition: AttackDefinition) -> AttackDefinition:
    """Validate a structured attack definition."""

    if not definition.attack_id.strip():
        raise ValueError("attack_id must not be empty")
    if not definition.name.strip():
        raise ValueError("name must not be empty")
    if not definition.description.strip():
        raise ValueError("description must not be empty")
    if not definition.objectives:
        raise ValueError("objectives must not be empty")
    if not definition.supported_modes:
        raise ValueError("supported_modes must not be empty")

    # ensure supported_execution_modes are valid ExecutionMode values
    if not getattr(definition, "supported_execution_modes", None):
        raise ValueError("supported_execution_modes must not be empty")

    normalized_modes: list[ExecutionMode] = []
    for mode in definition.supported_execution_modes:
        if isinstance(mode, ExecutionMode):
            normalized_modes.append(mode)
            continue
        # allow strings to be provided
        try:
            normalized_modes.append(ExecutionMode.normalize(mode))
        except Exception as exc:
            raise ValueError(f"Unsupported execution mode: {mode!r}") from exc

    definition.supported_execution_modes = normalized_modes

    _ensure_unique(
        [variant.variant_id for variant in definition.variants],
        label="variant_id",
        attack_id=definition.attack_id,
    )
    for variant in definition.variants:
        validate_attack_variant(variant)

    return definition


def validate_attack_library(definitions: Iterable[AttackDefinition]) -> list[AttackDefinition]:
    """Validate a collection of attack definitions and return them as a list."""

    validated = [validate_attack_definition(definition) for definition in definitions]
    _ensure_unique(
        [definition.attack_id for definition in validated],
        label="attack_id",
        attack_id="library",
    )
    return validated


def normalize_category(category: str | AttackCategory) -> AttackCategory:
    return AttackCategory.normalize(category)


def normalize_technique(technique: str | AttackTechnique) -> AttackTechnique:
    return AttackTechnique.normalize(technique)


def normalize_severity(severity: str | AttackSeverity) -> AttackSeverity:
    return AttackSeverity.normalize(severity)
