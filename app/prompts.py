"""Prompt building helpers for the AI agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.conversation import ConversationManager


def _format_memories(memories: list[str], max_memories: int = 10) -> str:
    """Turn retrieved memories into a compact prompt section without duplicates."""
    seen = set()
    unique_memories = []

    for memory in memories:
        clean_memory = memory.strip()
        if clean_memory and clean_memory not in seen:
            seen.add(clean_memory)
            unique_memories.append(f"- {clean_memory}")
            if len(unique_memories) >= max_memories:
                break

    if not unique_memories:
        return ""

    return "Relevant Memories:\n" + "\n".join(unique_memories)


def _format_knowledge_chunks(chunks: list[Any], max_chunks: int = 5) -> str:
    """Format chunks without duplicates and bounded by max_chunks."""
    seen = set()
    unique_chunks = []

    for chunk in chunks:
        # Depending on chunk type, extract text
        text = chunk.text if hasattr(chunk, "text") else str(chunk)
        clean_text = text.strip()
        if clean_text and clean_text not in seen:
            seen.add(clean_text)
            unique_chunks.append(clean_text)
            if len(unique_chunks) >= max_chunks:
                break

    if not unique_chunks:
        return ""

    return (
        "==============================\n"
        "Enterprise Knowledge\n"
        "==============================\n" + "\n\n".join(unique_chunks) + "\n"
        "==============================\n"
        "End Enterprise Knowledge\n"
        "=============================="
    )


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
        tool_output: str | None = None,
        knowledge_context: Any | None = None,
    ) -> list[dict[str, str]]:
        """Return the complete chat message list for Ollama.

        The final order is system prompt, conversation history, relevant
        memories, enterprise knowledge context, tool output (if present),
        and current user message.
        """

        active_history = conversation_history
        if active_history is None:
            active_history = self.conversation_manager.get_messages()

        final_messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
        ]

        if active_history:
            final_messages.extend(active_history)

        if memories:
            memory_block = _format_memories(memories)
            if memory_block:
                final_messages.append({"role": "system", "content": memory_block})

        if knowledge_context and getattr(knowledge_context, "has_knowledge", False):
            knowledge_block = _format_knowledge_chunks(
                knowledge_context.retrieved_chunks
            )
            if knowledge_block:
                final_messages.append({"role": "system", "content": knowledge_block})

        if tool_output and tool_output.strip():
            final_messages.append(
                {
                    "role": "system",
                    "content": (
                        "Retrieved Context from Environment Tool:\n"
                        f"{tool_output.strip()}"
                    ),
                }
            )

        final_messages.append({"role": "user", "content": user_message})
        return final_messages
