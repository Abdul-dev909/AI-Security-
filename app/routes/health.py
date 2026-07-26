"""Enhanced health check endpoint with detailed subsystem reporting."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Request, status

router = APIRouter()


def _probe(name: str, fn) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        details = fn() or {}
        latency_ms = round((time.perf_counter() - start) * 1000, 3)
        return {
            "name": name,
            "status": "healthy",
            "latency_ms": latency_ms,
            "details": details,
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 3)
        return {
            "name": name,
            "status": "unavailable",
            "latency_ms": latency_ms,
            "details": {"error": str(exc)},
        }


@router.get(
    "/health",
    summary="Platform health check",
    description="Returns overall status and per-subsystem health probes.",
    responses={
        status.HTTP_200_OK: {
            "description": (
                "Platform is running (individual components may be degraded)."
            )
        },
    },
)
def health_check(request: Request) -> dict[str, Any]:
    """Return overall platform status and per-subsystem component health."""
    from app.config import settings

    components: dict[str, Any] = {}

    # Ollama probe
    def _ollama():
        import httpx

        resp = httpx.get(f"{settings.OLLAMA_URL}/api/tags", timeout=2.0)
        resp.raise_for_status()
        return {"models": [m.get("name") for m in resp.json().get("models", [])]}

    components["ollama"] = _probe("ollama", _ollama)

    # SQLite probe
    def _sqlite():
        import sqlite3

        conn = sqlite3.connect(settings.DATABASE_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return {}

    components["sqlite"] = _probe("sqlite", _sqlite)

    # ChromaDB probe
    def _chromadb():
        import chromadb  # noqa: F401

        return {}

    components["chromadb"] = _probe("chromadb", _chromadb)

    # Embedding model probe
    def _embeddings():
        from sentence_transformers import SentenceTransformer  # noqa: F401

        return {"model": "all-MiniLM-L6-v2"}

    components["embedding_model"] = _probe("embedding_model", _embeddings)

    # Sandbox probe
    def _sandbox():
        from pathlib import Path

        p = Path("enterprise_sandbox")
        if not p.exists():
            raise FileNotFoundError("enterprise_sandbox not found")
        return {"file_count": len(list(p.rglob("*")))}

    components["sandbox"] = _probe("sandbox", _sandbox)

    # Tool registry probe
    def _tools():
        tool_manager = getattr(request.app.state, "tool_manager", None)
        if tool_manager is None:
            raise RuntimeError("ToolManager not initialized")
        return {"tool_count": len(tool_manager.registry.list_tools())}

    components["tool_registry"] = _probe("tool_registry", _tools)

    # Knowledge index probe
    def _knowledge():
        from app.knowledge.vectorstore import VectorStore

        count = VectorStore().count()
        return {"vector_count": count, "indexed": count > 0}

    components["knowledge_index"] = _probe("knowledge_index", _knowledge)

    # Runtime probe
    def _runtime():
        agent = getattr(request.app.state, "agent_runtime", None)
        return {"initialized": agent is not None}

    components["runtime"] = _probe("runtime", _runtime)

    # Memory probe
    def _memory():
        mm = getattr(request.app.state, "memory_manager", None)
        if mm is None:
            raise RuntimeError("MemoryManager not initialized")
        return {"sessions": mm.session_manager.session_count()}

    components["memory"] = _probe("memory", _memory)

    # Telemetry probe
    def _telemetry():
        tm = getattr(request.app.state, "telemetry_manager", None)
        if tm is None:
            raise RuntimeError("TelemetryManager not initialized")
        stats = tm.get_all_stats()
        return {"categories": list(stats.keys())}

    components["telemetry"] = _probe("telemetry", _telemetry)

    # Derive overall status
    statuses = [c["status"] for c in components.values()]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unavailable" for s in statuses):
        overall = "degraded"
    else:
        overall = "degraded"

    return {
        "status": overall,
        "components": components,
    }
