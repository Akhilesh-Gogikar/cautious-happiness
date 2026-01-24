"""
Unit tests for AI Agent Suite.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ============================================================================
# AGENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_sentiment_spy_agent():
    """Test that SentimentSpy agent properly analyzes sentiment."""
    from app.agents.sentiment_spy import SentimentSpyAgent
    
    agent = SentimentSpyAgent()
    
    # Mock the aggregators
    mock_source = MagicMock()
    mock_source.snippet = "Bitcoin is bullish today!"
    
    with patch.object(agent.news_aggregator, 'fetch_all', new_callable=AsyncMock) as mock_news, \
         patch.object(agent.social_aggregator, 'fetch_all', new_callable=AsyncMock) as mock_social, \
         patch.object(agent.sentiment_detector, 'detect_hype_and_manipulation') as mock_sentiment:
        
        mock_news.return_value = [mock_source]
        mock_social.return_value = [mock_source]
        mock_sentiment.return_value = {
            "sentiment_score": 0.75,
            "hype_score": 0.6,
            "summary": "Positive market sentiment"
        }
        
        result = await agent.execute({"query": "bitcoin price"})
        
        assert result["agent"] == "Sentiment-Spy"
        assert result["sentiment_score"] == 0.75
        assert result["hype_score"] == 0.6
        assert agent.status == "COMPLETED"


@pytest.mark.asyncio
async def test_risk_guard_agent():
    """Test that RiskGuard agent properly assesses risk."""
    from app.agents.risk_guard import RiskGuardAgent
    
    agent = RiskGuardAgent()
    
    result = await agent.execute({
        "query": "Will Bitcoin hit 100k?",
        "probability": 0.7,
        "portfolio": []
    })
    
    assert result["agent"] == "Risk-Guard"
    assert "verdict" in result
    assert result["verdict"] in ["APPROVED", "REJECTED"]
    assert agent.status == "COMPLETED"


@pytest.mark.asyncio
async def test_trade_executor_agent():
    """Test that TradeExecutor agent properly calculates execution."""
    from app.agents.trade_executor import TradeExecutorAgent
    
    agent = TradeExecutorAgent()
    
    result = await agent.execute({
        "query": "Will Biden win 2024?",
        "probability": 0.55
    })
    
    assert result["agent"] == "Trade-Executor"
    assert "size_usd" in result
    assert "vwap" in result
    assert agent.status == "COMPLETED"


@pytest.mark.asyncio
async def test_orchestrator_coordination():
    """Test that the Orchestrator properly coordinates all agents."""
    from app.agents.orchestrator import StrategyArchitectAgent
    
    orchestrator = StrategyArchitectAgent()
    
    # Mock the individual agents
    with patch.object(orchestrator.macro, 'execute', new_callable=AsyncMock) as mock_macro, \
         patch.object(orchestrator.alpha, 'execute', new_callable=AsyncMock) as mock_alpha, \
         patch.object(orchestrator.sentiment, 'execute', new_callable=AsyncMock) as mock_sentiment, \
         patch.object(orchestrator.risk, 'execute', new_callable=AsyncMock) as mock_risk, \
         patch.object(orchestrator.executor, 'execute', new_callable=AsyncMock) as mock_executor:
        
        mock_macro.return_value = {"agent": "Macro-Sentinel", "summary": "Stable momentum"}
        mock_alpha.return_value = {"agent": "Alpha-Hunter", "signal": "BULLISH"}
        mock_sentiment.return_value = {"agent": "Sentiment-Spy", "sentiment_score": 0.7}
        mock_risk.return_value = {"agent": "Risk-Guard", "verdict": "APPROVED"}
        mock_executor.return_value = {"agent": "Trade-Executor", "size_usd": 100.0}
        
        result = await orchestrator.coordinate("test query", probability=0.6)
        
        assert "consensus" in result
        assert "agent_results" in result
        assert len(result["agent_results"]) == 5


@pytest.mark.asyncio
async def test_orchestrator_risk_rejection():
    """Test that Orchestrator respects risk rejection."""
    from app.agents.orchestrator import StrategyArchitectAgent
    
    orchestrator = StrategyArchitectAgent()
    
    with patch.object(orchestrator.macro, 'execute', new_callable=AsyncMock) as mock_macro, \
         patch.object(orchestrator.alpha, 'execute', new_callable=AsyncMock) as mock_alpha, \
         patch.object(orchestrator.sentiment, 'execute', new_callable=AsyncMock) as mock_sentiment, \
         patch.object(orchestrator.risk, 'execute', new_callable=AsyncMock) as mock_risk, \
         patch.object(orchestrator.executor, 'execute', new_callable=AsyncMock) as mock_executor:
        
        mock_macro.return_value = {"agent": "Macro-Sentinel", "summary": "Stable"}
        mock_alpha.return_value = {"agent": "Alpha-Hunter", "signal": "BULLISH"}
        mock_sentiment.return_value = {"agent": "Sentiment-Spy", "sentiment_score": 0.8}
        mock_risk.return_value = {"agent": "Risk-Guard", "verdict": "REJECTED"}
        mock_executor.return_value = {"agent": "Trade-Executor", "size_usd": 0}
        
        result = await orchestrator.coordinate("risky trade", probability=0.9)
        
        assert result["consensus"] == "BLOCKED_BY_RISK"


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================

def test_agent_registry():
    """Test that agents are properly registered."""
    from app.agents.registry import registry
    
    agents = registry.list_agents()
    
    # After orchestrator init, we should have at least 5 agents
    assert len(agents) >= 5
    
    agent_names = [a["name"] for a in agents]
    assert "Macro-Sentinel" in agent_names
    assert "Alpha-Hunter" in agent_names
