"""Tools administration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.admin.dependencies import get_admin_dependency
from app.admin.models import ToolMetrics

router = APIRouter(prefix="/tools", tags=["Admin — Tools"])


@router.get("", response_model=ToolMetrics, summary="Tool registry metrics")
def get_tool_metrics(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> ToolMetrics:
    """Return registered tools and execution statistics from telemetry."""
    tool_manager = getattr(request.app.state, "tool_manager", None)
    registered: list[dict] = []
    if tool_manager:
        try:
            registered = tool_manager.registry.list_tools()
        except Exception:
            pass

    telemetry_manager = getattr(request.app.state, "telemetry_manager", None)
    total_executions = 0
    executions_by_tool: dict[str, int] = {}
    successes = 0

    if telemetry_manager:
        events = telemetry_manager.get_tool_events(limit=500)
        total_executions = len(events)
        for ev in events:
            executions_by_tool[ev.tool_name] = (
                executions_by_tool.get(ev.tool_name, 0) + 1
            )
            if ev.success:
                successes += 1

    success_rate = round(successes / max(total_executions, 1), 4)

    return ToolMetrics(
        registered_tools=registered,
        total_registered=len(registered),
        total_executions=total_executions,
        executions_by_tool=executions_by_tool,
        success_rate=success_rate,
    )


@router.get("/registry", summary="Raw tool registry listing")
def get_tool_registry(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> list[dict]:
    """List all tools registered in the tool registry."""
    tool_manager = getattr(request.app.state, "tool_manager", None)
    if not tool_manager:
        return []
    try:
        return tool_manager.registry.list_tools()
    except Exception:
        return []


@router.get("/executions", summary="Recent tool execution events")
def get_tool_executions(
    request: Request,
    limit: int = 50,
    _: None = Depends(get_admin_dependency),
) -> list[dict]:
    """Return recent tool telemetry events from the buffer."""
    telemetry_manager = getattr(request.app.state, "telemetry_manager", None)
    if not telemetry_manager:
        return []
    events = telemetry_manager.get_tool_events(limit=limit)
    return [e.model_dump(mode="json") for e in events]
