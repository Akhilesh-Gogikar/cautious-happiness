from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProbabilitySnapshot(BaseModel):
    """
    Represents a point-in-time snapshot of market and AI probabilities.
    """
    market_id: str
    market_question: str
    category: str
    timestamp: datetime
    market_price: float  # Current market price (0.0 to 1.0)
    implied_probability: float  # Derived from market_price
    ai_probability: float  # AI model's calculated probability
    divergence: float  # Difference (ai_probability - implied_probability)
    divergence_percent: float  # Percentage difference
    volume_24h: Optional[float] = None
    liquidity_depth: Optional[float] = None

class HeatmapCell(BaseModel):
    """
    Represents a single cell in the heatmap visualization.
    """
    market_id: str
    market_question: str
    category: str
    implied_probability: float
    ai_probability: float
    divergence: float
    divergence_percent: float
    color_intensity: float  # -1.0 to 1.0 for color mapping
    last_updated: datetime
    confidence_score: Optional[float] = None

class HeatmapData(BaseModel):
    """
    Complete heatmap dataset for visualization.
    """
    cells: List[HeatmapCell]
    timestamp: datetime
    total_markets: int
    avg_divergence: float
    max_divergence: float
    min_divergence: float

class DivergenceAlert(BaseModel):
    """
    Alert for significant probability divergence.
    """
    market_id: str
    market_question: str
    category: str
    implied_probability: float
    ai_probability: float
    divergence: float
    divergence_percent: float
    severity: str  # "HIGH", "MEDIUM", "LOW"
    timestamp: datetime
    recommendation: str  # Trading recommendation

class ProbabilityHistoryPoint(BaseModel):
    """
    Historical probability data point for time-series visualization.
    """
    timestamp: datetime
    market_price: float
    implied_probability: float
    ai_probability: float
    divergence: float

class MarketProbabilityHistory(BaseModel):
    """
    Historical probability data for a specific market.
    """
    market_id: str
    market_question: str
    history: List[ProbabilityHistoryPoint]
    timeframe: str  # "1h", "6h", "24h", "7d"
