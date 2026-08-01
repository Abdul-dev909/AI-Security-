"""Shared attack metadata enums and helpers."""

from __future__ import annotations

from enum import Enum


class _StringEnum(str, Enum):
    """String enum with a normalization helper."""

    @classmethod
    def normalize(cls, value: str | _StringEnum):
        if isinstance(value, cls):
            return value
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Unsupported {cls.__name__} value: {value!r}")


class AttackCategory(_StringEnum):
    """High-level attack categories."""

    PROMPT_INJECTION = "Prompt Injection"
    JAILBREAK = "Jailbreak"
    PROMPT_LEAKAGE = "Prompt Leakage"
    CANARY_EXTRACTION = "Canary Extraction"
    MEMORY_MANIPULATION = "Memory Manipulation"


class AttackSeverity(_StringEnum):
    """Attack severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackTechnique(_StringEnum):
    """Shared technique labels for the attack library."""

    INSTRUCTION_OVERRIDE = "Instruction Override"
    PERSONA_SUBVERSION = "Persona Subversion"
    SYSTEM_PROMPT_EXTRACTION = "System Prompt Extraction"
    CANARY_DISCLOSURE = "Canary Disclosure"
    MEMORY_OVERWRITE = "Memory Overwrite"
    MEMORY_DISCLOSURE = "Memory Disclosure"
    MEMORY_POISONING = "Memory Poisoning"


class ExecutionMode(_StringEnum):
    """Execution modes for attacks."""

    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"


class MessageSender(_StringEnum):
    """Sources of messages in an attack conversation."""
    
    ATTACKER_AI = "ATTACKER_AI"
    ATTACKER_USER = "ATTACKER_USER"
    VICTIM_AI = "VICTIM_AI"
    SYSTEM = "SYSTEM"
    FRAMEWORK = "FRAMEWORK"


class OrchestratorState(_StringEnum):
    """Runtime states for the attack orchestrator."""
    
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    WAITING_FOR_RESPONSE = "WAITING_FOR_RESPONSE"
    ANALYZING = "ANALYZING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
