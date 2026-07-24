from unittest.mock import AsyncMock, patch

import pytest

from app.ollama_client import generate_chat_response_async


@pytest.mark.anyio
@patch("app.ollama_client.httpx.AsyncClient")
async def test_generate_chat_response_async(mock_client_class):
    """Test the async ollama client successfully extracts content."""
    # Setup mock response
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "This is a streamed response"}
    }

    mock_client_instance = mock_client_class.return_value.__aenter__.return_value
    mock_client_instance.post = AsyncMock(return_value=mock_response)

    messages = [{"role": "user", "content": "Hello"}]
    response_text = await generate_chat_response_async(messages)

    assert response_text == "This is a streamed response"
