import os
import re
from typing import List, Dict, Any, Tuple

class SentimentDetector:
    """
    NLP module to detect sentiment and 'irrational exuberance' (hype).
    Uses a combination of keyword analysis and emotional intensity heuristics.
    """
    
    # Keywords associated with "Irrational Exuberance" and FOMO
    HYPE_KEYWORDS = [
        "to the moon", "lfg", "moon", "rocket", "100x", "1000x", "gem", "ape",
        "parabolic", "generational wealth", "don't miss out", "fomo", "huge",
        "insane", "massive", "bullishaf", "diamond hands", "hodl", "wagmi"
    ]
    
    # Keywords associated with potential market manipulation or coordinated pumps
    MANIPULATION_KEYWORDS = [
        "pump", "pumping", "dump", "coordinated", "signal", "buy now", 
        "short squeeze", "gamma squeeze", "everyone buy", "raiding"
    ]

    def __init__(self):
        # In a production environment, this would use a transformer model (e.g., RoBERTa-base-sentiment)
        # or an LLM call. For this implementation, we use a robust heuristic-based approach
        # that can be easily extended.
        pass

    def analyze_sentiment(self, text: str) -> float:
        """
        Returns a sentiment score from 0.0 (very bearish) to 1.0 (very bullish).
        0.5 is neutral.
        """
        text = text.lower()
        
        bullish_words = ["up", "buy", "bull", "growth", "high", "positive", "win", "gain", "profit", "surge", "breakout"]
        bearish_words = ["down", "sell", "bear", "drop", "low", "negative", "loss", "crash", "dump", "plunge", "decline"]
        
        bull_count = sum(1 for word in bullish_words if word in text)
        bear_count = sum(1 for word in bearish_words if word in text)
        
        total = bull_count + bear_count
        if total == 0:
            return 0.5
            
        # Basic scoring: shift 0.5 center by the ratio
        score = 0.5 + (bull_count - bear_count) / (total * 2)
        return max(0.0, min(1.0, score))

    def detect_hype_and_manipulation(self, snippets: List[str]) -> Dict[str, Any]:
        """
        Analyzes multiple text snippets to detect irrational exuberance and manipulation.
        """
        total_hype_score = 0.0
        manipulation_signals = []
        
        combined_text = " ".join(snippets).lower()
        
        # 1. Keyword Density for Hype
        hype_matches = [word for word in self.HYPE_KEYWORDS if word in combined_text]
        hype_density = len(hype_matches) / len(self.HYPE_KEYWORDS)
        
        # 2. Emotional Intensity (Exclamation points, CAPS)
        exclamation_count = combined_text.count("!")
        words = " ".join(snippets).split()
        caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
        caps_ratio = caps_words / (len(words) + 1)
        
        # 3. Manipulation Detection
        manip_matches = [word for word in self.MANIPULATION_KEYWORDS if word in combined_text]
        if manip_matches:
            manipulation_signals.extend(list(set(manip_matches)))
            
        # Composite Hype Score
        # Keywords are the strongest signal of "irrational exuberance"
        keyword_score = min(len(hype_matches) / 3, 1.0) # 3 keywords already high hype
        
        hype_score = (keyword_score * 0.7) + (min(exclamation_count / 5, 1.0) * 0.2) + (min(caps_ratio * 4, 1.0) * 0.1)
        
        # If manipulation detected, boost hype score as it often correlates with artificial hype
        if manipulation_signals:
            hype_score = min(1.0, hype_score + 0.15)

        return {
            "hype_score": round(hype_score, 3),
            "sentiment_score": self.analyze_sentiment(combined_text),
            "manipulation_signals": manipulation_signals,
            "irrational_exuberance": hype_score > 0.7,
            "summary": self._generate_discouse_summary(hype_score, manipulation_signals)
        }

    def _generate_discouse_summary(self, hype_score: float, signals: List[str]) -> str:
        if hype_score > 0.8:
            summary = "EXTREME HYPE: Discourse shows signs of extreme irrational exuberance."
        elif hype_score > 0.5:
            summary = "MODERATE HYPE: Active social interest with some emotional weighting."
        else:
            summary = "NORMAL: Public discourse appears grounded or disinterested."
            
        if signals:
            summary += f" Potential manipulation signals detected: {', '.join(signals)}."
            
        return summary
