from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Literal
from enum import Enum
import datetime

class OrderBookLevel(BaseModel):
    price: float
    amount: float

class OrderBook(BaseModel):
    asks: List[OrderBookLevel]
    bids: List[OrderBookLevel]

class ExecutionStrategy(str, Enum):
    SINGLE_SHOT = "SINGLE_SHOT"
    TWAP = "TWAP"
    VWAP = "VWAP"
    ICEBERG = "ICEBERG"
    LIQUIDITY_SNIPE = "LIQUIDITY_SNIPE"

class ExecutionParameters(BaseModel):
    strategy: ExecutionStrategy = ExecutionStrategy.SINGLE_SHOT
    duration_minutes: Optional[float] = None
    interval_seconds: Optional[float] = 30
    display_size_shares: Optional[float] = None # For Iceberg
    max_slippage_bps: Optional[int] = 100 # 1% default
    min_depth_usd: Optional[float] = None # For Liquidity Snipe
    snipe_max_price: Optional[float] = None # For Liquidity Snipe

class Source(BaseModel):
    title: str
    url: str
    snippet: str

class AlternativeSignal(BaseModel):
    source_type: str # "SATELLITE", "SHIPPING", "FLIGHT"
    signal_name: str # e.g., "Mato Grosso Soy Canal"
    value: str # e.g., "75% Greenness Index"
    impact: str # "BULLISH", "BEARISH", "NEUTRAL"
    confidence: float # 0.0 to 1.0
    description: str

class ForecastResult(BaseModel):
    search_query: str
    news_summary: List[Source]
    initial_forecast: float
    critique: str
    adjusted_forecast: float
    hype_score: float = 0.0
    sentiment_score: float = 0.5
    discourse_analysis: Optional[str] = None
    alternative_signals: List[AlternativeSignal] = []
    reasoning: Optional[str] = None
    verification_report: Optional[str] = None
    category: Optional[str] = None
    data_sources_used: List[str] = []
    model_name: Optional[str] = None
    error: Optional[str] = None

class TradeSignal(BaseModel):
    """
    Represents a proposed or executed trade.
    """
    market_id: str
    market_question: str
    signal_side: str # "BUY_YES" or "BUY_NO" (we usually buy outcome tokens)
    price_estimate: float
    kelly_size_usd: float
    expected_value: float
    rationale: str
    status: str = "PENDING" # PENDING, APPROVED, REJECTED, EXECUTED, FAILED
    timestamp: float
    # Optional execution details
    tx_hash: Optional[str] = None
    # Compliance fields
    wallet_address: Optional[str] = None
    compliance_status: str = "NOT_CHECKED" # NOT_CHECKED, PENDING, APPROVED, REJECTED
    compliance_message: Optional[str] = None
    # Attribution fields
    model_used: Optional[str] = None  # AI model that generated the signal
    data_sources: List[str] = []  # Data sources used (e.g., ["RAG", "ALT_DATA", "SOCIAL"])
    strategy_type: Optional[str] = None  # Strategy classification (e.g., "KELLY", "ARBITRAGE")
    category: Optional[str] = None  # Market category (e.g., "Economics", "Politics")
    confidence_score: Optional[float] = None  # Model confidence 0-1

class ChatRequest(BaseModel):
    user_message: str
    context: Optional[str] = None
    selected_agents: List[str] = []

class ChatResponse(BaseModel):
    response: str

class ChatMessage(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime.datetime if 'datetime' in globals() and hasattr(datetime, 'datetime') else Any
    context: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PortfolioPosition(BaseModel):
    asset_id: str
    condition_id: str
    question: str
    outcome: str # "Yes" or "No"
    price: float
    size: float
    svalue: float # Current Value
    pnl: float

class PortfolioSummary(BaseModel):
    balance: float
    exposure: float
    positions: List[PortfolioPosition]

class HistoricalMarketResponse(BaseModel):
    id: int
    market_id: str
    question: str
    outcome: Optional[str]
    close_time: datetime.datetime
    category: str
    volume: float

    class Config:
        from_attributes = True

class BacktestRequest(BaseModel):
    market_ids: List[int]
    model_name: str = "openforecaster"

class BacktestResultResponse(BaseModel):
    market_id: int
    predicted_outcome: float
    actual_outcome: Optional[str]
    is_correct: bool
    reasoning: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class ArbitrageOpportunity(BaseModel):
    market_name: str
    polymarket_id: str
    polymarket_price: float
    kalshi_id: str
    kalshi_price: float
    discrepancy: float
    timestamp: float

class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class RiskStatus(BaseModel):
    name: str
    status: str
    level: RiskLevel
    latency: Optional[str] = None
    details: Optional[str] = None

class RiskReport(BaseModel):
    overall_health: RiskLevel
    components: List[RiskStatus]
    last_updated: float

class DrawdownLimitRequest(BaseModel):
    max_daily_drawdown_percent: float
    is_active: bool = True

class DrawdownLimitResponse(BaseModel):
    id: int
    user_id: int
    max_daily_drawdown_percent: float
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class DailyStatsResponse(BaseModel):
    id: int
    user_id: int
    date: datetime.datetime
    starting_balance: float
    current_pnl: float
    max_drawdown_reached: float
    is_paused: bool
    pause_reason: Optional[str]

    class Config:
        from_attributes = True

class RiskAlert(BaseModel):
    severity: str # "HIGH", "MEDIUM", "LOW"
    message: str
    factor: str
    current_exposure: float
    proposed_add: float


class PnLSnapshot(BaseModel):
    timestamp: datetime.datetime
    pnl: float

class PnLVelocityResponse(BaseModel):
    market_id: str
    snapshots: List[PnLSnapshot]

class AlgoOrderRequest(BaseModel):
    market_id: str
    type: Literal["TWAP", "VWAP", "ICEBERG"]
    total_size_usd: float
    display_size_usd: Optional[float] = None  # For Iceberg
    duration_minutes: Optional[int] = None  # For TWAP/VWAP

class AlgoOrderResponse(BaseModel):
    id: int
    user_id: int
    market_id: str
    type: str
    total_size_usd: float
    remaining_size_usd: float
    display_size_usd: Optional[float]
    duration_minutes: Optional[int]
    status: str
    created_at: datetime.datetime
    last_executed_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class RiskParametersRequest(BaseModel):
    """Request model for updating risk parameters."""
    max_order_size_usd: Optional[float] = None
    max_price_deviation_pct: Optional[float] = None
    enabled: Optional[bool] = None


class RiskParametersResponse(BaseModel):
    """Response model for risk parameters."""
    id: int
    user_id: Optional[int]
    max_order_size_usd: float
    max_price_deviation_pct: float
    enabled: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class OrderValidationErrorResponse(BaseModel):
    """Response model for order validation failures."""
    error: bool = True
    error_code: str
    message: str
    details: Optional[dict] = None
