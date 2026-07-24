import hashlib
import json
import logging
import os
from pathlib import Path

from app.config import settings
from app.knowledge.chunker import DocumentChunker
from app.knowledge.embeddings import EmbeddingProvider
from app.knowledge.loader import DocumentLoader
from app.knowledge.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """Coordinates document loading, chunking, and incremental vector DB updates."""

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.vectorstore = VectorStore()
        self.embeddings = EmbeddingProvider()

        # Track state to avoid full rebuilds
        self.state_file = (
            Path(getattr(settings, "VECTOR_DB_DIR", "app/data/vector_db"))
            / "index_state.json"
        )

    def _get_sandbox_hash(self) -> str:
        """Compute a simple hash of sandbox files to detect changes."""
        sandbox_dir = self.loader.sandbox_dir
        if not sandbox_dir.exists():
            return ""

        hasher = hashlib.md5()
        for root, _, files in os.walk(sandbox_dir):
            for file in sorted(files):
                file_path = Path(root) / file
                if file_path.suffix.lower() in [".txt", ".md", ".csv", ".json", ".log"]:
                    try:
                        hasher.update(str(file_path.relative_to(sandbox_dir)).encode())
                        hasher.update(str(file_path.stat().st_mtime).encode())
                        hasher.update(str(file_path.stat().st_size).encode())
                    except Exception:
                        pass
        return hasher.hexdigest()

    def check_and_index(self, force: bool = False) -> None:
        """Check if indexing is needed, and run the pipeline if so."""
        try:
            current_hash = self._get_sandbox_hash()

            # Check previous state
            previous_hash = ""
            if self.state_file.exists():
                try:
                    state = json.loads(self.state_file.read_text())
                    previous_hash = state.get("sandbox_hash", "")
                except Exception:
                    pass

            # If no changes and vector store exists, skip indexing
            if not force and current_hash and current_hash == previous_hash:
                try:
                    count = self.vectorstore.count()
                    if count > 0:
                        logger.info(
                            "Knowledge index is up-to-date (hash matched, %d chunks). Skipping indexing.",
                            count,
                        )
                        return
                except Exception:
                    pass  # Store might be empty or uninitialized

            logger.info("Knowledge index requires update. Starting indexing process...")

            # Load
            documents = self.loader.load_documents()
            if not documents:
                logger.warning("No documents found to index.")
                return

            # Chunk
            chunks = self.chunker.chunk_documents(documents)
            logger.info(
                "Created %d chunks from %d documents.", len(chunks), len(documents)
            )

            # Embed
            texts = [c.text for c in chunks]
            embeddings = self.embeddings.embed_texts(texts)

            # Store
            self.vectorstore.add_chunks(chunks, embeddings)

            # Save state
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps({"sandbox_hash": current_hash}))

            logger.info("Knowledge indexing completed successfully.")

        except Exception as e:
            logger.error("Failed to execute KnowledgeIndexer: %s", e, exc_info=True)
