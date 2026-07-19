"""Database module for managing SQLite connections and schema initialization.

This module provides functions to establish connections to an SQLite database
and initialize the database schema with required tables. The database file is
stored in the project root directory and is automatically created on import.

Typical usage example:
    from app.database import get_connection, initialize_database

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories")
    rows = cursor.fetchall()
    conn.close()
"""

import sqlite3
from pathlib import Path

# Database path in project root (one level above app folder)
DB_PATH = Path(__file__).parent.parent / "memory.db"

# SQL schema for the memories table
_MEMORIES_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def get_connection() -> sqlite3.Connection:
    """Establish and return a connection to the SQLite database.

    Opens a connection to the SQLite database file at DB_PATH. Creates the
    database file if it does not already exist. The connection uses row factory
    to enable column name access in query results.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.

    Raises:
        sqlite3.DatabaseError: If a database access error occurs.
        sqlite3.OperationalError: If a database operation fails.

    Example:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories")
        finally:
            conn.close()
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        # Enable column name access in query results
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise sqlite3.DatabaseError(
            f"Failed to connect to database at {DB_PATH}: {e}"
        ) from e


def initialize_database() -> None:
    """Initialize the database and create the memories table if needed.

    Connects to the SQLite database and creates the memories table with the
    predefined schema using CREATE TABLE IF NOT EXISTS. This function is
    idempotent and can be safely called multiple times.

    The memories table schema includes:
        - id: Integer primary key with autoincrement
        - memory: Text field storing memory content (not null)
        - created_at: Text field storing creation timestamp (not null)
        - updated_at: Text field storing update timestamp (not null)

    Raises:
        sqlite3.DatabaseError: If a database access error occurs.
        sqlite3.OperationalError: If table creation fails.

    Example:
        initialize_database()  # Safe to call multiple times
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(_MEMORIES_TABLE_SCHEMA)
            conn.commit()
    except sqlite3.Error as e:
        raise sqlite3.OperationalError(
            f"Failed to initialize database at {DB_PATH}: {e}"
        ) from e


# Automatically initialize the database when the module is imported
initialize_database()
