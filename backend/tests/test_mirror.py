import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.mirror.service import MirrorService
from app.mirror.models import Competitor, AnalysisResult

@pytest.mark.asyncio
async def test_get_competitors():
    service = MirrorService()
    competitors = await service.get_competitors()
    assert len(competitors) > 0
    assert isinstance(competitors[0], Competitor)
    assert competitors[0].id == "comp_citadel_commodity"

@pytest.mark.asyncio
async def test_analyze_target_mocked():
    # Mock DDGS and httpx
    with patch('app.mirror.service.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        # Mock standard ddgs.text to return a list
        # Note: In service we use asyncio.to_thread(self.ddgs.text ...)
        # So we need to ensure the mock passed to to_thread works.
        # However, asyncio.to_thread executes the function in a thread.
        # It's easier to patch 'app.mirror.service.asyncio.to_thread' or just patch the method.
        
        # Let's patch the internal _search_intelligence and _analyze_with_llm for a unit test of the orchestrator
        service = MirrorService()
        
        service._search_intelligence = AsyncMock(return_value=[])
        service._analyze_with_llm = AsyncMock(return_value=(0.8, 0.9, "Bullish summary", ["Buy", "Long"]))
        
        result = await service.analyze_target("Crude Oil", "oil_1")
        
        assert isinstance(result, AnalysisResult)
        assert result.sentiment_score == 0.8
        assert result.crowd_conviction == 0.9
        assert result.summary == "Bullish summary"
