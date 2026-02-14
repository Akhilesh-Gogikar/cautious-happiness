import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.engine import IntelligenceMirrorEngine
from app.models import Source
from app.services.intelligence import IntelligenceService
from app.services.critic import CriticService

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")

@pytest.mark.asyncio
async def test_search_market_news(mock_env):
    # Mock DDGS in IntelligenceService
    with patch('app.services.intelligence.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {'title': 'Test News', 'href': 'http://test.com', 'body': 'This is a test snippet.'}
        ]
        
        service = IntelligenceService()
        sources = service.search_market_news("Test Question")
        assert len(sources) == 1
        assert sources[0].title == "Test News"
        assert sources[0].url == "http://test.com"

@pytest.mark.asyncio
async def test_generate_forecast_parsing(mock_env):
    """
    Test that the probability is correctly parsed from the LLM response.
    """
    service = IntelligenceService()
    
    # Mock httpx for Ollama
    with patch('httpx.AsyncClient') as MockClient:
        mock_client_instance = MockClient.return_value.__aenter__.return_value
        
        # Mock response with specific probability format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Reasoning: valid reasoning.\nMirror Confidence: 0.75"
        }
        mock_client_instance.post.return_value = mock_response

        prob, reasoning = await service.generate_forecast_with_reasoning("Win?", [])
        
        assert prob == 0.75
        assert "valid reasoning" in reasoning

@pytest.mark.asyncio
async def test_critique_forecast(mock_env):
    service = CriticService()
    
    # Mock Gemini Client
    service.gemini_client = MagicMock()
    mock_genai_response = MagicMock()
    mock_genai_response.text = "Critique: Risky bet.\nAdjusted Mirror Score: 0.60"
    
    # Mock the aio.models.generate_content path
    service.gemini_client.aio.models.generate_content = AsyncMock(return_value=mock_genai_response)
    
    critique, adj_prob = await service.critique_forecast("Q", [], 0.8, "Reason")
    
    assert adj_prob == 0.60
    assert critique == "Risky bet."

@pytest.mark.asyncio
async def test_engine_integration(mock_env):
    """
    Test the engine orchestrating services.
    """
    engine = IntelligenceMirrorEngine()
    
    # Mock services
    engine.intelligence_service.search_market_news = MagicMock(return_value=[])
    engine.intelligence_service.generate_forecast_with_reasoning = AsyncMock(return_value=(0.8, "Reason"))
    engine.critic_service.critique_forecast = AsyncMock(return_value=("Critique", 0.7))
    
    result = await engine.run_analysis("Q")
    
    assert result.initial_forecast == 0.8
    assert result.adjusted_forecast == 0.7
    assert result.critique == "Critique"
