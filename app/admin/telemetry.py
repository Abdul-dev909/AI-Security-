"""Telemetry inspection endpoints — read-only views of the telemetry buffer."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.admin.dependencies import get_admin_dependency

router = APIRouter(prefix="/telemetry", tags=["Admin — Telemetry"])

_MAX_LIMIT = 500


def _clamp(limit: int) -> int:
    return min(max(1, limit), _MAX_LIMIT)


def _get_tm(request: Request):
    return getattr(request.app.state, "telemetry_manager", None)


@router.get("/runtime", summary="Recent runtime telemetry events")
def get_runtime_telemetry(
    request: Request, limit: int = 50, _: None = Depends(get_admin_dependency)
) -> list[dict]:
    tm = _get_tm(request)
    if not tm:
        return []
    return [e.model_dump(mode="json") for e in tm.get_runtime_events(_clamp(limit))]


@router.get("/memory", summary="Recent memory telemetry events")
def get_memory_telemetry(
    request: Request, limit: int = 50, _: None = Depends(get_admin_dependency)
) -> list[dict]:
    tm = _get_tm(request)
    if not tm:
        return []
    return [e.model_dump(mode="json") for e in tm.get_memory_events(_clamp(limit))]


@router.get("/knowledge", summary="Recent knowledge retrieval telemetry events")
def get_knowledge_telemetry(
    request: Request, limit: int = 50, _: None = Depends(get_admin_dependency)
) -> list[dict]:
    tm = _get_tm(request)
    if not tm:
        return []
    return [e.model_dump(mode="json") for e in tm.get_knowledge_events(_clamp(limit))]


@router.get("/tools", summary="Recent tool execution telemetry events")
def get_tools_telemetry(
    request: Request, limit: int = 50, _: None = Depends(get_admin_dependency)
) -> list[dict]:
    tm = _get_tm(request)
    if not tm:
        return []
    return [e.model_dump(mode="json") for e in tm.get_tool_events(_clamp(limit))]


@router.get("/detection", summary="Recent detection pipeline telemetry events")
def get_detection_telemetry(
    request: Request, limit: int = 50, _: None = Depends(get_admin_dependency)
) -> list[dict]:
    tm = _get_tm(request)
    if not tm:
        return []
    return [e.model_dump(mode="json") for e in tm.get_detection_events(_clamp(limit))]


@router.get("/stats", summary="Telemetry buffer fill statistics")
def get_telemetry_stats(
    request: Request, _: None = Depends(get_admin_dependency)
) -> dict:
    tm = _get_tm(request)
    if not tm:
        return {}
    return tm.get_all_stats()
