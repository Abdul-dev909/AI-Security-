"""Main AgentRuntime orchestrator implementing a modular staged execution pipeline."""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.agent.context import AgentContext
from app.agent.decisions import CapabilityResolver
from app.agent.executor import AgentExecutor
from app.agent.models import AgentRequest, AgentResponse
from app.agent.planner import AgentPlanner
from app.config import settings
from app.conversation import ConversationManager
from app.detection import DetectionCoordinator
from app.detection.models import DetectionContext, DetectionReport
from app.ollama_client import (
    OllamaClientError,
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
    generate_chat_response,
)
from app.prompts import PromptBuilder
from app.tools.manager import ToolManager
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Staged Execution Pipeline for the AI Security Platform Agent.

    Executes modular processing stages:
    1. Context & History Preparation
    2. Memory Search Stage
    3. Capability Resolution Stage
    4. Tool Execution Stage
    5. Prompt Building Stage
    6. Model Inference Stage
    7. Detection & Telemetry Stage
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
        prompt_builder: PromptBuilder,
        detection_coordinator: DetectionCoordinator | None = None,
        tool_manager: ToolManager | None = None,
        capability_resolver: CapabilityResolver | None = None,
        planner: AgentPlanner | None = None,
        executor: AgentExecutor | None = None,
        generate_chat_fn: Callable[[list[dict[str, str]]], str] | None = None,
    ) -> None:
        self.conversation_manager = conversation_manager
        self.prompt_builder = prompt_builder
        self.detection_coordinator = detection_coordinator
        self.tool_manager = tool_manager or ToolManager()
        self.capability_resolver = capability_resolver or CapabilityResolver()
        self.planner = planner or AgentPlanner()
        self.executor = executor or AgentExecutor(tool_manager=self.tool_manager)
        self.generate_chat_fn = generate_chat_fn or generate_chat_response

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process an incoming request through the staged pipeline."""
        context = AgentContext(
            request_id=request.request_id,
            session_id=request.session_id,
            user_prompt=request.user_prompt,
        )

        with execution_timer() as total_timer:
            # Stage 1: Context & History Preparation
            self._stage_context_preparation(context)

            # Stage 2: Memory Retrieval
            self._stage_memory_retrieval(context)

            # Stage 3: Capability Resolution
            self._stage_capability_resolution(context)

            # Stage 4: Tool Execution (Optional)
            self._stage_tool_execution(context)

            # Stage 5: Prompt Building
            self._stage_prompt_building(context)

            # Stage 6: Model Inference
            self._stage_model_inference(context)

            # Stage 7: Detection & Telemetry Pipeline
            self._stage_detection_pipeline(context)

        total_duration_ms = round(total_timer() * 1000, 3)

        # Update in-memory conversation history
        if context.raw_ai_response:
            self.conversation_manager.add_user_message(request.user_prompt)
            self.conversation_manager.add_assistant_message(context.raw_ai_response)
            self.conversation_manager.save_memory_if_important(request.user_prompt)

        capability_name = (
            context.capability_resolution.tool_request.tool_name
            if context.capability_resolution
            and context.capability_resolution.tool_request
            else None
        )

        return AgentResponse(
            request_id=context.request_id,
            session_id=context.session_id,
            response_text=context.raw_ai_response or "",
            conversation_history=self.conversation_manager.get_messages(),
            capability_used=capability_name,
            tool_result=(
                None if not context.tool_result else None
            ),  # Can be expanded for API response
            total_duration_ms=total_duration_ms,
            stage_telemetry=context.stage_telemetry,
        )

    # --- Pipeline Stage Implementations ---

    def _stage_context_preparation(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            context.conversation_history = self.conversation_manager.get_messages()
            context.available_tools = self.tool_manager.registry.list_tools()
        context.record_stage(
            "context_preparation",
            timer() * 1000,
            details={
                "history_count": len(context.conversation_history),
                "tool_count": len(context.available_tools),
            },
        )

    def _stage_memory_retrieval(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            memories = self.conversation_manager.search_memories(context.user_prompt)
            context.memories = memories
        context.record_stage(
            "memory_retrieval", timer() * 1000, details={"memory_count": len(memories)}
        )

    def _stage_capability_resolution(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            resolution = self.capability_resolver.resolve(context)
            refined_resolution = self.planner.plan(context, resolution)
            context.capability_resolution = refined_resolution
        tool_name = (
            refined_resolution.tool_request.tool_name
            if refined_resolution.tool_request
            else None
        )
        context.record_stage(
            "capability_resolution",
            timer() * 1000,
            details={
                "capability_type": refined_resolution.capability_type,
                "selected_tool": tool_name,
            },
        )

    def _stage_tool_execution(self, context: AgentContext) -> None:
        resolution = context.capability_resolution
        if not resolution or not resolution.tool_request:
            context.record_stage(
                "tool_execution",
                0.0,
                status="SKIPPED",
                details={"reason": "No tool requested"},
            )
            return

        tool_req = resolution.tool_request
        with execution_timer() as timer:
            result = self.executor.execute_capability(context, tool_req)
            context.tool_result = result
        context.record_stage(
            "tool_execution",
            timer() * 1000,
            status="SUCCESS" if result.success else "FAILED",
            details={
                "tool_name": result.tool_name,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error_message,
            },
        )

    def _stage_prompt_building(self, context: AgentContext) -> None:
        tool_output = (
            context.tool_result.formatted_output if context.tool_result else None
        )
        with execution_timer() as timer:
            messages = self.prompt_builder.build_messages(
                user_message=context.user_prompt,
                memories=context.memories,
                conversation_history=context.conversation_history,
                tool_output=tool_output,
            )
            context.formatted_messages = messages
        context.record_stage(
            "prompt_building", timer() * 1000, details={"message_count": len(messages)}
        )

    def _stage_model_inference(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            try:
                import app.routes.chat as chat_routes

                fn = getattr(
                    chat_routes, "generate_chat_response", self.generate_chat_fn
                )
                response_text = fn(context.formatted_messages)
            except (
                OllamaTimeoutError,
                OllamaConnectionError,
                OllamaResponseError,
                OllamaClientError,
            ) as exc:
                logger.warning("Ollama inference failed, falling back: %s", exc)
                response_text = settings.FALLBACK_RESPONSE
            context.raw_ai_response = response_text
        context.record_stage(
            "model_inference",
            timer() * 1000,
            details={"response_length": len(response_text)},
        )

    def _stage_detection_pipeline(self, context: AgentContext) -> None:
        if not self.detection_coordinator:
            context.record_stage("detection_pipeline", 0.0, status="SKIPPED")
            return

        with execution_timer() as timer:
            det_context = DetectionContext(
                user_prompt=context.user_prompt,
                ai_response=context.raw_ai_response or "",
                conversation_history=context.conversation_history,
            )
            report: DetectionReport = self.detection_coordinator.run_detection(
                det_context
            )
            context.detection_report = report

        context.record_stage(
            "detection_pipeline",
            timer() * 1000,
            details={
                "total_detectors": report.total_detectors_executed,
                "total_detections": report.total_detections,
                "highest_severity": report.highest_severity,
            },
        )
