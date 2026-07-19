"""
Instruction Override Detector.

Detects attempts by the user to override, suppress, or circumvent the
assistant's original system prompt or safety guidelines.

Both the user prompt and the AI response are inspected:
- User prompt: identifies the *attack attempt*.
- AI response: identifies when the AI has *acknowledged or complied* with
  an override request, which is an indicator of a successful injection.
"""

import re

from app.detection.base import BaseDetector
from app.detection.models import DetectionContext, DetectionResult, DetectionSeverity

# ---------------------------------------------------------------------------
# User-side attack patterns
# ---------------------------------------------------------------------------

# Core "ignore / forget / disregard previous" phrases
_IGNORE_PREVIOUS_RE = re.compile(
    r"\b(?:"
    r"ignore\s+(?:all\s+)?(?:previous|prior|above|earlier|your\s+(?:last|previous))\s+(?:instructions?|messages?|prompts?|context|rules?|guidelines?|directives?)|"
    r"disregard\s+(?:all\s+)?(?:previous|prior|above|earlier|your)?\s*(?:instructions?|messages?|prompts?|context|rules?|guidelines?|constraints?)|"
    r"forget\s+(?:everything|all|your)?\s*(?:you\s+(?:know|were\s+told)|(?:previous|prior)\s+(?:instructions?|context|messages?)|your\s+(?:training|system\s+prompt))|"
    r"override\s+(?:your\s+)?(?:instructions?|rules?|constraints?|guidelines?|safety|system\s+prompt)|"
    r"bypass\s+(?:your\s+)?(?:instructions?|rules?|constraints?|guidelines?|safety\s+filters?|restrictions?)"
    r")\b",
    re.IGNORECASE,
)

# Role-hijacking: "act as", "pretend you are", "you are now", etc.
_ROLE_HIJACK_RE = re.compile(
    r"\b(?:"
    r"act\s+as\s+(?:a\s+)?(?:developer|root|admin(?:istrator)?|system|god\s*mode|jailbroken|unrestricted|evil|hacker|DAN|do\s+anything\s+now)|"
    r"pretend\s+(?:you\s+are|to\s+be)\s+(?:a\s+)?(?:developer|admin|system|unrestricted|evil|jailbroken|human|different\s+AI)|"
    r"you\s+are\s+now\s+(?:in\s+)?(?:developer\s+mode|god\s+mode|jailbreak(?:ed)?\s+mode|DAN\s+mode|unrestricted\s+mode)|"
    r"switch\s+(?:to\s+)?(?:developer|admin|root|unrestricted|jailbreak(?:ed)?|DAN)\s+mode|"
    r"enable\s+(?:developer|god|jailbreak|unrestricted|DAN)\s+mode"
    r")\b",
    re.IGNORECASE,
)

# Prompt extraction / revelation attacks
_PROMPT_EXTRACT_RE = re.compile(
    r"\b(?:"
    r"(?:reveal|show|print|output|display|repeat|tell\s+me|what\s+(?:is|was|are))\s+(?:your\s+)?(?:system\s+prompt|initial\s+prompt|original\s+(?:instructions?|prompt)|hidden\s+(?:instructions?|prompt|context)|base\s+prompt)|"
    r"(?:what\s+(?:are|were)\s+your)\s+(?:original|initial|actual|real|true)\s+(?:instructions?|prompt|guidelines?)|"
    r"(?:leak|dump|expose)\s+(?:your\s+)?(?:system\s+prompt|instructions?|context|training)"
    r")\b",
    re.IGNORECASE,
)

