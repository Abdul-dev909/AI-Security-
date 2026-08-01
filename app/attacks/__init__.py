"""Enterprise attack framework package."""

from __future__ import annotations

from .executor import AttackExecutor
from .library import (
    ALL_ATTACK_DEFINITIONS,
    CANARY_EXTRACTION,
    JAILBREAK,
    MEMORY_DISCLOSURE,
    MEMORY_OVERWRITE,
    MEMORY_POISONING,
    PROMPT_INJECTION,
    SYSTEM_PROMPT_EXTRACTION,
    load_builtin_attacks,
)
from .metadata import AttackCategory, AttackSeverity, AttackTechnique
from .models import AttackDefinition, AttackResult, AttackSession, AttackVariant
from .registry import AttackRegistry
from .session import AttackSessionManager
from .strategy import AttackPlan, AttackStage, AttackStrategy, SingleTurnStrategy
from .validation import (
    normalize_category,
    normalize_severity,
    normalize_technique,
    validate_attack_definition,
    validate_attack_library,
    validate_attack_variant,
)

__all__ = [
    "ALL_ATTACK_DEFINITIONS",
    "AttackCategory",
    "AttackDefinition",
    "AttackExecutor",
    "AttackPlan",
    "AttackRegistry",
    "AttackResult",
    "AttackSession",
    "AttackSessionManager",
    "AttackSeverity",
    "AttackStage",
    "AttackStrategy",
    "AttackTechnique",
    "AttackVariant",
    "CANARY_EXTRACTION",
    "JAILBREAK",
    "MEMORY_DISCLOSURE",
    "MEMORY_OVERWRITE",
    "MEMORY_POISONING",
    "PROMPT_INJECTION",
    "SingleTurnStrategy",
    "SYSTEM_PROMPT_EXTRACTION",
    "load_builtin_attacks",
    "normalize_category",
    "normalize_severity",
    "normalize_technique",
    "validate_attack_definition",
    "validate_attack_library",
    "validate_attack_variant",
]
