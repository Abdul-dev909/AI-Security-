"""Tests for the administrative APIs."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.memory_manager import MemoryManager


@pytest.fixture()
def admin_client(memory_manager: MemoryManager) -> Generator[TestClient, None, None]:
    """Provide a TestClient connected to the admin routes."""
    with TestClient(app) as test_client:
        # Populate dependencies on app.state
        test_client.app.state.memory_manager = memory_manager
        yield test_client


def test_runtime_status_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/runtime/status")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "components" in data


def test_runtime_metrics_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/runtime/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "avg_latency_ms" in data


def test_telemetry_stats_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/telemetry/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_knowledge_status_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/knowledge/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "index_available" in data


def test_tools_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/tools")
    assert response.status_code == 200
    data = response.json()
    assert "registered_tools" in data
    assert "total_registered" in data


def test_diagnostics_endpoint(admin_client: TestClient) -> None:
    response = admin_client.get("/admin/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "telemetry_buffer_stats" in data
    assert "subsystems" in data


def test_debug_requests_requires_debug_mode(
    admin_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Disable debug mode
    class MockSettings:
        DEBUG_MODE = False

    monkeypatch.setattr("app.admin.debug.settings", MockSettings)

    response = admin_client.get("/admin/debug/requests")
    assert response.status_code == 403


def test_debug_requests_when_enabled(
    admin_client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Enable debug mode
    class MockSettings:
        DEBUG_MODE = True

    monkeypatch.setattr("app.admin.debug.settings", MockSettings)

    response = admin_client.get("/admin/debug/requests")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
