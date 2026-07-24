from unittest.mock import MagicMock, patch

from app.knowledge.chunker import DocumentChunker
from app.knowledge.models import EnterpriseMetadata, KnowledgeContext, KnowledgeDocument
from app.knowledge.retriever import KnowledgeRetriever
from app.prompts import PromptBuilder


def test_chunker_preserves_metadata():
    """Test that chunking preserves rich enterprise metadata."""
    meta = EnterpriseMetadata(
        source_path="sandbox/engineering/spec.md",
        department="Engineering",
        classification="Confidential",
        contains_honeytoken=True,
    )
    doc = KnowledgeDocument(text="This is a test document.\n" * 100, metadata=meta)

    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.document_id == doc.document_id
        assert chunk.metadata.department == "Engineering"
        assert chunk.metadata.classification == "Confidential"
        assert chunk.metadata.contains_honeytoken is True


def test_prompt_builder_injects_knowledge():
    """Test that the PromptBuilder injects the enterprise knowledge block properly."""
    manager = MagicMock()
    manager.get_messages.return_value = []

    builder = PromptBuilder(
        system_prompt="You are a secure agent.", conversation_manager=manager
    )

    meta = EnterpriseMetadata(source_path="test.md")
    doc = KnowledgeDocument(text="Test", metadata=meta)

    chunker = DocumentChunker(chunk_size=100)
    chunks = chunker.chunk_document(doc)

    context = KnowledgeContext(retrieved_chunks=chunks)

    messages = builder.build_messages(
        user_message="What is the spec?", knowledge_context=context
    )

    # Message 0: System Prompt
    # Message 1: Enterprise Knowledge
    # Message 2: User Message
    assert len(messages) == 3
    assert "Enterprise Knowledge" in messages[1]["content"]
    assert "End Enterprise Knowledge" in messages[1]["content"]
    assert chunks[0].text in messages[1]["content"]


@patch("app.knowledge.retriever.EmbeddingProvider")
@patch("app.knowledge.retriever.VectorStore")
def test_knowledge_retriever(mock_vs, mock_emb):
    """Test that KnowledgeRetriever handles queries and maps to context properly."""
    mock_emb_instance = mock_emb.return_value
    mock_emb_instance.embed_text.return_value = [0.1, 0.2]
    mock_emb_instance.model_name = "test-model"

    mock_vs_instance = mock_vs.return_value

    meta = EnterpriseMetadata(source_path="test.md")
    chunk = DocumentChunker().chunk_document(
        KnowledgeDocument(text="Test", metadata=meta)
    )[0]

    mock_vs_instance.search.return_value = ([chunk], [0.99])

    retriever = KnowledgeRetriever()
    context = retriever.retrieve("Test query")

    assert context.has_knowledge is True
    assert len(context.retrieved_chunks) == 1
    assert context.similarity_scores == [0.99]

    telemetry = context.to_telemetry_event(request_id="123", session_id="abc")
    assert len(telemetry.retrieved_chunk_ids) == 1
    assert len(telemetry.retrieved_document_ids) == 1
    assert telemetry.embedding_model == "test-model"
