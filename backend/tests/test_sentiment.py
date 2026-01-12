import pytest
from app.sentiment import SentimentDetector

def test_sentiment_analysis():
    detector = SentimentDetector()
    
    # Test Bullish
    bullish_text = "I am very bullish on this, it's a great buy and will gain value!"
    assert detector.analyze_sentiment(bullish_text) > 0.6
    
    # Test Bearish
    bearish_text = "This is a total dump, I am selling everything, it's a loss."
    assert detector.analyze_sentiment(bearish_text) < 0.4
    
    # Test Neutral
    neutral_text = "The market is stable today with no major movements."
    assert detector.analyze_sentiment(neutral_text) == 0.5

def test_hype_detection():
    detector = SentimentDetector()
    
    # Test High Hype
    hype_snippets = [
        "LFG! To the moon!!! 🚀🚀🚀",
        "DON'T MISS OUT ON THIS 100X GEM!!!",
        "WAGMI DIAMOND HANDS ONLY"
    ]
    results = detector.detect_hype_and_manipulation(hype_snippets)
    assert results["hype_score"] > 0.7
    assert results["irrational_exuberance"] is True
    
    # Test Low Hype
    low_hype_snippets = [
        "The consumer price index grew by 0.2% last month.",
        "Analysts suggest a stable outlook for the sector.",
        "Market volume remains consistent with historical averages."
    ]
    results = detector.detect_hype_and_manipulation(low_hype_snippets)
    assert results["hype_score"] < 0.4
    assert results["irrational_exuberance"] is False

def test_manipulation_detection():
    detector = SentimentDetector()
    
    # Test Manipulation Signals
    manip_snippets = [
        "Everyone buy now! This is a coordinated pump!",
        "Check out the signal in the premium group.",
        "Short squeeze incoming, raid the order book!"
    ]
    results = detector.detect_hype_and_manipulation(manip_snippets)
    assert len(results["manipulation_signals"]) > 0
    assert "pump" in results["manipulation_signals"]
    assert "signal" in results["manipulation_signals"]
