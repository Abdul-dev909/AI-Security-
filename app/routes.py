"""API routes for the AI Agent application.

The router keeps HTTP concerns separate from app startup so the project stays
easy to extend when new endpoints are added later.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Body, Depends, Request, status

from app.config import settings
from app.conversation import ConversationManager
from app.detection import DetectionCoordinator
from app.detection.models import DetectionContext
from app.ollama_client import (
    OllamaClientError,
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
    generate_chat_response,
)
from app.prompts import PromptBuilder
from app.schemas import ChatRequest, ChatResponse, HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_conversation_manager(request: Request) -> ConversationManager:
    """Return the shared conversation manager stored on the FastAPI app."""

    return request.app.state.conversation_manager


def get_prompt_builder(request: Request) -> PromptBuilder:
    """Return the shared prompt builder stored on the FastAPI app."""

    return request.app.state.prompt_builder


def get_detection_coordinator(request: Request) -> DetectionCoordinator:
    """Return the shared detection coordinator stored on the FastAPI app."""

    return request.app.state.detection_coordinator


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check whether the API is running",
    description=(
        "Use this endpoint to confirm that the FastAPI application is online.\n\n"
        "Example request:\n"
        "GET /health\n\n"
        "Example response:\n"
        '{"status": "running"}\n\n'
        "Status codes:\n"
        "200 OK"
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "The API is running normally.",
            "content": {
                "application/json": {
                    "example": {"status": "running"},
                }
            },
        }
    },
)
def health_check() -> HealthResponse:
    """Return a simple status payload so users can verify the server is up."""

    return HealthResponse(status="running")


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the local AI model",
    description=(
        "Send a chat message to the local Ollama server and receive the model's\n"
        "reply. The route uses the prompt builder first, then sends the final\n"
        "message list to the Ollama client.\n\n"
        "Example request:\n"
        '{"message": "Hello"}\n\n'
        "Example response:\n"
        '{"response": "Hello! How can I help you today?"}\n\n'
        "Status codes:\n"
        "200 OK, 422 Unprocessable Entity, 503 Service Unavailable"
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "The assistant returned a chat response.",
            "content": {
                "application/json": {
                    "example": {"response": "Hello! How can I help you today?"},
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body failed validation.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The local Ollama server is unavailable.",
        },
    },
)
def chat(
    request: ChatRequest = Body(
        ...,
        description="User message sent to the AI assistant.",
    ),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    detection_coordinator: DetectionCoordinator = Depends(get_detection_coordinator),
) -> ChatResponse:
    """Send a user message to Ollama and return the assistant response."""

    logger.info("User message received: %s", request.message)
    messages = conversation_manager.build_messages(prompt_builder, request.message)

    try:
        response_text = generate_chat_response(messages)
    except (
        OllamaTimeoutError,
        OllamaConnectionError,
        OllamaResponseError,
        OllamaClientError,
    ) as exc:
        logger.warning(
            "Falling back to a graceful response because Ollama failed: %s", exc
        )
        response_text = settings.FALLBACK_RESPONSE

    conversation_manager.add_user_message(request.message)
    conversation_manager.add_assistant_message(response_text)
    conversation_manager.save_memory_if_important(request.message)
    logger.info("Assistant response sent: %s", response_text)

    context = DetectionContext(
        user_prompt=request.message,
        ai_response=response_text,
        conversation_history=conversation_manager.get_messages(),
    )
    report = detection_coordinator.run_detection(context)

    return ChatResponse(
        response=response_text,
        history=conversation_manager.get_messages(),
        detection=report,
    )
