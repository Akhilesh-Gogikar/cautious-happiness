import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.engine import ForecasterCriticEngine, Source

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")

@pytest.mark.asyncio
async def test_search_market_news(mock_env):
    # Mock DDGS
    with patch('app.engine.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {'title': 'Test News', 'href': 'http://test.com', 'body': 'This is a test snippet.'}
        ]
        
        engine = ForecasterCriticEngine()
        sources = engine.search_market_news("Test Question")
        assert len(sources) == 1
        assert sources[0].title == "Test News"
        assert sources[0].url == "http://test.com"

@pytest.mark.asyncio
async def test_generate_forecast_parsing(mock_env):
    """
    Test that the probability is correctly parsed from the LLM response.
    """
    engine = ForecasterCriticEngine()
    
    # Mock search to return empty
    engine.search_market_news = MagicMock(return_value=[])
    
    # Mock httpx for Ollama
    with patch('httpx.AsyncClient') as MockClient:
        mock_client_instance = MockClient.return_value.__aenter__.return_value
        
        # Mock response with specific probability format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Reasoning: valid reasoning.\nProbability: 0.75"
        }
        mock_client_instance.post.return_value = mock_response

        prob, reasoning = await engine.generate_forecast_with_reasoning("Win?", [])
        
        assert prob == 0.75
        assert "valid reasoning" in reasoning

@pytest.mark.asyncio
async def test_generate_forecast_parsing_fallback(mock_env):
    """
    Test fallback parsing when "Probability:" label is missing.
    """
    engine = ForecasterCriticEngine()
    
    with patch('httpx.AsyncClient') as MockClient:
        mock_client_instance = MockClient.return_value.__aenter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Text ending with a float
        mock_response.json.return_value = {
            "response": "Some analysis concluding with 0.82"
        }
        mock_client_instance.post.return_value = mock_response

        prob, reasoning = await engine.generate_forecast_with_reasoning("Win?", [])
        assert prob == 0.82

@pytest.mark.asyncio
async def test_critique_forecast(mock_env):
    engine = ForecasterCriticEngine()
    
    # Mock Gemini Client
    engine.gemini_client = MagicMock()
    mock_genai_response = MagicMock()
    mock_genai_response.text = "Critique: Risky bet.\nAdjusted Probability: 0.60"
    
    # Mock the aio.models.generate_content path
    engine.gemini_client.aio.models.generate_content = AsyncMock(return_value=mock_genai_response)
    
    critique, adj_prob = await engine.critique_forecast("Q", [], 0.8, "Reason")
    
    assert adj_prob == 0.60
    assert critique == "Risky bet."
