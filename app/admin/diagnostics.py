"""Comprehensive runtime diagnostics endpoint."""

from __future__ import annotations

import contextlib
import time

from fastapi import APIRouter, Depends, Request

from app.admin.dependencies import get_admin_dependency
from app.admin.models import DiagnosticsReport
from app.admin.probes import collect_all_probes

router = APIRouter(prefix="/diagnostics", tags=["Admin — Diagnostics"])

_START_TIME = time.time()


@router.get(
    "", response_model=DiagnosticsReport, summary="Full runtime diagnostics snapshot"
)
def get_diagnostics(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> DiagnosticsReport:
    """Return a comprehensive snapshot of all runtime subsystems."""
    uptime = time.time() - _START_TIME

    # --- Sessions ---
    memory_manager = getattr(request.app.state, "memory_manager", None)
    active_sessions = 0
    if memory_manager and hasattr(memory_manager, "session_manager"):
        with contextlib.suppress(Exception):
            active_sessions = memory_manager.session_manager.session_count()

    # --- Telemetry buffer stats ---
    telemetry_manager = getattr(request.app.state, "telemetry_manager", None)
    buffer_stats: dict = {}
    total_requests = 0
    stage_timing_avgs: dict[str, float] = {}
    tool_execs_total = 0

    if telemetry_manager:
        buffer_stats = telemetry_manager.get_all_stats()
        total_requests = buffer_stats.get("runtime", {}).get("total_pushed", 0)

        runtime_events = telemetry_manager.get_runtime_events(limit=500)
        if runtime_events:
            n = len(runtime_events)
            stage_timing_avgs = {
                "memory_retrieval": round(
                    sum(e.memory_latency_ms for e in runtime_events) / n, 3
                ),
                "knowledge_retrieval": round(
                    sum(e.knowledge_latency_ms for e in runtime_events) / n, 3
                ),
                "model_inference": round(
                    sum(e.llm_latency_ms for e in runtime_events) / n, 3
                ),
                "tool_execution": round(
                    sum(e.tool_latency_ms for e in runtime_events) / n, 3
                ),
            }

        telemetry_manager.get_tool_events(limit=500)
        tool_execs_total = buffer_stats.get("tools", {}).get("total_pushed", 0)

    # --- Vector count ---
    vector_count = 0
    indexed_docs = 0
    try:
        from app.knowledge.vectorstore import VectorStore

        vector_count = VectorStore().count()
    except Exception:
        pass
    try:
        from app.knowledge.loader import DocumentLoader

        docs = DocumentLoader().load_documents()
        indexed_docs = len(docs)
    except Exception:
        pass

    # --- Subsystem probes ---
    tool_manager = getattr(request.app.state, "tool_manager", None)
    subsystems = collect_all_probes(tool_manager)

    return DiagnosticsReport(
        uptime_seconds=round(uptime, 2),
        active_sessions=active_sessions,
        total_requests_served=total_requests,
        vector_count=vector_count,
        indexed_documents=indexed_docs,
        tool_executions_total=tool_execs_total,
        stage_timing_averages=stage_timing_avgs,
        subsystems=subsystems,
        telemetry_buffer_stats=buffer_stats,
    )
