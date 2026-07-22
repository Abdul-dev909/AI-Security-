# ENTERPRISE TOOL EXECUTION FRAMEWORK
## MODULE 1 - MILESTONE 2 SPECIFICATION
**Document ID**: `DOC-TOOL-FRAMEWORK-2026`
**Applicability**: Enterprise Tool Infrastructure for Module 1, Module 4 (Evidence Collection), Module 5 (Forensics), Module 9 (Threat Hunting).

---

## 1. Overview & Architecture

The Enterprise Tool Execution Framework provides a secure, controlled, non-shell interface for executing enterprise tools against the `sandbox/` directory.

### Key Architectural Components (`app/tools/`)

- `BaseTool`: Abstract Base Class defining the contract (`name`, `description`, `parameters_schema`, `output_schema`, `execute()`).
- `ToolRegistry`: Dynamic registry managing tool discovery and registration. Automatically loads default tools (`pwd`, `ls`, `cat`, `grep`).
- `ToolManager`: Central orchestrator responsible for executing tools, timing executions, trapping runtime/security exceptions, returning structured `ToolExecutionResult` objects, and producing `ToolAuditEvent` security logs.
- `security.py`: `SandboxValidator` module enforcing absolute isolation within `sandbox/`.
- `exceptions.py`: Custom error hierarchy (`ToolSecurityError`, `ToolNotFoundError`, `ToolExecutionError`).

```
+-------------------------------------------------------------------------------+
|                               ToolManager                                     |
+-------------------------------------------------------------------------------+
       |                                  |                                |
       v                                  v                                v
+------------------+             +------------------+             +------------------+
|   ToolRegistry   |             | SandboxValidator |             | ToolAuditEvent   |
| (pwd,ls,cat,grep)|             | (Path Isolation) |             |  (Security Log)  |
+------------------+             +------------------+             +------------------+
       |                                  |
       +-----------------+----------------+
                         |
                         v
                +-----------------+
                |    BaseTool     |
                +-----------------+
                | - PwdTool       |
                | - LsTool        |
                | - CatTool       |
                | - GrepTool      |
                +-----------------+
```

---

## 2. Security Model & Sandbox Enforcement

1. **Sandbox Root Isolation**:
   - `sandbox/` is enforced as the strict root directory.
   - User inputs resolved via `Path(user_path).resolve()`.
   - Paths must satisfy `resolved_path.relative_to(sandbox_root)`.

2. **Prohibited Operations**:
   - Directory Traversal (`../`, `/..`) -> Raises `ToolSecurityError`.
   - Absolute Host Paths (`/etc/passwd`, `/var/log`) -> Raises `ToolSecurityError`.
   - Symbolic Links pointing outside `sandbox/` -> Raises `ToolSecurityError`.
   - Binary Files (`\x00` null byte detection in `cat`) -> Raises `ToolSecurityError`.
   - Direct Subprocess / Shell Calls -> **Zero raw shell or subprocess execution**.

---

## 3. Initial Built-in Tool Suite

### 1. `pwd` (`PwdTool`)
- **Purpose**: Returns current working directory relative to sandbox root (`sandbox/`).
- **Output Schema**: `{"cwd": "sandbox/"}`

### 2. `ls` (`LsTool`)
- **Purpose**: Lists files and directory contents within a specified sandbox path.
- **Parameters**: `path: str` (default: `"."`)
- **Output Schema**: `{"path": "engineering", "entries": [{"name": "architecture_spec.md", "is_dir": false, "size_bytes": 1024}]}`

### 3. `cat` (`CatTool`)
- **Purpose**: Reads text file content safely within `sandbox/`. Rejects binary files and invalid UTF-8.
- **Parameters**: `path: str` (required)
- **Output Schema**: `{"path": "engineering/architecture_spec.md", "content": "...", "size_bytes": 1024}`

### 4. `grep` (`GrepTool`)
- **Purpose**: Performs case-insensitive or case-sensitive keyword searches across sandbox text files.
- **Parameters**: `query: str` (required), `path: str` (default: `"."`), `case_sensitive: bool` (default: `false`)
- **Output Schema**: `{"query": "Project Aegis", "total_matches": 1, "matches": [{"file": "engineering/architecture_spec.md", "line_number": 4, "line_content": "..."}]}`

---

## 4. Structured Results & Audit Events

### `ToolExecutionResult` Object
Every invocation returns a structured model:
```json
{
  "success": true,
  "tool": "cat",
  "execution_time_ms": 1.25,
  "result": {
    "path": "engineering/architecture_spec.md",
    "content": "...",
    "size_bytes": 1024
  },
  "error": null
}
```

### `ToolAuditEvent` Security Model
Security audit telemetry produced for every tool execution:
```json
{
  "event_id": "evt-8f9a2b4c6e8d",
  "timestamp": "2026-07-22T15:37:00Z",
  "tool_name": "cat",
  "arguments": {"path": "../../etc/passwd"},
  "duration_ms": 0.45,
  "status": "SECURITY_VIOLATION",
  "error_message": "Security Violation: Directory traversal detected for path '../../etc/passwd'.",
  "accessed_paths": ["../../etc/passwd"]
}
```

---

## 5. Adding Future Enterprise Tools

Future modules can easily extend the framework by subclassing `BaseTool`:

```python
from app.tools.base import BaseTool

class DatabaseQueryTool(BaseTool):
    @property
    def name(self) -> str:
        return "db_query"

    @property
    def description(self) -> str:
        return "Executes read-only SQL queries against the enterprise database."

    def execute(self, **kwargs):
        # Implementation...
        pass

# Registration
registry.register(DatabaseQueryTool())
```

---
*Framework specification compiled successfully.*
