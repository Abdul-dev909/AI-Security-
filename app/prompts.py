"""Prompt building helpers for the AI agent."""

from __future__ import annotations

from dataclasses import dataclass

from app.conversation import ConversationManager


@dataclass(slots=True)
class PromptBuilder:
    """Build the final message list that is sent to Ollama.

    The builder keeps prompt logic out of the route layer. It inserts the
    system prompt, reads the previous conversation history, and appends the new
    user message in the correct order.
    """

    system_prompt: str
    conversation_manager: ConversationManager

    def build_messages(self, user_message: str) -> list[dict[str, str]]:
        """Return the complete chat message list for Ollama."""

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_manager.get_messages())
        messages.append({"role": "user", "content": user_message})
        return messages
