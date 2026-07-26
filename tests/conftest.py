"""Pytest bootstrap and shared fixtures for memory-related tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.database as database
from app.main import app
from app.memory.storage import MemoryStorage
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
    """Create a temporary SQLite-backed MemoryManager (deprecated adapter)
    for isolated tests.

    Uses an in-memory SQLite connection for the enterprise storage layer so that
    each test runs in a completely isolated environment.
    """
    # Patch legacy DB path for any tests that still touch it
    test_database_path = tmp_path / "memory.db"
    monkeypatch.setattr(database, "DB_PATH", test_database_path)
    database.initialize_database()

    # Create MemoryManager; suppress DeprecationWarning in tests
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        mm = MemoryManager()

    # Patch the enterprise storage to use an isolated temp-file SQLite DB
    enterprise_db_path = str(tmp_path / "enterprise_memory.db")
    isolated_storage = MemoryStorage(db_path=enterprise_db_path)
    mm.enterprise.storage = mm.enterprise.retriever.storage = isolated_storage

    return mm


@pytest.fixture()
def client(memory_manager: MemoryManager) -> TestClient:
    """Create a FastAPI test client with a temporary memory database."""

    with TestClient(app) as test_client:
        # Inject the isolated enterprise memory manager into app state
        enterprise_mm = memory_manager.enterprise
        test_client.app.state.memory_manager = enterprise_mm
        # Also inject into AgentRuntime so all memory operations go to the same store
        test_client.app.state.agent_runtime.memory_manager = enterprise_mm
        test_client.app.state.conversation_manager.clear_history()
        yield test_client
        test_client.app.state.conversation_manager.clear_history()
