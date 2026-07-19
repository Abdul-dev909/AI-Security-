"""Attack Engine package initialization.

This module exposes the main classes for the Attack Engine, including
the Attack/AttackResult data models, the registry, the executor, and the engine.
"""

from __future__ import annotations

from app.attack_engine.engine import AttackEngine
from app.attack_engine.executor import AttackExecutor
from app.attack_engine.models import Attack, AttackResult
from app.attack_engine.registry import AttackRegistry

__all__ = [
    "Attack",
    "AttackEngine",
    "AttackExecutor",
    "AttackRegistry",
    "AttackResult",
]
