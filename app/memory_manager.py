"""Memory management module for storing and retrieving memories from SQLite database.

This module provides the MemoryManager class for managing memories with operations
like create, read, update, search, and delete. It uses the database module to
establish connections and manage the memories table.

Typical usage example:
    from app.memory_manager import MemoryManager

    manager = MemoryManager()
    memory_id = manager.save_memory("User asked about Python")
    memories = manager.list_memories()
    manager.update_memory(memory_id, "User asked about Python OOP")
    manager.delete_memory(memory_id)
"""

import sqlite3
from datetime import datetime, timezone

from .database import get_connection


class MemoryManager:
    """Manage memory storage and retrieval from SQLite database.

    This class provides CRUD operations for memories including save, list,
    search, update, and delete functionality. All memories are stored with
    creation and update timestamps.
    """

    def save_memory(self, memory: str) -> int:
        """Save a new memory to the database.

        Inserts a new memory record with the provided text and automatically
        sets the created_at and updated_at timestamps to the current time
        in ISO format.

        Args:
            memory: The memory text to save. Must not be empty.

        Returns:
            int: The ID (primary key) of the newly inserted memory record.

        Raises:
            sqlite3.Error: If the database operation fails.
            ValueError: If memory is empty or None.

        Example:
            manager = MemoryManager()
            memory_id = manager.save_memory("Important task to remember")
            print(f"Saved with ID: {memory_id}")
        """
        if not memory or not isinstance(memory, str):
            raise ValueError("Memory must be a non-empty string")

        now = datetime.now(timezone.utc).isoformat()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO memories (memory, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (memory, now, now),
                )
                conn.commit()
                return cursor.lastrowid or 0
        except sqlite3.Error as e:
            raise Exception(f"Failed to save memory: {e}") from e

    def list_memories(self) -> list[dict]:
        """Retrieve all memories ordered by ID in ascending order.

        Fetches all memories from the database and returns them as a list
        of dictionaries ordered by creation ID.

        Returns:
            list[dict]: A list of memory records as dictionaries with keys:
                - id: The memory ID
                - memory: The memory text
                - created_at: ISO format creation timestamp
                - updated_at: ISO format update timestamp
                Empty list if no memories exist.

        Raises:
            sqlite3.Error: If the database query fails.

        Example:
            manager = MemoryManager()
            memories = manager.list_memories()
            for mem in memories:
                print(f"ID {mem['id']}: {mem['memory']}")
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memories ORDER BY id ASC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to list memories: {e}") from e

    def load_memories(self, limit: int | None = None) -> list[dict]:
        """Retrieve memories with optional limit to most recent records.

        Fetches memories from the database. If limit is specified, returns
        only the most recent (highest ID) memories up to the limit.

        Args:
            limit: Optional maximum number of most recent memories to return.
                   If None, returns all memories. Must be positive if provided.

        Returns:
            list[dict]: A list of memory records as dictionaries with keys:
                - id: The memory ID
                - memory: The memory text
                - created_at: ISO format creation timestamp
                - updated_at: ISO format update timestamp
                Empty list if no memories exist.

        Raises:
            sqlite3.Error: If the database query fails.
            ValueError: If limit is not a positive integer.

        Example:
            manager = MemoryManager()
            recent_5 = manager.load_memories(limit=5)
            all_memories = manager.load_memories()
        """
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValueError("Limit must be a positive integer")

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                if limit is None:
                    cursor.execute("SELECT * FROM memories ORDER BY id DESC")
                else:
                    cursor.execute(
                        "SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,)
                    )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to load memories: {e}") from e

    def search_memories(self, query: str) -> list[dict]:
        """Search memories using case-insensitive partial matching.

        Searches the memory column for records containing the query string
        using case-insensitive LIKE pattern matching. Returns all matching
        memories ordered by ID.

        Args:
            query: The search query string. Must not be empty.

        Returns:
            list[dict]: A list of memory records matching the query as
                dictionaries with keys:
                - id: The memory ID
                - memory: The memory text
                - created_at: ISO format creation timestamp
                - updated_at: ISO format update timestamp
                Empty list if no matches found.

        Raises:
            sqlite3.Error: If the database query fails.
            ValueError: If query is empty or None.

        Example:
            manager = MemoryManager()
            results = manager.search_memories("python")
            for mem in results:
                print(f"Found: {mem['memory']}")
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM memories
                    WHERE LOWER(memory) LIKE LOWER(?)
                    ORDER BY id ASC
                    """,
                    (f"%{query}%",),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to search memories: {e}") from e

    def update_memory(self, memory_id: int, new_memory: str) -> bool:
        """Update the text of an existing memory.

        Updates the memory text and sets updated_at to the current time
        in ISO format. Returns True only if exactly one row was updated.

        Args:
            memory_id: The ID of the memory to update.
            new_memory: The new memory text. Must not be empty.

        Returns:
            bool: True if exactly one memory was updated, False otherwise
                (including if the ID doesn't exist).

        Raises:
            sqlite3.Error: If the database operation fails.
            ValueError: If memory_id is not a positive integer or
                       new_memory is empty.

        Example:
            manager = MemoryManager()
            success = manager.update_memory(1, "Updated memory text")
            if success:
                print("Memory updated")
            else:
                print("Memory not found")
        """
        if not isinstance(memory_id, int) or memory_id <= 0:
            raise ValueError("Memory ID must be a positive integer")

        if not new_memory or not isinstance(new_memory, str):
            raise ValueError("New memory must be a non-empty string")

        now = datetime.now(timezone.utc).isoformat()

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE memories
                    SET memory = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_memory, now, memory_id),
                )
                conn.commit()
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            raise Exception(f"Failed to update memory: {e}") from e

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory by ID.

        Removes the memory record with the specified ID from the database.
        Returns True only if exactly one row was deleted.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            bool: True if exactly one memory was deleted, False otherwise
                (including if the ID doesn't exist).

        Raises:
            sqlite3.Error: If the database operation fails.
            ValueError: If memory_id is not a positive integer.

        Example:
            manager = MemoryManager()
            success = manager.delete_memory(1)
            if success:
                print("Memory deleted")
            else:
                print("Memory not found")
        """
        if not isinstance(memory_id, int) or memory_id <= 0:
            raise ValueError("Memory ID must be a positive integer")

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            raise Exception(f"Failed to delete memory: {e}") from e
