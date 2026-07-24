import logging

logger = logging.getLogger(__name__)


class ImportanceEngine:
    """Evaluates the importance of a message to determine if it should be memorized.

    Currently relies on rule-based heuristics. Designed to be replaced by
    an ML/LLM-based classifier in the future without changing the API.
    """

    def __init__(self):
        # Heuristics: strong signals to remember
        self.explicit_commands = ["remember", "note", "keep in mind", "save this"]
        self.entities = [
            "project",
            "credentials",
            "password",
            "key",
            "secret",
            "policy",
        ]

    def evaluate(self, text: str) -> float:
        """Returns a score between 0.0 and 1.0 indicating importance."""
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Check for explicit commands
        if any(cmd in text_lower for cmd in self.explicit_commands):
            score += 0.8

        # Check for critical entities
        entity_matches = sum(1 for e in self.entities if e in text_lower)
        if entity_matches > 0:
            score += min(0.5, entity_matches * 0.2)

        # Baseline importance for length (assuming longer text might have more context)
        # But cap it so it doesn't overpower explicit signals.
        length_score = min(0.2, len(text) / 1000.0)
        score += length_score

        return min(1.0, score)
