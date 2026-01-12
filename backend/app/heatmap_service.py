from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
from app.heatmap_models import (
    ProbabilitySnapshot,
    HeatmapCell,
    HeatmapData,
    DivergenceAlert,
    ProbabilityHistoryPoint,
    MarketProbabilityHistory
)

logger = logging.getLogger(__name__)

class HeatmapService:
    """
    Service for calculating and managing probability heatmap data.
    """
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.probability_history: Dict[str, List[ProbabilitySnapshot]] = {}
        
    def calculate_implied_probability(self, market_price: float) -> float:
        """
        Convert market price to implied probability.
        In prediction markets, price ≈ probability.
        
        Args:
            market_price: Current market price (0.0 to 1.0)
            
        Returns:
            Implied probability (0.0 to 1.0)
        """
        # For most prediction markets, price directly represents probability
        # Apply minor adjustments for market inefficiencies if needed
        return max(0.0, min(1.0, market_price))
    
    def calculate_divergence(self, ai_probability: float, implied_probability: float) -> tuple[float, float]:
        """
        Calculate divergence between AI and market probabilities.
        
        Args:
            ai_probability: AI model's probability estimate
            implied_probability: Market-implied probability
            
        Returns:
            Tuple of (absolute_divergence, percent_divergence)
        """
        absolute_divergence = ai_probability - implied_probability
        
        # Calculate percentage divergence
        if implied_probability > 0:
            percent_divergence = (absolute_divergence / implied_probability) * 100
        else:
            percent_divergence = 0.0
            
        return absolute_divergence, percent_divergence
    
    def calculate_color_intensity(self, divergence: float, max_divergence: float = 0.5) -> float:
        """
        Map divergence to color intensity for visualization.
        
        Args:
            divergence: Probability divergence (-1.0 to 1.0)
            max_divergence: Maximum expected divergence for normalization
            
        Returns:
            Color intensity (-1.0 to 1.0)
            Positive = AI higher than market (green)
            Negative = Market higher than AI (red)
        """
        # Normalize to -1.0 to 1.0 range
        intensity = divergence / max_divergence
        return max(-1.0, min(1.0, intensity))
    
    def track_probability_snapshot(self, snapshot: ProbabilitySnapshot):
        """
        Store a probability snapshot for historical tracking.
        
        Args:
            snapshot: ProbabilitySnapshot to store
        """
        market_id = snapshot.market_id
        
        if market_id not in self.probability_history:
            self.probability_history[market_id] = []
        
        self.probability_history[market_id].append(snapshot)
        
        # Keep only last 7 days of data
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        self.probability_history[market_id] = [
            s for s in self.probability_history[market_id]
            if s.timestamp > cutoff_time
        ]
        
        logger.info(f"Tracked probability snapshot for market {market_id}")
    
    def get_heatmap_data(
        self,
        markets: List[Dict],
        category_filter: Optional[str] = None,
        min_divergence: Optional[float] = None
    ) -> HeatmapData:
        """
        Generate heatmap data from current market states.
        
        Args:
            markets: List of market dictionaries with price and AI probability data
            category_filter: Optional category to filter by
            min_divergence: Minimum absolute divergence to include
            
        Returns:
            HeatmapData object for visualization
        """
        cells = []
        divergences = []
        
        for market in markets:
            # Apply category filter
            if category_filter and market.get('category') != category_filter:
                continue
            
            market_price = market.get('market_price', 0.5)
            ai_probability = market.get('ai_probability', 0.5)
            
            implied_prob = self.calculate_implied_probability(market_price)
            divergence, divergence_percent = self.calculate_divergence(ai_probability, implied_prob)
            
            # Apply divergence filter
            if min_divergence and abs(divergence) < min_divergence:
                continue
            
            divergences.append(divergence)
            
            # Create snapshot for tracking
            snapshot = ProbabilitySnapshot(
                market_id=market['market_id'],
                market_question=market['question'],
                category=market.get('category', 'Other'),
                timestamp=datetime.utcnow(),
                market_price=market_price,
                implied_probability=implied_prob,
                ai_probability=ai_probability,
                divergence=divergence,
                divergence_percent=divergence_percent,
                volume_24h=market.get('volume_24h'),
                liquidity_depth=market.get('liquidity_depth')
            )
            
            self.track_probability_snapshot(snapshot)
            
            # Calculate color intensity
            max_div = max(abs(d) for d in divergences) if divergences else 0.5
            color_intensity = self.calculate_color_intensity(divergence, max_div)
            
            cell = HeatmapCell(
                market_id=market['market_id'],
                market_question=market['question'],
                category=market.get('category', 'Other'),
                implied_probability=implied_prob,
                ai_probability=ai_probability,
                divergence=divergence,
                divergence_percent=divergence_percent,
                color_intensity=color_intensity,
                last_updated=datetime.utcnow(),
                confidence_score=market.get('confidence_score')
            )
            
            cells.append(cell)
        
        # Calculate statistics
        avg_divergence = sum(divergences) / len(divergences) if divergences else 0.0
        max_divergence = max(divergences) if divergences else 0.0
        min_divergence = min(divergences) if divergences else 0.0
        
        return HeatmapData(
            cells=cells,
            timestamp=datetime.utcnow(),
            total_markets=len(cells),
            avg_divergence=avg_divergence,
            max_divergence=max_divergence,
            min_divergence=min_divergence
        )
    
    def get_divergence_alerts(
        self,
        markets: List[Dict],
        high_threshold: float = 0.2,
        medium_threshold: float = 0.1
    ) -> List[DivergenceAlert]:
        """
        Generate alerts for significant probability divergences.
        
        Args:
            markets: List of market dictionaries
            high_threshold: Threshold for HIGH severity alerts
            medium_threshold: Threshold for MEDIUM severity alerts
            
        Returns:
            List of DivergenceAlert objects
        """
        alerts = []
        
        for market in markets:
            market_price = market.get('market_price', 0.5)
            ai_probability = market.get('ai_probability', 0.5)
            
            implied_prob = self.calculate_implied_probability(market_price)
            divergence, divergence_percent = self.calculate_divergence(ai_probability, implied_prob)
            
            abs_divergence = abs(divergence)
            
            # Determine severity
            if abs_divergence >= high_threshold:
                severity = "HIGH"
            elif abs_divergence >= medium_threshold:
                severity = "MEDIUM"
            else:
                continue  # Skip low divergence
            
            # Generate recommendation
            if divergence > 0:
                recommendation = f"AI predicts {ai_probability:.1%} vs market {implied_prob:.1%}. Consider LONG position."
            else:
                recommendation = f"Market at {implied_prob:.1%} vs AI {ai_probability:.1%}. Consider SHORT or avoid."
            
            alert = DivergenceAlert(
                market_id=market['market_id'],
                market_question=market['question'],
                category=market.get('category', 'Other'),
                implied_probability=implied_prob,
                ai_probability=ai_probability,
                divergence=divergence,
                divergence_percent=divergence_percent,
                severity=severity,
                timestamp=datetime.utcnow(),
                recommendation=recommendation
            )
            
            alerts.append(alert)
        
        # Sort by absolute divergence (highest first)
        alerts.sort(key=lambda a: abs(a.divergence), reverse=True)
        
        return alerts
    
    def get_market_history(
        self,
        market_id: str,
        timeframe: str = "24h"
    ) -> Optional[MarketProbabilityHistory]:
        """
        Get historical probability data for a specific market.
        
        Args:
            market_id: Market identifier
            timeframe: Time range ("1h", "6h", "24h", "7d")
            
        Returns:
            MarketProbabilityHistory or None if no data
        """
        if market_id not in self.probability_history:
            return None
        
        # Parse timeframe
        timeframe_map = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7)
        }
        
        time_delta = timeframe_map.get(timeframe, timedelta(hours=24))
        cutoff_time = datetime.utcnow() - time_delta
        
        # Filter snapshots by timeframe
        snapshots = [
            s for s in self.probability_history[market_id]
            if s.timestamp > cutoff_time
        ]
        
        if not snapshots:
            return None
        
        # Convert to history points
        history = [
            ProbabilityHistoryPoint(
                timestamp=s.timestamp,
                market_price=s.market_price,
                implied_probability=s.implied_probability,
                ai_probability=s.ai_probability,
                divergence=s.divergence
            )
            for s in snapshots
        ]
        
        return MarketProbabilityHistory(
            market_id=market_id,
            market_question=snapshots[0].market_question,
            history=history,
            timeframe=timeframe
        )

# Global instance
heatmap_service = HeatmapService()
