import pytest
from app.services.kelly import SlippageAwareKellyEngine

def test_vwap_calculation():
    engine = SlippageAwareKellyEngine()
    order_book = [
        {"price": 0.80, "size": 100},
        {"price": 0.90, "size": 100}
    ]
    
    # Fill exactly first level
    assert engine._calculate_vwap(100, order_book) == 0.80
    
    # Fill both levels
    # (100*0.8 + 100*0.9)/200 = 170/200 = 0.85
    assert engine._calculate_vwap(200, order_book) == 0.85
    
    # Partial fill
    # (100*0.8 + 50*0.9)/150 = (80+45)/150 = 125/150 = 0.8333
    assert round(engine._calculate_vwap(150, order_book), 4) == 0.8333

def test_kelly_sizing():
    engine = SlippageAwareKellyEngine()
    order_book = [
        {"price": 0.50, "size": 1000}
    ]
    
    # Model prob > price -> Edge exists
    result = engine.calculate_optimal_size(
        model_probability=0.7,
        order_book=order_book,
        bankroll=1000
    )
    
    assert result["optimal_size"] > 0
    assert result["expected_vwap"] == 0.50
    # Kelly: (0.7 - 0.5) / (1 - 0.5) = 0.2 / 0.5 = 0.4
    # Max EV found at bankroll * fraction? The engine walks by steps.
    assert result["kelly_fraction"] == pytest.approx(0.4)

def test_kelly_no_edge():
    engine = SlippageAwareKellyEngine()
    order_book = [{"price": 0.80, "size": 1000}]
    
    # Model prob < price -> No edge
    result = engine.calculate_optimal_size(
        model_probability=0.7,
        order_book=order_book,
        bankroll=1000
    )
    
    assert result["optimal_size"] == 0
    assert result["expected_value"] == -1.0
