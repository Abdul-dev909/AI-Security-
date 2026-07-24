"""Admin route dependency placeholders.

Provides a central hook for future authentication enforcement.
All admin routes declare ``Depends(get_admin_dependency)``; currently
unenforced but wired so future PRs can swap in a real auth check
without touching every route handler.
"""

from __future__ import annotations

from fastapi import Request


def get_admin_dependency(request: Request) -> None:
    """Placeholder admin auth dependency. Currently unenforced.

    Future implementation: validate API key / JWT from request headers.
    Raise ``fastapi.HTTPException(401)`` on failure.
    """
