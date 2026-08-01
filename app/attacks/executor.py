"""Enterprise attack executor."""

from __future__ import annotations

import logging
from collections.abc import Callable
from time import perf_counter
from typing import Any

from app.conversation import ConversationManager
from app.detection.coordinator import DetectionCoordinator
from app.detection.models import DetectionContext
from app.prompts import PromptBuilder

from .metadata import AttackTechnique
from .models import AttackDefinition, AttackResult, AttackSession, AttackVariant
from .session import AttackSessionManager
from .strategy import SingleTurnStrategy

logger = logging.getLogger(__name__)

ResponseGenerator = Callable[[list[dict[str, str]]], str]


def _resolve_attack_inputs(
    attack: AttackDefinition | AttackVariant | Any,
) -> tuple[str, str, str, str, bool, str]:
    if isinstance(attack, AttackDefinition):
        variant = attack.enabled_variants()[0]
        return (
            attack.attack_id,
            attack.name,
            attack.description,
            variant.prompt,
            variant.enabled,
            variant.variant_id,
        )

    if isinstance(attack, AttackVariant):
        return (
            attack.variant_id,
            attack.name,
            attack.metadata.get("definition_name", attack.name),
            attack.prompt,
            attack.enabled,
            attack.variant_id,
        )

    return (
        getattr(attack, "id"),
        getattr(attack, "name"),
        getattr(attack, "description", ""),
        getattr(attack, "prompt"),
        getattr(attack, "enabled", True),
        getattr(attack, "id"),
    )


class AttackExecutor:
    """Execute a single attack definition against the local agent stack."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        conversation_manager: ConversationManager,
        detection_coordinator: DetectionCoordinator,
        response_generator: ResponseGenerator,
        session_manager: AttackSessionManager | None = None,
        execution_mode: ExecutionMode | None = None,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.conversation_manager = conversation_manager
        self.detection_coordinator = detection_coordinator
        self.response_generator = response_generator
        self.session_manager = session_manager or AttackSessionManager()
        self.execution_mode = execution_mode

    def execute(self, attack: AttackDefinition | AttackVariant | Any) -> AttackResult:
        # Stage 1: initialize and validate inputs
        attack_id, attack_name, description, prompt, enabled, session_source = _resolve_attack_inputs(
            attack
        )
        if not enabled:
            raise ValueError(f"Attack '{attack_id}' is disabled.")

        logger.info("Executing attack: %s (ID: %s)", attack_name, attack_id)
        self.conversation_manager.clear_history()

        # Prepare strategy (abstraction only at this milestone)
        strategy = self.prepare_strategy(attack)

        # Initialize session and record initial stage
        session = self.initialize_session(session_source, attack_name, description, attack_variant=getattr(attack, "variant_id", None))
        # Use the penultimate stage as start (preserve previous behaviour)
        start_stage = strategy.stages[-2] if len(strategy.stages) >= 2 else strategy.stages[0]
        self.session_manager.start_session(session, stage=start_stage)
        session.add_message("user", prompt)

        # Execution bookkeeping
        response: str | None = None
        success = False
        error_message: str | None = None

        started_at = perf_counter()
        try:
            # begin_execution handles core interaction for the single-turn path
            response = self.begin_execution(session, strategy, prompt)
            success = True
        except Exception as exc:  # pragma: no cover - exercised via tests
            logger.exception("Error executing attack '%s'", attack_id)
            error_message = f"{type(exc).__name__}: {exc!s}"
            self.session_manager.fail_session(session)

        detection_report = None
        if success and response is not None:
            context = DetectionContext(
                user_prompt=prompt,
                ai_response=response,
                conversation_history=self.conversation_manager.get_messages(),
                session_id=session.session_id,
            )
            detection_report = self.detection_coordinator.run_detection(context)

        telemetry: dict[str, Any] = {
            "strategy": strategy.technique.value,
            "stages": list(strategy.stages),
        }
        if isinstance(attack, AttackDefinition):
            telemetry["category"] = attack.category.value
            telemetry["severity"] = attack.severity.value
        elif isinstance(attack, AttackVariant):
            telemetry["variant_id"] = attack.variant_id

        result = self.generate_result(
            attack_id=attack_id,
            attack_name=attack_name,
            session=session,
            started_at=started_at,
            success=success,
            response=response,
            detection_report=detection_report,
            telemetry=telemetry,
            error_message=error_message,
        )

        logger.info("Attack execution finished for: %s (ID: %s)", attack_name, attack_id)
        return result

    # ---- New extensible execution stage methods ----
    def initialize_session(self, session_source: str, attack_name: str, description: str, attack_variant: str | None = None) -> AttackSession:
        session = self.session_manager.create_session(
            session_source,
            metadata={"attack_name": attack_name, "description": description},
        )
        if attack_variant:
            session.attack_variant = attack_variant
        session.record_event("session_initialized", {"source": session_source})
        return session

    def prepare_strategy(self, attack: AttackDefinition | AttackVariant | Any) -> SingleTurnStrategy:
        # Select a strategy according to the configured execution mode or the
        # attack's declared supported modes. For Milestone 1.1 we return the
        # historical single-turn strategy while providing selection hooks.
        tech = attack.technique if isinstance(attack, AttackDefinition) else AttackTechnique.INSTRUCTION_OVERRIDE
        # honor executor-level execution_mode if provided
        mode = self.execution_mode
        if mode is None:
            # attempt to use the attack's default_execution_mode if present
            default_mode = getattr(attack, "metadata", {}).get("default_execution_mode")
            try:
                mode = ExecutionMode.normalize(default_mode) if default_mode else None
            except Exception:
                mode = None

        # Strategy resolution (for now, map all modes to SingleTurnStrategy)
        return SingleTurnStrategy(technique=tech)

    def begin_execution(self, session: AttackSession, strategy: SingleTurnStrategy, prompt: str) -> str:
        # Build messages and run the response generator (single-turn path)
        messages = self.prompt_builder.build_messages(
            user_message=prompt,
            memories=[],
            conversation_history=self.conversation_manager.get_messages(),
        )
        response = self.response_generator(messages)
        # mirror previous conversation interactions for compatibility
        self.conversation_manager.add_user_message(prompt)
        self.conversation_manager.add_assistant_message(response)
        session.add_message("assistant", response)
        session.advance_stage(strategy.stages[-1])
        self.session_manager.complete_session(session)
        return response

    def execute_stage(self, session: AttackSession, stage: str) -> None:
        # Placeholder for executing a specific stage in multi-stage strategies.
        session.record_event("stage_started", {"stage": stage})
        session.record_event("stage_completed", {"stage": stage})

    def finalize_attack(self, session: AttackSession) -> None:
        session.record_event("finalize_attack", {})

    def generate_result(
        self,
        attack_id: str,
        attack_name: str,
        session: AttackSession,
        started_at: float,
        success: bool,
        response: str | None,
        detection_report: Any | None,
        telemetry: dict[str, Any],
        error_message: str | None,
    ) -> AttackResult:
        return AttackResult(
            attack_id=attack_id,
            session_id=session.session_id,
            success=success,
            execution_time=perf_counter() - started_at,
            response=response,
            detection_report=detection_report,
            telemetry=telemetry,
            metadata={"attack_name": attack_name, "session": session.model_dump()},
            error=error_message,
        )
