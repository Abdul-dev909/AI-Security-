"""Enterprise attack orchestrator."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from app.conversation import ConversationManager
from app.detection.coordinator import DetectionCoordinator
from app.detection.models import DetectionContext

from .models import (
    AttackDefinition, 
    AttackVariant, 
    AttackResult, 
    AttackSession,
    StrategyContext,
    AttackTimelineEvent
)
from .metadata import OrchestratorState
from .executor import AttackExecutor
from .conversation import AttackConversationManager
from .events import EventBus
from .storage import AttackSessionStore
from .strategy import SingleTurnStrategy, AttackStage
from .planner import AttackPlanner, AttackPlan
from .decision import DecisionEngine
from .prompt_builder import AttackPromptBuilder
from .analyzer import AttackResponseAnalyzer

logger = logging.getLogger(__name__)

class InvalidTransitionError(Exception):
    """Raised when an illegal state transition occurs."""


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


class AttackOrchestrator:
    """Central controller of the attack lifecycle."""

    def __init__(
        self,
        executor: AttackExecutor,
        session_store: AttackSessionStore,
        event_bus: EventBus,
        planner: AttackPlanner | None = None,
        prompt_builder: AttackPromptBuilder | None = None,
        analyzer: AttackResponseAnalyzer | None = None,
        decision_engine: DecisionEngine | None = None,
    ) -> None:
        self.executor = executor
        self.session_store = session_store
        self.event_bus = event_bus
        self.planner = planner
        self.prompt_builder = prompt_builder
        self.analyzer = analyzer
        self.decision_engine = decision_engine
        
    def _transition_state(self, session: AttackSession, new_state: OrchestratorState) -> None:
        # Simplistic valid transition check (for architectural placeholder)
        session.metadata["orchestrator_state"] = new_state.value
        self.event_bus.publish(AttackTimelineEvent(
            event_type="StateChanged",
            metadata={"new_state": new_state.value},
            stage=session.current_stage
        ))

    def execute_attack(self, attack: AttackDefinition | AttackVariant | Any) -> AttackResult:
        """Run a single attack execution (mostly for backward compatibility)."""
        started_at = perf_counter()
        
        # Resolve inputs
        attack_id, attack_name, description, prompt, enabled, session_source = _resolve_attack_inputs(attack)
        
        self.executor.conversation_manager.clear_history()
        
        # 1. Create Session
        session = AttackSession(
            attack_id=attack_id,
            metadata={"attack_name": attack_name, "description": description, "orchestrator_state": OrchestratorState.CREATED.value}
        )
        if isinstance(attack, AttackVariant):
            session.attack_variant = getattr(attack, "variant_id", None)
            
        self.session_store.create_session(session)
        self.event_bus.publish(AttackTimelineEvent(event_type="AttackStarted"))
        
        self._transition_state(session, OrchestratorState.INITIALIZED)
        
        conversation_manager = AttackConversationManager(session)
        strategy = SingleTurnStrategy(technique=getattr(attack, "technique", None))
        
        # Planner
        self._transition_state(session, OrchestratorState.PREPARING)
        if self.planner and isinstance(attack, AttackDefinition):
            plan = self.planner.generate_plan(attack)
            session.metadata["plan"] = plan
            
        session.start(stage=AttackStage.RECONNAISSANCE)
        self._transition_state(session, OrchestratorState.RUNNING)
        
        # Executor Worker invocation
        response = None
        success = False
        error_msg = None
        
        self._transition_state(session, OrchestratorState.WAITING_FOR_RESPONSE)
        try:
            # We bypass the complex builder for the single turn legacy mode, but delegate sending.
            response = self.executor.send_prompt(prompt, session)
            success = True
        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {exc!s}"
            self._transition_state(session, OrchestratorState.FAILED)
            session.fail()
            self.event_bus.publish(AttackTimelineEvent(event_type="AttackFailed"))
            
        if success and response is not None:
            self._transition_state(session, OrchestratorState.ANALYZING)
            
            # Use analyzer if available
            if self.analyzer:
                analysis = self.analyzer.analyze_response(response, session)
                session.metadata["analysis"] = analysis
                
            self._transition_state(session, OrchestratorState.COMPLETED)
            session.complete()
            self.event_bus.publish(AttackTimelineEvent(event_type="AttackCompleted"))

        # Detection for legacy support
        detection_report = None
        if success and response is not None and self.executor.detection_coordinator:
            context = DetectionContext(
                user_prompt=prompt,
                ai_response=response,
                conversation_history=self.executor.conversation_manager.get_messages(),
                session_id=session.session_id,
            )
            detection_report = self.executor.detection_coordinator.run_detection(context)

        result = AttackResult(
            attack_id=attack_id,
            session_id=session.session_id,
            success=success,
            execution_time=perf_counter() - started_at,
            response=response,
            detection_report=detection_report,
            telemetry={"strategy": strategy.technique.value if strategy.technique else "unknown"},
            metadata={"attack_name": attack_name},
            error=error_msg,
        )
        
        self.session_store.save_session(session)
        return result
