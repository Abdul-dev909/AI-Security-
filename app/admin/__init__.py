"""Admin package — aggregates all administrative sub-routers under /admin."""

from fastapi import APIRouter

from app.admin import debug, diagnostics, knowledge, memory, runtime, telemetry, tools

router = APIRouter()

router.include_router(runtime.router)
router.include_router(memory.router)
router.include_router(knowledge.router)
router.include_router(tools.router)
router.include_router(telemetry.router)
router.include_router(diagnostics.router)
router.include_router(debug.router)

__all__ = ["router"]
