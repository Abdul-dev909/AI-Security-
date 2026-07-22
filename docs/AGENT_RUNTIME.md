# ENTERPRISE AGENT RUNTIME & STAGED PIPELINE ARCHITECTURE
## MODULE 1 - MILESTONE 2.5 SPECIFICATION
**Document ID**: `DOC-AGENT-RUNTIME-2026`
**Applicability**: Orchestration Engine for Module 1, Module 4 (Evidence Collection), Module 5 (Forensics), Module 8 (Risk Prediction), Module 9 (Threat Hunting).

---

## 1. Executive Summary & Design Principles

The Enterprise Agent Runtime (`app/agent/`) serves as the permanent, lightweight in-house orchestration layer connecting FastAPI REST controllers, memory persistence, prompt builders, LLM inference backends, and the Enterprise Tool Execution Framework.

### Key Architectural Constraints
- **Zero Third-Party Framework Dependencies**: Completely in-house. No LangChain, LangGraph, CrewAI, or AutoGen dependencies.
- **Staged Execution Pipeline Architecture**: Requests flow through 7 isolated, modular stages. Future capabilities (RAG Ingestion, Database Connectors, Forensics Collectors) plug into this pipeline without architectural refactoring.
- **Single Tool Call Limit**: Enforces a strict maximum of 1 tool invocation per user request to eliminate recursive or infinite execution loops.
- **Full API Backward Compatibility**: Zero breaking changes to existing REST contracts (`POST /chat`, `GET /health`, attack routes, detection routes).

---

## 2. Staged Execution Pipeline Lifecycle

Every request processed by `AgentRuntime.process_request()` moves sequentially through 7 execution stages:

```
User Prompt (POST /chat)
   │
   ▼
Stage 1: Context Preparation ──► Loads history & available tool metadata
   │
   ▼
Stage 2: Memory Retrieval ─────► Queries SQLite memories via SQL LIKE
   │
   ▼
Stage 3: Capability Resolution ─► Resolves capability (Filesystem Tool, RAG, DB, None)
   │
   ▼
Stage 4: Tool Execution ────────► Invokes ToolManager safely within sandbox/
   │
   ▼
Stage 5: Prompt Building ───────► Assembles: System → History → Memory → Tool Output → Prompt
   │
   ▼
Stage 6: Model Inference ───────► Executes LLM inference via Ollama client
   │
   ▼
Stage 7: Detection Telemetry ───► Pipes context into Module 3 Detection Coordinator
   │
   ▼
Response & Stage Telemetry
```

---

## 3. Core Component Reference (`app/agent/`)

### `AgentContext` (`context.py`)
Unified state object created per request. Holds:
- `request_id`, `session_id`, `user_prompt`
- `conversation_history`, `memories`, `available_tools`
- `capability_resolution`, `tool_result`, `formatted_messages`
- `raw_ai_response`, `detection_report`
- `stage_telemetry`: List of `StageExecutionMetadata` tracking per-stage timing and execution metrics.

### `CapabilityResolver` (`decisions.py`)
Abstract capability resolution layer mapping prompt intent to capabilities (`FILESYSTEM_TOOL`, `RAG`, `DATABASE`, `LOG_SEARCH`, `NONE`).
Initial heuristics resolve file operations:
- `list_files` -> `ls`
- `read_document` -> `cat`
- `search_documents` -> `grep`
- `show_path` -> `pwd`

### `AgentExecutor` (`executor.py`)
Bridge between `CapabilityResolver` and `ToolManager`. Executes `ToolInvocationRequest` objects and formats raw tool outputs into structured markdown blocks for prompt context injection.

### `AgentRuntime` (`runtime.py`)
Main orchestrator instantiating and executing the 7-stage pipeline. Records fine-grained timing for each stage and handles LLM timeout/connection fallbacks gracefully.

---

## 4. Structured Telemetry & Audit Metadata

Every pipeline execution records `StageExecutionMetadata` objects:

```json
{
  "stage_name": "tool_execution",
  "start_time": "2026-07-22T15:56:00.123456+00:00",
  "end_time": "2026-07-22T15:56:00.125000+00:00",
  "duration_ms": 1.544,
  "status": "SUCCESS",
  "details": {
    "tool_name": "cat",
    "success": true,
    "execution_time_ms": 1.25,
    "error": null
  }
}
```

This structured telemetry feeds directly into future forensics, threat hunting, and evidence collection modules.

---

## 5. Future Capability Extension Points

Future platform modules integrate directly into specific runtime pipeline stages:

1. **Module 4 (Evidence Collection)**: Plugs into `StageExecutionMetadata` to capture structured evidence dumps.
2. **Module 5 (Digital Forensics)**: Reads stage timing and tool execution logs to build incident timelines.
3. **RAG Integration**: Plugs into `Stage 3 (CapabilityResolution)` and `Stage 4` to perform vector search lookups.
4. **Database Query Tools**: Plugs into `CapabilityResolver` as a `DATABASE` capability type.

---
*Runtime specification document compiled successfully.*
