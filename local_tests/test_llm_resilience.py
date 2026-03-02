import asyncio
import httpx
import pytest
from unittest.mock import MagicMock, patch
from app.core.ai_client import AIClient
from app.engine import IntelligenceMirrorEngine
from app.models import ChatRequest

@pytest.mark.asyncio
async def test_ai_client_retry():
    """Verify that AIClient retries on connection error."""
    with patch("httpx.AsyncClient.request") as mock_request:
        # Mock 2 failures then 1 success
        mock_request.side_effect = [
            httpx.ConnectError("Fake connection error"),
            httpx.ConnectError("Fake connection error"),
            MagicMock(status_code=200, json=lambda: {"content": "Success content"}, raise_for_status=lambda: None)
        ]
        
        client = AIClient()
        # We need to speed up the sleep for the test
        with patch("asyncio.sleep", return_value=None):
            result = await client.generate("Test prompt", provider="llama-cpp")
            
        assert result == "Success content"
        assert mock_request.call_count == 3
        await client.close()

@pytest.mark.asyncio
async def test_engine_fallback():
    """Verify that IntelligenceMirrorEngine falls back to secondary model on failure."""
    engine = IntelligenceMirrorEngine()
    
    # Mock the intelligence service
    with patch.object(engine.intelligence_service, 'chat_with_model') as mock_chat:
        # Define a helper to simulate the async response
        async def mock_chat_side_effect(*args, **kwargs):
            if mock_chat.call_count == 1:
                raise asyncio.TimeoutError("Model timed out")
            return "Fallback response"
        
        mock_chat.side_effect = mock_chat_side_effect
        
        req = ChatRequest(question="What is the price of gold?")
        
        # Run chat_with_model. It should try once, fail, then try again and succeed.
        response = await engine.chat_with_model(req)
            
        assert response == "Fallback response"
        assert mock_chat.call_count == 2

if __name__ == "__main__":
    asyncio.run(test_ai_client_retry())
    asyncio.run(test_engine_fallback())
    print("Resilience tests passed!")
