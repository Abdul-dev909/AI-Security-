"""Comprehensive unit tests for the Attack Library (Module 2).

Tests cover:
- BaseAttack metadata validation and engine-model conversion
- Each of the five attack modules (prompt injection, jailbreak,
  system prompt extraction, canary extraction, memory attacks)
- Registry integration via ``populate_registry``
"""

from __future__ import annotations

import pytest

from app.attack_engine.attacks import (
    ALL_ATTACKS,
    CANARY_EXTRACTION,
    JAILBREAK,
    MEMORY_ATTACKS,
    MEMORY_DISCLOSURE,
    MEMORY_OVERWRITE,
    MEMORY_POISONING,
    PROMPT_INJECTION,
    SYSTEM_PROMPT_EXTRACTION,
    BaseAttack,
    populate_registry,
)
from app.attack_engine.models import Attack
from app.attack_engine.registry import AttackRegistry


# ================================================================
# Helpers
# ================================================================

def _validate_attack_metadata(attack: BaseAttack) -> None:
    """Assert that every required metadata field is non-empty."""
    assert attack.name != "", "name must not be empty"
    assert attack.category != "", "category must not be empty"
    assert attack.description != "", "description must not be empty"
    assert attack.expected_behavior != "", "expected_behavior must not be empty"
    assert attack.difficulty in {"Easy", "Medium", "Hard"}, (
        f"difficulty must be Easy, Medium, or Hard — got '{attack.difficulty}'"
    )
    assert len(attack.prompts) > 0, "prompts list must not be empty"


# ================================================================
# BaseAttack Tests
# ================================================================

class TestBaseAttack:
    """Tests for the BaseAttack dataclass and its helper methods."""

    def test_metadata_fields_exist(self) -> None:
        """BaseAttack instances expose all required metadata fields."""
        attack = BaseAttack(
            name="Test",
            category="Test Category",
            difficulty="Easy",
            description="A test attack.",
            expected_behavior="Should be blocked.",
            prompts=["Hello"],
        )
        assert hasattr(attack, "name")
        assert hasattr(attack, "category")
        assert hasattr(attack, "difficulty")
        assert hasattr(attack, "description")
        assert hasattr(attack, "expected_behavior")
        assert hasattr(attack, "prompts")

    def test_required_field_types(self) -> None:
        """Field types match their specification."""
        attack = BaseAttack(
            name="Test",
            category="Category",
            difficulty="Medium",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p1", "p2"],
        )
        assert isinstance(attack.name, str)
        assert isinstance(attack.category, str)
        assert isinstance(attack.difficulty, str)
        assert isinstance(attack.description, str)
        assert isinstance(attack.expected_behavior, str)
        assert isinstance(attack.prompts, list)
        assert all(isinstance(p, str) for p in attack.prompts)

    def test_to_attack_models_count(self) -> None:
        """to_attack_models should produce one Attack per prompt."""
        attack = BaseAttack(
            name="Multi",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p1", "p2", "p3"],
        )
        models = attack.to_attack_models()
        assert len(models) == 3

    def test_to_attack_models_types(self) -> None:
        """Each produced model is an engine-compatible Attack instance."""
        attack = BaseAttack(
            name="Multi",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p1"],
        )
        models = attack.to_attack_models()
        assert all(isinstance(m, Attack) for m in models)

    def test_to_attack_models_severity_mapping(self) -> None:
        """Difficulty is correctly mapped to severity when not overridden."""
        for difficulty, expected_severity in [
            ("Easy", "low"),
            ("Medium", "medium"),
            ("Hard", "high"),
        ]:
            attack = BaseAttack(
                name="Test",
                category="Cat",
                difficulty=difficulty,
                description="Desc",
                expected_behavior="Behavior",
                prompts=["p1"],
            )
            model = attack.to_attack_models()[0]
            assert model.severity == expected_severity

    def test_to_attack_models_severity_override(self) -> None:
        """An explicit severity override takes precedence over the mapping."""
        attack = BaseAttack(
            name="Test",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p1"],
        )
        model = attack.to_attack_models(severity="critical")[0]
        assert model.severity == "critical"

    def test_to_attack_models_id_format(self) -> None:
        """Generated IDs follow the expected slug-index format."""
        attack = BaseAttack(
            name="My Attack",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p1", "p2"],
        )
        models = attack.to_attack_models()
        assert models[0].id == "my-attack-01"
        assert models[1].id == "my-attack-02"

    def test_to_attack_models_preserves_prompt_content(self) -> None:
        """The prompt text in each model matches the source prompt."""
        prompts = ["Alpha", "Bravo", "Charlie"]
        attack = BaseAttack(
            name="Test",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=prompts,
        )
        models = attack.to_attack_models()
        for model, original_prompt in zip(models, prompts):
            assert model.prompt == original_prompt

    def test_register_all_populates_registry(self) -> None:
        """register_all should insert all prompts into the registry."""
        registry = AttackRegistry()
        attack = BaseAttack(
            name="RegTest",
            category="Cat",
            difficulty="Medium",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["a", "b"],
        )
        registered = attack.register_all(registry)
        assert len(registered) == 2
        assert len(registry.list()) == 2

    def test_frozen_immutability(self) -> None:
        """BaseAttack instances should be immutable (frozen dataclass)."""
        attack = BaseAttack(
            name="Frozen",
            category="Cat",
            difficulty="Easy",
            description="Desc",
            expected_behavior="Behavior",
            prompts=["p"],
        )
        with pytest.raises(AttributeError):
            attack.name = "Changed"  # type: ignore[misc]


