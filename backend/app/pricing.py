import math
import logging

logger = logging.getLogger(__name__)

class PriceConverter:
    """
    Translates LLM confidence scores into bid/ask limits.
    """
    
    @staticmethod
    def convert_to_limits(probability: float, spread: float = 0.02) -> dict:
        """
        Translates a probability (0.0 to 1.0) into a bid and ask price.
        
        Args:
            probability: The estimated probability of the event.
            spread: The desired spread between bid and ask (default: 0.02).
            
        Returns:
            A dictionary with 'bid' and 'ask' prices.
        """
        # Ensure probability is within [0, 1]
        probability = max(0.0, min(1.0, probability))
        
        half_spread = spread / 2.0
        
        bid = probability - half_spread
        ask = probability + half_spread
        
        # Ensure limits are within realistic prediction market bounds [0.01, 0.99]
        # Most markets don't allow 0 or 1 limit orders
        bid = max(0.01, min(0.99, bid))
        ask = max(0.01, min(0.99, ask))
        
        # Round to 2 decimal places as is standard for prediction markets
        return {
            "bid": round(bid, 2),
            "ask": round(ask, 2)
        }
