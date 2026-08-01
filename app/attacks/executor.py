"""Enterprise attack executor (Stateless Worker)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from time import perf_counter

from app.conversation import ConversationManager
from app.detection.coordinator import DetectionCoordinator
from app.prompts import PromptBuilder
from .models import AttackSession

logger = logging.getLogger(__name__)

ResponseGenerator = Callable[[list[dict[str, str]]], str]


class AttackExecutor:
    """Worker responsible for executing prompts and returning responses.
    
    This component no longer orchestrates the attack lifecycle.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
        detection_coordinator: DetectionCoordinator,
        response_generator: ResponseGenerator,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager
        self.detection_coordinator = detection_coordinator
        self.response_generator = response_generator

    def send_prompt(self, prompt: str, session: AttackSession | None = None) -> str:
        """Send a prompt to the AI and receive a response.
        
        This is a stateless operation. Any state recording must be done
        by the orchestrator or conversation manager.
        """
        messages = self.prompt_builder.build_messages(
            user_message=prompt,
            memories=[],
            conversation_history=self.conversation_manager.get_messages(),
        )
        
        response = self.response_generator(messages)
        
        # We still sync with the global conversation manager for compatibility
        # We do this after response generation so exceptions do not leave the user message hanging
        self.conversation_manager.add_user_message(prompt)
        self.conversation_manager.add_assistant_message(response)
        
        return response
