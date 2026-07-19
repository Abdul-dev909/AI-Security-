"""Central configuration values for the AI Agent application."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Grouped configuration values used across the application.

    Keeping these values together avoids magic numbers and hard-coded strings
    scattered across the codebase.
    """

    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "qwen3"
    SYSTEM_PROMPT: str = "You are a helpful AI assistant."
    MAX_HISTORY: int = 20
    ENABLE_MEMORY: bool = True
    DATABASE_PATH: str = str(Path(__file__).resolve().parent.parent / "memory.db")
    MEMORY_LIMIT: int = 5
    REQUEST_TIMEOUT: float = 30.0
    LOG_LEVEL: str = "INFO"
    API_TITLE: str = "AI Agent"
    API_VERSION: str = "1.1.0"
    API_DESCRIPTION: str = (
        "A beginner-friendly FastAPI backend that sends chat messages to a local Ollama model "
        "and keeps short conversation history in memory."
    )
    FALLBACK_MODEL_NAMES: tuple[str, ...] = ("qwen3:8b",)
    FALLBACK_RESPONSE: str = (
        "I’m temporarily unable to reach the AI service. Please try again shortly."
    )


settings = Settings()
