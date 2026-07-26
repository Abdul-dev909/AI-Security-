"""Conversation management for in-memory chat history."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.config import settings
from app.utils import normalize_text

logger = logging.getLogger(__name__)


def is_important(text: str) -> bool:
    """Placeholder used for future memory saving decisions.

    The project does not implement importance detection yet, so this always
    returns False.
    """

    return False


@dataclass(slots=True)
class ConversationManager:
    """Store and manage the latest chat messages in memory.

    The manager keeps only the newest messages so the history does not grow
    forever. This keeps the project simple and avoids long-term storage.
    """

    max_history: int = settings.MAX_HISTORY
    _messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the configured history size."""

        if self.max_history < 1:
            raise ValueError("max_history must be at least 1.")

    def add_user_message(self, message: str) -> None:
        """Store a user message in memory."""

        self._append_message("user", message)

    def add_assistant_message(self, message: str) -> None:
        """Store an assistant message in memory."""

        self._append_message("assistant", message)

    def clear_history(self) -> None:
        """Remove every stored message from memory."""

        self._messages.clear()

    def get_messages(self) -> list[dict[str, str]]:
        """Return a copy of the stored messages in the original order."""

        return [message.copy() for message in self._messages]

    def _append_message(self, role: str, message: str) -> None:
        """Add a message to the list and trim old entries if needed."""

        content = normalize_text(message)
        if not content:
            raise ValueError("Messages must not be empty.")

        self._messages.append({"role": role, "content": content})
        self._trim_history()

    def _trim_history(self) -> None:
        """Keep only the newest messages allowed by the configured limit."""

        if len(self._messages) > self.max_history:
            del self._messages[: -self.max_history]
