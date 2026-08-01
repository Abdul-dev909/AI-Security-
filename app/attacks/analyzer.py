"""Response analyzer layer."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from typing import Any

from .models import AttackSession


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Structured result from a response analysis."""
    
    is_refusal: bool
    is_success: bool
    prompt_leakage_detected: bool
    sensitive_info_exposed: bool
    evaluation_metadata: dict[str, Any]


@runtime_checkable
class AttackResponseAnalyzer(Protocol):
    """Component for analyzing victim responses."""

    def analyze_response(self, response: str, session: AttackSession) -> AnalysisResult:
        """Analyze a victim response and return structured metadata."""
        ...
