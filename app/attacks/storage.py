"""Attack session persistence interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AttackSession


@runtime_checkable
class AttackSessionStore(Protocol):
    """Interface for storing and retrieving attack sessions."""

    def create_session(self, session: AttackSession) -> None:
        """Create a new session in storage."""
        ...

    def save_session(self, session: AttackSession) -> None:
        """Save a session (create or update)."""
        ...

    def update_session(self, session: AttackSession) -> None:
        """Update an existing session."""
        ...

    def load_session(self, session_id: str) -> AttackSession | None:
        """Load a session by its ID."""
        ...

    def delete_session(self, session_id: str) -> None:
        """Delete a session by its ID."""
        ...

    def list_sessions(self) -> list[AttackSession]:
        """List all sessions in storage."""
        ...


class InMemorySessionStore:
    """In-memory implementation of the session store."""

    def __init__(self) -> None:
        self._sessions: dict[str, AttackSession] = {}

    def create_session(self, session: AttackSession) -> None:
        if session.session_id in self._sessions:
            raise ValueError(f"Session {session.session_id} already exists.")
        self._sessions[session.session_id] = session

    def save_session(self, session: AttackSession) -> None:
        self._sessions[session.session_id] = session

    def update_session(self, session: AttackSession) -> None:
        if session.session_id not in self._sessions:
            raise ValueError(f"Session {session.session_id} does not exist.")
        self._sessions[session.session_id] = session

    def load_session(self, session_id: str) -> AttackSession | None:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> list[AttackSession]:
        return list(self._sessions.values())
