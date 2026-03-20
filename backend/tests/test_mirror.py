import asyncio
from unittest.mock import AsyncMock, patch

from app.intelligence.application.mirror import MirrorService
from app.mirror.models import AnalysisResult, Competitor, Source


def test_get_competitors():
    service = MirrorService()
    competitors = asyncio.run(service.get_competitors())
    assert len(competitors) > 0
    assert isinstance(competitors[0], Competitor)
    assert competitors[0].id == "comp_citadel_commodity"


def test_analyze_target_includes_sources_and_llm_summary():
    sources = [
        Source(
            id="src_1",
            url="https://example.com/story",
            domain="example.com",
            title="Crowd chases refinery outage narrative",
            snippet="Participants expect tighter inventories in the Atlantic basin.",
        )
    ]
    service = MirrorService()
    service._search_intelligence = AsyncMock(return_value=sources)

    with patch(
        "app.intelligence.application.mirror.generate_text",
        new=AsyncMock(
            return_value='{"sentiment_score": 0.8, "crowd_conviction": 0.9, "summary": "Bullish summary", "key_phrases": ["Buy", "Long"]}'
        ),
    ):
        result = asyncio.run(service.analyze_target("Crude Oil", "oil_1"))

    assert isinstance(result, AnalysisResult)
    assert result.sentiment_score == 0.8
    assert result.crowd_conviction == 0.9
    assert result.summary == "Bullish summary"
    assert result.sources == sources
    assert result.analysis_status == "completed"


def test_analyze_target_marks_no_sources_without_llm_call():
    service = MirrorService()
    service._search_intelligence = AsyncMock(return_value=[])

    result = asyncio.run(service.analyze_target("Crude Oil", "oil_1"))

    assert result.sources == []
    assert result.analysis_status == "no_sources"
    assert result.summary == "No intelligence found."
