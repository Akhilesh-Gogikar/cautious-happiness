from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database_users import BaseUsers

class User(BaseUsers):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    security_question = relationship("SecurityQuestion", back_populates="user", uselist=False)
    logs = relationship("ActionLog", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    backtest_results = relationship("BacktestResult", back_populates="user")

class UserProfile(BaseUsers):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, default="")
    role = Column(String, default="user") # 'user', 'admin', 'institution'
    preferences = Column(JSON, default={})
    
    user = relationship("User", back_populates="profile")

class SecurityQuestion(BaseUsers):
    __tablename__ = "security_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(String)
    hashed_answer = Column(String)

    user = relationship("User", back_populates="security_question")

class ActionLog(BaseUsers):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # e.g. "LOGIN", "TRADE", "VIEW_PROFILE"
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={}) # Stores specific info about the action (e.g. trade_id)

    user = relationship("User", back_populates="logs")

class ChatHistory(BaseUsers):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(String)
    context = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_history")

class EventRegistry(BaseUsers):
    __tablename__ = "event_registry"

    market_id = Column(String, primary_key=True, index=True)
    question = Column(String)
    category = Column(String) # Economics, Politics, Science, Other
    last_updated = Column(DateTime, default=datetime.utcnow)

class HistoricalMarket(BaseUsers):
    __tablename__ = "historical_markets"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(String, unique=True, index=True) # condition_id
    question = Column(String)
    outcome = Column(String) # "Yes" or "No"
    close_time = Column(DateTime)
    category = Column(String, default="General")
    volume = Column(Float, default=0.0)
    metadata_json = Column(JSON, default={}) # Raw market data

    backtest_results = relationship("BacktestResult", back_populates="market")

class BacktestResult(BaseUsers):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    market_id = Column(Integer, ForeignKey("historical_markets.id"))
    model_name = Column(String)
    predicted_outcome = Column(Float) # 0.0 to 1.0 (probability)
    reasoning = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="backtest_results")
    market = relationship("HistoricalMarket", back_populates="backtest_results")
class AlgoOrder(BaseUsers):
    __tablename__ = "algo_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    market_id = Column(String, index=True)
    type = Column(String) # "TWAP", "VWAP", "ICEBERG"
    total_size_usd = Column(Float)
    remaining_size_usd = Column(Float)
    display_size_usd = Column(Float, nullable=True) # For Iceberg
    duration_minutes = Column(Integer, nullable=True) # For TWAP/VWAP
    status = Column(String, default="PENDING") # PENDING, ACTIVE, COMPLETED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
    last_executed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="algo_orders")

User.algo_orders = relationship("AlgoOrder", back_populates="user")

class RiskParameter(BaseUsers):
    """User-specific or global risk management parameters."""
    __tablename__ = "risk_parameters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = global default
    max_order_size_usd = Column(Float, default=10000.0)
    max_price_deviation_pct = Column(Float, default=10.0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="risk_parameters")

User.risk_parameters = relationship("RiskParameter", back_populates="user")
User.drawdown_limits = relationship("DrawdownLimit", back_populates="user")
User.daily_stats = relationship("AgentDailyStats", back_populates="user")
User.exposure_limits = relationship("ExposureLimit", back_populates="user")

class DrawdownLimit(BaseUsers):
    __tablename__ = "drawdown_limits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    max_daily_drawdown_percent = Column(Float, default=5.0) # e.g., 5%
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="drawdown_limits")

class AgentDailyStats(BaseUsers):
    __tablename__ = "agent_daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    starting_balance = Column(Float)
    current_pnl = Column(Float, default=0.0)
    max_drawdown_reached = Column(Float, default=0.0)
    is_paused = Column(Boolean, default=False)
    pause_reason = Column(String, nullable=True)

    user = relationship("User", back_populates="daily_stats")

class WhitelistedAddress(BaseUsers):
    __tablename__ = "whitelisted_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    custody_provider = Column(String, default="mock") # "fireblocks", "coinbase", "mock"
    kyc_verified = Column(Boolean, default=False)
    aml_status = Column(String, default="PENDING") # "PENDING", "APPROVED", "FLAGGED", "REJECTED"
    verification_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON, default={}) # Additional custody provider data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="whitelisted_addresses")

