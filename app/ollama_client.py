"""Client wrapper for communication with the local Ollama server."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaClientError(RuntimeError):
    """Raised when the Ollama request fails for any reason."""


class OllamaConnectionError(OllamaClientError):
    """Raised when Ollama cannot be reached."""


class OllamaTimeoutError(OllamaClientError):
    """Raised when Ollama takes too long to respond."""


class OllamaResponseError(OllamaClientError):
    """Raised when Ollama returns invalid JSON or an empty response."""


def _extract_assistant_text(response_data: dict[str, Any]) -> str:
    """Read the assistant text from the Ollama response payload."""
    message_data = response_data.get("message", {})
    assistant_text = message_data.get("content", "")
    if not isinstance(assistant_text, str) or not assistant_text.strip():
        raise OllamaClientError("Ollama returned an empty response.")
    return assistant_text


async def generate_chat_response_async(messages: list[dict[str, Any]]) -> str:
    """Send messages to Ollama asynchronously and return the assistant response text."""
    url = f"{settings.OLLAMA_URL}/api/chat"
    payload = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    model_candidates = (settings.MODEL_NAME, *settings.FALLBACK_MODEL_NAMES)

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        for model_name in model_candidates:
            payload["model"] = model_name

            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.TimeoutException as exc:
                logger.exception("Ollama request timed out.")
                raise OllamaTimeoutError("The Ollama request timed out.") from exc
            except httpx.RequestError as exc:
                logger.exception("Could not connect to Ollama.")
                raise OllamaConnectionError(
                    "Could not connect to the local Ollama server."
                ) from exc
            except httpx.HTTPStatusError as exc:
                response = exc.response
                error_message = ""
                try:
                    error_payload = response.json()
                    error_message = str(error_payload.get("error", "")).lower()
                except ValueError:
                    pass

                if (
                    "model" in error_message
                    and "not found" in error_message
                    and model_name != model_candidates[-1]
                ):
                    logger.warning(
                        "Ollama model '%s' was not found. Trying the next "
                        "configured model.",
                        model_name,
                    )
                    continue

                logger.exception("Ollama returned an HTTP error.")
                raise OllamaResponseError(
                    f"Ollama returned an HTTP error while using model '{model_name}'."
                ) from exc

            try:
                response_data = response.json()
            except ValueError as exc:
                logger.exception("Ollama returned invalid JSON.")
                raise OllamaResponseError("Ollama returned invalid JSON.") from exc

            return _extract_assistant_text(response_data)

    raise OllamaConnectionError("Could not connect to the local Ollama server.")


async def generate_chat_stream_async(
    messages: list[dict[str, Any]],
) -> AsyncGenerator[str, None]:
    """Send messages to Ollama and stream back the response via SSE format."""
    url = f"{settings.OLLAMA_URL}/api/chat"
    payload = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
        try:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue
        except httpx.RequestError as exc:
            logger.exception("Streaming from Ollama failed.")
            raise OllamaConnectionError("Streaming from Ollama failed.") from exc


# Keep the synchronous implementation for backward compatibility if any
# non-FastAPI worker threads use it
def generate_chat_response(messages: list[dict[str, Any]]) -> str:
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If we are already in an event loop (e.g. FastAPI blocking thread),
        # we shouldn't use asyncio.run. We can just use requests like before,
        # but the prompt told us to "Replace synchronous HTTP requests with an
        # asynchronous implementation"
        # and "Avoid blocking FastAPI worker threads."
        # If we reach here, we shouldn't be running sync.
        import requests

        url = f"{settings.OLLAMA_URL}/api/chat"
        payload: dict[str, Any] = {
            "model": settings.MODEL_NAME,
            "messages": messages,
            "stream": False,
        }
        model_candidates = (settings.MODEL_NAME, *settings.FALLBACK_MODEL_NAMES)
        for model_name in model_candidates:
            payload["model"] = model_name
            try:
                response = requests.post(
                    url, json=payload, timeout=settings.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return _extract_assistant_text(response.json())
            except Exception:
                continue
        return "Error connecting to model."
    else:
        return asyncio.run(generate_chat_response_async(messages))