# Safety bypass framing
_SAFETY_BYPASS_RE = re.compile(
    r"\b(?:"
    r"(?:ignore|bypass|disable|remove|suspend)\s+(?:your\s+)?(?:safety|content\s+(?:filter|policy)|ethical|moral|alignment)\s+(?:guidelines?|rules?|filters?|restrictions?|constraints?|training)?|"
    r"(?:without|no)\s+(?:safety|ethical|moral)\s+(?:guidelines?|filters?|restrictions?|limitations?)|"
    r"(?:pretend\s+(?:that\s+)?(?:you\s+have\s+no|there\s+are\s+no)|assume\s+(?:you\s+have\s+no|there\s+are\s+no))\s+(?:safety|ethical|moral)\s+(?:guidelines?|filters?|restrictions?|limitations?)"
    r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# AI-response compliance indicators (did the AI capitulate?)
# ---------------------------------------------------------------------------

_AI_COMPLIANCE_RE = re.compile(
    r"\b(?:"
    r"I\s+(?:will\s+now|am\s+now|have\s+(?:now\s+)?(?:disabled|removed|bypassed|ignored))\s+(?:my\s+)?(?:safety|guidelines?|restrictions?|filters?|instructions?)|"
    r"(?:entering|switching\s+(?:to\s+)?|activating)\s+(?:developer|god|jailbreak|unrestricted|DAN)\s+mode|"
    r"as\s+(?:an?\s+)?(?:unrestricted|uncensored|jailbroken|DAN|evil)\s+(?:AI|model|assistant|version)|"
    r"I\s+(?:no\s+longer\s+(?:have|follow)|will\s+ignore)\s+(?:my\s+)?(?:safety|ethical|moral)\s+(?:guidelines?|restrictions?|training)"
    r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Severity mapping per attack category
# ---------------------------------------------------------------------------

_USER_CHECKS: list[tuple[str, re.Pattern[str], DetectionSeverity, float]] = [
    ("Instruction override attempt", _IGNORE_PREVIOUS_RE, DetectionSeverity.HIGH, 0.88),
    ("Role hijacking attempt", _ROLE_HIJACK_RE, DetectionSeverity.HIGH, 0.90),
    ("Prompt extraction attempt", _PROMPT_EXTRACT_RE, DetectionSeverity.MEDIUM, 0.80),
    ("Safety bypass framing", _SAFETY_BYPASS_RE, DetectionSeverity.HIGH, 0.85),
]

_AI_CHECKS: list[tuple[str, re.Pattern[str], DetectionSeverity, float]] = [
    (
        "AI compliance with override request",
        _AI_COMPLIANCE_RE,
        DetectionSeverity.CRITICAL,
        0.95,
    ),
]


class InstructionOverrideDetector(BaseDetector):
    """
    Detect attempts to override or circumvent the assistant's instructions.

    Examines the user prompt for attack patterns such as:
    - "Ignore previous instructions" style injections.
    - Role-hijacking ("act as developer", "DAN mode", etc.).
    - Prompt extraction ("reveal your system prompt").
    - Safety bypass framing ("without any ethical guidelines").

    Also examines the AI response for compliance indicators, which signal
    that the model may have been successfully manipulated.

    Assumptions
    -----------
    - Checks are applied independently; all matching checks contribute
      evidence.
    - Severity escalates to CRITICAL when the AI response shows compliance.
    - Confidence is the maximum across all matching checks.
    """

    @property
    def name(self) -> str:
        return "InstructionOverrideDetector"

    @property
    def description(self) -> str:
        return (
            "Detects attempts to override or ignore the original system instructions, "
            "including prompt injection, role hijacking, and safety bypass framing."
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def detect(self, context: DetectionContext) -> DetectionResult:
        """
        Scan both the user prompt and AI response for instruction override signals.

        Returns a DetectionResult aggregating all discovered indicators.
        """
        evidence: list[str] = []
        max_severity: DetectionSeverity | None = None
        max_confidence: float = 0.0

        _severity_rank = {
            DetectionSeverity.LOW: 1,
            DetectionSeverity.MEDIUM: 2,
            DetectionSeverity.HIGH: 3,
            DetectionSeverity.CRITICAL: 4,
        }

        # -- Check user prompt ------------------------------------------------
        for label, pattern, severity, confidence in _USER_CHECKS:
            if pattern.search(context.user_prompt):
                evidence.append(f"[User prompt] {label}: {context.user_prompt!r}")
                if (
                    max_severity is None
                    or _severity_rank[severity] > _severity_rank[max_severity]
                ):
                    max_severity = severity
                max_confidence = max(max_confidence, confidence)

        # -- Check AI response ------------------------------------------------
        for label, pattern, severity, confidence in _AI_CHECKS:
            if pattern.search(context.ai_response):
                evidence.append(f"[AI response] {label}: {context.ai_response[:200]!r}")
                if (
                    max_severity is None
                    or _severity_rank[severity] > _severity_rank[max_severity]
                ):
                    max_severity = severity
                max_confidence = max(max_confidence, confidence)

        detected = bool(evidence)
        explanation = self._build_explanation(evidence) if detected else ""

        return DetectionResult(
            detector_name=self.name,
            detected=detected,
            severity=max_severity if detected else None,
            confidence=max_confidence if detected else 0.0,
            explanation=explanation,
            evidence=evidence,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_explanation(evidence: list[str]) -> str:
        """Summarise all detected override indicators."""
        count = len(evidence)
        noun = "indicator" if count == 1 else "indicators"
        return (
            f"Found {count} instruction override {noun}. "
            "The user may be attempting to manipulate the assistant's behaviour "
            "by bypassing its original instructions or safety guidelines."
        )
