import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """Wrapper around sentence-transformers to generate embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: Any = None

    def _lazy_load(self) -> None:
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model: %s", self.model_name)
                self.model = SentenceTransformer(self.model_name)
            except ImportError:
                logger.error("sentence-transformers is not installed.")
                raise RuntimeError(
                    "sentence-transformers is required for EmbeddingProvider."
                )

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string of text."""
        self._lazy_load()
        if not text:
            return []
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of strings."""
        self._lazy_load()
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
