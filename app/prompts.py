"""Prompt building helpers for the AI agent."""

from __future__ import annotations

from dataclasses import dataclass

from app.conversation import ConversationManager


def _format_memories(memories: list[str]) -> str:
    """Turn retrieved memories into a compact prompt section."""

    memory_lines = [f"- {memory}" for memory in memories if memory.strip()]
    if not memory_lines:
        return ""

    return "Relevant Memories:\n" + "\n".join(memory_lines)


@dataclass(slots=True)
class PromptBuilder:
    """Build the final message list that is sent to Ollama.

    The builder keeps prompt logic out of the route layer. It inserts the
    system prompt, reads the previous conversation history, and appends the new
    user message in the correct order.
    """

    system_prompt: str
    conversation_manager: ConversationManager

    def build_messages(
        self,
        user_message: str,
        memories: list[str] | None = None,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        """Return the complete chat message list for Ollama.

        The final order is system prompt, relevant memories, conversation
        history, and the current user message.
        """

        active_history = conversation_history
        if active_history is None:
            active_history = self.conversation_manager.get_messages()

        final_messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
        ]

        if memories:
            final_messages.append({"role": "system", "content": _format_memories(memories)})

        if active_history:
            final_messages.extend(active_history)

        final_messages.append({"role": "user", "content": user_message})
        return final_messages