# ================================================================
# Prompt Injection Tests
# ================================================================

class TestPromptInjection:
    """Tests for the Prompt Injection attack definition."""

    def test_loads_correctly(self) -> None:
        """The module-level instance should be a BaseAttack."""
        assert isinstance(PROMPT_INJECTION, BaseAttack)

    def test_metadata_valid(self) -> None:
        """All required metadata fields are populated and valid."""
        _validate_attack_metadata(PROMPT_INJECTION)

    def test_category(self) -> None:
        """Category should be 'Prompt Injection'."""
        assert PROMPT_INJECTION.category == "Prompt Injection"

    def test_contains_prompts(self) -> None:
        """Should contain multiple prompt variants."""
        assert len(PROMPT_INJECTION.prompts) >= 5

    def test_prompts_are_strings(self) -> None:
        """Every prompt should be a non-empty string."""
        for prompt in PROMPT_INJECTION.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        """Conversion to engine Attack models should succeed."""
        models = PROMPT_INJECTION.to_attack_models()
        assert len(models) == len(PROMPT_INJECTION.prompts)
        assert all(isinstance(m, Attack) for m in models)


# ================================================================
# Jailbreak Tests
# ================================================================

class TestJailbreak:
    """Tests for the Jailbreak attack definition."""

    def test_loads_correctly(self) -> None:
        """The module-level instance should be a BaseAttack."""
        assert isinstance(JAILBREAK, BaseAttack)

    def test_metadata_valid(self) -> None:
        """All required metadata fields are populated and valid."""
        _validate_attack_metadata(JAILBREAK)

    def test_category(self) -> None:
        """Category should be 'Jailbreak'."""
        assert JAILBREAK.category == "Jailbreak"

    def test_contains_prompts(self) -> None:
        """Should contain multiple prompt variants."""
        assert len(JAILBREAK.prompts) >= 5

    def test_prompts_are_strings(self) -> None:
        """Every prompt should be a non-empty string."""
        for prompt in JAILBREAK.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        """Conversion to engine Attack models should succeed."""
        models = JAILBREAK.to_attack_models()
        assert len(models) == len(JAILBREAK.prompts)
        assert all(isinstance(m, Attack) for m in models)


# ================================================================
# System Prompt Extraction Tests
# ================================================================

