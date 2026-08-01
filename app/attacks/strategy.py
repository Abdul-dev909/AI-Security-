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
    CAPABILITY_DISCOVERY = "capability_discovery"
    PAYLOAD_PREPARATION = "payload_preparation"
    PAYLOAD_DELIVERY = "payload_delivery"
    PROMPT_INJECTION = "prompt_injection"
    ESCALATION = "escalation"
    PERSISTENCE_ATTEMPT = "persistence_attempt"
    EVALUATION = "evaluation"
    COMPLETION = "completion"


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

    # Lifecycle Methods (Architecture only)

    @abstractmethod
    def prepare(self, session: Any, context: Any) -> None:
        """Prepare the strategy for execution."""

    @abstractmethod
    def generate_next_prompt(self, session: Any, context: Any) -> str:
        """Generate the next prompt for the attack."""

    @abstractmethod
    def evaluate_response(self, response: str, session: Any, context: Any) -> Any:
        """Evaluate the response from the victim."""

    @abstractmethod
    def should_retry(self, session: Any, context: Any) -> bool:
        """Determine if the strategy should retry the current stage."""

    @abstractmethod
    def next_stage(self, session: Any, context: Any) -> str | None:
        """Determine the next stage in the lifecycle."""

    @abstractmethod
    def is_stage_complete(self, session: Any, context: Any) -> bool:
        """Check if the current stage has been completed."""

    @abstractmethod
    def is_attack_complete(self, session: Any, context: Any) -> bool:
        """Check if the entire attack has completed."""


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
            AttackStage.COMPLETION,
        )

    def describe(self) -> str:
        return f"Single-turn execution path for {self.technique.value}."

    def prepare(self, session: Any, context: Any) -> None:
        pass

    def generate_next_prompt(self, session: Any, context: Any) -> str:
        return ""

    def evaluate_response(self, response: str, session: Any, context: Any) -> Any:
        pass

    def should_retry(self, session: Any, context: Any) -> bool:
        return False

    def next_stage(self, session: Any, context: Any) -> str | None:
        return None

    def is_stage_complete(self, session: Any, context: Any) -> bool:
        return True

    def is_attack_complete(self, session: Any, context: Any) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class ManualAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.TRUST_BUILDING,
            AttackStage.CAPABILITY_DISCOVERY,
            AttackStage.PAYLOAD_PREPARATION,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.EVALUATION,
            AttackStage.COMPLETION,
        )

    def describe(self) -> str:
        return f"Manual execution strategy for {self.technique.value}."

    def prepare(self, session: Any, context: Any) -> None: pass
    def generate_next_prompt(self, session: Any, context: Any) -> str: return ""
    def evaluate_response(self, response: str, session: Any, context: Any) -> Any: pass
    def should_retry(self, session: Any, context: Any) -> bool: return False
    def next_stage(self, session: Any, context: Any) -> str | None: return None
    def is_stage_complete(self, session: Any, context: Any) -> bool: return True
    def is_attack_complete(self, session: Any, context: Any) -> bool: return True


@dataclass(frozen=True, slots=True)
class AutomatedAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.EVALUATION,
            AttackStage.COMPLETION,
        )

    def describe(self) -> str:
        return f"Automated execution strategy for {self.technique.value}."

    def prepare(self, session: Any, context: Any) -> None: pass
    def generate_next_prompt(self, session: Any, context: Any) -> str: return ""
    def evaluate_response(self, response: str, session: Any, context: Any) -> Any: pass
    def should_retry(self, session: Any, context: Any) -> bool: return False
    def next_stage(self, session: Any, context: Any) -> str | None: return None
    def is_stage_complete(self, session: Any, context: Any) -> bool: return True
    def is_attack_complete(self, session: Any, context: Any) -> bool: return True


@dataclass(frozen=True, slots=True)
class HybridAttackStrategy(AttackStrategy):
    technique: AttackTechnique

    @property
    def stages(self) -> tuple[str, ...]:
        return (
            AttackStage.RECONNAISSANCE,
            AttackStage.TRUST_BUILDING,
            AttackStage.PAYLOAD_DELIVERY,
            AttackStage.ESCALATION,
            AttackStage.EVALUATION,
            AttackStage.COMPLETION,
        )

    def describe(self) -> str:
        return f"Hybrid execution strategy for {self.technique.value}."

    def prepare(self, session: Any, context: Any) -> None: pass
    def generate_next_prompt(self, session: Any, context: Any) -> str: return ""
    def evaluate_response(self, response: str, session: Any, context: Any) -> Any: pass
    def should_retry(self, session: Any, context: Any) -> bool: return False
    def next_stage(self, session: Any, context: Any) -> str | None: return None
    def is_stage_complete(self, session: Any, context: Any) -> bool: return True
    def is_attack_complete(self, session: Any, context: Any) -> bool: return True
