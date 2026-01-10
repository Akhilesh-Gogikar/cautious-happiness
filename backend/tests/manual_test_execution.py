from app.execution import SlippageAwareKelly
from app.market_client import MockMarketClient

def test_execution_logic():
    print("Testing Slippage-Aware Execution...")
    
    # Setup
    kelly = SlippageAwareKelly(bankroll=10000.0) # $10k bankroll
    client = MockMarketClient()
    
    # Scenario: High Probability (0.8) vs Market Price starting ~0.4
    # Should bet heavily.
    
    book = client.get_order_book("test")
    probability = 0.8
    
    print(f"Scenario: Probability {probability} vs Market Top Ask {book.asks[0].price}")
    
    size_usd, shares, vwap = kelly.optimal_allocation(probability, book)
    
    print(f"Result: Invest ${size_usd:.2f} to buy {shares:.2f} shares @ VWAP {vwap:.3f}")
    
    assert size_usd > 0, "Should have found a valid bet size"
    assert vwap > book.asks[0].price, "VWAP should reflect slippage (higher than best ask)"
    
    # Scenario: Low Probability (0.3) vs Market Price ~0.4
    # Should not bet.
    
    prob_low = 0.3
    size_low, _, _ = kelly.optimal_allocation(prob_low, book)
    print(f"Scenario Low Prob ({prob_low}): Size ${size_low}")
    assert size_low == 0, "Should not bet on negative edge"
    
    print("Test Passed!")

if __name__ == "__main__":
    test_execution_logic()
