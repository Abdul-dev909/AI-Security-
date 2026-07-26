"""Unit tests for the MemoryManager implementation."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

import app.logging_utils as logging_utils
from app.memory_manager import MemoryManager


class TestMemorySaveOperations:
    """Tests for saving new memories into the SQLite-backed store."""

    def test_save_memory_persists_data_and_returns_id(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_id = memory_manager.save_memory("User likes Python")

        assert isinstance(memory_id, str)
        assert len(memory_id) > 0

        stored_memories = memory_manager.load_memories()
        assert len(stored_memories) == 1
        assert stored_memories[0]["memory"] == "User likes Python"

    def test_save_memory_allows_multiple_and_duplicate_entries(
        self, memory_manager: MemoryManager
    ) -> None:
        first_id = memory_manager.save_memory("First memory")
        second_id = memory_manager.save_memory("First memory")

        assert first_id != second_id
        persisted = memory_manager.load_memories()
        assert [row["memory"] for row in persisted] == ["First memory", "First memory"]

    @pytest.mark.parametrize("invalid_value", [None, ""])
    def test_save_memory_rejects_empty_or_none_values(
        self, memory_manager: MemoryManager, invalid_value: object
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.save_memory(invalid_value)  # type: ignore[arg-type]

    def test_save_memory_accepts_whitespace_only_text(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_id = memory_manager.save_memory("   ")

        assert len(memory_id) > 0
        assert memory_manager.load_memories()[0]["memory"] == "   "

    def test_save_memory_handles_long_text_and_special_characters(
        self, memory_manager: MemoryManager
    ) -> None:
        long_text = "A" * 2000 + "\n\tO'Reilly & C++"
        memory_id = memory_manager.save_memory(long_text)

        assert len(memory_id) > 0
        saved = memory_manager.load_memories()[0]
        assert saved["memory"] == long_text


class TestMemorySearchOperations:
    """Tests for searching stored memories with partial matching."""

    def test_search_memories_returns_exact_and_partial_matches(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_manager.save_memory("Python is great")
        memory_manager.save_memory("I like Python for automation")
        memory_manager.save_memory("FastAPI is lightweight")

        matches = memory_manager.search_memories("python")

        assert [row["memory"] for row in matches] == [
            "Python is great",
            "I like Python for automation",
        ]

    def test_search_memories_is_case_insensitive_and_returns_no_results(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_manager.save_memory("Arabic lesson")
        memory_manager.save_memory("Chinese characters")

        assert [row["memory"] for row in memory_manager.search_memories("arabic")] == [
            "Arabic lesson"
        ]
        assert memory_manager.search_memories("does-not-exist") == []

    @pytest.mark.parametrize("query", ["O'Reilly", "A&B", "C++"])
    def test_search_memories_handles_special_characters(
        self, memory_manager: MemoryManager, query: str
    ) -> None:
        memory_manager.save_memory("O'Reilly loves C++")
        memory_manager.save_memory("A&B example")

        matches = memory_manager.search_memories(query)
        assert len(matches) == 1
        assert (
            matches[0]["memory"].startswith("O'Reilly") or "A&B" in matches[0]["memory"]
        )

    @pytest.mark.parametrize("invalid_value", [None, ""])
    def test_search_memories_rejects_empty_or_none_queries(
        self, memory_manager: MemoryManager, invalid_value: object
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.search_memories(invalid_value)  # type: ignore[arg-type]


class TestMemoryUpdateOperations:
    """Tests for updating existing memories."""

    def test_update_memory_updates_existing_record(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_id = memory_manager.save_memory("Old text")

        import time

        time.sleep(0.001)  # Ensure updated_at is strictly greater than created_at

        updated = memory_manager.update_memory(memory_id, "New text")

        assert updated is True
        stored = memory_manager.load_memories()[0]
        assert stored["memory"] == "New text"
        assert stored["updated_at"] >= stored["created_at"]

    def test_update_memory_returns_false_for_missing_id(
        self, memory_manager: MemoryManager
    ) -> None:
        assert memory_manager.update_memory("non-existent-id", "Replacement") is False

    @pytest.mark.parametrize("invalid_value", [None, ""])
    def test_update_memory_rejects_empty_or_none_values(
        self, memory_manager: MemoryManager, invalid_value: object
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.update_memory("1", invalid_value)  # type: ignore[arg-type]

    def test_update_memory_rejects_invalid_ids(
        self, memory_manager: MemoryManager
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.update_memory("", "Valid")


class TestMemoryDeleteOperations:
    """Tests for deleting memories from the SQLite store."""

    def test_delete_memory_removes_existing_record(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_id = memory_manager.save_memory("To remove")
        deleted = memory_manager.delete_memory(memory_id)

        assert deleted is True
        assert memory_manager.load_memories() == []

    def test_delete_memory_returns_false_for_missing_id(
        self, memory_manager: MemoryManager
    ) -> None:
        assert memory_manager.delete_memory("non-existent-id") is False

    def test_delete_memory_rejects_invalid_ids(
        self, memory_manager: MemoryManager
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.delete_memory("")


class TestMemoryLoadOperations:
    """Tests for loading memories from the database."""

    def test_load_memories_returns_empty_list_when_database_is_empty(
        self, memory_manager: MemoryManager
    ) -> None:
        assert memory_manager.load_memories() == []

    def test_load_memories_returns_all_records_and_respects_limit(
        self, memory_manager: MemoryManager
    ) -> None:
        memory_manager.save_memory("One")
        memory_manager.save_memory("Two")
        memory_manager.save_memory("Three")

        all_memories = memory_manager.load_memories()
        recent_memories = memory_manager.load_memories(limit=2)

        assert [row["memory"] for row in all_memories] == ["Three", "Two", "One"]
        assert [row["memory"] for row in recent_memories] == ["Three", "Two"]

    def test_load_memories_rejects_invalid_limits(
        self, memory_manager: MemoryManager
    ) -> None:
        with pytest.raises(ValueError):
            memory_manager.load_memories(limit=0)


class TestMemoryEdgeCases:
    """Regression tests for unicode, whitespace, and large payloads."""

    @pytest.mark.parametrize(
        "text",
        [
            "English sentence",
            "مرحبا بالعالم",
            "中文内容",
            "🚀 emoji memory",
            "line1\nline2",
            "tab\tvalue",
            'quote: "hello"',
            "SQL' OR 1=1 --",
        ],
    )
    def test_save_and_search_handle_unicode_and_special_characters(
        self, memory_manager: MemoryManager, text: str
    ) -> None:
        memory_id = memory_manager.save_memory(text)
        matches = memory_manager.search_memories(text[-4:])

        assert len(memory_id) > 0
        assert len(matches) >= 1

    def test_large_volume_of_memories_can_be_inserted(
        self, memory_manager: MemoryManager
    ) -> None:
        for index in range(250):
            memory_manager.save_memory(f"memory-{index}")

        loaded = memory_manager.load_memories()
        assert len(loaded) == 250
        assert loaded[0]["memory"] == "memory-249"
        assert loaded[-1]["memory"] == "memory-0"


def test_logging_setup_creates_log_file_and_emits_messages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Logging should be configurable and write to a file for later inspection."""

    root_logger = logging.getLogger()
    monkeypatch.setattr(
        root_logger, "_ai_agent_logging_configured", False, raising=False
    )
    root_logger.handlers.clear()

    log_file = tmp_path / "app.log"
    monkeypatch.setattr(logging_utils, "get_log_file_path", lambda: log_file)

    logging_utils.setup_logging()
    logger = logging.getLogger("memory.tests")
    logger.info("memory test log entry")

    assert log_file.exists()
    assert "memory test log entry" in log_file.read_text(encoding="utf-8")
