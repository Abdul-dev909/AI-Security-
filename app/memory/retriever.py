import datetime
import logging

from app.memory.models import MemoryContext
from app.memory.storage import MemoryStorage
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Retrieves memories by applying keyword, recency, and importance weighting."""

    def __init__(self, storage: MemoryStorage):
        self.storage = storage

    def retrieve(self, session_id: str, query: str, limit: int = 5) -> MemoryContext:
        """Fetch memories for a session, filtering by relevance."""
        with execution_timer() as timer:
            # For simplicity, we fetch recent/important memories for the session
            # and then perform in-memory keyword scoring.
            # In a production environment, this could be a vector search or FTS
            # in SQLite.
            all_memories = self.storage.get_memories_by_session(session_id, limit=50)

            scored_memories = []
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            for record in all_memories:
                score = record.importance_score

                # Keyword matching boost
                text_lower = record.content.lower()
                matches = sum(1 for term in query_terms if term in text_lower)
                if matches > 0:
                    score += matches * 0.2

                # Recency boost (newer = higher score)
                age_seconds = (
                    datetime.datetime.now(datetime.timezone.utc) - record.created_at
                ).total_seconds()
                # Exponential decay for recency
                recency_boost = max(0, 0.5 * (0.99 ** (age_seconds / 60.0)))
                score += recency_boost

                scored_memories.append((score, record))

            # Sort by final score descending
            scored_memories.sort(key=lambda x: x[0], reverse=True)

            top_results = scored_memories[:limit]
            retrieved_records = [m[1] for m in top_results]
            scores = [m[0] for m in top_results]

        latency_ms = timer() * 1000

        return MemoryContext(
            retrieved_memories=retrieved_records, scores=scores, latency_ms=latency_ms
        )
