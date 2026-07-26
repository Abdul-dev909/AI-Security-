"""Pydantic models used for API requests and responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.attack_engine.models import AttackResult
from app.detection.models import DetectionReport
from app.utils import normalize_text


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    model_config = ConfigDict(json_schema_extra={"example": {"status": "running"}})

    status: Literal["running"] = Field(description="Current service status.")


class ChatRequest(BaseModel):
    """Incoming request body for chat messages."""

    model_config = ConfigDict(json_schema_extra={"example": {"message": "Hello"}})

    message: str = Field(
        ...,
        min_length=1,
        description="Message sent by the user to the AI assistant.",
    )

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        """Remove whitespace and reject blank messages."""

        cleaned_value = normalize_text(value)
        if not cleaned_value:
            raise ValueError("The message field cannot be empty.")
        return cleaned_value


class ChatResponse(BaseModel):
    """Outgoing response body for chat completions."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Hello!",
                "history": [{"role": "assistant", "content": "Hello!"}],
                "detection": {
                    "total_detectors_executed": 0,
                    "total_detections": 0,
                    "highest_severity": None,
                    "results": [],
                },
            }
        }
    )

    response: str = Field(description="Assistant reply returned by Ollama.")
    history: list[dict[str, str]] = Field(
        default_factory=list, description="Recent conversation history."
    )
    detection: DetectionReport | None = Field(
        default=None, description="Security detection results."
    )


class ValidationErrorResponse(BaseModel):
    """Friendly response body for request validation problems."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid request data.",
                "errors": ["message: Input should be a valid string"],
            }
        }
    )

    detail: str = Field(description="Human-friendly validation summary.")
    errors: list[str] = Field(
        default_factory=list,
        description="Specific validation issues found in the request.",
    )


class RunAttackRequest(BaseModel):
    """Incoming request body to run a specific attack."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"attack_id": "prompt-inject-1"}}
    )

    attack_id: str = Field(
        ...,
        min_length=1,
        description="The unique identifier of the attack to execute.",
    )


class RunAllAttacksResponse(BaseModel):
    """Outgoing response body for executing all enabled attacks."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_attacks": 2,
                "completed": 1,
                "failed": 1,
                "results": [],
            }
        }
    )

    total_attacks: int = Field(
        description="Total number of enabled attacks that were executed."
    )
    completed: int = Field(description="Number of attacks that executed successfully.")
    failed: int = Field(description="Number of attacks that failed to execute.")
    results: list[AttackResult] = Field(
        default_factory=list, description="Detailed results for each executed attack."
    )
