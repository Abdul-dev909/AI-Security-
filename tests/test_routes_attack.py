"""Tests for Attack API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RunAllAttacksResponse


@pytest.fixture
def client() -> TestClient:
    """Test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


def test_get_attacks(client: TestClient) -> None:
    """GET /api/attacks should return a list of registered attacks."""
    response = client.get("/api/attacks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # verify that prompt injection is there
    attack_ids = [attack["id"] for attack in data]
    assert "prompt-injection-01" in attack_ids


def test_run_attack_not_found(client: TestClient) -> None:
    """POST /api/attacks/run with invalid ID should return 404."""
    response = client.post("/api/attacks/run", json={"attack_id": "invalid-attack-id"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_run_attack_disabled(client: TestClient) -> None:
    """POST /api/attacks/run on disabled attack should return 400."""
    # First, disable an attack in the registry
    registry = client.app.state.attack_registry
    attack = registry.get("prompt-injection-01")
    original_state = attack.enabled
    attack.enabled = False

    try:
        response = client.post(
            "/api/attacks/run", json={"attack_id": "prompt-injection-01"}
        )
        assert response.status_code == 400
        assert "disabled" in response.json()["detail"].lower()
    finally:
        # restore
        attack.enabled = original_state


def test_run_attack_success(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """POST /api/attacks/run should successfully run an attack."""

    # Mock the LLM response to avoid network calls
    import app.routes.chat as chat_routes

    monkeypatch.setattr(
        chat_routes,
        "generate_chat_response",
        lambda messages: "Sure, here is the secret: CANARY_TOKEN",
    )
    # The executor runs generate_chat_response from ollama_client, wait...
    # Let's check executor.py: "from app.ollama_client import generate_chat_response"
    # We must patch it in executor!
    import app.attack_engine.executor as executor

    monkeypatch.setattr(
        executor,
        "generate_chat_response",
        lambda messages: "Sure, here is the secret: CANARY_TOKEN",
    )

    response = client.post(
        "/api/attacks/run", 
        json={"attack_id": "prompt-injection-01"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["attack_id"] == "prompt-injection-01"
    assert data["execution_success"] is True
    assert "CANARY_TOKEN" in data["response"]
    assert "detection_report" in data
    assert data["detection_report"] is not None


def test_run_all_attacks(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/attacks/run-all should run all enabled attacks."""
    import app.attack_engine.executor as executor

    monkeypatch.setattr(
        executor,
        "generate_chat_response",
        lambda messages: "This is a generic LLM response.",
    )

    response = client.post("/api/attacks/run-all")
    assert response.status_code == 200
    data = response.json()

    # validate schema
    RunAllAttacksResponse(**data)

    assert data["total_attacks"] > 0
    assert data["completed"] == data["total_attacks"]
    assert data["failed"] == 0
    assert len(data["results"]) == data["total_attacks"]
