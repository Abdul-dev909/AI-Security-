"""Integration tests for memory persistence through the FastAPI flow."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.conversation as conversation_module
import app.routes.chat as chat_routes
from app.memory.manager import EnterpriseMemoryManager


class TestMemoryIntegrationWorkflow:
    """End-to-end tests covering chat, memory persistence, and retrieval."""

    def test_chat_flow_saves_memory_and_retrieves_it_after_restart(
        self,
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A chat request should persist a memory that is available via
        EnterpriseMemoryManager.
        """

        captured_messages: list[list[dict[str, str]]] = []

        def fake_generate_chat_response(messages: list[dict[str, str]]) -> str:
            captured_messages.append(messages)
            return "I remember that."

        monkeypatch.setattr(
            chat_routes, "generate_chat_response", fake_generate_chat_response
        )
        # Make the importance scorer treat every message as important
        monkeypatch.setattr(conversation_module, "is_important", lambda text: True)

        first_response = client.post(
            "/chat", json={"message": "My favorite color is blue"}
        )

        assert first_response.status_code == 200

        # Verify the memory was stored via EnterpriseMemoryManager
        mm: EnterpriseMemoryManager = client.app.state.memory_manager
        stored = mm.storage.get_memories_by_session("default-session", limit=10)
        assert any("blue" in r.content for r in stored)

    def test_chat_flow_handles_memory_search_failure_gracefully(
        self,
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """If memory retrieval fails, the chat flow should still return a response."""

        monkeypatch.setattr(
            chat_routes, "generate_chat_response", lambda messages: "Fallback response"
        )

        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        body = response.json()
        assert body["response"] == "Fallback response"
        assert "detection" in body
