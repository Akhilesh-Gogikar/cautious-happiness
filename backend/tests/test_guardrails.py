import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from app.engine import ForecasterCriticEngine
# Import types for mocking if needed, but we trust the mocks.

@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('app.engine.VectorDBClient'), \
         patch('app.engine.NewsIngestor'), \
         patch('app.engine.SentimentDetector'), \
         patch('app.engine.AlternativeDataClient'), \
         patch('app.engine.DataAggregator'), \
         patch('app.engine.TwitterConnector'), \
         patch('app.engine.RedditConnector'), \
         patch('app.engine.DiscordConnector'), \
         patch('app.engine.ReutersConnector'), \
         patch('app.engine.APNewsConnector'), \
         patch('app.engine.BloombergConnector'), \
         patch('app.engine.NOAAConnector'), \
         patch('app.engine.CSPANConnector'):
        yield

@pytest.mark.asyncio
async def test_extract_claims():
    """
    Test extraction of claims from reasoning.
    """
    # Patch DDGS before Init
    with patch('app.engine.DDGS') as MockDDGS:
        engine = ForecasterCriticEngine()
    
    # Mock LLM to return a JSON list of claims
    with patch.object(engine, '_call_llm', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '["Inflation is 3.2%", "Fed rates are 5.5%"]'
        
        claims = await engine.extract_claims("Some reasoning text where inflation is mentioned.")
        
        assert len(claims) == 2
        assert "Inflation is 3.2%" in claims
        assert "Fed rates are 5.5%" in claims

@pytest.mark.asyncio
async def test_verify_claims_pass():
    """
    Test successful verification.
    """
    # Patch DDGS before Init so self.ddgs is the mock
    with patch('app.engine.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        # When text() is called, return results
        mock_ddgs_instance.text.return_value = [{'body': 'Latest CPI report shows inflation at 3.2%.'}]
        
        engine = ForecasterCriticEngine()
        
        # Mock LLM verdict
        with patch.object(engine, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "TRUE: Evidence confirms inflation is 3.2%."
            
            report, passed = await engine.verify_claims(["Inflation is 3.2%"])
            
            assert passed is True
            assert "TRUE" in report
            assert "inflation is 3.2%" in report

@pytest.mark.asyncio
async def test_verify_claims_fail():
    """
    Test verification failure.
    """
    with patch('app.engine.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [{'body': 'Inflation has dropped to 2.5%.'}]
        
        engine = ForecasterCriticEngine()
        
        # Mock LLM verdict
        with patch.object(engine, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "FALSE: Evidence suggests inflation is 2.5%, not 3.2%."
            
            report, passed = await engine.verify_claims(["Inflation is 3.2%"])
            
            assert passed is False
            assert "FALSE" in report

@pytest.mark.asyncio
async def test_integration_run_analysis_with_verification_fail():
    """
    Test the full pipeline adjustment on verification failure.
    """
    with patch('app.engine.DDGS'):
        engine = ForecasterCriticEngine()
    
    # Mock methods to isolate guardrail logic
    engine.search_market_news = AsyncMock(return_value=[])
    engine.aggregator.fetch_all = AsyncMock(return_value=[])
    engine.alt_data_client.get_signals_for_market = MagicMock(return_value=[])
    engine.social_aggregator.fetch_all = AsyncMock(return_value=[])
    engine.classify_market = AsyncMock(return_value="Economics")
    engine.sentiment_detector.detect_hype_and_manipulation = MagicMock(return_value={
        "hype_score": 0.0,
        "sentiment_score": 0.5,
        "summary": "Neutral"
    })
    engine.risk_engine.check_portfolio_risk = MagicMock(return_value=[])
    
    async def mock_gen(*args, **kwargs):
        print(f"MOCK GEN ARGS: {args} KWARGS: {kwargs}")
        return 0.8, "Inflation is soaring."
    engine.generate_forecast_with_reasoning = mock_gen

    async def mock_critique(*args, **kwargs):
        print(f"MOCK CRITIQUE ARGS: {args}")
        # Adjust index if self is passed
        p = args[2] 
        return "Critique", p
    engine.critique_forecast = mock_critique

    engine.extract_claims = AsyncMock(return_value=["Inflation soaring"])
    engine.verify_claims = AsyncMock(return_value=("Report: FALSE", False))
    
    print(">>> STARTING RUN_ANALYSIS")
    result = await engine.run_analysis("Will inflation rise?")
    print(f">>> FINISHED RUN_ANALYSIS. Forecast: {result.initial_forecast}")
    
    # Initial was 0.8. Failed verification should penalize it.
    # Logic: max(0.5, 0.8 - 0.2) = 0.6
    assert abs(result.initial_forecast - 0.6) < 1e-9
    assert "Probability adjusted due to failed verification" in result.reasoning
    assert "Report: FALSE" in result.verification_report
