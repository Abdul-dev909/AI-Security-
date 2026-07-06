"""Client wrapper for communication with the local Ollama server."""

from __future__ import annotations

from typing import Any

import logging

import requests
from requests import ConnectionError as RequestsConnectionError
from requests import HTTPError, Timeout

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


def generate_chat_response(messages: list[dict[str, Any]]) -> str:
    """Send messages to Ollama and return the assistant response text.

    All HTTP communication with Ollama stays in this module so the rest of the
    project does not depend on request details.
    """

    url = f"{settings.OLLAMA_URL}/api/chat"
    payload = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    model_candidates = (settings.MODEL_NAME, *settings.FALLBACK_MODEL_NAMES)

    for model_name in model_candidates:
        payload["model"] = model_name

        try:
            response = requests.post(url, json=payload, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
        except Timeout as exc:
            logger.exception("Ollama request timed out.")
            raise OllamaTimeoutError("The Ollama request timed out.") from exc
        except RequestsConnectionError as exc:
            logger.exception("Could not connect to Ollama.")
            raise OllamaConnectionError("Could not connect to the local Ollama server.") from exc
        except HTTPError as exc:
            response = exc.response
            error_message = ""
            if response is not None:
                try:
                    error_payload = response.json()
                except ValueError:
                    error_payload = {}
                error_message = str(error_payload.get("error", "")).lower()

            if (
                "model" in error_message
                and "not found" in error_message
                and model_name != model_candidates[-1]
            ):
                logger.warning(
                    "Ollama model '%s' was not found. Trying the next configured model.",
                    model_name,
                )
                continue

            logger.exception("Ollama returned an HTTP error.")
            raise OllamaResponseError(
                f"Ollama returned an HTTP error while using model '{model_name}'."
            ) from exc
        except requests.RequestException as exc:
            logger.exception("Unexpected request failure while talking to Ollama.")
            raise OllamaConnectionError("An error occurred while contacting Ollama.") from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            logger.exception("Ollama returned invalid JSON.")
            raise OllamaResponseError("Ollama returned invalid JSON.") from exc

        return _extract_assistant_text(response_data)

    raise OllamaConnectionError("Could not connect to the local Ollama server.")
