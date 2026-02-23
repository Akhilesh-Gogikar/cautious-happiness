import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.engine import IntelligenceMirrorEngine
from app.domain.intelligence.dtypes import StructuredCriticResult

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")

@pytest.mark.asyncio
async def test_adversarial_critic_integration(mock_env):
    """
    Test that the engine properly integrates the adversarial red-teaming
    fields from the Critic service into the final ForecastResult.
    """
    engine = IntelligenceMirrorEngine()
    
    # Mock services
    engine.intelligence_service.search_market_news = AsyncMock(return_value=[])
    engine.intelligence_service.search_physical_data = AsyncMock(return_value=[])
    
    from app.models import StructuredAnalysisResult, MirrorAnalysis, NoiseAnalysis, DivergenceAnalysis, AlgoAnalysis
    comp = {"score": 0.9, "reasoning": "Highly confident reasoning"}
    mock_analysis = StructuredAnalysisResult(
        mirror=MirrorAnalysis(**comp),
        noise=NoiseAnalysis(**comp),
        divergence=DivergenceAnalysis(**comp),
        algo=AlgoAnalysis(**comp)
    )
    
    engine.intelligence_service.generate_forecast_with_reasoning = AsyncMock(return_value=(0.9, "Reason", mock_analysis))
    engine.intelligence_service.search_semantic_correlations = AsyncMock(return_value=[])
    
    # Mock adversarial critic response
    mock_critic_result = StructuredCriticResult(
        critique="The analyst is ignoring major supply chain risks.",
        score=0.4,
        risk_factors=["Supply chain disruptions"],
        adversarial_score=8.5,
        logical_fallacies=["Confirmation Bias: Ignoring negative data"],
        counter_arguments=["If port strike occurs, supply drops by 20%"]
    )
    engine.critic_service.critique_forecast = AsyncMock(return_value=mock_critic_result)
    
    # Run analysis
    result = await engine.run_analysis("Will crude oil hit $90?")
    
    # Assertions for adversarial fields
    assert result.initial_forecast == 0.9
    assert result.adjusted_forecast == 0.4
    assert result.critique == "The analyst is ignoring major supply chain risks."
    assert result.adversarial_score == 8.5
    assert "Confirmation Bias: Ignoring negative data" in result.logical_fallacies
    assert "If port strike occurs, supply drops by 20%" in result.counter_arguments
