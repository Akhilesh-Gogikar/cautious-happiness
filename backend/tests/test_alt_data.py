import pytest
from app.alt_data_client import AlternativeDataClient, AlternativeSignal

def test_alt_data_keywords():
    client = AlternativeDataClient()
    
    # Test Satellite (Agriculture)
    signals = client.get_signals_for_market("Will corn yields in Brazil exceed expectations?")
    assert len(signals) > 0
    assert signals[0].source_type == "SATELLITE"
    assert "Vegetation Index" in signals[0].signal_name
    
    # Test Shipping
    signals = client.get_signals_for_market("Are shipping costs rising due to port congestion?")
    assert len(signals) > 0
    assert signals[0].source_type == "SHIPPING"
    assert "Port Congestion" in signals[0].signal_name
    
    # Test Flight
    signals = client.get_signals_for_market("Will Company X announce a merger after the CEO travels to NY?")
    assert len(signals) > 0
    assert signals[0].source_type == "FLIGHT"
    assert "Corporate Jet" in signals[0].signal_name
    
    # Test General/Fallback
    signals = client.get_signals_for_market("Will the Fed raise rates?")
    # Should either return generic or specific macro if implemented, or empty/generic
    # Based on current implementation, it checks key words. "Fed" might not match generic ones, 
    # but the client adds a "GENERAL" signal if no others match.
    assert len(signals) > 0
    assert signals[0].source_type == "GENERAL"

def test_signal_impact():
    client = AlternativeDataClient()
    signals = client.get_signals_for_market("corn yield")
    # code logic: impact="BEARISH" if "yield" in q else "BULLISH"
    # Wait, simple logic in mock: if "yield" in q -> BEARISH? (High yield = lower price?)
    # Let's check the code: 'impact="BEARISH" if "yield" in q else "BULLISH"'
    assert signals[0].impact == "BEARISH"
