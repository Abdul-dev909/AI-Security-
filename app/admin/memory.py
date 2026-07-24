"""Memory administration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Request

from app.admin.dependencies import get_admin_dependency
from app.admin.models import MemoryAdminRecord, MemoryMetrics

router = APIRouter(prefix="/memory", tags=["Admin — Memory"])


def _get_storage(request: Request):
    mm = getattr(request.app.state, "memory_manager", None)
    if mm is None:
        raise HTTPException(status_code=503, detail="Memory manager not available")
    return mm.storage


@router.get("", response_model=list[MemoryAdminRecord], summary="List all memories")
def list_all_memories(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    _: None = Depends(get_admin_dependency),
) -> list[MemoryAdminRecord]:
    storage = _get_storage(request)
    records = storage.get_all_memories(limit=limit, offset=offset)
    return [
        MemoryAdminRecord(
            memory_id=r.memory_id,
            session_id=r.session_id,
            content=r.content,
            importance_score=r.importance_score,
            created_at=r.created_at.isoformat(),
            metadata=r.metadata,
        )
        for r in records
    ]


@router.get(
    "/metrics", response_model=MemoryMetrics, summary="Memory subsystem metrics"
)
def get_memory_metrics(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> MemoryMetrics:
    storage = _get_storage(request)
    total = storage.count_memories()
    by_session = storage.count_by_session()
    all_records = storage.get_all_memories(limit=500)
    avg_score = 0.0
    if all_records:
        avg_score = round(
            sum(r.importance_score for r in all_records) / len(all_records), 4
        )
    return MemoryMetrics(
        total_memories=total,
        total_sessions=len(by_session),
        avg_importance_score=avg_score,
        memories_by_session=by_session,
    )


@router.get(
    "/{session_id}",
    response_model=list[MemoryAdminRecord],
    summary="Memories for a session",
)
def get_memories_by_session(
    session_id: str,
    request: Request,
    limit: int = 100,
    _: None = Depends(get_admin_dependency),
) -> list[MemoryAdminRecord]:
    storage = _get_storage(request)
    records = storage.get_memories_by_session(session_id=session_id, limit=limit)
    return [
        MemoryAdminRecord(
            memory_id=r.memory_id,
            session_id=r.session_id,
            content=r.content,
            importance_score=r.importance_score,
            created_at=r.created_at.isoformat(),
            metadata=r.metadata,
        )
        for r in records
    ]


@router.post(
    "/search", response_model=list[MemoryAdminRecord], summary="Search memories"
)
def search_memories(
    request: Request,
    query: str = Body(..., embed=True),
    session_id: str | None = Body(default=None, embed=True),
    limit: int = Body(default=10, embed=True),
    _: None = Depends(get_admin_dependency),
) -> list[MemoryAdminRecord]:
    mm = getattr(request.app.state, "memory_manager", None)
    if mm is None:
        return []
    if session_id:
        ctx = mm.retriever.retrieve(session_id=session_id, query=query, limit=limit)
        records = ctx.retrieved_memories
    else:
        # Cross-session: fetch all then keyword filter
        all_recs = mm.storage.get_all_memories(limit=500)
        q = query.lower()
        records = [r for r in all_recs if q in r.content.lower()][:limit]
    return [
        MemoryAdminRecord(
            memory_id=r.memory_id,
            session_id=r.session_id,
            content=r.content,
            importance_score=r.importance_score,
            created_at=r.created_at.isoformat(),
            metadata=r.metadata,
        )
        for r in records
    ]


@router.delete("/{memory_id}", summary="Delete a single memory record")
def delete_memory(
    memory_id: str,
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> dict:
    storage = _get_storage(request)
    deleted = storage.delete_memory_by_id(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Memory {memory_id!r} not found")
    return {"deleted": memory_id}


@router.delete("/session/{session_id}", summary="Purge all memories for a session")
def delete_session_memories(
    session_id: str,
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> dict:
    storage = _get_storage(request)
    storage.delete_memories_for_session(session_id)
    return {"purged_session": session_id}


@router.delete("/all/purge", summary="Purge ALL memories (admin-only)")
def delete_all_memories(
    request: Request,
    _: None = Depends(get_admin_dependency),
) -> dict:
    storage = _get_storage(request)
    count = storage.delete_all_memories()
    return {"deleted_count": count}
