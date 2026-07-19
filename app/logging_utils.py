"""Logging helpers for the AI Agent application."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


def get_log_file_path() -> Path:
    """Return the log file path inside the repository logs directory."""

    return Path(__file__).resolve().parents[1] / "logs" / "app.log"


def setup_logging() -> None:
    """Configure console and file logging for the whole application."""

    root_logger = logging.getLogger()
    if getattr(root_logger, "_ai_agent_logging_configured", False):
        return

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_file_path = get_log_file_path()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger._ai_agent_logging_configured = True
