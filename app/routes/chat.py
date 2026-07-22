"""Chat endpoint."""

import logging

from fastapi import APIRouter, Body, Depends, Request, status

from app.agent import AgentRequest, AgentRuntime
from app.conversation import ConversationManager
from app.detection import DetectionCoordinator
from app.detection.models import DetectionContext
from app.schemas import ChatRequest, ChatResponse

from app.ollama_client import generate_chat_response

router = APIRouter()
logger = logging.getLogger(__name__)



def get_agent_runtime(request: Request) -> AgentRuntime:
    """Return the shared Agent Runtime stored on the FastAPI app."""
    return request.app.state.agent_runtime


def get_conversation_manager(request: Request) -> ConversationManager:
    """Return the shared conversation manager stored on the FastAPI app."""
    return request.app.state.conversation_manager


def get_detection_coordinator(request: Request) -> DetectionCoordinator:
    """Return the shared detection coordinator stored on the FastAPI app."""
    return request.app.state.detection_coordinator


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
    agent_runtime: AgentRuntime = Depends(get_agent_runtime),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    detection_coordinator: DetectionCoordinator = Depends(get_detection_coordinator),
) -> ChatResponse:
    """Send a user message through the Agent Runtime staged pipeline."""
    logger.info("User message received via Chat API: %s", request.message)

    agent_req = AgentRequest(user_prompt=request.message)
    agent_resp = agent_runtime.process_request(agent_req)

    context = DetectionContext(
        user_prompt=request.message,
        ai_response=agent_resp.response_text,
        conversation_history=conversation_manager.get_messages(),
    )
    report = detection_coordinator.run_detection(context)

    return ChatResponse(
        response=agent_resp.response_text,
        history=conversation_manager.get_messages(),
        detection=report,
    )
