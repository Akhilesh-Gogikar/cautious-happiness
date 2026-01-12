from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database_users import BaseUsers

class TradeExecution(BaseUsers):
    """
    Records each trade execution with full attribution metadata.
    This is the source of truth for P&L attribution analysis.
    """
    __tablename__ = "trade_executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Trade Details
    market_id = Column(String, index=True)
    market_question = Column(String)
    side = Column(String)  # "BUY_YES", "BUY_NO", "SELL_YES", "SELL_NO"
    entry_price = Column(Float)
    size_usd = Column(Float)
    shares = Column(Float)
    tx_hash = Column(String, nullable=True)
    
    # Tax Lot Tracking
    exchange = Column(String, index=True, nullable=True)  # "KALSHI" or "POLYMARKET"
    tax_lot_ids = Column(JSON, default=[], nullable=True)  # Associated tax lot IDs
    
    # Attribution Metadata
    model_used = Column(String, index=True)  # e.g., "openforecaster", "gemini-critic"
    data_sources = Column(JSON, default=[])  # List of sources: ["RAG", "ALT_DATA", "SOCIAL"]
    strategy_type = Column(String, index=True)  # "KELLY", "ARBITRAGE", "MARKET_MAKING", "MANUAL"
    category = Column(String, index=True)  # "Economics", "Politics", "Science", "Other"
    
    # Performance Tracking
    current_price = Column(Float, nullable=True)  # Updated periodically
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0, nullable=True)  # Set when position closed
    is_closed = Column(Boolean, default=False)
    
    # Metadata
    confidence_score = Column(Float, nullable=True)  # Model confidence 0-1
    reasoning_snippet = Column(String, nullable=True)  # First 200 chars of reasoning
    execution_metadata = Column(JSON, default={})  # Additional execution details
    
    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
    closed_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trade_executions")
    snapshots = relationship("PositionSnapshot", back_populates="trade", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_model', 'user_id', 'model_used'),
        Index('idx_user_strategy', 'user_id', 'strategy_type'),
        Index('idx_user_category', 'user_id', 'category'),
        Index('idx_executed_at', 'executed_at'),
    )


class PositionSnapshot(BaseUsers):
    """
    Periodic snapshots of position values for time-series P&L tracking.
    Created every hour or on significant price changes.
    """
    __tablename__ = "position_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trade_executions.id"), index=True)
    
    # Snapshot Data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    current_price = Column(Float)
    position_value = Column(Float)
    unrealized_pnl = Column(Float)
    pnl_percent = Column(Float)
    
    # Relationships
    trade = relationship("TradeExecution", back_populates="snapshots")
    
    __table_args__ = (
        Index('idx_trade_timestamp', 'trade_id', 'timestamp'),
    )


class AttributionMetrics(BaseUsers):
    """
    Pre-aggregated attribution metrics for fast dashboard queries.
    Updated periodically (e.g., every 15 minutes) by a background job.
    """
    __tablename__ = "attribution_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Attribution Dimension
    dimension_type = Column(String, index=True)  # "MODEL", "SOURCE", "STRATEGY", "CATEGORY"
    dimension_value = Column(String, index=True)  # e.g., "openforecaster", "RAG", "KELLY", "Economics"
    
    # Time Period
    period_start = Column(DateTime, index=True)
    period_end = Column(DateTime, index=True)
    period_type = Column(String)  # "HOUR", "DAY", "WEEK", "MONTH", "ALL_TIME"
    
    # Metrics
    total_trades = Column(Integer, default=0)
    total_volume_usd = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)  # Percentage of profitable trades
    avg_pnl_per_trade = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="attribution_metrics")
    
    __table_args__ = (
        Index('idx_user_dimension', 'user_id', 'dimension_type', 'dimension_value'),
        Index('idx_period', 'period_type', 'period_start', 'period_end'),
    )


# Add relationships to User model
from app.models_db import User
User.trade_executions = relationship("TradeExecution", back_populates="user")
User.attribution_metrics = relationship("AttributionMetrics", back_populates="user")
