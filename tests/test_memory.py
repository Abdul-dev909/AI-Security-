from app.memory.importance import ImportanceEngine
from app.memory.models import MemoryRecord
from app.memory.sessions import SessionManager


def test_session_isolation():
    """Test that SessionManager properly isolates sessions."""
    manager = SessionManager()

    # Create session 1
    session1 = manager.get_or_create_session("sess-1")
    manager.set_runtime_state(session1.session_id, "key1", "value1")

    # Create session 2
    session2 = manager.get_or_create_session("sess-2")
    manager.set_runtime_state(session2.session_id, "key1", "value2")

    assert manager.get_runtime_state("sess-1", "key1") == "value1"
    assert manager.get_runtime_state("sess-2", "key1") == "value2"


def test_importance_engine():
    """Test the rule-based heuristics in ImportanceEngine."""
    engine = ImportanceEngine()

    # Weak/no signal
    assert engine.evaluate("Hello, how are you?") < 0.3

    # Explicit command
    assert engine.evaluate("Please remember my project name.") >= 0.8

    # Critical entity
    score = engine.evaluate("The password is password123.")
    assert score >= 0.2


def test_enterprise_memory_flow():
    """Test end-to-end memory management flow using a temporary in-memory SQLite
    setup if possible.
    """
    # We will mock the SQLite storage path to :memory: for tests
    from app.memory.storage import MemoryStorage

    storage = MemoryStorage(db_path=":memory:")

    # Add memories for different sessions
    record1 = MemoryRecord(session_id="a", content="test A1", importance_score=0.9)
    record2 = MemoryRecord(session_id="b", content="test B1", importance_score=0.8)

    storage.add_memory(record1)
    storage.add_memory(record2)

    # Ensure they don't bleed
    memories_a = storage.get_memories_by_session("a")
    assert len(memories_a) == 1
    assert memories_a[0].content == "test A1"

    memories_b = storage.get_memories_by_session("b")
    assert len(memories_b) == 1
    assert memories_b[0].content == "test B1"
