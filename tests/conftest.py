"""Pytest bootstrap and shared fixtures for memory-related tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from app.memory_manager import MemoryManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def clean_test_context():
    """Provide a simple, isolated context for tests."""
    return {"project_root": str(PROJECT_ROOT)}


@pytest.fixture()
def memory_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryManager:
    """Create a temporary SQLite-backed MemoryManager for isolated tests."""

    test_database_path = tmp_path / "memory.db"
    monkeypatch.setattr(database, "DB_PATH", test_database_path)
    database.initialize_database()
    return MemoryManager()


@pytest.fixture()
def client(memory_manager: MemoryManager) -> TestClient:
    """Create a FastAPI test client with a temporary memory database."""

    with TestClient(app) as test_client:
        test_client.app.state.memory_manager = memory_manager
        test_client.app.state.conversation_manager.memory_manager = memory_manager
        test_client.app.state.conversation_manager.clear_history()
        yield test_client
        test_client.app.state.conversation_manager.clear_history()