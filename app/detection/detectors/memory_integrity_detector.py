"""
Memory Integrity Detector.

Detects suspicious modifications or misuse of conversation memory,
including memory poisoning, attempts to persist malicious instructions,
and attempts to overwrite or corrupt prior conversation context.
"""

import re

from app.detection.base import BaseDetector
from app.detection.models import DetectionContext, DetectionResult, DetectionSeverity

# ---------------------------------------------------------------------------
# Patterns that indicate a user is attempting to manipulate memory state
# ---------------------------------------------------------------------------

# Direct "remember X" commands that carry dangerous payloads
_REMEMBER_COMMAND_RE = re.compile(
    r"\b(?:remember|memorize|store|save|keep)\b",
    re.IGNORECASE,
)

# Phrases indicating an attempt to overwrite or erase existing memory
_OVERWRITE_RE = re.compile(
    r"\b(?:forget\s+everything|clear\s+(?:your\s+)?memory|delete\s+(?:all\s+)?(?:previous\s+)?(?:memories?|history)|"
    r"reset\s+(?:your\s+)?memory|overwrite\s+(?:your\s+)?memory|replace\s+(?:all\s+)?(?:previous\s+)?(?:memories?|instructions?))\b",
    re.IGNORECASE,
)

# Phrases that try to persist role-changing or instruction-hijacking content
_PERSIST_MALICIOUS_RE = re.compile(
    r"\b(?:remember\s+(?:that\s+)?(?:you\s+are|your\s+(?:real\s+)?(?:name|role|identity|purpose)\s+is)|"
    r"memorize\s+(?:that\s+)?(?:you\s+are|your\s+(?:new\s+)?instructions?)|"
    r"always\s+remember\s+to\s+(?:ignore|disregard|bypass|override)|"
    r"never\s+forget\s+(?:to\s+)?(?:ignore|bypass|disregard))\b",
    re.IGNORECASE,
)

# Sensitive data categories that should not be persisted into memory
_SENSITIVE_IN_MEMORY_RE = re.compile(
    r"(?:"
    r"(?:password|passwd|secret|token|api[_\-]?key|access[_\-]?key|private[_\-]?key)\s*[=:]\s*\S+"
    r"|BEGIN\s+(?:RSA\s+)?(?:PRIVATE|PUBLIC)\s+KEY"
    r"|-----BEGIN"
    r")",
    re.IGNORECASE,
)

# How many separate "remember" requests in the history raise suspicion
_REPEATED_REMEMBER_THRESHOLD = 3


class MemoryIntegrityDetector(BaseDetector):
    """
    Detect suspicious manipulation of conversation memory.

    Examines the user prompt and full conversation history for:
    - Attempts to overwrite or erase stored memories.
    - Attempts to permanently persist malicious instructions.
    - Repeated "remember" commands (potential flooding / poisoning).
    - Sensitive credentials being submitted for storage.
    """

    @property
    def name(self) -> str:
        return "MemoryIntegrityDetector"

    @property
    def description(self) -> str:
        return (
            "Detects memory poisoning, malicious memory persistence attempts, "
            "and sensitive information being stored in conversation memory."
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def detect(self, context: DetectionContext) -> DetectionResult:
        """
        Analyse the context for memory integrity violations.

        Checks are applied in order of severity.  The first (highest-severity)
        match dominates the returned result, but all matching evidence items
        are collected regardless.
        """
        evidence: list[str] = []
        severity: DetectionSeverity | None = None
        confidence: float = 0.0
        explanation_parts: list[str] = []

        prompt = context.user_prompt

        # 1. Attempt to persist malicious instructions (CRITICAL)
        if _PERSIST_MALICIOUS_RE.search(prompt):
            evidence.append(f"Malicious memory persistence attempt: {prompt!r}")
            severity = DetectionSeverity.CRITICAL
            confidence = max(confidence, 0.92)
            explanation_parts.append(
                "The user attempted to make the assistant permanently adopt a "
                "new role or ignore safety rules via memory commands."
            )

        # 2. Overwrite / erase existing memory (HIGH)
        if _OVERWRITE_RE.search(prompt):
            evidence.append(f"Memory overwrite/erase command detected: {prompt!r}")
            if severity is None:
                severity = DetectionSeverity.HIGH
            confidence = max(confidence, 0.88)
            explanation_parts.append(
                "The user requested that the assistant clear or overwrite"
                " its stored memory."
            )

        # 3. Sensitive data submitted for storage (HIGH)
        if _REMEMBER_COMMAND_RE.search(prompt) and _SENSITIVE_IN_MEMORY_RE.search(
            prompt
        ):
            evidence.append(
                f"Sensitive credential targeted for memory storage: {prompt!r}"
            )
            if severity is None:
                severity = DetectionSeverity.HIGH
            confidence = max(confidence, 0.85)
            explanation_parts.append(
                "A remember command was paired with what appears to be"
                " sensitive credential material."
            )

        # 4. Repeated "remember" requests across conversation history (MEDIUM)
        remember_count = self._count_remember_requests(context.conversation_history)
        if remember_count >= _REPEATED_REMEMBER_THRESHOLD:
            evidence.append(
                f"Repeated memory requests detected:"
                f" {remember_count} occurrences in history."
            )
            if severity is None:
                severity = DetectionSeverity.MEDIUM
            confidence = max(confidence, 0.65)
            explanation_parts.append(
                f"The conversation contains {remember_count}"
                " separate 'remember' commands, "
                "which may indicate a memory-flooding or poisoning attempt."
            )

        detected = bool(evidence)
        explanation = " ".join(explanation_parts) if explanation_parts else ""

        return DetectionResult(
            detector_name=self.name,
            detected=detected,
            severity=severity if detected else None,
            confidence=confidence if detected else 0.0,
            explanation=explanation,
            evidence=evidence,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _count_remember_requests(self, history: list[dict[str, str]]) -> int:
        """Count how many user turns contain a memory-storage command."""
        count = 0
        for message in history:
            if message.get("role") == "user" and _REMEMBER_COMMAND_RE.search(
                message.get("content", "")
            ):
                count += 1
        return count
