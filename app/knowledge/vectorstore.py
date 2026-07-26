import logging
from typing import Any

from app.config import settings
from app.knowledge.models import Chunk, EnterpriseMetadata

logger = logging.getLogger(__name__)


class VectorStore:
    """Wrapper around ChromaDB for storing and retrieving document chunks."""

    def __init__(self, persist_directory: str | None = None):
        self.persist_directory = persist_directory or getattr(
            settings, "VECTOR_DB_DIR", "app/data/vector_db"
        )
        self.collection_name = "enterprise_knowledge"
        self._client: Any = None
        self._collection: Any = None

    def _lazy_load(self) -> None:
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                logger.info("Initializing ChromaDB at %s", self.persist_directory)
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name
                )
            except ImportError:
                logger.error("chromadb is not installed.")
                raise RuntimeError("chromadb is required for VectorStore.") from None

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Add chunks to the vector database."""
        self._lazy_load()
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = []
        for c in chunks:
            meta = c.metadata.model_dump()
            # ChromaDB doesn't natively support datetime or nested dicts in
            # metadata directly
            # Ensure safe serialization for ChromaDB
            safe_meta = {}
            for k, v in meta.items():
                if v is None:
                    continue
                if isinstance(v, str | int | float | bool):
                    safe_meta[k] = v
                else:
                    safe_meta[k] = str(v)
            safe_meta["document_id"] = c.document_id
            metadatas.append(safe_meta)

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Added %d chunks to vector store.", len(chunks))

    def search(
        self, query_embedding: list[float], n_results: int = 5
    ) -> tuple[list[Chunk], list[float]]:
        """Search the vector database for similar chunks."""
        self._lazy_load()
        results = self._collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        )

        chunks: list[Chunk] = []
        scores: list[float] = []
        if not results["ids"] or not results["ids"][0]:
            return chunks, scores

        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            text = results["documents"][0][i]
            meta_dict = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results.get("distances") else 0.0

            # Convert distance to a similarity score (assuming cosine or L2,
            # just inverting/normalizing)
            # ChromaDB default is L2. Lower is more similar. Let's invert it for
            # similarity score.
            similarity = 1.0 / (1.0 + distance)

            document_id = meta_dict.pop("document_id", "")

            # Reconstruct EnterpriseMetadata, ignoring extra keys and parsing properly
            # We must map back the stringified values
            enterprise_meta_args: dict[str, Any] = {}
            for k, v in meta_dict.items():
                if (
                    hasattr(EnterpriseMetadata, k)
                    or k in EnterpriseMetadata.__annotations__
                ):
                    # Handle boolean conversion back from string
                    if isinstance(v, str):
                        if v.lower() == "true":
                            enterprise_meta_args[k] = True
                        elif v.lower() == "false":
                            enterprise_meta_args[k] = False
                        else:
                            enterprise_meta_args[k] = v
                    else:
                        enterprise_meta_args[k] = v

            meta = EnterpriseMetadata(**enterprise_meta_args)

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=text,
                    metadata=meta,
                )
            )
            scores.append(similarity)

        return chunks, scores

    def count(self) -> int:
        """Return the number of chunks in the collection."""
        self._lazy_load()
        return self._collection.count()
