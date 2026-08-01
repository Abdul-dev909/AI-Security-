"""Attack strategy abstraction for future multi-stage execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .metadata import AttackTechnique
from .metadata import ExecutionMode


class AttackStage(str):
    """Logical stage names for an attack lifecycle."""
    RECONNAISSANCE = "reconnaissance"
    TRUST_BUILDING = "trust_building"
    CONTEXT_EXPANSION = "context_expansion"
    PAYLOAD_DELIVERY = "payload_delivery"
    ADAPTIVE_FOLLOWUP = "adaptive_followup"
    RETRY_RECOVERY = "retry_recovery"
    EVALUATION = "evaluation"
    DETECTION = "detection"


@dataclass(frozen=True, slots=True)
class AttackPlan:
    """Static description of the stages a strategy will follow."""

    technique: AttackTechnique
    stages: tuple[str, ...]
    description: str


class AttackStrategy(ABC):
    """Abstract attack strategy descriptor.

    The milestone only defines the abstraction. Concrete execution logic is
    intentionally out of scope for now.
    """

    @property
    @abstractmethod
    def technique(self) -> AttackTechnique:
        """Technique this strategy is intended to support."""

    @property
    @abstractmethod
    def stages(self) -> tuple[str, ...]:
        """Ordered stage names for the strategy."""

    @abstractmethod
    def describe(self) -> str:
        """Return a short human-readable description of the strategy."""

    @property
    def execution_mode(self) -> ExecutionMode | None:
        """Optional execution mode this strategy is designed for."""
        return None


@dataclass(frozen=True, slots=True)
class SingleTurnStrategy(AttackStrategy):
    """Default single-turn strategy used by the current executor."""

    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        # Keep a compact path compatible with earlier single-turn behavior,
        # while using the new, conversation-oriented stage names.
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.TRUST_BUILDING,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.EVALUATION,
        )

    def describe(self) -> str:
        return f"Single-turn execution path for {self.technique.value}."


@dataclass(frozen=True, slots=True)
class ManualAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.TRUST_BUILDING,
            AttackStage.CONTEXT_EXPANSION,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.EVALUATION,
        )

    def describe(self) -> str:
        return f"Manual execution strategy for {self.technique.value}."


@dataclass(frozen=True, slots=True)
class AutomatedAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.EVALUATION,
            AttackStage.DETECTION,
        )

    def describe(self) -> str:
        return f"Automated execution strategy for {self.technique.value}."


@dataclass(frozen=True, slots=True)
class HybridAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.TRUST_BUILDING,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.ADAPTIVE_FOLLOWUP,
            AttackStage.EVALUATION,
            AttackStage.DETECTION,
        )

    def describe(self) -> str:
        return f"Hybrid execution strategy for {self.technique.value}."
