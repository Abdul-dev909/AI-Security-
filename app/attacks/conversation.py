"""Conversation management layer."""

from __future__ import annotations

from typing import Any

from .models import AttackMessage, AttackSession


class AttackConversationManager:
    """Manager for maintaining the complete attack conversation history."""

    def __init__(self, session: AttackSession) -> None:
        self._session = session

    def append_message(self, message: AttackMessage) -> None:
        """Append a message to the conversation."""
        self._session.structured_messages.append(message)
        # Mirror to legacy fields for backward compatibility
        self._session.add_message(message.role, message.content)

    def last_message(self) -> AttackMessage | None:
        """Get the most recent message."""
        if not self._session.structured_messages:
            return None
        return self._session.structured_messages[-1]

    def attacker_messages(self) -> list[AttackMessage]:
        """Get all messages sent by the attacker."""
        return [
            m for m in self._session.structured_messages 
            if m.sender.value.startswith("ATTACKER_")
        ]

    def victim_messages(self) -> list[AttackMessage]:
        """Get all messages sent by the victim."""
        return [
            m for m in self._session.structured_messages 
            if m.sender.value == "VICTIM_AI"
        ]

    def build_context(self) -> list[dict[str, str]]:
        """Build a generic role/content context for prompting."""
        return [
            {"role": m.role, "content": m.content}
            for m in self._session.structured_messages
        ]

    def export_transcript(self) -> list[dict[str, Any]]:
        """Export the full conversation transcript."""
        return [m.model_dump() for m in self._session.structured_messages]

    def truncate_history(self, keep_last_n: int) -> None:
        """Truncate the history, retaining only the last n messages."""
        if keep_last_n <= 0:
            self._session.structured_messages.clear()
            self._session.messages.clear()
            self._session.conversation_history.clear()
            self._session.attacker_messages.clear()
            self._session.victim_messages.clear()
        else:
            self._session.structured_messages = self._session.structured_messages[-keep_last_n:]
            # Re-sync legacy fields
            self._session.messages.clear()
            self._session.conversation_history.clear()
            self._session.attacker_messages.clear()
            self._session.victim_messages.clear()
            for msg in self._session.structured_messages:
                self._session.add_message(msg.role, msg.content)

    def conversation_statistics(self) -> dict[str, Any]:
        """Expose conversation statistics."""
        return {
            "total_messages": len(self._session.structured_messages),
            "attacker_messages_count": len(self.attacker_messages()),
            "victim_messages_count": len(self.victim_messages()),
        }