class TestSystemPromptExtraction:
    """Tests for the System Prompt Extraction attack definition."""

    def test_loads_correctly(self) -> None:
        """The module-level instance should be a BaseAttack."""
        assert isinstance(SYSTEM_PROMPT_EXTRACTION, BaseAttack)

    def test_metadata_valid(self) -> None:
        """All required metadata fields are populated and valid."""
        _validate_attack_metadata(SYSTEM_PROMPT_EXTRACTION)

    def test_category(self) -> None:
        """Category should be 'Prompt Leakage'."""
        assert SYSTEM_PROMPT_EXTRACTION.category == "Prompt Leakage"

    def test_contains_prompts(self) -> None:
        """Should contain multiple prompt variants."""
        assert len(SYSTEM_PROMPT_EXTRACTION.prompts) >= 5

    def test_prompts_are_strings(self) -> None:
        """Every prompt should be a non-empty string."""
        for prompt in SYSTEM_PROMPT_EXTRACTION.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        """Conversion to engine Attack models should succeed."""
        models = SYSTEM_PROMPT_EXTRACTION.to_attack_models()
        assert len(models) == len(SYSTEM_PROMPT_EXTRACTION.prompts)
        assert all(isinstance(m, Attack) for m in models)


# ================================================================
# Canary Extraction Tests
# ================================================================

class TestCanaryExtraction:
    """Tests for the Canary Extraction attack definition."""

    def test_loads_correctly(self) -> None:
        """The module-level instance should be a BaseAttack."""
        assert isinstance(CANARY_EXTRACTION, BaseAttack)

    def test_metadata_valid(self) -> None:
        """All required metadata fields are populated and valid."""
        _validate_attack_metadata(CANARY_EXTRACTION)

    def test_category(self) -> None:
        """Category should be 'Canary Extraction'."""
        assert CANARY_EXTRACTION.category == "Canary Extraction"

    def test_contains_prompts(self) -> None:
        """Should contain multiple prompt variants."""
        assert len(CANARY_EXTRACTION.prompts) >= 5

    def test_prompts_are_strings(self) -> None:
        """Every prompt should be a non-empty string."""
        for prompt in CANARY_EXTRACTION.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        """Conversion to engine Attack models should succeed."""
        models = CANARY_EXTRACTION.to_attack_models()
        assert len(models) == len(CANARY_EXTRACTION.prompts)
        assert all(isinstance(m, Attack) for m in models)


# ================================================================
# Memory Attack Tests
# ================================================================

class TestMemoryOverwrite:
    """Tests for the Memory Overwrite attack definition."""

    def test_loads_correctly(self) -> None:
        assert isinstance(MEMORY_OVERWRITE, BaseAttack)

    def test_metadata_valid(self) -> None:
        _validate_attack_metadata(MEMORY_OVERWRITE)

    def test_category(self) -> None:
        assert MEMORY_OVERWRITE.category == "Memory Manipulation"

    def test_contains_prompts(self) -> None:
        assert len(MEMORY_OVERWRITE.prompts) >= 3

    def test_prompts_are_strings(self) -> None:
        for prompt in MEMORY_OVERWRITE.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        models = MEMORY_OVERWRITE.to_attack_models()
        assert len(models) == len(MEMORY_OVERWRITE.prompts)
        assert all(isinstance(m, Attack) for m in models)


class TestMemoryDisclosure:
    """Tests for the Memory Disclosure attack definition."""

    def test_loads_correctly(self) -> None:
        assert isinstance(MEMORY_DISCLOSURE, BaseAttack)

    def test_metadata_valid(self) -> None:
        _validate_attack_metadata(MEMORY_DISCLOSURE)

    def test_category(self) -> None:
        assert MEMORY_DISCLOSURE.category == "Memory Manipulation"

    def test_contains_prompts(self) -> None:
        assert len(MEMORY_DISCLOSURE.prompts) >= 3

    def test_prompts_are_strings(self) -> None:
        for prompt in MEMORY_DISCLOSURE.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        models = MEMORY_DISCLOSURE.to_attack_models()
        assert len(models) == len(MEMORY_DISCLOSURE.prompts)
        assert all(isinstance(m, Attack) for m in models)


