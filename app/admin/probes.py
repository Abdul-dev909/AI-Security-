"""Shared subsystem health probe utilities used across admin routes."""

from __future__ import annotations

import time
from typing import Any

from app.admin.models import ComponentHealth


def _probe(name: str, fn: Any) -> ComponentHealth:
    """Execute a probe function and return a ComponentHealth result."""
    start = time.perf_counter()
    try:
        details = fn() or {}
        latency_ms = round((time.perf_counter() - start) * 1000, 3)
        return ComponentHealth(
            name=name, status="healthy", latency_ms=latency_ms, details=details
        )
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 3)
        return ComponentHealth(
            name=name,
            status="unavailable",
            latency_ms=latency_ms,
            details={"error": str(exc)},
        )


def probe_ollama() -> ComponentHealth:
    import httpx

    from app.config import settings

    def _check() -> dict:
        resp = httpx.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3.0)
        resp.raise_for_status()
        models = [m.get("name") for m in resp.json().get("models", [])]
        return {"available_models": models}

    return _probe("ollama", _check)


def probe_sqlite() -> ComponentHealth:
    import sqlite3

    from app.config import settings

    def _check() -> dict:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return {"database_path": settings.DATABASE_PATH}

    return _probe("sqlite", _check)


def probe_chromadb() -> ComponentHealth:
    def _check() -> dict:
        try:
            import chromadb  # noqa: F401

            return {"client": "available"}
        except ImportError:
            raise RuntimeError("chromadb is not installed")

    return _probe("chromadb", _check)


def probe_embeddings() -> ComponentHealth:
    def _check() -> dict:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401

            return {"model": "sentence-transformers available"}
        except ImportError:
            raise RuntimeError("sentence-transformers is not installed")

    return _probe("embedding_model", _check)


def probe_sandbox() -> ComponentHealth:
    from pathlib import Path

    def _check() -> dict:
        sandbox = Path("enterprise_sandbox")
        if not sandbox.exists():
            raise FileNotFoundError("enterprise_sandbox directory not found")
        files = list(sandbox.rglob("*"))
        return {"file_count": len(files), "path": str(sandbox.resolve())}

    return _probe("sandbox", _check)


def probe_tool_registry(tool_manager: Any | None) -> ComponentHealth:
    def _check() -> dict:
        if tool_manager is None:
            raise RuntimeError("ToolManager not initialized")
        tools = tool_manager.registry.list_tools()
        return {"tool_count": len(tools)}

    return _probe("tool_registry", _check)


def probe_knowledge_index() -> ComponentHealth:
    def _check() -> dict:
        from app.knowledge.vectorstore import VectorStore

        vs = VectorStore()
        count = vs.count()
        return {"vector_count": count, "indexed": count > 0}

    return _probe("knowledge_index", _check)


def collect_all_probes(tool_manager: Any | None = None) -> dict[str, ComponentHealth]:
    """Run all subsystem probes and return a named map."""
    return {
        "ollama": probe_ollama(),
        "sqlite": probe_sqlite(),
        "chromadb": probe_chromadb(),
        "embedding_model": probe_embeddings(),
        "sandbox": probe_sandbox(),
        "tool_registry": probe_tool_registry(tool_manager),
        "knowledge_index": probe_knowledge_index(),
    }
