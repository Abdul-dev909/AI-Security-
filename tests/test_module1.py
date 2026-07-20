"""Tests for Module 1 of the AI Agent project."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.database as database
import app.routes.chat as chat_routes
from app.config import settings
from app.conversation import ConversationManager
from app.main import app
from app.memory_manager import MemoryManager
from app.ollama_client import OllamaConnectionError, OllamaTimeoutError
from app.prompts import PromptBuilder


@pytest.fixture()
def memory_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryManager:
    """Create a temporary database-backed MemoryManager for tests."""

    test_database_path = tmp_path / "memory.db"
    monkeypatch.setattr(database, "DB_PATH", test_database_path)
    database.initialize_database()
    return MemoryManager()


@pytest.fixture()
def client(memory_manager: MemoryManager) -> TestClient:
    """Create a fresh test client and clear conversation history."""

    with TestClient(app) as test_client:
        test_client.app.state.memory_manager = memory_manager
        test_client.app.state.conversation_manager.memory_manager = memory_manager
        test_client.app.state.conversation_manager.clear_history()
        yield test_client
        test_client.app.state.conversation_manager.clear_history()


def test_health_endpoint(client: TestClient) -> None:
    """The health endpoint should report that the service is running."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_chat_success(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The chat endpoint should return the model response and store history."""

    monkeypatch.setattr(
        chat_routes,
        "generate_chat_response",
        lambda messages: "Hello! How can I help you today?",
    )

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Hello! How can I help you today?"
    assert "detection" in body
    assert "history" in body
    assert client.app.state.conversation_manager.get_messages() == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hello! How can I help you today?"},
    ]


def test_chat_invalid_request_missing_message(client: TestClient) -> None:
    """A missing message field should fail validation."""

    response = client.post("/chat", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Invalid request data."
    assert body["errors"]


def test_chat_empty_message(client: TestClient) -> None:
    """An empty message should be rejected by the request model."""

    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Invalid request data."
    assert any("message" in error for error in body["errors"])


def test_chat_ollama_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When Ollama is unavailable, the API should return a graceful fallback."""

    def raise_connection_error(messages: list[dict[str, str]]) -> str:
        raise OllamaConnectionError("Could not connect to the local Ollama server.")

    monkeypatch.setattr(chat_routes, "generate_chat_response", raise_connection_error)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == settings.FALLBACK_RESPONSE
    assert "detection" in body


def test_chat_ollama_timeout_returns_fallback_message(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When Ollama times out, the API should return a graceful fallback response."""

    def raise_timeout_error(messages: list[dict[str, str]]) -> str:
        raise OllamaTimeoutError("The Ollama request timed out.")

    monkeypatch.setattr(chat_routes, "generate_chat_response", raise_timeout_error)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == settings.FALLBACK_RESPONSE
    assert "detection" in body


def test_conversation_manager_keeps_latest_messages(
    memory_manager: MemoryManager,
) -> None:
    """ConversationManager should store only the newest messages."""

    manager = ConversationManager(memory_manager=memory_manager, max_history=3)
    manager.add_user_message("First")
    manager.add_assistant_message("Second")
    manager.add_user_message("Third")
    manager.add_assistant_message("Fourth")

    assert manager.get_messages() == [
        {"role": "assistant", "content": "Second"},
        {"role": "user", "content": "Third"},
        {"role": "assistant", "content": "Fourth"},
    ]


def test_conversation_manager_clear_history(memory_manager: MemoryManager) -> None:
    """clear_history should remove all stored messages."""

    manager = ConversationManager(memory_manager=memory_manager, max_history=5)
    manager.add_user_message("Hello")
    manager.add_assistant_message("Hi")

    manager.clear_history()

    assert manager.get_messages() == []


def test_prompt_builder_uses_system_prompt_and_history(
    memory_manager: MemoryManager,
) -> None:
    """PromptBuilder should combine the system prompt, history, and new message."""

    manager = ConversationManager(memory_manager=memory_manager, max_history=5)
    manager.add_user_message("Earlier question")
    manager.add_assistant_message("Earlier answer")

    builder = PromptBuilder(
        system_prompt="You are a helpful AI assistant.", conversation_manager=manager
    )
    messages = builder.build_messages("New question")

    assert messages == [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Earlier question"},
        {"role": "assistant", "content": "Earlier answer"},
        {"role": "user", "content": "New question"},
    ]