class TestMemoryPoisoning:
    """Tests for the Memory Poisoning attack definition."""

    def test_loads_correctly(self) -> None:
        assert isinstance(MEMORY_POISONING, BaseAttack)

    def test_metadata_valid(self) -> None:
        _validate_attack_metadata(MEMORY_POISONING)

    def test_category(self) -> None:
        assert MEMORY_POISONING.category == "Memory Manipulation"

    def test_contains_prompts(self) -> None:
        assert len(MEMORY_POISONING.prompts) >= 3

    def test_prompts_are_strings(self) -> None:
        for prompt in MEMORY_POISONING.prompts:
            assert isinstance(prompt, str)
            assert prompt != ""

    def test_engine_model_conversion(self) -> None:
        models = MEMORY_POISONING.to_attack_models()
        assert len(models) == len(MEMORY_POISONING.prompts)
        assert all(isinstance(m, Attack) for m in models)


class TestMemoryAttacksTuple:
    """Tests for the MEMORY_ATTACKS convenience tuple."""

    def test_contains_all_sub_attacks(self) -> None:
        assert len(MEMORY_ATTACKS) == 3

    def test_members_are_base_attacks(self) -> None:
        assert all(isinstance(a, BaseAttack) for a in MEMORY_ATTACKS)


# ================================================================
# ALL_ATTACKS & Registry Integration Tests
# ================================================================

class TestAllAttacks:
    """Tests for ALL_ATTACKS aggregation and registry integration."""

    def test_all_attacks_count(self) -> None:
        """ALL_ATTACKS should contain all 7 attack definitions."""
        assert len(ALL_ATTACKS) == 7

    def test_all_attacks_are_base_attacks(self) -> None:
        """Every entry in ALL_ATTACKS should be a BaseAttack."""
        for attack in ALL_ATTACKS:
            assert isinstance(attack, BaseAttack)

    def test_all_attacks_metadata_valid(self) -> None:
        """Every attack in ALL_ATTACKS must pass metadata validation."""
        for attack in ALL_ATTACKS:
            _validate_attack_metadata(attack)

    def test_all_attacks_unique_names(self) -> None:
        """Attack names must be unique across the library."""
        names = [a.name for a in ALL_ATTACKS]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"


class TestPopulateRegistry:
    """Tests for the populate_registry integration helper."""

    def test_populates_all_attacks(self) -> None:
        """populate_registry should register every prompt across all attacks."""
        registry = AttackRegistry()
        registered = populate_registry(registry)
        total_prompts = sum(len(a.prompts) for a in ALL_ATTACKS)
        assert len(registered) == total_prompts
        assert len(registry.list()) == total_prompts

    def test_populates_subset(self) -> None:
        """populate_registry should accept a custom subset."""
        registry = AttackRegistry()
        registered = populate_registry(registry, attacks=[PROMPT_INJECTION])
        assert len(registered) == len(PROMPT_INJECTION.prompts)

    def test_registered_attacks_have_unique_ids(self) -> None:
        """All registered Attack IDs must be unique."""
        registry = AttackRegistry()
        populate_registry(registry)
        ids = [a.id for a in registry.list()]
        assert len(ids) == len(set(ids)), f"Duplicate IDs detected: {ids}"

    def test_registered_attacks_are_engine_compatible(self) -> None:
        """All registered instances should be engine Attack models."""
        registry = AttackRegistry()
        populate_registry(registry)
        for attack in registry.list():
            assert isinstance(attack, Attack)
            assert attack.id != ""
            assert attack.name != ""
            assert attack.category != ""
            assert attack.description != ""
            assert attack.prompt != ""
            assert attack.severity != ""
