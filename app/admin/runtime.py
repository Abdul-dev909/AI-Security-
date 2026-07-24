"""Runtime administration endpoints."""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Request

from app.admin.dependencies import get_admin_dependency
from app.admin.models import (
    ComponentHealth,
    RuntimeMetrics,
    RuntimeStatus,
    SessionSummary,
)
from app.admin.probes import collect_all_probes
from app.configuration import ConfigurationService

router = APIRouter(prefix="/runtime", tags=["Admin — Runtime"])

# Application start time for uptime tracking
_START_TIME = time.time()
_config_service = ConfigurationService()


@router.get("/status", response_model=RuntimeStatus, summary="Runtime status overview")
def get_runtime_status(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> RuntimeStatus:
    """Return current runtime status including component health."""
    uptime = time.time() - _START_TIME

    tool_manager = getattr(request.app.state, "tool_manager", None)
    probes = collect_all_probes(tool_manager)
    components = list(probes.values())

    memory_manager = getattr(request.app.state, "memory_manager", None)
    active_sessions = 0
    if memory_manager and hasattr(memory_manager, "session_manager"):
        try:
            active_sessions = len(memory_manager.session_manager.list_sessions())
        except Exception:
            pass

    telemetry_manager = getattr(request.app.state, "telemetry_manager", None)
    total_requests = 0
    stage_averages: dict[str, float] = {}
    if telemetry_manager:
        events = telemetry_manager.get_runtime_events(limit=500)
        total_requests = len(
            telemetry_manager._buffers.buffer("runtime").stats().get("total_pushed", 0)
            and events
            or events
        )
        total_requests = telemetry_manager._buffers.buffer("runtime").stats()[
            "total_pushed"
        ]
        if events:
            stage_avgs: dict[str, float] = {}
            stage_counts: dict[str, int] = {}
            for ev in events:
                for stage, latency in [
                    ("memory", ev.memory_latency_ms),
                    ("knowledge", ev.knowledge_latency_ms),
                    ("llm", ev.llm_latency_ms),
                    ("tool", ev.tool_latency_ms),
                ]:
                    stage_avgs[stage] = stage_avgs.get(stage, 0.0) + latency
                    stage_counts[stage] = stage_counts.get(stage, 0) + 1
            stage_averages = {
                k: round(v / stage_counts[k], 3) for k, v in stage_avgs.items()
            }

    return RuntimeStatus(
        uptime_seconds=round(uptime, 2),
        active_sessions=active_sessions,
        total_requests_served=total_requests,
        stage_timing_averages=stage_averages,
        components=components,
    )


@router.get(
    "/metrics", response_model=RuntimeMetrics, summary="Runtime performance metrics"
)
def get_runtime_metrics(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> RuntimeMetrics:
    """Computed performance metrics from the telemetry buffer."""
    telemetry_manager = getattr(request.app.state, "telemetry_manager", None)
    if not telemetry_manager:
        return RuntimeMetrics()

    runtime_events = telemetry_manager.get_runtime_events(limit=500)
    tool_events = telemetry_manager.get_tool_events(limit=500)
    detection_events = telemetry_manager.get_detection_events(limit=500)

    total = len(runtime_events)
    avg_latency = 0.0
    p95 = 0.0
    avg_mem = 0.0
    avg_llm = 0.0
    avg_knowledge = 0.0

    if total:
        latencies = sorted(e.total_latency_ms for e in runtime_events)
        avg_latency = round(sum(latencies) / total, 3)
        p95 = round(latencies[int(total * 0.95)], 3) if total > 1 else latencies[0]
        avg_mem = round(sum(e.memory_latency_ms for e in runtime_events) / total, 3)
        avg_llm = round(sum(e.llm_latency_ms for e in runtime_events) / total, 3)
        avg_knowledge = round(
            sum(e.knowledge_latency_ms for e in runtime_events) / total, 3
        )

    return RuntimeMetrics(
        total_events=total,
        avg_latency_ms=avg_latency,
        p95_latency_ms=p95,
        avg_memory_latency_ms=avg_mem,
        avg_llm_latency_ms=avg_llm,
        avg_knowledge_latency_ms=avg_knowledge,
        tool_executions=len(tool_events),
        detection_scans=len(detection_events),
    )


@router.get("/config", summary="Runtime configuration snapshot")
def get_runtime_config(
    _: None = Depends(get_admin_dependency),
) -> dict:
    """Read-only view of active configuration. Sensitive values are masked."""
    return _config_service.get_snapshot()


@router.get("/sessions", response_model=list[SessionSummary], summary="Active sessions")
def get_sessions(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> list[SessionSummary]:
    """List all known sessions from the SessionManager."""
    memory_manager = getattr(request.app.state, "memory_manager", None)
    if not memory_manager or not hasattr(memory_manager, "session_manager"):
        return []
    try:
        sessions = memory_manager.session_manager.list_sessions()
        return [
            SessionSummary(
                session_id=s.session_id,
                created_at=(
                    s.created_at.isoformat()
                    if hasattr(s.created_at, "isoformat")
                    else str(s.created_at)
                ),
                last_active=(
                    s.last_active.isoformat()
                    if hasattr(s.last_active, "isoformat")
                    else str(s.last_active)
                ),
                metadata=s.metadata if hasattr(s, "metadata") else {},
            )
            for s in sessions
        ]
    except Exception:
        return []


@router.get(
    "/components",
    response_model=list[ComponentHealth],
    summary="Component health checks",
)
def get_components(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> list[ComponentHealth]:
    """Run live health probes on all subsystems and return results."""
    tool_manager = getattr(request.app.state, "tool_manager", None)
    probes = collect_all_probes(tool_manager)
    return list(probes.values())
