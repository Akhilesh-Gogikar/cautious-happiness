import pytest
from unittest.mock import MagicMock, patch
from app.arbitrage import ArbitrageEngine
from app.models import ArbitrageOpportunity

@pytest.mark.asyncio
async def test_find_opportunities_mocked():
    # Mock data for Kalshi
    mock_kalshi_data = [
        {
            "ticker": "FED-CUT-2025-01-01",
            "title": "Will the Fed cut rates in January 2025?",
            "yes_ask": 45,
            "no_ask": 55,
            "close_time": "2025-01-01T00:00:00Z"
        }
    ]
    
    # Mock data for AlphaSignals
    mock_poly_data = [
        {
            "condition_id": "0xpoly1",
            "question": "Will the Federal Reserve cut interest rates in January 2025?",
            "active": True,
            "tokens": [
                {"outcome": "Yes", "price": "0.40"},
                {"outcome": "No", "price": "0.60"}
            ]
        }
    ]

    engine = ArbitrageEngine()
    
    with patch.object(engine.kalshi, 'get_active_markets', return_value=mock_kalshi_data):
        with patch.object(engine.poly, 'get_markets', return_value={'data': mock_poly_data}):
            opportunities = await engine.find_opportunities(min_discrepancy=0.01)
            
            assert len(opportunities) == 1
            opp = opportunities[0]
            assert opp.market_name == "Will the Fed cut rates in January 2025?"
            assert opp.polymarket_price == 0.40
            assert opp.kalshi_price == 0.45
            assert abs(opp.discrepancy - 0.05) < 0.001

@pytest.mark.asyncio
async def test_find_opportunities_no_match():
    mock_kalshi_data = [
        {"ticker": "K1", "title": "Totally Different Event", "yes_ask": 50}
    ]
    mock_poly_data = [
        {
            "condition_id": "P1",
            "question": "Some Other Topic",
            "active": True,
            "tokens": [{"outcome": "Yes", "price": "0.50"}]
        }
    ]

    engine = ArbitrageEngine()
    
    with patch.object(engine.kalshi, 'get_active_markets', return_value=mock_kalshi_data):
        with patch.object(engine.poly, 'get_markets', return_value={'data': mock_poly_data}):
            opportunities = await engine.find_opportunities(min_discrepancy=0.01)
            assert len(opportunities) == 0
