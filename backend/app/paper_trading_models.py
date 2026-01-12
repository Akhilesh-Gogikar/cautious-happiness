from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PaperSessionCreate(BaseModel):
    """Request model for creating a new paper trading session."""
    model_name: str
    model_version: Optional[str] = "default"
    initial_balance: float = 10000.0
    description: Optional[str] = None


class PaperSessionResponse(BaseModel):
    """Response model for paper trading session."""
    id: int
    user_id: int
    model_name: str
    model_version: str
    initial_balance: float
    current_balance: float
    total_pnl: float
    num_trades: int
    win_rate: float
    sharpe_ratio: Optional[float]
    max_drawdown: float
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    metadata_json: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class PaperTradeResponse(BaseModel):
    """Response model for individual paper trade."""
    id: int
    session_id: int
    market_id: str
    market_question: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    shares: float
    realized_pnl: float
    entry_time: datetime
    exit_time: Optional[datetime]
    status: str
    execution_strategy: str
    metadata_json: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class PaperPositionResponse(BaseModel):
    """Response model for paper trading position."""
    id: int
    session_id: int
    market_id: str
    shares: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    last_updated: datetime
    
    class Config:
        from_attributes = True


class PaperPerformanceResponse(BaseModel):
    """Response model for paper trading performance metrics."""
    session_id: int
    initial_balance: float
    current_balance: float
    total_value: float
    total_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    total_return_pct: float
    num_trades: int
    win_rate: float
    num_positions: int
    total_exposure: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: float = 0.0
    avg_trade_pnl: Optional[float] = None


class PaperModeRequest(BaseModel):
    """Request model for setting trading mode."""
    mode: str  # "REAL" or "PAPER"


class PaperModeResponse(BaseModel):
    """Response model for current trading mode."""
    mode: str
    active_session_id: Optional[int] = None
    session_info: Optional[Dict[str, Any]] = None


class SessionComparisonRequest(BaseModel):
    """Request model for comparing multiple sessions."""
    session_ids: List[int]


class SessionComparisonResponse(BaseModel):
    """Response model for session comparison."""
    sessions: List[PaperSessionResponse]
    comparison_metrics: Dict[str, Any]
