import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.engine import IntelligenceMirrorEngine
from app.models import Source
from app.domain.intelligence.service import IntelligenceService
from app.domain.intelligence.critic import CriticService
from app.domain.intelligence.dtypes import StructuredCriticResult

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")

@pytest.mark.asyncio
async def test_search_market_news(mock_env):
    # Mock DDGS in IntelligenceService
    with patch('app.domain.intelligence.service.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {'title': 'Test News', 'href': 'http://test.com', 'body': 'This is a test snippet.'}
        ]
        
        service = IntelligenceService()
        sources = await service.search_market_news("Test Question")
        assert len(sources) == 1
        assert sources[0].title == "Test News"
        assert sources[0].url == "http://test.com"

@pytest.mark.asyncio
async def test_generate_forecast_parsing(mock_env):
    """
    Test that the probability is correctly parsed from the LLM response.
    """
    # Mock httpx globally before service init
    with patch('httpx.AsyncClient') as MockClient:
        mock_client_instance = MockClient.return_value
        # For AsyncClient as a context manager (if we ever switch back) or direct use
        mock_client_instance.__aenter__.return_value = mock_client_instance
        
        # Mock response with specific probability format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_json = {
            "mirror": {"score": 0.75, "reasoning": "valid reasoning"},
            "noise": {"score": 0.5, "reasoning": "N/A"},
            "divergence": {"score": 0.5, "reasoning": "N/A"},
            "algo": {"score": 0.5, "reasoning": "N/A"}
        }
        mock_response.json.return_value = {
            "response": json.dumps(mock_json),
            "content": json.dumps(mock_json)
        }
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        service = IntelligenceService()
        prob, reasoning, analysis = await service.generate_forecast_with_reasoning("Win?", [])
        
        assert prob == 0.5625
        assert "valid reasoning" in reasoning
        assert analysis.mirror.score == 0.75

@pytest.mark.asyncio
async def test_critique_forecast(mock_env):
    service = CriticService()
    
    # Mock ai_client.generate_json directly
    with patch('app.domain.intelligence.critic.ai_client') as mock_ai_client:
        mock_ai_client.generate_json = AsyncMock(return_value={
            "critique": "Risky bet.",
            "score": 0.60,
            "risk_factors": ["High volatility"],
            "adversarial_score": 7.5,
            "logical_fallacies": ["Confirmation bias"],
            "counter_arguments": ["Market could crash"]
        })
        mock_ai_client.providers = ["gemini"]
        
        result = await service.critique_forecast("Q", [], 0.8, "Reason")
        
        assert isinstance(result, StructuredCriticResult)
        assert result.score == 0.60
        assert result.critique == "Risky bet."
        assert result.adversarial_score == 7.5
    assert result.critique == "Risky bet."

@pytest.mark.asyncio
async def test_engine_integration(mock_env):
    """
    Test the engine orchestrating services.
    """
    engine = IntelligenceMirrorEngine()
    
    # Mock services
    engine.intelligence_service.search_market_news = AsyncMock(return_value=[])
    engine.intelligence_service.search_physical_data = AsyncMock(return_value=[])
    
    from app.models import StructuredAnalysisResult, MirrorAnalysis, NoiseAnalysis, DivergenceAnalysis, AlgoAnalysis
    comp = {"score": 0.8, "reasoning": "Reason"}
    mock_analysis = StructuredAnalysisResult(
        mirror=MirrorAnalysis(**comp),
        noise=NoiseAnalysis(**comp),
        divergence=DivergenceAnalysis(**comp),
        algo=AlgoAnalysis(**comp)
    )
    
    engine.intelligence_service.generate_forecast_with_reasoning = AsyncMock(return_value=(0.8, "Reason", mock_analysis))
    
    # Update to return StructuredCriticResult
    mock_critic_result = StructuredCriticResult(
        critique="Critique",
        score=0.7,
        risk_factors=["Test risk"]
    )
    engine.critic_service.critique_forecast = AsyncMock(return_value=mock_critic_result)
    
    result = await engine.run_analysis("Q")
    
    assert result.initial_forecast == 0.8
    assert result.adjusted_forecast == 0.7
    assert result.critique == "Critique"
    assert result.mirror.score == 0.8
