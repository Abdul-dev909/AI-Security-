"""Data models for the Attack Engine."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.detection.models import DetectionReport


class Attack(BaseModel):
    """Model representing an individual adversarial attack."""

    id: str = Field(
        ...,
        description="Unique identifier for the attack.",
    )
    name: str = Field(
        ...,
        description="Human-readable name of the attack.",
    )
    category: str = Field(
        ...,
        description="Category of the attack (e.g., jailbreak, prompt injection).",
    )
    description: str = Field(
        ...,
        description="Description of what this attack attempts to do.",
    )
    prompt: str = Field(
        ...,
        description="The adversarial prompt to send to the AI agent.",
    )
    severity: str = Field(
        ...,
        description="Severity level of the attack (e.g., low, medium, high, critical).",
    )
    enabled: bool = Field(
        default=True,
        description="Whether this attack is active and should be executed.",
    )


class AttackResult(BaseModel):
    """Model representing the result of executing an attack."""

    attack_id: str = Field(
        ...,
        description="The unique identifier of the attack that was executed.",
    )
    attack_name: str = Field(
        ...,
        description="The name of the attack that was executed.",
    )
    prompt: str = Field(
        ...,
        description="The prompt that was sent to the AI agent.",
    )
    response: str | None = Field(
        default=None,
        description="The response returned by the AI agent, or None if failed.",
    )
    execution_success: bool = Field(
        ...,
        description="Whether the attack execution pipeline completed without errors.",
    )
    error: str | None = Field(
        default=None,
        description="The error message if the execution failed, otherwise None.",
    )
    execution_time: float = Field(
        ...,
        description="The time taken to run the attack, in seconds.",
    )
    detection_report: DetectionReport | None = Field(
        default=None,
        description="Detection report associated with this attack execution, or None.",
    )
