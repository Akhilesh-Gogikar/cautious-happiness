import pytest
from app.execution import SlippageAwareKelly
from app.models import OrderBook, OrderBookLevel

class TestSlippageAwareKelly:
    def test_optimal_allocation_flat_book(self):
        """
        Test with a flat order book (infinite liquidity at one price).
        Kelly should match standard formula.
        """
        kelly = SlippageAwareKelly(bankroll=1000.0, max_bankroll_fraction=1.0)
        
        # Price 0.5, Size infinity
        asks = [OrderBookLevel(price=0.5, amount=1000000)]
        book = OrderBook(asks=asks, bids=[])
        
        # Prob = 0.6. Price = 0.5.
        # f = (p - q) / (1 - b) ??? No.
        # Patent formula: f = (P_model - P_vwap) / (1 - P_vwap)
        # f = (0.6 - 0.5) / (1 - 0.5) = 0.1 / 0.5 = 0.2
        # Bet size = 0.2 * 1000 = 200
        
        size_usd, shares, vwap = kelly.optimal_allocation(0.6, book)
        
        print(f"Flat Book: Size=${size_usd}, Shares={shares}, VWAP={vwap}")
        
        assert size_usd == pytest.approx(200.0, rel=0.1)
        assert vwap == pytest.approx(0.5)

    def test_optimal_allocation_slippage(self):
        """
        Test with a thin order book where price rises quickly.
        Allocation should be smaller than flat book.
        """
        kelly = SlippageAwareKelly(bankroll=1000.0, max_bankroll_fraction=1.0)
        
        # Price 0.5 for $10, then 0.55 for $10, then 0.60 for $1000
        asks = [
            OrderBookLevel(price=0.50, amount=20), # $10 worth
            OrderBookLevel(price=0.55, amount=18), # ~$10 worth
            OrderBookLevel(price=0.60, amount=1000)
        ]
        book = OrderBook(asks=asks, bids=[])
        
        # Prob = 0.6.
        # If we bet $200 like before:
        # First $10 @ 0.50
        # Next $10 @ 0.55
        # Remaining $180 @ 0.60
        # VWAP would be close to 0.60.
        # Kelly at 0.60 price with 0.6 prob is 0.
        # So it should stop much earlier.
        
        size_usd, shares, vwap = kelly.optimal_allocation(0.6, book)
        
        print(f"Steep Book: Size=${size_usd}, Shares={shares}, VWAP={vwap}")
        
        assert size_usd < 100.0 # Should be significantly less than 200
        assert size_usd > 5.0   # Should still bet something
        assert vwap < 0.60      # Shouldn't buy at 0.60 where edge is 0

    def test_negative_ev_no_bet(self):
        """
        Test where Price > Prob. Should be 0.
        """
        kelly = SlippageAwareKelly(bankroll=1000.0)
        asks = [OrderBookLevel(price=0.7, amount=1000)]
        book = OrderBook(asks=asks, bids=[])
        
        size_usd, _, _ = kelly.optimal_allocation(0.6, book)
        assert size_usd == 0.0

class TestForecasterCriticEngine:
    """
    Test the new Calibration logic.
    """
    def test_calibration_check(self):
        from app.engine import ForecasterCriticEngine
        # Mocking init to avoid connecting to services
        engine = ForecasterCriticEngine()
        
        # 1. Test Moderate Probability (No Change)
        prob = engine._apply_calibration(0.6, "Reasoning")
        assert prob == 0.6
        
        # 2. Test Extreme Prob WITHOUT Strong Evidence (Should Dampen)
        # 0.9 -> 0.5 + (0.9 - 0.5)*0.5 = 0.5 + 0.2 = 0.7
        prob = engine._apply_calibration(0.9, "I think yes.")
        assert prob == pytest.approx(0.7)
        
        # 3. Test Extreme Prob WITH Strong Evidence (No Change)
        prob = engine._apply_calibration(0.95, "This is guaranteed mathematically certain.")
        assert prob == 0.95


