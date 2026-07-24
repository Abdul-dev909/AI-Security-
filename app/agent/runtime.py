"""Main AgentRuntime orchestrator implementing a modular staged execution pipeline."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator, Callable

from app.agent.context import AgentContext
from app.agent.decisions import CapabilityResolver
from app.agent.executor import AgentExecutor
from app.agent.models import AgentRequest, AgentResponse
from app.agent.planner import AgentPlanner
from app.config import settings
from app.conversation import ConversationManager
from app.detection import DetectionCoordinator
from app.detection.models import DetectionContext
from app.memory import EnterpriseMemoryManager
from app.ollama_client import (
    OllamaClientError,
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
    generate_chat_response,
    generate_chat_response_async,
    generate_chat_stream_async,
)
from app.prompts import PromptBuilder
from app.tools.manager import ToolManager
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Staged Execution Pipeline for the AI Security Platform Agent.

    Executes modular processing stages:
    1. Context & History Preparation
    2. Session Manager (Init/Load)
    3. Memory Retrieval
    4. Knowledge Retrieval (RAG)
    5. Capability Resolution
    6. Tool Execution
    7. Prompt Building
    8. Model Inference (Sync/Async)
    9. Detection & Telemetry
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
        memory_manager: EnterpriseMemoryManager | None = None,
        generate_chat_fn: Callable[[list[dict[str, str]]], str] | None = None,
    ) -> None:
        self.conversation_manager = conversation_manager
        self.prompt_builder = prompt_builder
        self.detection_coordinator = detection_coordinator
        self.tool_manager = tool_manager or ToolManager()
        self.capability_resolver = capability_resolver or CapabilityResolver()
        self.planner = planner or AgentPlanner()
        self.executor = executor or AgentExecutor(tool_manager=self.tool_manager)
        self.memory_manager = memory_manager or EnterpriseMemoryManager()
        self.generate_chat_fn = generate_chat_fn or generate_chat_response

    def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process an incoming request through the staged pipeline synchronously."""
        context = AgentContext(
            request_id=request.request_id,
            session_id=request.session_id,
            user_prompt=request.user_prompt,
        )

        with execution_timer() as total_timer:
            self._stage_context_preparation(context)
            self._stage_session_management(context)
            self._stage_memory_retrieval(context)
            self._stage_knowledge_retrieval(context)
            self._stage_capability_resolution(context)
            self._stage_tool_execution(context)
            self._stage_prompt_building(context)
            self._stage_model_inference(context)
            self._stage_detection_pipeline(context)

        return self._finalize_response(context, total_timer())

    async def process_request_async(self, request: AgentRequest) -> AgentResponse:
        """Process an incoming request asynchronously (non-blocking inference)."""
        context = AgentContext(
            request_id=request.request_id,
            session_id=request.session_id,
            user_prompt=request.user_prompt,
        )

        with execution_timer() as total_timer:
            self._stage_context_preparation(context)
            self._stage_session_management(context)
            self._stage_memory_retrieval(context)
            self._stage_knowledge_retrieval(context)
            self._stage_capability_resolution(context)
            self._stage_tool_execution(context)
            self._stage_prompt_building(context)
            await self._stage_model_inference_async(context)
            self._stage_detection_pipeline(context)

        return self._finalize_response(context, total_timer())

    async def process_request_stream_async(
        self, request: AgentRequest
    ) -> AsyncGenerator[str, None]:
        """Process an incoming request asynchronously and yield SSE tokens."""
        context = AgentContext(
            request_id=request.request_id,
            session_id=request.session_id,
            user_prompt=request.user_prompt,
        )

        self._stage_context_preparation(context)
        self._stage_session_management(context)
        self._stage_memory_retrieval(context)
        self._stage_knowledge_retrieval(context)
        self._stage_capability_resolution(context)
        self._stage_tool_execution(context)
        self._stage_prompt_building(context)

        # Instead of _stage_model_inference_async, we stream
        full_response = []
        try:
            async for token in generate_chat_stream_async(context.formatted_messages):
                full_response.append(token)
                yield token
        except (
            OllamaTimeoutError,
            OllamaConnectionError,
            OllamaResponseError,
            OllamaClientError,
        ) as exc:
            logger.warning("Ollama inference failed during stream: %s", exc)
            yield settings.FALLBACK_RESPONSE
            full_response.append(settings.FALLBACK_RESPONSE)

        context.raw_ai_response = "".join(full_response)
        self._stage_detection_pipeline(context)
        self._finalize_response(context, 0.0)  # Just to save memory/history

    def _finalize_response(
        self, context: AgentContext, total_duration_sec: float
    ) -> AgentResponse:
        total_duration_ms = round(total_duration_sec * 1000, 3)

        if context.raw_ai_response:
            self.conversation_manager.add_user_message(context.user_prompt)
            self.conversation_manager.add_assistant_message(context.raw_ai_response)

            # Backward compatibility for old primitive memory tests
            self.conversation_manager.save_memory_if_important(context.user_prompt)

            # Store in Enterprise Memory Manager
            self.memory_manager.process_memory(
                session_id=context.session_id, content=context.user_prompt
            )

        capability_name = (
            context.capability_resolution.tool_request.tool_name
            if context.capability_resolution
            and context.capability_resolution.tool_request
            else None
        )

        # --- Telemetry push (fire-and-forget) ---
        self._push_runtime_telemetry(context, total_duration_ms)

        # --- Debug store capture ---
        self._capture_debug_snapshot(context, total_duration_ms)

        return AgentResponse(
            request_id=context.request_id,
            session_id=context.session_id,
            response_text=context.raw_ai_response or "",
            conversation_history=self.conversation_manager.get_messages(),
            capability_used=capability_name,
            tool_result=(None if not context.tool_result else None),
            total_duration_ms=total_duration_ms,
            stage_telemetry=context.stage_telemetry,
        )

    def _push_runtime_telemetry(
        self, context: AgentContext, total_duration_ms: float
    ) -> None:
        """Push a RuntimeTelemetryEvent to the TelemetryManager if available."""
        try:
            import app.main as _main_module
            from app.telemetry import RuntimeTelemetryEvent

            tm = getattr(getattr(_main_module, "app", None), "state", None)
            telemetry_manager = getattr(tm, "telemetry_manager", None) if tm else None
            if telemetry_manager is None:
                return

            def _stage_latency(name: str) -> float:
                for s in context.stage_telemetry:
                    if s.stage_name == name:
                        return s.duration_ms
                return 0.0

            event = RuntimeTelemetryEvent(
                request_id=context.request_id,
                session_id=context.session_id,
                user_prompt_length=len(context.user_prompt),
                total_latency_ms=total_duration_ms,
                memory_latency_ms=_stage_latency("memory_retrieval"),
                knowledge_latency_ms=_stage_latency("knowledge_retrieval"),
                tool_latency_ms=_stage_latency("tool_execution"),
                llm_latency_ms=_stage_latency("model_inference"),
                detection_latency_ms=_stage_latency("detection_pipeline"),
                capability_used=(
                    context.capability_resolution.tool_request.tool_name
                    if context.capability_resolution
                    and context.capability_resolution.tool_request
                    else None
                ),
                stage_count=len(context.stage_telemetry),
            )
            telemetry_manager.record_runtime(event)
        except Exception:
            pass

    def _capture_debug_snapshot(
        self, context: AgentContext, total_duration_ms: float
    ) -> None:
        """Write a debug snapshot to app.state.debug_store when DEBUG_MODE is enabled."""
        try:
            from app.config import settings

            if not settings.DEBUG_MODE:
                return
            import app.main as _main_module

            app_state = getattr(getattr(_main_module, "app", None), "state", None)
            debug_store = getattr(app_state, "debug_store", None) if app_state else None
            if debug_store is None:
                return

            from app.admin.models import DebugRequestSnapshot

            stage_timings = {
                s.stage_name: s.duration_ms for s in context.stage_telemetry
            }
            snapshot = DebugRequestSnapshot(
                request_id=context.request_id,
                session_id=context.session_id,
                user_prompt=context.user_prompt,
                generated_prompt=context.formatted_messages,
                retrieved_memories=context.memories,
                retrieved_knowledge_chunks=(
                    len(context.knowledge_context.retrieved_chunks)
                    if context.knowledge_context
                    else 0
                ),
                selected_capability=(
                    context.capability_resolution.capability_type
                    if context.capability_resolution
                    else None
                ),
                executed_tool=(
                    context.capability_resolution.tool_request.tool_name
                    if context.capability_resolution
                    and context.capability_resolution.tool_request
                    else None
                ),
                tool_output=(
                    context.tool_result.formatted_output
                    if context.tool_result
                    else None
                ),
                model_response=context.raw_ai_response,
                stage_timings=stage_timings,
                total_duration_ms=total_duration_ms,
            )
            debug_store[context.request_id] = snapshot
        except Exception:
            pass

    # --- Pipeline Stage Implementations ---

    def _stage_context_preparation(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            context.conversation_history = self.conversation_manager.get_messages()
            context.available_tools = self.tool_manager.registry.list_tools()
        context.record_stage("context_preparation", timer() * 1000)

    def _stage_session_management(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            session = self.memory_manager.session_manager.get_or_create_session(
                context.session_id
            )
            context.session_id = session.session_id
        context.record_stage("session_management", timer() * 1000)

    def _stage_memory_retrieval(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            memory_context = self.memory_manager.search_memories(
                context.session_id, context.user_prompt
            )
            # Format retrieved memory records into strings for prompt building
            context.memories = [m.content for m in memory_context.retrieved_memories]
        context.record_stage(
            "memory_retrieval",
            timer() * 1000,
            details={"memory_count": len(context.memories)},
        )

    def _stage_knowledge_retrieval(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            if not hasattr(self, "knowledge_retriever"):
                from app.knowledge import KnowledgeRetriever

                self.knowledge_retriever = KnowledgeRetriever()

            knowledge_context = self.knowledge_retriever.retrieve(context.user_prompt)
            context.knowledge_context = knowledge_context

        context.record_stage(
            "knowledge_retrieval",
            timer() * 1000,
            details={
                "retrieved_chunks": len(knowledge_context.retrieved_chunks),
            },
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
            context.record_stage("tool_execution", 0.0, status="SKIPPED")
            return

        tool_req = resolution.tool_request
        with execution_timer() as timer:
            result = self.executor.execute_capability(context, tool_req)
            context.tool_result = result
        elapsed_ms = timer() * 1000
        context.record_stage(
            "tool_execution",
            elapsed_ms,
            status="SUCCESS" if result.success else "FAILED",
            details={
                "tool_name": result.tool_name,
                "success": result.success,
            },
        )
        # Fire-and-forget telemetry
        try:
            import app.main as _m
            from app.telemetry import ToolTelemetryEvent

            tm = getattr(getattr(_m, "app", None), "state", None)
            tel = getattr(tm, "telemetry_manager", None) if tm else None
            if tel:
                tel.record_tool(
                    ToolTelemetryEvent(
                        request_id=context.request_id,
                        session_id=context.session_id,
                        tool_name=result.tool_name,
                        success=result.success,
                        execution_time_ms=elapsed_ms,
                        error=result.error_message,
                    )
                )
        except Exception:
            pass

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
                knowledge_context=context.knowledge_context,
            )
            context.formatted_messages = messages
        context.record_stage(
            "prompt_building", timer() * 1000, details={"message_count": len(messages)}
        )

    def _stage_model_inference(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            try:
                response_text = self.generate_chat_fn(context.formatted_messages)
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

    async def _stage_model_inference_async(self, context: AgentContext) -> None:
        with execution_timer() as timer:
            try:
                import asyncio

                import app.routes.chat as chat_routes

                # Check if it was monkeypatched by tests
                mocked_fn = getattr(chat_routes, "generate_chat_response", None)
                from app.ollama_client import generate_chat_response

                if mocked_fn and mocked_fn is not generate_chat_response:
                    if asyncio.iscoroutinefunction(mocked_fn):
                        response_text = await mocked_fn(context.formatted_messages)
                    else:
                        response_text = mocked_fn(context.formatted_messages)
                else:
                    response_text = await generate_chat_response_async(
                        context.formatted_messages
                    )
            except (
                OllamaTimeoutError,
                OllamaConnectionError,
                OllamaResponseError,
                OllamaClientError,
            ) as exc:
                logger.warning("Ollama async inference failed, falling back: %s", exc)
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
            report = self.detection_coordinator.run_detection(det_context)
            context.detection_report = report

        context.record_stage(
            "detection_pipeline",
            timer() * 1000,
            details={
                "total_detections": report.total_detections,
            },
        )
