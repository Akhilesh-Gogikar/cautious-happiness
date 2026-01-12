
import pytest
import asyncio
from app.execution import SmartOrderRouter
from app.market_client import MockMarketClient
from app.models import ExecutionParameters, ExecutionStrategy, OrderBook, OrderBookLevel

class MockClientWithLogs(MockMarketClient):
    def __init__(self):
        self.orders = []
        
    def get_order_book(self, market_id: str) -> OrderBook:
        # Default empty book for basic tests unless overridden
        # We need at least some price for _get_execution_price_estimate to default to 0.5 or work
        return OrderBook(asks=[OrderBookLevel(price=0.5, amount=1000)], bids=[])

    def place_order(self, market_id: str, size_usd: float, side: str = "BUY") -> bool:
        self.orders.append({"market_id": market_id, "size": size_usd, "side": side})
        return True

class MockDynamicClient(MockClientWithLogs):
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.scenario_books = []

    def get_order_book(self, market_id: str) -> OrderBook:
        if not self.scenario_books:
            return super().get_order_book(market_id)
        idx = min(self.call_count, len(self.scenario_books) - 1)
        self.call_count += 1
        return self.scenario_books[idx]

@pytest.mark.asyncio
async def test_sor_execution_liquidity_snipe():
    client = MockDynamicClient()
    sor = SmartOrderRouter(client)
    
    # Scene 1: Low liquidity (Price 0.50, Amt 100 -> Depth $50)
    low_liq = OrderBook(asks=[OrderBookLevel(price=0.50, amount=100)], bids=[]) 
    
    # Scene 2: High liquidity (Price 0.50, Amt 5000 -> Depth $2500)
    high_liq = OrderBook(asks=[OrderBookLevel(price=0.50, amount=5000)], bids=[])
    
    # Sequence: Low -> Low -> High
    client.scenario_books = [low_liq, low_liq, high_liq]
    
    params = ExecutionParameters(
        strategy=ExecutionStrategy.LIQUIDITY_SNIPE,
        min_depth_usd=1000.0,
        interval_seconds=0 # Fast loop check
    )
    
    # We want to buy 200 shares.
    # The snippet will wait until high_liq appears.
    # Cost = 200 * 0.50 = $100.
    
    await sor.execute_strategy("test_market", 200, params)
    
    assert len(client.orders) == 1
    # 200 shares * 0.50 price = 100 USD
    assert client.orders[0]["size"] == 100.0
    assert client.orders[0]["side"] == "BUY"
    
    # Expect 3 calls: 1(low), 2(low), 3(high -> triggering execution)
    assert client.call_count >= 3

@pytest.mark.asyncio
async def test_sor_execution_twap():
    client = MockClientWithLogs()
    sor = SmartOrderRouter(client)
    
    # Return a dummy book so price estimate works (0.5 price)
    book = OrderBook(asks=[OrderBookLevel(price=0.5, amount=1000)], bids=[])
    client.get_order_book = lambda mid: book
    
    params = ExecutionParameters(
        strategy=ExecutionStrategy.TWAP,
        duration_minutes=0.05, # 3 seconds total
        interval_seconds=1 # 3 chunks
    )
    
    await sor.execute_strategy("test_market", 60, params) # 60 shares
    
    assert len(client.orders) == 3
    # 60 shares / 3 = 20 shares per chunk.
    # 20 shares * 0.5 price = 10 USD
    assert client.orders[0]["size"] == 10.0

@pytest.mark.asyncio
async def test_sor_execution_iceberg():
    client = MockClientWithLogs()
    sor = SmartOrderRouter(client)
    
    params = ExecutionParameters(
        strategy=ExecutionStrategy.ICEBERG,
        display_size_shares=20
    )
    
    # 50 shares, 20 display = 20, 20, 10
    # Iceberg sleep is hardcoded to 2s in execution.py
    # We should override it? 
    # Or just wait 6s total. Acceptable.
    await sor.execute_strategy("test_market", 50, params)
    assert len(client.orders) == 3
    # 20 shares * 0.5 = 10 USD
    assert client.orders[0]["size"] == 10.0
    # 10 shares * 0.5 = 5 USD
    assert client.orders[2]["size"] == 5.0
