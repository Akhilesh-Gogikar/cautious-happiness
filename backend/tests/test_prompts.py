import pytest
from unittest.mock import AsyncMock, MagicMock
from app.engine import ForecasterCriticEngine
from app.models import Source

@pytest.mark.asyncio
async def test_forecast_parsing_with_thinking():
    engine = ForecasterCriticEngine()
    
    # Mock LLM response with <think> tag
    mock_response = """<think>
    Thinking about the probability...
    </think>
    ```json
    {
        "reasoning": "Based on the news, it is likely.",
        "probability": 0.75
    }
    ```"""
    
    engine._call_llm = AsyncMock(return_value=mock_response)
    
    sources = [Source(title="News", snippet="Snippet", url="http://test.com", published_date="2023-01-01")]
    prob, reasoning = await engine.generate_forecast_with_reasoning("Test Question", sources)
    
    assert prob == 0.75
    assert "Based on the news, it is likely." in reasoning
    assert "<think>" not in reasoning  # Should interpret final reasoning

@pytest.mark.asyncio
async def test_forecast_parsing_without_thinking():
    engine = ForecasterCriticEngine()
    
    # Mock LLM response without <think> tag
    mock_response = """
    ```json
    {
        "reasoning": "Direct reasoning.",
        "probability": 0.60
    }
    ```"""
    
    engine._call_llm = AsyncMock(return_value=mock_response)
    
    sources = [Source(title="News", snippet="Snippet", url="http://test.com", published_date="2023-01-01")]
    prob, reasoning = await engine.generate_forecast_with_reasoning("Test Question", sources)
    
    assert prob == 0.60
    assert "Direct reasoning." in reasoning

@pytest.mark.asyncio
async def test_classify_market_parsing():
    engine = ForecasterCriticEngine()
    
    # Mock LLM with think tag
    mock_response = "<think>Analyzing...</think>Economics"
    engine._call_llm = AsyncMock(return_value=mock_response)
    
    category = await engine.classify_market("Inflation rate?")
    assert category == "Economics"
