import datetime
import logging
import uuid
from typing import Any

from app.memory.models import Session

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session lifecycle, metadata, and in-memory runtime state.

    This class strictly separates session management from persistent memory storage.
    """

    def __init__(self):
        # In a distributed environment, this could be Redis.
        # For our zero-setup architecture, it's an in-memory dictionary.
        self._sessions: dict[str, Session] = {}
        # Simple tracking of short-term state that shouldn't be persisted to
        # long-term memory
        self._runtime_state: dict[str, dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str | None = None) -> Session:
        """Retrieve an existing session or create a new one."""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_accessed_at = datetime.datetime.now(datetime.timezone.utc)
            return session

        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        self._runtime_state[session_id] = {}
        logger.info("Created new session: %s", session_id)
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session without creating it if it doesn't exist."""
        session = self._sessions.get(session_id)
        if session:
            session.last_accessed_at = datetime.datetime.now(datetime.timezone.utc)
        return session

    def set_session_metadata(self, session_id: str, key: str, value: Any) -> None:
        """Store permanent metadata for the session (e.g. user details)."""
        session = self.get_session(session_id)
        if session:
            session.metadata[key] = value

    def set_runtime_state(self, session_id: str, key: str, value: Any) -> None:
        """Store ephemeral runtime state for the session."""
        if session_id in self._runtime_state:
            self._runtime_state[session_id][key] = value

    def get_runtime_state(self, session_id: str, key: str, default: Any = None) -> Any:
        """Retrieve ephemeral runtime state."""
        return self._runtime_state.get(session_id, {}).get(key, default)

    def delete_session(self, session_id: str) -> None:
        """Remove a session from tracking."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._runtime_state:
            del self._runtime_state[session_id]
        logger.info("Deleted session: %s", session_id)

    def list_sessions(self) -> list[Session]:
        """Return all known sessions."""
        return list(self._sessions.values())

    def session_count(self) -> int:
        """Return the number of active sessions."""
        return len(self._sessions)
