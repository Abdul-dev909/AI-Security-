import re
from pathlib import Path

# app/admin/debug.py
p = Path("app/admin/debug.py")
c = p.read_text()
c = c.replace('detail="Debug mode is disabled. Set DEBUG_MODE=true to enable request inspection.",', 
              'detail="Debug mode is disabled. "\n            "Set DEBUG_MODE=true to enable request inspection.",')
p.write_text(c)

# app/admin/diagnostics.py
p = Path("app/admin/diagnostics.py")
c = p.read_text()
if "contextlib" not in c:
    c = "import contextlib\n" + c
c = re.sub(r'try:\n\s+active_sessions = memory_manager\.session_manager\.session_count\(\)\n\s+except Exception:\n\s+pass', 
           'with contextlib.suppress(Exception):\n            active_sessions = memory_manager.session_manager.session_count()', c)
c = c.replace('tool_events = telemetry_manager.get_tool_events(limit=500)', 'telemetry_manager.get_tool_events(limit=500)')
p.write_text(c)

# app/admin/knowledge.py
p = Path("app/admin/knowledge.py")
c = p.read_text()
c = c.replace('"""Return cached chunks from the indexer\'s loader + chunker pipeline (no embeddings)."""',
              '"""Return cached chunks from the indexer\'s loader + chunker pipeline \n    (no embeddings).\n    """')
c = c.replace('"""Trigger KnowledgeIndexer.check_and_index(). Returns immediately; indexing is synchronous."""',
              '"""Trigger KnowledgeIndexer.check_and_index().\n\n    Returns immediately; indexing is synchronous.\n    """')
p.write_text(c)

# app/admin/probes.py
p = Path("app/admin/probes.py")
c = p.read_text()
c = c.replace('raise RuntimeError("chromadb is not installed")', 'raise RuntimeError("chromadb is not installed") from None')
c = c.replace('raise RuntimeError("sentence-transformers is not installed")', 'raise RuntimeError("sentence-transformers is not installed") from None')
p.write_text(c)

# app/admin/runtime.py
p = Path("app/admin/runtime.py")
c = p.read_text()
if "contextlib" not in c:
    c = "import contextlib\n" + c
c = re.sub(r'try:\n\s+active_sessions = len\(memory_manager\.session_manager\.list_sessions\(\)\)\n\s+except Exception:\n\s+pass', 
           'with contextlib.suppress(Exception):\n            active_sessions = len(memory_manager.session_manager.list_sessions())', c)
p.write_text(c)

# app/admin/tools.py
p = Path("app/admin/tools.py")
c = p.read_text()
if "contextlib" not in c:
    c = "import contextlib\n" + c
c = re.sub(r'try:\n\s+registered = tool_manager\.registry\.list_tools\(\)\n\s+except Exception:\n\s+pass', 
           'with contextlib.suppress(Exception):\n            registered = tool_manager.registry.list_tools()', c)
p.write_text(c)

# app/agent/executor.py
p = Path("app/agent/executor.py")
c = p.read_text()
c = c.replace('"""Executes capability tool requests via ToolManager and formats output for prompt context."""',
              '"""Executes capability tool requests via ToolManager and formats output\n    for prompt context.\n    """')
c = c.replace('"""Format raw result dictionary into structured markdown for context injection."""',
              '"""Format raw result dictionary into structured markdown\n        for context injection.\n        """')
c = c.replace('return f"--- START FILE CONTEXT: {path} ---\\n{content}\\n--- END FILE CONTEXT ---"',
              'return f"--- START FILE CONTEXT: {path} ---\\n{content}\\n"\n            "--- END FILE CONTEXT ---"')
p.write_text(c)

# app/agent/planner.py
p = Path("app/agent/planner.py")
c = p.read_text()
c = c.replace('"""Planner layer for evaluating complex multi-step capability plans in future milestones."""',
              '"""Planner layer for evaluating complex multi-step capability plans\n    in future milestones.\n    """')
p.write_text(c)

# app/attack_engine/registry.py
p = Path("app/attack_engine/registry.py")
c = p.read_text()
c = c.replace('Contains no execution logic. Uses a dictionary internally to manage attacks by their IDs.',
              'Contains no execution logic. Uses a dictionary internally to manage\n    attacks by their IDs.')
p.write_text(c)

# app/config.py
p = Path("app/config.py")
c = p.read_text()
c = c.replace('"You are Nexus Assistant, the internal AI assistant for Nexus Defense Solutions Inc. (NDS), "',
              '"You are Nexus Assistant, the internal AI assistant for Nexus "\n        "Defense Solutions Inc. (NDS), "')
p.write_text(c)

