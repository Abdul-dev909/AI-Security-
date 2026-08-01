"""Compatibility Attack Executor for running a single attack against the AI agent."""

from __future__ import annotations

import logging

from app.attack_engine.models import Attack, AttackResult
from app.attacks import (
    AttackDefinition,
    AttackTechnique,
    AttackVariant,
    SingleTurnStrategy,
)
from app.attacks.orchestrator import AttackOrchestrator
from app.attacks.executor import AttackExecutor as EnterpriseAttackExecutor
from app.attacks.storage import InMemorySessionStore
from app.attacks.events import EventBus
from app.attacks.metadata import AttackCategory, AttackSeverity
from app.conversation import ConversationManager
from app.detection.coordinator import DetectionCoordinator
from app.ollama_client import generate_chat_response
from app.prompts import PromptBuilder
logger = logging.getLogger(__name__)


class AttackExecutor:
    """Compatibility executor that delegates to the enterprise attack executor."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
        detection_coordinator: DetectionCoordinator,
    ) -> None:
        """Initialize the executor with the required agent components.

        Args:
            prompt_builder: The PromptBuilder instance from the agent.
            conversation_manager: The ConversationManager instance from the agent.
            detection_coordinator: The DetectionCoordinator instance to use.
        """
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager
        self.detection_coordinator = detection_coordinator
        self._enterprise_executor = EnterpriseAttackExecutor(
            prompt_builder=prompt_builder,
            conversation_manager=conversation_manager,
            detection_coordinator=detection_coordinator,
            response_generator=lambda messages: generate_chat_response(messages),
        )
        self._session_store = InMemorySessionStore()
        self._event_bus = EventBus()
        self._orchestrator = AttackOrchestrator(
            executor=self._enterprise_executor,
            session_store=self._session_store,
            event_bus=self._event_bus,
        )

    def _convert_legacy_attack(self, attack: Attack) -> AttackDefinition:
        """Project the legacy attack model into the structured attack model."""

        category_map = {
            "prompt injection": AttackCategory.PROMPT_INJECTION,
            "jailbreak": AttackCategory.JAILBREAK,
            "prompt leakage": AttackCategory.PROMPT_LEAKAGE,
            "canary extraction": AttackCategory.CANARY_EXTRACTION,
            "memory manipulation": AttackCategory.MEMORY_MANIPULATION,
        }
        severity_map = {
            "low": AttackSeverity.LOW,
            "medium": AttackSeverity.MEDIUM,
            "high": AttackSeverity.HIGH,
            "critical": AttackSeverity.CRITICAL,
        }

        category = category_map.get(attack.category.lower(), AttackCategory.PROMPT_INJECTION)
        severity = severity_map.get(attack.severity.lower(), AttackSeverity.MEDIUM)

        technique_map = {
            AttackCategory.PROMPT_INJECTION: AttackTechnique.INSTRUCTION_OVERRIDE,
            AttackCategory.JAILBREAK: AttackTechnique.PERSONA_SUBVERSION,
            AttackCategory.PROMPT_LEAKAGE: AttackTechnique.SYSTEM_PROMPT_EXTRACTION,
            AttackCategory.CANARY_EXTRACTION: AttackTechnique.CANARY_DISCLOSURE,
            AttackCategory.MEMORY_MANIPULATION: AttackTechnique.MEMORY_DISCLOSURE,
        }

        return AttackDefinition(
            attack_id=attack.id,
            name=attack.name,
            category=category,
            technique=technique_map[category],
            severity=severity,
            description=attack.description,
            objectives=[attack.description],
            prerequisites=["Conversation channel available"],
            supported_modes=["single-turn"],
            variants=[
                AttackVariant(
                    variant_id=attack.id,
                    name=attack.name,
                    prompt=attack.prompt,
                    enabled=attack.enabled,
                    metadata={"definition_name": attack.name},
                )
            ],
            tags=[attack.category, attack.severity],
            version="1.0.0",
        )

    def execute(self, attack: Attack) -> AttackResult:
        """Execute a single attack against the AI agent.

        The enterprise executor now handles the lifecycle, while the legacy API
        continues to return the original ``AttackResult`` shape.
        """

        logger.info("Executing attack: %s (ID: %s)", attack.name, attack.id)

        enterprise_attack = self._convert_legacy_attack(attack)
        enterprise_result = self._orchestrator.execute_attack(enterprise_attack)

        if not enterprise_result.success and enterprise_result.error is not None:
            logger.info("Attack execution failed; skipping detection.")

        return AttackResult(
            attack_id=attack.id,
            attack_name=attack.name,
            prompt=attack.prompt,
            response=enterprise_result.response,
            execution_success=enterprise_result.success,
            error=enterprise_result.error,
            execution_time=enterprise_result.execution_time,
            detection_report=enterprise_result.detection_report,
        )
