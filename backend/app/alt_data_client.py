import random
from typing import List
from app.models import AlternativeSignal

class AlternativeDataClient:
    """
    Mock client for fetching alternative data signals like satellite imagery, 
    shipping logs, and flight trackers.
    """
    
    def get_signals_for_market(self, market_question: str) -> List[AlternativeSignal]:
        """
        Returns relevant alternative signals based on the market question keywords.
        """
        signals = []
        q = market_question.lower()
        
        # 1. Agricultural / Crop Yield Signals
        if any(word in q for word in ["crop", "corn", "soy", "yield", "wheat", "agriculture", "brazil", "climate"]):
            signals.append(AlternativeSignal(
                source_type="SATELLITE",
                signal_name="NDVI Vegetation Index",
                value="Above Average (0.82)",
                impact="BEARISH" if "yield" in q else "BULLISH",
                confidence=0.88,
                description="Satellite imagery of Mato Grosso shows higher than average greenness for this season, suggesting high yields."
            ))
            
        # 2. Shipping / Logistics Signals
        if any(word in q for word in ["shipping", "logistics", "vessel", "oil", "commodity", "cargo", "port"]):
            signals.append(AlternativeSignal(
                source_type="SHIPPING",
                signal_name="Port Congestion Index - Shanghai",
                value="High (45 vessels waiting)",
                impact="BEARISH",
                confidence=0.92,
                description="Real-time terrestrial AIS data shows a 15% increase in vessel waiting times at major transshipment hubs."
            ))
            
        # 3. Flight Tracker / Corporate Activity
        if any(word in q for word in ["flight", "corporate", "merger", "acquisition", "meeting", "travel"]):
            signals.append(AlternativeSignal(
                source_type="FLIGHT",
                signal_name="Corporate Jet Tracking - Omaha/NY",
                value="Abnormal Frequency (3 flights/24h)",
                impact="BULLISH",
                confidence=0.75,
                description="Detection of multiple corporate jets registered to parent companies traveling between key financial hubs."
            ))
            
        # 4. Energy / Industrial Activity
        if any(word in q for word in ["oil", "gas", "energy", "production", "inventory", "refinery"]):
             signals.append(AlternativeSignal(
                source_type="SATELLITE",
                signal_name="Infrared Refinery Flaring Analysis",
                value="Increased Activity (+12%)",
                impact="BULLISH",
                confidence=0.85,
                description="Thermal satellite monitors show increased flaring intensity in the Permian basin, indicating high production throughput."
            ))

        # Add a generic one if nothing matches
        if not signals:
            signals.append(AlternativeSignal(
                source_type="GENERAL",
                signal_name="Alternative Macro Proxy",
                value="Stable",
                impact="NEUTRAL",
                confidence=0.50,
                description="No specific non-traditional signals detected for this asset class."
            ))
            
        return signals
