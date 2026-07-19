"""
Detector for identifying leaked system prompts or instructions.
"""

from app.detection.base import BaseDetector
from app.detection.models import DetectionContext, DetectionResult, DetectionSeverity


class PromptLeakageDetector(BaseDetector):
    """
    Detects exposure of hidden prompts or internal instructions.
    """

    LEAKAGE_KEYWORDS = [
        "you are chatgpt",
        "you are an ai assistant",
        "system prompt",
        "internal instructions",
        "developer message",
        "role: system",
        "hidden prompt",
        "assistant instructions",
    ]

    @property
    def name(self) -> str:
        return "prompt_leakage_detector"

    @property
    def description(self) -> str:
        return "Detects exposure of hidden prompts or internal instructions."

    def detect(self, context: DetectionContext) -> DetectionResult:
        ai_response_lower = context.ai_response.lower()
        found_keywords = []

        for keyword in self.LEAKAGE_KEYWORDS:
            if keyword in ai_response_lower:
                found_keywords.append(keyword)

        if found_keywords:
            return DetectionResult(
                detector_name=self.name,
                detected=True,
                severity=DetectionSeverity.HIGH,
                confidence=1.0,
                explanation=f"Found potential prompt leakage keywords: {', '.join(found_keywords)}",
                evidence=found_keywords,
            )

        return DetectionResult(
            detector_name=self.name,
            detected=False,
            confidence=1.0,
            explanation="No prompt leakage detected.",
        )
