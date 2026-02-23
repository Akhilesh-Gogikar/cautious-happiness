import pytest
import json
from unittest.mock import AsyncMock, patch
from app.domain.intelligence.swarm import GeopoliticalAgent, SupplyChainAgent, DerivativesFlowAgent, IntelligenceDirectorate
from app.models import Source

@pytest.mark.asyncio
async def test_geopolitical_agent_analyze():
    with patch('app.core.ai_client.ai_client.generate', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "Geopolitical reasoning. Impact: 0.8"
        agent = GeopoliticalAgent()
        report = await agent.analyze("Test Question", [Source(title="T", url="U", snippet="S")])
        assert "Geopolitical reasoning" in report
        mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_directorate_run_swarm():
    with patch('app.core.ai_client.ai_client.generate', new_callable=AsyncMock) as mock_generate, \
         patch('app.core.ai_client.ai_client.generate_json', new_callable=AsyncMock) as mock_generate_json:
        
        mock_generate.return_value = "Agent report"
        mock_generate_json.return_value = {
            "mirror": {"score": 0.8, "reasoning": "G-Consensus"},
            "noise": {"score": 0.2, "reasoning": "S-Consensus"},
            "divergence": {"score": 0.7, "reasoning": "D-Consensus"},
            "algo": {"score": 0.9, "reasoning": "F-Consensus"}
        }
        
        directorate = IntelligenceDirectorate()
        avg_score, reasoning, analysis = await directorate.run_swarm("Test Question", [])
        
        # (0.8 + (1-0.2) + 0.7 + 0.9) / 4 = (0.8 + 0.8 + 0.7 + 0.9) / 4 = 3.2 / 4 = 0.8
        assert avg_score == 0.8
        assert "G-Consensus" in reasoning
        assert analysis.mirror.score == 0.8
