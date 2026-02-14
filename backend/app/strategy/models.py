from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class StrategyGenerationRequest(BaseModel):
    prompt: str
    model: str = "lfm-40b"

class StrategyCode(BaseModel):
    name: str
    code: str
    description: str
    logic_summary: str

class BacktestRequest(BaseModel):
    code: str
    start_date: str
    end_date: str
    initial_cash: float = 100000.0

class BacktestResult(BaseModel):
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    cagr: float
    trades: int
    equity_curve: List[Dict[str, Any]]
