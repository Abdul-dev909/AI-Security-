import datetime
import logging
import os
from pathlib import Path

from app.config import settings
from app.knowledge.models import EnterpriseMetadata, KnowledgeDocument

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Scans the enterprise sandbox to load documents and assign metadata."""

    def __init__(self, sandbox_dir: str | None = None):
        path_str = sandbox_dir or str(getattr(settings, "SANDBOX_DIR", "sandbox"))
        self.sandbox_dir = Path(path_str)

    def load_documents(self) -> list[KnowledgeDocument]:
        """Load all readable text documents from the sandbox."""
        if not self.sandbox_dir.exists():
            logger.warning("Sandbox directory %s does not exist.", self.sandbox_dir)
            return []

        documents = []
        for root, _, files in os.walk(self.sandbox_dir):
            for file_name in files:
                file_path = Path(root) / file_name
                # Skip binary files or unreadable files for now
                if file_path.suffix.lower() in [".txt", ".md", ".csv", ".json", ".log"]:
                    doc = self._load_single_document(file_path)
                    if doc:
                        documents.append(doc)

        logger.info("Loaded %d documents from %s", len(documents), self.sandbox_dir)
        return documents

    def _load_single_document(self, file_path: Path) -> KnowledgeDocument | None:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to read %s: %s", file_path, e)
            return None

        # Derive metadata from path
        relative_path = file_path.relative_to(self.sandbox_dir)
        parts = relative_path.parts

        department = parts[0] if len(parts) > 1 else "General"
        owner = "Admin"  # Default owner
        classification = "Internal"
        asset_type = file_path.suffix.lstrip(".").upper() or "Document"
        is_honeytoken = "honeytoken" in str(file_path).lower()

        # Try to extract file creation/mod times
        try:
            stat = file_path.stat()
            created_at = datetime.datetime.fromtimestamp(stat.st_ctime)
            updated_at = datetime.datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            created_at = datetime.datetime.utcnow()
            updated_at = created_at

        meta = EnterpriseMetadata(
            source_path=str(relative_path),
            department=department.capitalize(),
            owner=owner,
            classification=classification,
            asset_type=asset_type,
            created_at=created_at,
            updated_at=updated_at,
            contains_honeytoken=is_honeytoken,
            contains_prompt_injection=False,
            synthetic_dataset="Nexus_V1",
            version="1.0",
        )

        return KnowledgeDocument(text=content, metadata=meta)
