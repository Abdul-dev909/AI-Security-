"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request, Response

from app.config import settings
from app.conversation import ConversationManager
from app.error_handlers import register_error_handlers
from app.logging_utils import setup_logging
from app.memory_manager import MemoryManager
from app.prompts import PromptBuilder
from app.routes import router
from app.utils import execution_timer

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
	"""Create shared services before the app starts serving requests."""

	memory_manager = MemoryManager()
	conversation_manager = ConversationManager(
		memory_manager=memory_manager,
		max_history=settings.MAX_HISTORY,
	)
	prompt_builder = PromptBuilder(
		system_prompt=settings.SYSTEM_PROMPT,
		conversation_manager=conversation_manager,
	)

	app.state.memory_manager = memory_manager
	app.state.conversation_manager = conversation_manager
	app.state.prompt_builder = prompt_builder
	logger.info("Application startup complete.")
	yield
	logger.info("Application shutdown complete.")


app = FastAPI(
	title=settings.API_TITLE,
	version=settings.API_VERSION,
	description=settings.API_DESCRIPTION,
	lifespan=lifespan,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Response:
	"""Log incoming requests and how long they take to complete."""

	logger.info("Incoming request: %s %s", request.method, request.url.path)
	with execution_timer() as elapsed_seconds:
		response = await call_next(request)

	duration = elapsed_seconds()
	if response.status_code >= 500:
		logger.error(
			"Request failed: %s %s -> %s in %.3fs",
			request.method,
			request.url.path,
			response.status_code,
			duration,
		)
	elif response.status_code >= 400:
		logger.warning(
			"Request returned a client error: %s %s -> %s in %.3fs",
			request.method,
			request.url.path,
			response.status_code,
			duration,
		)
	else:
		logger.info(
			"Request completed: %s %s -> %s in %.3fs",
			request.method,
			request.url.path,
			response.status_code,
			duration,
		)

	return response


register_error_handlers(app)

# The router keeps endpoint definitions out of this file so startup stays small.
app.include_router(router)
