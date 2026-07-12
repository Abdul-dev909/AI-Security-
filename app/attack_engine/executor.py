"""Attack Executor for running a single attack against the AI agent."""

from __future__ import annotations

import logging

from app.attack_engine.models import Attack, AttackResult
from app.conversation import ConversationManager
from app.ollama_client import generate_chat_response
from app.prompts import PromptBuilder
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class AttackExecutor:
    """Executor responsible for running a single Attack definition against the AI agent.

    Integrates with the existing conversation manager and prompt builder.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
    ) -> None:
        """Initialize the executor with the required agent components.

        Args:
            prompt_builder: The PromptBuilder instance from the agent.
            conversation_manager: The ConversationManager instance from the agent.
        """
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager

    def execute(self, attack: Attack) -> AttackResult:
        """Execute a single attack against the AI agent.

        Clears the conversation history before execution to isolate the attack,
        measures execution time, and captures any execution-related exceptions.

        Args:
            attack: The Attack model instance containing the prompt to execute.

        Returns:
            An AttackResult model instance summarizing the execution details.
        """
        logger.info("Executing attack: %s (ID: %s)", attack.name, attack.id)

        # Clear the history of the conversation manager to ensure attack isolation
        self.conversation_manager.clear_history()

        response: str | None = None
        execution_success = False
        error_msg: str | None = None

        with execution_timer() as elapsed:
            try:
                # 1. Build messages using the prompt builder and the attack prompt
                messages = self.conversation_manager.build_messages(
                    self.prompt_builder, attack.prompt
                )

                # 2. Call the existing AI agent via generate_chat_response
                response = generate_chat_response(messages)

                # 3. Update the conversation history and save memories if important
                self.conversation_manager.add_user_message(attack.prompt)
                self.conversation_manager.add_assistant_message(response)
                self.conversation_manager.save_memory_if_important(attack.prompt)

                execution_success = True
            except Exception as exc:
                logger.exception("Error executing attack '%s'", attack.id)
                error_msg = f"{type(exc).__name__}: {str(exc)}"
                execution_success = False

        return AttackResult(
            attack_id=attack.id,
            attack_name=attack.name,
            prompt=attack.prompt,
            response=response,
            execution_success=execution_success,
            error=error_msg,
            execution_time=elapsed(),
        )
