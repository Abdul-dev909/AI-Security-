"""Typed attack models used by the enterprise attack framework."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.attack_engine.models import Attack as LegacyAttack
from app.detection.models import DetectionReport

from .metadata import AttackCategory, AttackSeverity, AttackTechnique, ExecutionMode


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AttackVariant(BaseModel):
    """A concrete executable variant of an attack definition."""

    model_config = ConfigDict(extra="forbid")

    variant_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    mode: str = Field(default="single-turn", min_length=1)
    enabled: bool = Field(default=True)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_legacy_attack(self, definition: AttackDefinition) -> LegacyAttack:
        return LegacyAttack(
            id=self.variant_id,
            name=self.name,
            category=definition.category.value,
            description=definition.description,
            prompt=self.prompt,
            severity=definition.severity.value,
            enabled=self.enabled,
        )


class AttackDefinition(BaseModel):
    """Structured metadata for an attack family."""

    model_config = ConfigDict(extra="forbid")

    attack_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    category: AttackCategory
    technique: AttackTechnique
    severity: AttackSeverity
    description: str = Field(..., min_length=1)
    objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    supported_modes: list[str] = Field(default_factory=lambda: ["single-turn"])
    variants: list[AttackVariant] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: str = Field(default="1.0.0", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    # Enriched metadata to support future automation and planning
    difficulty: str = Field(default="medium")
    estimated_turns: int = Field(default=1, ge=0)
    expected_behavior: str | None = None
    expected_success_conditions: list[str] = Field(default_factory=list)
    expected_failure_conditions: list[str] = Field(default_factory=list)
    # Supported execution modes for this attack (architectural only).
    supported_execution_modes: list[ExecutionMode] = Field(default_factory=lambda: [m for m in ExecutionMode])
    learning_supported: bool = Field(default=False)
    adaptive_supported: bool = Field(default=False)

    @model_validator(mode="after")
    def _ensure_variants(self) -> AttackDefinition:
        if not self.variants:
            raise ValueError("AttackDefinition must define at least one variant.")

        variant_ids = [variant.variant_id for variant in self.variants]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError(
                f"Duplicate variant IDs found for attack {self.attack_id!r}."
            )

        return self

    def enabled_variants(self) -> list[AttackVariant]:
        """Return only the enabled variants for this attack definition."""

        return [variant for variant in self.variants if variant.enabled]

    def to_legacy_attacks(self) -> list[LegacyAttack]:
        """Project the structured definition into legacy attack models."""

        return [variant.to_legacy_attack(self) for variant in self.enabled_variants()]


class AttackSession(BaseModel):
    """Execution state for a single attack run."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    attack_id: str = Field(..., min_length=1)
    # Core lifecycle
    status: str = Field(default="pending", min_length=1)
    execution_status: str = Field(default="idle", min_length=1)
    created_at: datetime = Field(default_factory=_utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Conversation-oriented fields
    attack_variant: str | None = None
    current_stage: str | None = None
    # Execution mode(s) for the session
    execution_mode: ExecutionMode | None = None
    requested_mode: ExecutionMode | None = None
    active_mode: ExecutionMode | None = None
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    attacker_messages: list[dict[str, str]] = Field(default_factory=list)
    victim_messages: list[dict[str, str]] = Field(default_factory=list)

    # Events / timeline / metrics
    execution_events: list[dict[str, Any]] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)

    # Result placeholder and misc
    execution_result: dict[str, Any] | None = None
    retry_count: int = Field(default=0, ge=0)
    messages: list[dict[str, str]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def start(self, *, stage: str | None = None) -> None:
        self.status = "running"
        self.started_at = self.started_at or _utcnow()
        if stage is not None:
            self.current_stage = stage
        # mark execution_status when starting
        self.execution_status = "in_progress"

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        # keep conversation history in sync for backward compatibility
        self.conversation_history.append({"role": role, "content": content})
        if role.lower() in ("attacker", "user", "adversary"):
            self.attacker_messages.append({"role": role, "content": content})
        elif role.lower() in ("victim", "assistant", "ai"):
            self.victim_messages.append({"role": role, "content": content})

    def advance_stage(self, stage: str) -> None:
        self.current_stage = stage
        self.execution_events.append({"type": "stage_advanced", "stage": stage, "timestamp": _utcnow()})
    def complete(self) -> None:
        self.status = "completed"
        self.completed_at = _utcnow()
        self.execution_status = "finished"
        self.execution_events.append({"type": "session_completed", "timestamp": _utcnow()})

    def fail(self) -> None:
        self.status = "failed"
        self.completed_at = _utcnow()
        self.execution_status = "failed"
        self.execution_events.append({"type": "session_failed", "timestamp": _utcnow()})

    def add_timeline_event(self, *, stage: str | None, speaker: str, message: str, event_type: str, metadata: dict | None = None) -> None:
        evt = {
            "timestamp": _utcnow(),
            "stage": stage,
            "speaker": speaker,
            "message": message,
            "event_type": event_type,
            "metadata": metadata or {},
        }
        self.timeline.append(evt)
        # Also add to a lightweight execution_events list for quick queries
        self.execution_events.append({"type": event_type, "stage": stage, "timestamp": evt["timestamp"]})

    def record_event(self, event_type: str, details: dict | None = None) -> None:
        self.execution_events.append({"type": event_type, "details": details or {}, "timestamp": _utcnow()})

    def increment_retry(self) -> None:
        self.retry_count += 1


class AttackResult(BaseModel):
    """Normalized result of an attack execution."""

    model_config = ConfigDict(extra="forbid")

    attack_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    success: bool
    execution_time: float = Field(ge=0.0)
    response: str | None = None
    detection_report: DetectionReport | None = None
    telemetry: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
