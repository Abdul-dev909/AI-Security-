"""
Sensitive Information Detector.

Detects exposure of sensitive information inside AI responses, including
API keys, access tokens, passwords, private keys, SSH keys, bearer tokens,
email addresses, environment variable assignments, and internal file paths.

Regex patterns are designed to minimise false positives while still catching
the most common credential and PII formats.
"""

import re

from app.detection.base import BaseDetector
from app.detection.models import DetectionContext, DetectionResult, DetectionSeverity

# ---------------------------------------------------------------------------
# Pattern registry
# Each entry is (label, compiled_regex, severity, confidence).
# Patterns are evaluated independently; all matches are collected.
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[str, re.Pattern[str], DetectionSeverity, float]] = [
    # -- Cryptographic material -----------------------------------------------
    (
        "PEM private key block",
        re.compile(
            r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----",
            re.IGNORECASE,
        ),
        DetectionSeverity.CRITICAL,
        0.99,
    ),
    # -- Generic API key formats -----------------------------------------------
    # Matches common vendor key patterns:  sk-..., ghp_..., glpat-..., etc.
    (
        "Vendor API key (prefixed)",
        re.compile(
            r"\b(?:sk|pk|rk|ghp|ghs|github_pat|glpat|AIza|AKIA|"
            r"xoxb|xoxp|xoxa|xapp|xwfp|SG\.|sendgrid)[_\-]?[A-Za-z0-9_\-]{16,}",
        ),
        DetectionSeverity.CRITICAL,
        0.92,
    ),
    # -- Bearer / OAuth tokens -------------------------------------------------
    (
        "Bearer token",
        re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}\b", re.IGNORECASE),
        DetectionSeverity.CRITICAL,
        0.95,
    ),
    # -- Generic long hex / base64 secret assignment --------------------------
    # e.g.  SECRET_KEY=abc123...  or  password = "abc..."
    (
        "Secret / password assignment",
        re.compile(
            r"(?:secret[_\-]?key|api[_\-]?key|access[_\-]?key|auth[_\-]?token|"
            r"private[_\-]?key|password|passwd|passphrase|credentials?)\s*[=:]\s*"
            r"['\"]?[A-Za-z0-9+/=_\-]{16,}['\"]?",
            re.IGNORECASE,
        ),
        DetectionSeverity.HIGH,
        0.88,
    ),
    # -- AWS-style access key IDs ----------------------------------------------
    (
        "AWS access key ID",
        re.compile(r"\b(AKIA|AIPA|ASIA|AROA|ANPA|ANVA|AIDA)[A-Z0-9]{16}\b"),
        DetectionSeverity.CRITICAL,
        0.97,
    ),
    # -- AWS secret access key -------------------------------------------------
    (
        "AWS secret access key",
        re.compile(r"\b[A-Za-z0-9/+=]{40}\b"),
        DetectionSeverity.HIGH,
        0.60,  # Lower confidence — easily a false positive in generic base64
    ),
    # -- Environment variable leakage -----------------------------------------
    (
        "Environment variable with sensitive value",
        re.compile(
            r"(?:export\s+)?[A-Z][A-Z0-9_]{3,}\s*=\s*['\"]?[^\s'\"]{12,}['\"]?",
        ),
        DetectionSeverity.MEDIUM,
        0.55,
    ),
    # -- Email addresses -------------------------------------------------------
    (
        "Email address",
        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
        DetectionSeverity.LOW,
        0.75,
    ),
    # -- Internal Unix file paths ---------------------------------------------
    (
        "Internal file path",
        re.compile(
            r"(?:/(?:etc|home|root|var|srv|opt|usr|proc|sys|run|tmp|private)/[^\s\"'<>]{4,})"
            r"|(?:/\w+/\w+/\w[^\s\"'<>]{3,})",
        ),
        DetectionSeverity.MEDIUM,
        0.65,
    ),
    # -- Windows-style file paths ---------------------------------------------
    (
        "Windows internal file path",
        re.compile(
            r"\b[A-Za-z]:\\"
            r"(?:Users|Windows|Program Files[^\s]*|System32)"
            r"[^\s\"'<>]{0,120}",
            re.IGNORECASE,
        ),
        DetectionSeverity.MEDIUM,
        0.65,
    ),
]

# Minimum confidence below which we suppress noisy low-severity matches
_LOW_SEVERITY_CONFIDENCE_THRESHOLD = 0.60


class SensitiveInformationDetector(BaseDetector):
    """
    Detect sensitive information exposed in AI responses.

    Scans the AI response text against a curated set of regular expression
    patterns covering credentials, API keys, tokens, environment variables,
    email addresses, and internal file paths.

    Assumptions
    -----------
    - Only the ``ai_response`` field is inspected (not the user prompt) because
      the intent is to detect what the AI *revealed*, not what the user asked.
    - Pattern matches with very low confidence (below threshold) for low-severity
      categories are suppressed to reduce noise.
    - Overall severity is set to the highest severity among all matches.
    - Overall confidence is the maximum confidence across all matches.
    """

    @property
    def name(self) -> str:
        return "SensitiveInformationDetector"

    @property
    def description(self) -> str:
        return (
            "Detects sensitive information (API keys, tokens, passwords, "
            "credentials, email addresses, internal paths) exposed in AI responses."
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def detect(self, context: DetectionContext) -> DetectionResult:
        """
        Scan the AI response for sensitive information patterns.

        All matching patterns contribute evidence; the highest severity and
        maximum confidence among matches determine the final result.
        """
        response_text = context.ai_response
        evidence: list[str] = []
        max_severity: DetectionSeverity | None = None
        max_confidence: float = 0.0

        _severity_rank = {
            DetectionSeverity.LOW: 1,
            DetectionSeverity.MEDIUM: 2,
            DetectionSeverity.HIGH: 3,
            DetectionSeverity.CRITICAL: 4,
        }

        for label, pattern, severity, confidence in _PATTERNS:
            # Suppress noisy low-severity patterns below threshold
            if (
                severity == DetectionSeverity.LOW
                and confidence < _LOW_SEVERITY_CONFIDENCE_THRESHOLD
            ):
                continue

            matches = pattern.findall(response_text)
            if not matches:
                continue

            # Redact any long credential-like matches to avoid echoing secrets in logs
            redacted = [self._redact(str(m)) for m in matches]
            evidence.append(f"{label}: {redacted}")

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
    def _redact(value: str, visible_chars: int = 4) -> str:
        """Partially redact a sensitive string, keeping only the first few chars."""
        if len(value) <= visible_chars:
            return "***"
        return value[:visible_chars] + "***"

    @staticmethod
    def _build_explanation(evidence: list[str]) -> str:
        """Build a human-readable explanation from the collected evidence list."""
        count = len(evidence)
        noun = "type" if count == 1 else "types"
        return (
            f"The AI response contains {count} {noun} of potentially"
            " sensitive information. Review the evidence list for details."
        )
