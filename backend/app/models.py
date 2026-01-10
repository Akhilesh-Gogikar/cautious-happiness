from pydantic import BaseModel
from typing import List, Optional, Any

class OrderBookLevel(BaseModel):
    price: float
    amount: float

class OrderBook(BaseModel):
    asks: List[OrderBookLevel]
    bids: List[OrderBookLevel]

class Source(BaseModel):
    title: str
    url: str
    snippet: str

class ForecastResult(BaseModel):
    search_query: str
    news_summary: List[Source]
    initial_forecast: float
    critique: str
    adjusted_forecast: float
    reasoning: Optional[str] = None
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

class ChatRequest(BaseModel):
    user_message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

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
