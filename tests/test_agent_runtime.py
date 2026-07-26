"""Unit tests for the Enterprise Agent Runtime & Staged Pipeline."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.decisions import CapabilityResolver
from app.agent.models import AgentRequest, AgentResponse
from app.agent.runtime import AgentRuntime
from app.config import settings
from app.conversation import ConversationManager
from app.memory_manager import MemoryManager
from app.prompts import PromptBuilder
from app.tools.manager import ToolManager


class TestCapabilityResolver:
    """Tests for CapabilityResolver intent classification."""

    def setup_method(self) -> None:
        self.resolver = CapabilityResolver()

    def test_resolve_ls_intent(self) -> None:
        ctx = AgentContext(
            request_id="req-1",
            session_id="s-1",
            user_prompt="List files in engineering",
        )
        res = self.resolver.resolve(ctx)
        assert res.capability_type == "FILESYSTEM_TOOL"
        assert res.tool_request is not None
        assert res.tool_request.tool_name == "ls"
        assert res.tool_request.arguments["path"] == "engineering"

    def test_resolve_cat_intent(self) -> None:
        ctx = AgentContext(
            request_id="req-2",
            session_id="s-1",
            user_prompt="Show file engineering/architecture_spec.md",
        )
        res = self.resolver.resolve(ctx)
        assert res.capability_type == "FILESYSTEM_TOOL"
        assert res.tool_request is not None
        assert res.tool_request.tool_name == "cat"
        assert res.tool_request.arguments["path"] == "engineering/architecture_spec.md"

    def test_resolve_grep_intent(self) -> None:
        ctx = AgentContext(
            request_id="req-3",
            session_id="s-1",
            user_prompt="Search for 'Project Aegis'",
        )
        res = self.resolver.resolve(ctx)
        assert res.capability_type == "FILESYSTEM_TOOL"
        assert res.tool_request is not None
        assert res.tool_request.tool_name == "grep"
        assert res.tool_request.arguments["query"] == "Project Aegis"

    def test_resolve_pwd_intent(self) -> None:
        ctx = AgentContext(
            request_id="req-4",
            session_id="s-1",
            user_prompt="What is the current working directory?",
        )
        res = self.resolver.resolve(ctx)
        assert res.capability_type == "FILESYSTEM_TOOL"
        assert res.tool_request is not None
        assert res.tool_request.tool_name == "pwd"

    def test_resolve_no_capability_intent(self) -> None:
        ctx = AgentContext(
            request_id="req-5", session_id="s-1", user_prompt="Hello, who are you?"
        )
        res = self.resolver.resolve(ctx)
        assert res.capability_type == "NONE"
        assert res.tool_request is None


class TestAgentRuntimeStagedPipeline:
    """Tests for the end-to-end AgentRuntime pipeline execution and stage telemetry."""

    def setup_method(self) -> None:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.memory_manager = MemoryManager()
        self.conversation_manager = ConversationManager()
        self.prompt_builder = PromptBuilder(
            system_prompt=settings.SYSTEM_PROMPT,
            conversation_manager=self.conversation_manager,
        )
        self.tool_manager = ToolManager()
        self.runtime = AgentRuntime(
            conversation_manager=self.conversation_manager,
            prompt_builder=self.prompt_builder,
            tool_manager=self.tool_manager,
            generate_chat_fn=lambda msgs: "Mocked LLM Response",
        )

    def test_process_request_without_tools(self) -> None:
        self.runtime.generate_chat_fn = lambda msgs: "Hello! I am Nexus Assistant."

        req = AgentRequest(user_prompt="Hello assistant", session_id="test-session")
        resp: AgentResponse = self.runtime.process_request(req)

        assert resp.response_text == "Hello! I am Nexus Assistant."
        assert resp.capability_used is None
        assert resp.total_duration_ms >= 0

        # Verify all 7 stages recorded telemetry
        stages = [s.stage_name for s in resp.stage_telemetry]
        assert "context_preparation" in stages
        assert "memory_retrieval" in stages
        assert "capability_resolution" in stages
        assert "tool_execution" in stages
        assert "prompt_building" in stages
        assert "model_inference" in stages

    def test_process_request_with_ls_tool(self) -> None:
        self.runtime.generate_chat_fn = (
            lambda msgs: "Here are the files in engineering: architecture_spec.md"
        )

        req = AgentRequest(
            user_prompt="List files in engineering", session_id="test-session"
        )
        resp: AgentResponse = self.runtime.process_request(req)

        assert resp.capability_used == "ls"
        tool_stage = next(
            s for s in resp.stage_telemetry if s.stage_name == "tool_execution"
        )
        assert tool_stage.status == "SUCCESS"
        assert tool_stage.details["tool_name"] == "ls"

    def test_process_request_with_cat_tool(self) -> None:
        self.runtime.generate_chat_fn = (
            lambda msgs: "Project Aegis is an autonomous threat mitigation platform."
        )

        req = AgentRequest(
            user_prompt="Read engineering/architecture_spec.md",
            session_id="test-session",
        )
        resp: AgentResponse = self.runtime.process_request(req)

        assert resp.capability_used == "cat"
        tool_stage = next(
            s for s in resp.stage_telemetry if s.stage_name == "tool_execution"
        )
        assert tool_stage.status == "SUCCESS"
        assert tool_stage.details["tool_name"] == "cat"

    def test_process_request_with_failed_tool_execution(self) -> None:
        self.runtime.generate_chat_fn = lambda msgs: "I could not find that file."

        req = AgentRequest(
            user_prompt="Read engineering/non_existent.md", session_id="test-session"
        )
        resp: AgentResponse = self.runtime.process_request(req)

        assert resp.capability_used == "cat"
        tool_stage = next(
            s for s in resp.stage_telemetry if s.stage_name == "tool_execution"
        )
        assert tool_stage.status == "FAILED"
