"""Attack Engine API endpoints."""

import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status

from app.attack_engine.engine import AttackEngine
from app.attack_engine.models import Attack
from app.attack_engine.registry import AttackRegistry
from app.schemas import RunAllAttacksResponse, RunAttackRequest

router = APIRouter()
logger = logging.getLogger(__name__)


def get_attack_registry(request: Request) -> AttackRegistry:
    """Return the shared attack registry stored on the FastAPI app."""
    return request.app.state.attack_registry


def get_attack_engine(request: Request) -> AttackEngine:
    """Return the shared attack engine stored on the FastAPI app."""
    return request.app.state.attack_engine


@router.get(
    "/api/attacks",
    response_model=list[Attack],
    summary="List all registered attacks",
    description="Returns all adversarial attacks currently available in the system registry.",
)
def list_attacks(
    registry: AttackRegistry = Depends(get_attack_registry),
) -> list[Attack]:
    """Return a list of all registered attack definitions."""
    return registry.list()


@router.post(
    "/api/attacks/run",
    summary="Run a single attack by ID",
    description="Locates the specified attack in the registry and executes it via the AttackEngine.",
)
def run_attack(
    request: RunAttackRequest = Body(...),
    registry: AttackRegistry = Depends(get_attack_registry),
    engine: AttackEngine = Depends(get_attack_engine),
):
    """Execute a single attack."""
    attack = registry.get(request.attack_id)
    if not attack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attack with ID '{request.attack_id}' not found.",
        )

    if not attack.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attack '{attack.name}' is currently disabled.",
        )

    try:
        # engine.executor.execute expects a single Attack object
        result = engine.executor.execute(attack)
        return result
    except Exception as e:
        logger.error("Failed to execute attack '%s': %s", attack.id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during attack execution.",
        ) from e


@router.post(
    "/api/attacks/run-all",
    response_model=RunAllAttacksResponse,
    summary="Run all enabled attacks",
    description=(
        "Executes every enabled attack in the registry and returns aggregated results."
    ),
)
def run_all_attacks(
    registry: AttackRegistry = Depends(get_attack_registry),
    engine: AttackEngine = Depends(get_attack_engine),
) -> RunAllAttacksResponse:
    """Execute all enabled attacks sequentially."""
    try:
        results = engine.run(registry)

        completed = sum(1 for r in results if r.execution_success)
        failed = len(results) - completed

        return RunAllAttacksResponse(
            total_attacks=len(results),
            completed=completed,
            failed=failed,
            results=results,
        )
    except Exception as e:
        logger.error("Failed to execute batch attacks: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during batch attack execution.",
        ) from e
