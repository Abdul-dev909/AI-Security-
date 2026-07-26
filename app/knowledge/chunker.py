import logging

from app.knowledge.models import Chunk, KnowledgeDocument

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Splits KnowledgeDocuments into smaller Chunks while preserving metadata."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: KnowledgeDocument) -> list[Chunk]:
        """Splits a single KnowledgeDocument into a list of Chunks."""
        text = document.text
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size

            # If this isn't the last chunk, try to find a natural break point
            if end < text_length:
                # Look for a newline or space within the last 50 chars of the chunk
                break_point = text.rfind("\n", start, end)
                if break_point == -1 or break_point < end - 100:
                    break_point = text.rfind(" ", start, end)
                if break_point != -1 and break_point > start:
                    end = break_point + 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        document_id=document.document_id,
                        text=chunk_text,
                        metadata=document.metadata,  # Preserves rich metadata
                    )
                )

            start = end - self.chunk_overlap

            # Prevent infinite loop if overlap is misconfigured
            if start <= 0 or (end - start) <= 0:
                break

        return chunks

    def chunk_documents(self, documents: list[KnowledgeDocument]) -> list[Chunk]:
        """Splits a list of KnowledgeDocuments into a flat list of Chunks."""
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