class ComplianceCheck(BaseUsers):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wallet_address = Column(String, index=True, nullable=False)
    check_type = Column(String, nullable=False) # "PRE_TRADE", "KYC_VERIFICATION", "AML_SCREENING"
    check_result = Column(String, nullable=False) # "APPROVED", "REJECTED", "PENDING"
    trade_signal_id = Column(String, nullable=True) # Reference to trade if applicable
    reason = Column(String, nullable=True) # Reason for rejection/approval
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = Column(JSON, default={}) # Additional check details

    user = relationship("User", back_populates="compliance_checks")

# Add relationships to User model
User.whitelisted_addresses = relationship("WhitelistedAddress", back_populates="user")
User.compliance_checks = relationship("ComplianceCheck", back_populates="user")

class ExposureLimit(BaseUsers):
    __tablename__ = "exposure_limits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scope_type = Column(String) # "MARKET", "CATEGORY", "EXCHANGE"
    scope_value = Column(String, nullable=True) # e.g. "Politics", "polymarket" (Null for global per-type default if we want, or specific)
    # Actually, let's keep it simple:
    # If scope_type="MARKET", scope_value="<market_id>" (or specific market logic, but usually we want a generic "Max 10% per market")
    # Let's support:
    # 1. SCOPE_TYPE="PER_MARKET_CAP" -> scope_value="ALL" (Max $X per any single market)
    # 2. SCOPE_TYPE="CATEGORY_CAP" -> scope_value="Politics" (Max $X in Politics)
    # 3. SCOPE_TYPE="EXCHANGE_CAP" -> scope_value="AlphaSignals" (Max $X in AlphaSignals)
    
    max_exposure_usd = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)


    user = relationship("User", back_populates="exposure_limits")

class AuditLog(BaseUsers):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String, index=True) # AI_DECISION, TRADE_EXECUTION, MANUAL_OVERRIDE
    payload = Column(JSON, default={})
    user_id = Column(Integer, nullable=True) # Optional, for manual actions
    
    # Hash Chain Fields
    previous_hash = Column(String, nullable=False)
    record_hash = Column(String, nullable=False, unique=True)


# Paper Trading Models
class PaperTradingSession(BaseUsers):
    """Tracks paper trading sessions for testing LLM weights."""
    __tablename__ = "paper_trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_name = Column(String, nullable=False)  # LLM model being tested
    model_version = Column(String, default="default")  # Version/weight identifier
    initial_balance = Column(Float, default=10000.0)
    current_balance = Column(Float)
    total_pnl = Column(Float, default=0.0)
    num_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, default=0.0)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE")  # ACTIVE, COMPLETED, CANCELLED
    metadata_json = Column(JSON, default={})
    
    user = relationship("User", back_populates="paper_sessions")
    trades = relationship("PaperTrade", back_populates="session", cascade="all, delete-orphan")
    positions = relationship("PaperPosition", back_populates="session", cascade="all, delete-orphan")


class PaperTrade(BaseUsers):
    """Records individual paper trades."""
    __tablename__ = "paper_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("paper_trading_sessions.id"))
    market_id = Column(String, nullable=False)
    market_question = Column(String)
    side = Column(String, nullable=False)  # BUY_YES, BUY_NO, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    shares = Column(Float, nullable=False)
    realized_pnl = Column(Float, default=0.0)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    status = Column(String, default="OPEN")  # OPEN, CLOSED
    execution_strategy = Column(String, default="SINGLE")  # SINGLE, TWAP, VWAP, ICEBERG
    metadata_json = Column(JSON, default={})
    
    session = relationship("PaperTradingSession", back_populates="trades")


class PaperPosition(BaseUsers):
    """Tracks current paper trading positions."""
    __tablename__ = "paper_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("paper_trading_sessions.id"))
    market_id = Column(String, nullable=False, index=True)
    shares = Column(Float, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    session = relationship("PaperTradingSession", back_populates="positions")


# Add relationship to User model
User.paper_sessions = relationship("PaperTradingSession", back_populates="user")
