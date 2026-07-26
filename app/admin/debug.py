"""Per-request debug endpoint — only available when DEBUG_MODE=true."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.admin.dependencies import get_admin_dependency
from app.admin.models import DebugRequestSnapshot
from app.config import settings

router = APIRouter(prefix="/debug", tags=["Admin — Debug"])


@router.get(
    "/request/{request_id}",
    response_model=DebugRequestSnapshot,
    summary="Inspect full pipeline state for a specific request",
)
def get_debug_snapshot(
    request_id: str,
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> DebugRequestSnapshot:
    """Return the full captured agent context for a past request.

    Only available when ``DEBUG_MODE=true``. Returns 403 otherwise.
    """
    if not settings.DEBUG_MODE:
        raise HTTPException(
            status_code=403,
            detail="Debug mode is disabled. "
            "Set DEBUG_MODE=true to enable request inspection.",
        )

    debug_store: dict = getattr(request.app.state, "debug_store", {})
    snapshot = debug_store.get(request_id)
    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"No debug snapshot found for request_id={request_id!r}",
        )

    return snapshot


@router.get("/requests", summary="List captured debug request IDs")
def list_debug_requests(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> list[str]:
    """List all request IDs in the debug store.

    Returns 403 when DEBUG_MODE is disabled.
    """
    if not settings.DEBUG_MODE:
        raise HTTPException(
            status_code=403,
            detail="Debug mode is disabled.",
        )
    debug_store: dict = getattr(request.app.state, "debug_store", {})
    return list(debug_store.keys())
