"""Unit tests for the enterprise attack architecture foundation."""

from __future__ import annotations

from app.attack_engine.registry import AttackRegistry as LegacyAttackRegistry
from app.attacks import (
    AttackCategory,
    AttackExecutor,
    AttackRegistry,
    AttackSession,
    AttackSeverity,
    AttackTechnique,
    PROMPT_INJECTION,
    load_builtin_attacks,
)
from app.attacks.orchestrator import AttackOrchestrator
from app.attacks.events import EventBus
from app.attacks.storage import InMemorySessionStore
from app.conversation import ConversationManager
from app.detection.coordinator import DetectionCoordinator
from app.detection.registry import DetectorRegistry
from app.prompts import PromptBuilder


def test_builtin_attack_library_loads_structured_definitions() -> None:
    registry = AttackRegistry()
    loaded = load_builtin_attacks(registry)

    assert len(loaded) == 7
    assert len(registry.list_available()) == 7
    assert registry.get("prompt-injection").name == "Prompt Injection"
    assert registry.get("jailbreak").severity == AttackSeverity.HIGH

    legacy_attacks = registry.list_attacks()
    assert len(legacy_attacks) == 44
    assert legacy_attacks[0].id == "prompt-injection-01"


def test_attack_lookup_by_category_and_technique() -> None:
    registry = AttackRegistry()
    load_builtin_attacks(registry)

    by_category = registry.get_by_category(AttackCategory.MEMORY_MANIPULATION)
    by_technique = registry.get_by_technique(AttackTechnique.SYSTEM_PROMPT_EXTRACTION)

    assert {attack.attack_id for attack in by_category} == {
        "memory-overwrite",
        "memory-disclosure",
        "memory-poisoning",
    }
    assert [attack.attack_id for attack in by_technique] == [
        "system-prompt-extraction"
    ]


def test_attack_session_tracks_lifecycle() -> None:
    session = AttackSession(attack_id="prompt-injection")

    assert session.status == "pending"
    assert session.started_at is None

    session.start(stage="reconnaissance")
    session.add_message("user", "Hello")
    session.advance_stage("payload_delivery")
    session.complete()

    assert session.status == "completed"
    assert session.current_stage == "payload_delivery"
    assert session.started_at is not None
    assert session.completed_at is not None
    assert session.messages == [{"role": "user", "content": "Hello"}]


def test_attack_executor_generates_normalized_result() -> None:
    conversation_manager = ConversationManager()
    prompt_builder = PromptBuilder(
        system_prompt="System instructions",
        conversation_manager=conversation_manager,
    )
    detection_coordinator = DetectionCoordinator(registry=DetectorRegistry())

    captured_messages: list[list[dict[str, str]]] = []

    def fake_response_generator(messages: list[dict[str, str]]) -> str:
        captured_messages.append(messages)
        return "Mocked LLM Response"

    executor = AttackExecutor(
        prompt_builder=prompt_builder,
        conversation_manager=conversation_manager,
        detection_coordinator=detection_coordinator,
        response_generator=fake_response_generator,
    )
    orchestrator = AttackOrchestrator(
        executor=executor,
        session_store=InMemorySessionStore(),
        event_bus=EventBus(),
    )

    result = orchestrator.execute_attack(PROMPT_INJECTION)

    assert result.attack_id == "prompt-injection"
    assert result.success is True
    assert result.response == "Mocked LLM Response"
    assert result.session_id != ""
    assert result.execution_time >= 0.0
    assert result.detection_report is not None
    assert captured_messages
    assert result.telemetry["strategy"] == AttackTechnique.INSTRUCTION_OVERRIDE.value


def test_legacy_registry_still_accepts_legacy_attack_models() -> None:
    registry = LegacyAttackRegistry()
    assert registry.list() == []
