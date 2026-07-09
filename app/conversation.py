"""Conversation management for in-memory chat history."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from app.config import settings
from app.memory_manager import MemoryManager
from app.utils import normalize_text

if TYPE_CHECKING:
    from app.prompts import PromptBuilder

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

    memory_manager: MemoryManager
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

    def build_messages(
        self,
        prompt_builder: PromptBuilder,
        user_message: str,
    ) -> list[dict[str, str]]:
        """Collect memories and conversation history before building a prompt."""

        memories = self.search_memories(user_message)
        return prompt_builder.build_messages(
            user_message,
            memories=memories,
            conversation_history=self.get_messages(),
        )

    def save_memory_if_important(self, user_message: str) -> None:
        """Try to save an important memory without breaking the chat flow."""

        if not settings.ENABLE_MEMORY:
            return

        if not is_important(user_message):
            return

        try:
            self.memory_manager.save_memory(user_message)
        except Exception:
            logger.exception("Memory saving failed.")

    def search_memories(self, user_message: str) -> list[str]:
        """Retrieve relevant memories while keeping the conversation alive on errors."""

        if not settings.ENABLE_MEMORY:
            return []

        try:
            memories = self.memory_manager.search_memories(user_message)
        except Exception:
            logger.exception("Memory retrieval failed.")
            return []

        return self._normalize_memories(memories)

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
            del self._messages[:-self.max_history]

    def _normalize_memories(self, memories: Any) -> list[str]:
        """Convert memory results into a short list of displayable strings."""

        if not memories:
            return []

        if isinstance(memories, (str, bytes)):
            raw_memories = [memories]
        else:
            try:
                raw_memories = list(memories)
            except TypeError:
                raw_memories = [memories]

        normalized_memories: list[str] = []
        for item in raw_memories[: settings.MEMORY_LIMIT]:
            if isinstance(item, dict):
                text = str(item.get("content") or item.get("text") or item.get("memory") or item)
            else:
                text = str(item)

            cleaned_text = normalize_text(text)
            if cleaned_text:
                normalized_memories.append(cleaned_text)

        return normalized_memories

