# Enterprise Memory & Performance Architecture

This document describes the design and flow of the Enterprise Memory subsystem and the accompanying runtime performance observability introduced in Module 1 Milestone 4.

## Core Concepts

The architecture ensures **strict separation of concerns** between session lifecycle tracking and persistent storage logic.

### 1. Multi-Session Isolation
Every interaction with the Agent Runtime operates within a `session_id`.
- **SessionManager (`app/memory/sessions.py`)**: Manages the ephemeral lifecycle of a session. It maintains memory-based runtime state, tracking last access times and contextual metadata. It does *not* read or write to persistent memory databases.
- **MemoryStorage (`app/memory/storage.py`)**: Manages persistent interaction history (via SQLite in `memory.db`). All queries enforce a `session_id` filter to prevent leakage of memory across distinct user contexts.

### 2. Importance Engine (`app/memory/importance.py`)
Not all conversation lines are worth remembering. The `ImportanceEngine` scores text (0.0 to 1.0) using rule-based heuristics:
- **Explicit commands**: Detects "remember", "note", "save this"
- **Critical Entities**: Detects "password", "project", "credentials"

If the score crosses a predefined threshold, the `EnterpriseMemoryManager` saves it via `MemoryStorage`.

### 3. Memory Retriever (`app/memory/retriever.py`)
The `MemoryRetriever` pulls memories belonging to a session and applies multi-factor ranking:
- **Importance Weighting**: High-score memories rank higher.
- **Recency Decay**: Exponential decay favors newer memories over old ones.
- **Keyword Relevance**: Immediate contextual relevance adds additive weight.

## Runtime Pipeline Integration

Memory is a first-class citizen in the `AgentRuntime` execution pipeline:

1. Context & History Prep
2. Session Manager Load
3. Memory Retrieval
4. Knowledge Retrieval (RAG)
5. Capability Resolution
6. Tool Execution
7. Prompt Building (with strict bounding logic)
8. **Async Model Inference & Streaming**
9. Detection & Telemetry

### Asynchronous Operations & Streaming
To support scalable low-latency LLM calls without blocking FastAPI threads, `app/ollama_client.py` uses `httpx.AsyncClient` with connection pooling.
- `POST /chat`: Preserved as a backward-compatible async endpoint.
- `POST /chat/stream`: Uses Server-Sent Events (SSE) via `process_request_stream_async` in the runtime for progressive responses.

### Telemetry Pipeline
Every request generates a unified `RuntimePerformanceEvent` capturing:
- `total_latency_ms`
- `memory_latency_ms`
- `llm_latency_ms`
- `tokens_in` & `tokens_out`

This granular metric payload guarantees observability for future integration with the Threat Hunting and Risk Prediction modules.
