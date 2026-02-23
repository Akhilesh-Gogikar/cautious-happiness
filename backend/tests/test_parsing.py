import pytest
import json
from app.domain.intelligence.service import IntelligenceService
from app.models import Source
from app.domain.intelligence.dtypes import StructuredAnalysisResult
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_structured_parsing_success():
    service = IntelligenceService()
    
    mock_json = {
        "mirror": {"score": 0.8, "reasoning": "High mirror confidence"},
        "noise": {"score": 0.2, "reasoning": "Low noise"},
        "divergence": {"score": 0.7, "reasoning": "Clear divergence"},
        "algo": {"score": 0.9, "reasoning": "Algo will follow trend"}
    }
    
    with patch.object(IntelligenceService, '_call_llm_json', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_json
        
        sources = [Source(title="Test", url="http://test.com", snippet="Snippet")]
        avg_score, reasoning, components = await service.generate_forecast_with_reasoning("Test Question", sources)
        
        assert avg_score == (0.8 + (1 - 0.2) + 0.7 + 0.9) / 4
        assert "Mirror: High mirror confidence" in reasoning
        assert components.mirror.score == 0.8
        assert components.noise.score == 0.2

@pytest.mark.asyncio
async def test_structured_parsing_failure():
    service = IntelligenceService()
    
    with patch.object(IntelligenceService, '_call_llm_json', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("Parsing error")
        
        sources = []
        avg_score, reasoning, components = await service.generate_forecast_with_reasoning("Test Question", sources)
        
        assert avg_score == 0.5
        assert "Error: Parsing error" in reasoning
        assert components.mirror.score == 0.5
