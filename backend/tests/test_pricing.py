import pytest
from app.pricing import PriceConverter

def test_convert_to_limits_standard():
    # 75% confidence -> Bid $0.74 / Ask $0.76 (Default 0.02 spread)
    result = PriceConverter.convert_to_limits(0.75)
    assert result == {"bid": 0.74, "ask": 0.76}

def test_convert_to_limits_mid():
    # 50% confidence -> Bid $0.49 / Ask $0.51
    result = PriceConverter.convert_to_limits(0.50)
    assert result == {"bid": 0.49, "ask": 0.51}

def test_convert_to_limits_high_edge():
    # 99% confidence -> should stay within [0.01, 0.99]
    # 0.99 - 0.01 = 0.98, 0.99 + 0.01 = 1.00 -> 0.99
    result = PriceConverter.convert_to_limits(0.99)
    assert result == {"bid": 0.98, "ask": 0.99}

def test_convert_to_limits_low_edge():
    # 1% confidence -> should stay within [0.01, 0.99]
    # 0.01 - 0.01 = 0.00 -> 0.01, 0.01 + 0.01 = 0.02
    result = PriceConverter.convert_to_limits(0.01)
    assert result == {"bid": 0.01, "ask": 0.02}

def test_convert_to_limits_custom_spread():
    # 75% confidence with 0.10 spread
    result = PriceConverter.convert_to_limits(0.75, spread=0.10)
    assert result == {"bid": 0.70, "ask": 0.80}

def test_convert_to_limits_zero_prob():
    result = PriceConverter.convert_to_limits(0.0)
    assert result == {"bid": 0.01, "ask": 0.01}

def test_convert_to_limits_one_prob():
    result = PriceConverter.convert_to_limits(1.0)
    assert result == {"bid": 0.99, "ask": 0.99}
