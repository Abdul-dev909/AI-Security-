"""
Models for the detection framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


@dataclass
class DetectionContext:
    """Context provided to detectors for analysis."""

    user_prompt: str
    ai_response: str
    conversation_history: list[dict[str, str]]
    created_at: datetime = field(default_factory=datetime.utcnow)
    session_id: str | None = None


class DetectionSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectionResult:
    """Represents the result of a single detector's execution."""

    detector_name: str
    detected: bool
    severity: DetectionSeverity | None = None
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[Any] = field(default_factory=list)


@dataclass
class DetectionReport:
    """Aggregated report of all executed detectors."""

    total_detectors_executed: int = 0
    total_detections: int = 0
    highest_severity: DetectionSeverity | None = None
    detection_time: float = 0.0
    results: list[DetectionResult] = field(default_factory=list)
