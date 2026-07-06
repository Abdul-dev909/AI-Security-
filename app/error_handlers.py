"""FastAPI error handlers for the AI Agent application."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import ValidationErrorResponse

logger = logging.getLogger(__name__)


def _format_validation_error(error: dict[str, object]) -> str:
    """Convert a Pydantic validation error into a readable string."""

    location = ".".join(str(part) for part in error.get("loc", []))
    message = str(error.get("msg", "Invalid value."))
    if location:
        return f"{location}: {message}"
    return message


def register_error_handlers(app: FastAPI) -> None:
    """Attach user-friendly handlers for common FastAPI errors."""

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return a clean response when request data fails validation."""

        validation_errors = [_format_validation_error(error) for error in exc.errors()]
        logger.warning(
            "Validation error for %s %s: %s",
            request.method,
            request.url.path,
            validation_errors,
        )
        response_body = ValidationErrorResponse(
            detail="Invalid request data.",
            errors=validation_errors,
        )
        return JSONResponse(status_code=422, content=response_body.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Return FastAPI HTTP errors while logging them with the right level."""

        log_level = logging.ERROR if exc.status_code >= 500 else logging.WARNING
        logger.log(
            log_level,
            "HTTP error for %s %s: %s",
            request.method,
            request.url.path,
            exc.detail,
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch unexpected failures and return a safe error message."""

        logger.exception(
            "Unexpected error for %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )