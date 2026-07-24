# Module 1 Administration Guide

This guide details the administrative and observability APIs available in Module 1. These endpoints provide introspection into the Agent Runtime, Memory Management, Knowledge Retrieval (RAG), Tool Execution, and the Detection Engine.

All admin endpoints are exposed under `/admin/*`.

---

## 1. Runtime Observability (`/admin/runtime`)

Provides an overview of the Agent Runtime and core backend platform health.

- `GET /admin/runtime/status`
  Returns uptime, active session counts, rolling latency averages for all runtime stages, and detailed probe results for dependent components (SQLite, ChromaDB, Ollama, Sandbox, etc.).

- `GET /admin/runtime/metrics`
  Aggregates performance statistics across the telemetry buffer for active sessions. Includes p95 latencies for memory retrieval, tool execution, and LLM inference.

- `GET /admin/runtime/sessions`
  Lists all active tracked sessions, their created timestamps, and last-active metrics.

- `GET /admin/runtime/components`
  Provides raw health probes directly against external system dependencies (e.g., verifying `sentence-transformers` is loaded, SQLite DB is accessible).

- `GET /admin/runtime/config`
  Read-only view of `app.config.settings`. Sensitve credentials or API keys (if any) are masked with `***`.

---

## 2. Telemetry Inspection (`/admin/telemetry`)

Module 1 uses an in-memory, thread-safe ring-buffer (`TelemetryManager`) designed to capture the last N (default: 500) events per subsystem.

- `GET /admin/telemetry/stats`
  Returns queue depth and throughput statistics for all tracked telemetry categories.

- `GET /admin/telemetry/runtime`
- `GET /admin/telemetry/memory`
- `GET /admin/telemetry/knowledge`
- `GET /admin/telemetry/tools`
- `GET /admin/telemetry/detection`
  Each of these endpoints returns an array of recent telemetry events in JSON format, capped at the requested `?limit=` (max 500).

---

## 3. Diagnostics & Debugging (`/admin/diagnostics`, `/admin/debug`)

- `GET /admin/diagnostics`
  A unified meta-endpoint that combines component health, telemetry buffer stats, uptime, and derived runtime metrics into a single JSON payload. Ideal for dashboard polling.

### Debug Mode (Per-Request Inspection)

When `DEBUG_MODE=true` is set in the configuration:

- `GET /admin/debug/requests`
  Lists the `request_id` values for all recently captured agent invocations.

- `GET /admin/debug/request/{request_id}`
  Returns the exact context that was captured for the specific request. This includes the generated LLM prompt array, retrieved memory payloads, chunks fetched from the vector DB, capabilities selected, and the raw LLM response.
  *(Note: This endpoint returns a 403 Forbidden if `DEBUG_MODE` is disabled).*

---

## 4. Memory Administration (`/admin/memory`)

Direct access to the Enterprise Session Memory SQLite store.

- `GET /admin/memory` (Paginated) Lists all stored memory fragments across all sessions.
- `GET /admin/memory/metrics` Aggregated count of stored memories and total active sessions.
- `GET /admin/memory/{session_id}` Returns memories specific to a user's session.
- `POST /admin/memory/search` Perform semantic or keyword searches directly against the memory store.
- `DELETE /admin/memory/session/{session_id}` Manually purge all memories associated with a session.
- `DELETE /admin/memory/all/purge` (DANGER) Wipes the entire memory store.

---

## 5. Knowledge Management (`/admin/knowledge`)

Manage the RAG subsystem and ChromaDB vector index.

- `GET /admin/knowledge/status` General index freshness and availability status.
- `GET /admin/knowledge/statistics` Breakdown of indexed documents by department, classification type, and chunk averages.
- `GET /admin/knowledge/documents` List all detected documents from the enterprise sandbox environment.
- `GET /admin/knowledge/chunks` Paginated view of the actual text chunks stored in the vector database.
- `POST /admin/knowledge/reindex` Triggers a fast incremental scan of the sandbox, adding new/modified files.
- `POST /admin/knowledge/reload` Forces a complete rebuild of the vector index.

---

## 6. Tool Registry (`/admin/tools`)

- `GET /admin/tools` High-level tool metrics, execution counts, and success rates.
- `GET /admin/tools/registry` Lists all currently registered tools and their provided descriptions.
- `GET /admin/tools/executions` Recent execution telemetry (inputs, outputs, latency, and success status) for the last N tool runs.
