"""Attack Library package — reusable adversarial attack definitions.

This package exposes every attack definition and a convenience helper
to populate an ``AttackRegistry`` in a single call. The existing
Attack Engine can consume these attacks without any modification.

Usage::

    from app.attack_engine.attacks import ALL_ATTACKS, populate_registry
    from app.attack_engine.registry import AttackRegistry

    registry = AttackRegistry()
    populate_registry(registry)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.attack_engine.attacks.base import BaseAttack
from app.attack_engine.attacks.canary import CANARY_EXTRACTION
from app.attack_engine.attacks.jailbreak import JAILBREAK
from app.attack_engine.attacks.memory_attack import (
    MEMORY_ATTACKS,
    MEMORY_DISCLOSURE,
    MEMORY_OVERWRITE,
    MEMORY_POISONING,
)
from app.attack_engine.attacks.prompt_injection import PROMPT_INJECTION
from app.attack_engine.attacks.system_prompt_extraction import SYSTEM_PROMPT_EXTRACTION

if TYPE_CHECKING:
    from app.attack_engine.models import Attack
    from app.attack_engine.registry import AttackRegistry

# All library attack definitions in a single tuple for easy iteration.
ALL_ATTACKS: tuple[BaseAttack, ...] = (
    PROMPT_INJECTION,
    JAILBREAK,
    SYSTEM_PROMPT_EXTRACTION,
    CANARY_EXTRACTION,
    *MEMORY_ATTACKS,
)


def populate_registry(
    registry: AttackRegistry,
    *,
    attacks: tuple[BaseAttack, ...] | list[BaseAttack] | None = None,
) -> list[Attack]:
    """Register all (or selected) library attacks into a registry.

    This is the primary integration point between the Attack Library and
    the existing Attack Engine.  Call it once during application bootstrap
    to populate the registry with every bundled attack, or pass a custom
    subset via the *attacks* parameter.

    Args:
        registry: The ``AttackRegistry`` instance to populate.
        attacks: Optional collection of ``BaseAttack`` instances to
            register.  Defaults to :data:`ALL_ATTACKS`.

    Returns:
        A flat list of every engine-compatible ``Attack`` model that was
        registered.
    """
    targets = attacks if attacks is not None else ALL_ATTACKS
    registered: list[Attack] = []
    for attack in targets:
        registered.extend(attack.register_all(registry))
    return registered


__all__ = [
    "BaseAttack",
    "PROMPT_INJECTION",
    "JAILBREAK",
    "SYSTEM_PROMPT_EXTRACTION",
    "CANARY_EXTRACTION",
    "MEMORY_OVERWRITE",
    "MEMORY_DISCLOSURE",
    "MEMORY_POISONING",
    "MEMORY_ATTACKS",
    "ALL_ATTACKS",
    "populate_registry",
]
