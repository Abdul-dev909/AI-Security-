"""Health check endpoint."""

from fastapi import APIRouter, status

from app.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check whether the API is running",
    description=(
        "Use this endpoint to confirm that the FastAPI application is online.\n\n"
        "Example request:\n"
        "GET /health\n\n"
        "Example response:\n"
        '{"status": "running"}\n\n'
        "Status codes:\n"
        "200 OK"
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "The API is running normally.",
            "content": {
                "application/json": {
                    "example": {"status": "running"},
                }
            },
        }
    },
)
def health_check() -> HealthResponse:
    """Return a simple status payload so users can verify the server is up."""
    return HealthResponse(status="running")
