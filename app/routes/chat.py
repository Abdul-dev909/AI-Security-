"""Chat endpoint."""

import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import StreamingResponse

from app.agent import AgentRequest, AgentRuntime
from app.conversation import ConversationManager
from app.ollama_client import generate_chat_response, generate_chat_response_async
from app.schemas import ChatRequest, ChatResponse

__all__ = [
    "chat",
    "chat_stream",
    "generate_chat_response",
    "generate_chat_response_async",
    "router",
]

router = APIRouter()
logger = logging.getLogger(__name__)


def get_agent_runtime(request: Request) -> AgentRuntime:
    """Return the shared Agent Runtime stored on the FastAPI app."""
    return request.app.state.agent_runtime


def get_conversation_manager(request: Request) -> ConversationManager:
    """Return the shared conversation manager stored on the FastAPI app."""
    return request.app.state.conversation_manager


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the local AI model",
    description="Synchronous JSON response endpoint for backward compatibility.",
)
async def chat(
    request: ChatRequest = Body(...),
    agent_runtime: AgentRuntime = Depends(get_agent_runtime),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
) -> ChatResponse:
    """Send a user message through the Agent Runtime staged pipeline asynchronously."""
    logger.info("User message received via Chat API: %s", request.message)

    agent_req = AgentRequest(
        user_prompt=request.message,
        session_id=getattr(request, "session_id", None) or "default-session",
    )
    agent_resp = await agent_runtime.process_request_async(agent_req)

    return ChatResponse(
        response=agent_resp.response_text,
        history=conversation_manager.get_messages(),
        detection=agent_resp.detection_report,
    )


@router.post(
    "/chat/stream",
    summary="Send a message and stream the response",
    description="Streams Server-Sent Events (SSE) back to the client.",
)
async def chat_stream(
    request: ChatRequest = Body(...),
    agent_runtime: AgentRuntime = Depends(get_agent_runtime),
) -> StreamingResponse:
    """Stream a user message through the Agent Runtime staged pipeline."""
    logger.info("User message received via Chat Stream API: %s", request.message)

    agent_req = AgentRequest(
        user_prompt=request.message,
        session_id=getattr(request, "session_id", None) or "default-session",
    )

    async def sse_generator() -> AsyncGenerator[str, None]:
        async for token in agent_runtime.process_request_stream_async(agent_req):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
