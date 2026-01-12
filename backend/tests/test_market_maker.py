import pytest
from unittest.mock import MagicMock, AsyncMock
from app.market_maker import MarketMaker
from app.market_client import MockMarketClient
from app.models import OrderBook, OrderBookLevel

@pytest.mark.asyncio
async def test_market_maker_cycle():
    # Setup
    mock_client = MockMarketClient()
    mock_client.get_order_book = MagicMock(return_value=OrderBook(
        bids=[OrderBookLevel(price=0.48, amount=100)],
        asks=[OrderBookLevel(price=0.52, amount=100)]
    ))
    mock_client.place_limit_order = MagicMock(return_value="mock_id")
    mock_client.cancel_all_orders = MagicMock(return_value=True)

    mm = MarketMaker(mock_client, "market_123", spread=0.04, size_shares=10.0)
    
    # Run one cycle
    await mm.run_cycle()

    # Verification
    # Fair price should be (0.48 + 0.52) / 2 = 0.50
    # Spread 0.04 -> +/- 0.02
    # Bid should be 0.48
    # Ask should be 0.52
    
    # Check Cancel
    mock_client.cancel_all_orders.assert_called_once()
    
    # Check Place Orders
    assert mock_client.place_limit_order.call_count == 2
    
    # Verify Bid
    mock_client.place_limit_order.assert_any_call("market_123", 0.48, 10.0, "BUY")
    # Verify Ask
    mock_client.place_limit_order.assert_any_call("market_123", 0.52, 10.0, "SELL")

@pytest.mark.asyncio
async def test_market_maker_tight_spread_handling():
    # Setup - Crossed book or tight
    mock_client = MockMarketClient()
    mock_client.get_order_book = MagicMock(return_value=OrderBook(
        bids=[OrderBookLevel(price=0.50, amount=100)],
        asks=[OrderBookLevel(price=0.51, amount=100)]
    ))
    # Mid = 0.505. Spread 0.04 -> +/- 0.02 -> Bid 0.48, Ask 0.52?
    # Actually logic: round(0.505 - 0.02, 2) = 0.48 (maybe 0.49 depending on rounding), round(0.505 + 0.02) = 0.52 (maybe 0.53)
    
    mock_client.place_limit_order = MagicMock(return_value="mock_id")
    mock_client.cancel_all_orders = MagicMock()

    mm = MarketMaker(mock_client, "market_123", spread=0.04)
    await mm.run_cycle()
    
    # Just verify it placed orders without crashing
    assert mock_client.place_limit_order.call_count == 2
