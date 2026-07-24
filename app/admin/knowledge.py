"""Knowledge administration endpoints."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, status

from app.admin.dependencies import get_admin_dependency
from app.admin.models import (
    KnowledgeChunkSummary,
    KnowledgeDocumentSummary,
    KnowledgeMetrics,
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["Admin — Knowledge"])

_STATE_FILE = (
    Path(getattr(settings, "VECTOR_DB_DIR", "app/data/vector_db")) / "index_state.json"
)


def _read_index_state() -> dict:
    if _STATE_FILE.exists():
        try:
            return json.loads(_STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def _get_vector_count() -> int:
    try:
        from app.knowledge.vectorstore import VectorStore

        return VectorStore().count()
    except Exception:
        return 0


def _get_document_chunks() -> tuple[list[Any], list[Any]]:
    """Return cached chunks from the indexer's loader + chunker pipeline (no embeddings)."""
    try:
        from app.knowledge.chunker import DocumentChunker
        from app.knowledge.loader import DocumentLoader

        docs = DocumentLoader().load_documents()
        chunks = DocumentChunker().chunk_documents(docs)
        return chunks, docs
    except Exception:
        return [], []


@router.get(
    "/status", response_model=KnowledgeMetrics, summary="Knowledge subsystem status"
)
def get_knowledge_status(
    _admin: None = Depends(get_admin_dependency),
) -> KnowledgeMetrics:
    state = _read_index_state()
    vector_count = _get_vector_count()
    chunks, docs = _get_document_chunks()

    db_status: Literal["healthy", "degraded", "unavailable"] = "unavailable"
    try:
        import chromadb  # noqa: F401

        db_status = "healthy" if vector_count > 0 else "degraded"
    except ImportError:
        pass

    return KnowledgeMetrics(
        total_documents=len(docs),
        total_chunks=len(chunks),
        vector_count=vector_count,
        indexed_at=state.get("indexed_at"),
        embedding_model="all-MiniLM-L6-v2",
        index_version=(
            state.get("sandbox_hash", "unknown")[:8]
            if state.get("sandbox_hash")
            else None
        ),
        vector_db_status=db_status,
        index_available=vector_count > 0,
    )


@router.get("/statistics", summary="Detailed knowledge statistics")
def get_knowledge_statistics(
    _admin: None = Depends(get_admin_dependency),
) -> dict:
    chunks, docs = _get_document_chunks()
    state = _read_index_state()
    vector_count = _get_vector_count()

    dept_map: dict[str, int] = {}
    class_map: dict[str, int] = {}
    for chunk in chunks:
        dept = chunk.metadata.department
        cls = chunk.metadata.classification
        dept_map[dept] = dept_map.get(dept, 0) + 1
        class_map[cls] = class_map.get(cls, 0) + 1

    return {
        "total_documents": len(docs),
        "total_chunks": len(chunks),
        "vector_count": vector_count,
        "avg_chunks_per_document": round(len(chunks) / max(len(docs), 1), 2),
        "chunks_by_department": dept_map,
        "chunks_by_classification": class_map,
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_db": "chromadb",
        "index_hash": state.get("sandbox_hash", "unknown"),
    }


@router.get(
    "/documents",
    response_model=list[KnowledgeDocumentSummary],
    summary="Indexed document list",
)
def get_documents(
    _admin: None = Depends(get_admin_dependency),
) -> list[KnowledgeDocumentSummary]:
    _, docs = _get_document_chunks()
    return [
        KnowledgeDocumentSummary(
            document_id=d.document_id,
            source_path=d.metadata.source_path,
            department=d.metadata.department,
            classification=d.metadata.classification,
            asset_type=d.metadata.asset_type,
            contains_honeytoken=d.metadata.contains_honeytoken,
            contains_prompt_injection=d.metadata.contains_prompt_injection,
        )
        for d in docs
    ]


@router.get(
    "/chunks",
    response_model=list[KnowledgeChunkSummary],
    summary="Paginated chunk listing",
)
def get_chunks(
    limit: int = 50,
    offset: int = 0,
    _admin: None = Depends(get_admin_dependency),
) -> list[KnowledgeChunkSummary]:
    chunks, _ = _get_document_chunks()
    page = chunks[offset : offset + limit]
    return [
        KnowledgeChunkSummary(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            source_path=c.metadata.source_path,
            text_preview=c.text[:120],
            classification=c.metadata.classification,
        )
        for c in page
    ]


@router.get("/embedding-model", summary="Active embedding model info")
def get_embedding_model(
    _admin: None = Depends(get_admin_dependency),
) -> dict:
    available = False
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401

        available = True
    except ImportError:
        pass
    return {
        "model_name": "all-MiniLM-L6-v2",
        "library": "sentence-transformers",
        "available": available,
        "dimension": 384,
    }


@router.get("/index-status", summary="Index version and freshness")
def get_index_status(
    _admin: None = Depends(get_admin_dependency),
) -> dict:
    state = _read_index_state()
    vector_count = _get_vector_count()
    return {
        "indexed": vector_count > 0,
        "vector_count": vector_count,
        "index_hash": state.get("sandbox_hash", "unknown"),
        "indexed_at": state.get("indexed_at"),
        "state_file": str(_STATE_FILE),
    }


@router.post(
    "/reindex",
    summary="Trigger incremental re-indexing",
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_reindex(
    _admin: None = Depends(get_admin_dependency),
) -> dict:
    """Trigger KnowledgeIndexer.check_and_index(). Returns immediately; indexing is synchronous."""
    try:
        from app.knowledge.indexer import KnowledgeIndexer

        indexer = KnowledgeIndexer()
        indexer.check_and_index()
        return {"status": "completed", "message": "Incremental reindex finished."}
    except Exception as exc:
        logger.warning("Reindex failed: %s", exc)
        return {"status": "failed", "message": str(exc)}


@router.post(
    "/reload",
    summary="Force full re-index (clears state)",
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_full_reload(
    _admin: None = Depends(get_admin_dependency),
) -> dict:
    """Delete the index state file and trigger a fresh full reindex."""
    try:
        if _STATE_FILE.exists():
            _STATE_FILE.unlink()
        from app.knowledge.indexer import KnowledgeIndexer

        indexer = KnowledgeIndexer()
        indexer.check_and_index(force=True)
        return {"status": "completed", "message": "Full reload finished."}
    except Exception as exc:
        logger.warning("Full reload failed: %s", exc)
        return {"status": "failed", "message": str(exc)}
