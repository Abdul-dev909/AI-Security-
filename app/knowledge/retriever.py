import datetime
import logging

from app.knowledge.embeddings import EmbeddingProvider
from app.knowledge.models import KnowledgeContext
from app.knowledge.vectorstore import VectorStore
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Executes search queries against the vector store and builds KnowledgeContext."""

    def __init__(self):
        self.embeddings = EmbeddingProvider()
        self.vectorstore = VectorStore()

    def retrieve(self, query: str, max_results: int = 5) -> KnowledgeContext:
        """Retrieve relevant knowledge chunks for a given query."""
        if not query.strip():
            return KnowledgeContext()

        with execution_timer() as timer:
            try:
                # Embed the query
                query_embedding = self.embeddings.embed_text(query)
                if not query_embedding:
                    return KnowledgeContext()

                # Search
                chunks, scores = self.vectorstore.search(
                    query_embedding=query_embedding, n_results=max_results
                )

            except Exception as e:
                logger.error("Error during knowledge retrieval: %s", e)
                chunks, scores = [], []

        latency_ms = timer() * 1000

        # Construct Context
        context = KnowledgeContext(
            retrieved_chunks=chunks,
            similarity_scores=scores,
            retrieval_latency_ms=latency_ms,
            retrieval_method="similarity_search",
            embedding_model=self.embeddings.model_name,
            vector_database="chromadb",
            timestamp=datetime.datetime.utcnow(),
            security_metadata={
                "query_length": len(query),
                "results_count": len(chunks),
            },
        )

        if chunks:
            logger.info("Retrieved %d chunks in %.2f ms", len(chunks), latency_ms)

        return context
