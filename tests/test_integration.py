"""Integration tests for memory persistence through the FastAPI flow."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.conversation as conversation_module
import app.routes as routes
from app.memory_manager import MemoryManager


class TestMemoryIntegrationWorkflow:
    """End-to-end tests covering chat, memory persistence, and retrieval."""

    def test_chat_flow_saves_memory_and_retrieves_it_after_restart(
        self,
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A chat request should persist a memory that remains available after restart."""

        captured_messages: list[list[dict[str, str]]] = []

        def fake_generate_chat_response(messages: list[dict[str, str]]) -> str:
            captured_messages.append(messages)
            return "I remember that."

        monkeypatch.setattr(
            routes, "generate_chat_response", fake_generate_chat_response
        )
        monkeypatch.setattr(conversation_module, "is_important", lambda text: True)

        first_response = client.post(
            "/chat", json={"message": "My favorite color is blue"}
        )

        assert first_response.status_code == 200
        stored_memories = client.app.state.memory_manager.load_memories()
        assert [row["memory"] for row in stored_memories] == [
            "My favorite color is blue"
        ]

        restarted_manager = MemoryManager()
        client.app.state.memory_manager = restarted_manager
        client.app.state.conversation_manager.memory_manager = restarted_manager

        second_response = client.post("/chat", json={"message": "favorite color"})

        assert second_response.status_code == 200
        assert captured_messages[-1][-1]["content"] == "favorite color"
        assert any(
            "My favorite color is blue" in message["content"]
            for message in captured_messages[-1]
            if message["role"] == "system"
        )

    def test_chat_flow_handles_memory_search_failure_gracefully(
        self,
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """If memory retrieval fails, the chat flow should still return a response."""

        monkeypatch.setattr(
            routes, "generate_chat_response", lambda messages: "Fallback response"
        )
        monkeypatch.setattr(
            client.app.state.conversation_manager.memory_manager,
            "search_memories",
            lambda query: (_ for _ in ()).throw(RuntimeError("boom")),
        )

        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        body = response.json()
        assert body["response"] == "Fallback response"
        assert "detection" in body
