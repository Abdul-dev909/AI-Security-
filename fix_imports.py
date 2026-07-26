from pathlib import Path

for filename in ["app/admin/diagnostics.py", "app/admin/runtime.py", "app/admin/tools.py"]:
    p = Path(filename)
    c = p.read_text()
    if c.startswith("import contextlib\n"):
        c = c.replace("import contextlib\n", "", 1)
        c = c.replace("from __future__ import annotations\n", "from __future__ import annotations\nimport contextlib\n")
        p.write_text(c)
