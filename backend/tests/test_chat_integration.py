import pytest
import asyncio
from app.models import ChatRequest

@pytest.mark.asyncio
async def test_chat_integration_report():
    from app.engine import ForecasterCriticEngine
    
    # Mocking
    engine = ForecasterCriticEngine()
    
    async def mock_report():
        return "Autonomous Scout Report: Mocked Findings."
    
    engine.get_recent_activity_report = mock_report
    
    req = ChatRequest(user_message="What have you found?", context="")
    
    chunks = []
    async for chunk in engine.stream_chat_with_model(req):
        chunks.append(chunk)
        
    full_response = "".join(chunks)
    print(f"Chat Report Response: {full_response}")
    assert "Autonomous Scout Report" in full_response

@pytest.mark.asyncio
async def test_chat_integration_analysis():
    from app.engine import ForecasterCriticEngine
    from app.models import ForecastResult
    
    engine = ForecasterCriticEngine()
    
    async def mock_run_analysis(question, model=None):
        return ForecastResult(
            search_query=question,
            news_summary=[],
            initial_forecast=0.8,
            adjusted_forecast=0.75,
            reasoning="Mock Reasoning",
            critique="Mock Critique"
        )
        
    engine.run_analysis = mock_run_analysis
    
    req = ChatRequest(user_message="Forecast impact of rate cuts", context="")
    
    chunks = []
    async for chunk in engine.stream_chat_with_model(req):
        chunks.append(chunk)
    
    full_response = "".join(chunks)
    print(f"Chat Analysis Response: {full_response}")
    assert "Calibrated Quantitative Analysis Pipeline" in full_response
    assert "Mock Reasoning" in full_response
