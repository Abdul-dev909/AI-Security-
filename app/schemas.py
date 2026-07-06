"""Pydantic models used for API requests and responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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

    model_config = ConfigDict(json_schema_extra={"example": {"response": "Hello!"}})

    response: str = Field(description="Assistant reply returned by Ollama.")


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

