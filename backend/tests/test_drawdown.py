import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models_db import BaseUsers, DrawdownLimit, AgentDailyStats, User
from app.trading_agent import TradingAgent
from app.market_client import MockMarketClient
from app.engine import ForecasterCriticEngine

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_drawdown.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    BaseUsers.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    BaseUsers.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def trading_agent():
    """Create a trading agent with mock client."""
    from unittest.mock import MagicMock
    mock_client = MockMarketClient()
    mock_engine = MagicMock(spec=ForecasterCriticEngine)
    agent = TradingAgent(mock_client, mock_engine)
    return agent

def test_create_drawdown_limit(db_session, test_user):
    """Test creating a drawdown limit."""
    limit = DrawdownLimit(
        user_id=test_user.id,
        max_daily_drawdown_percent=5.0,
        is_active=True
    )
    db_session.add(limit)
    db_session.commit()
    
    retrieved = db_session.query(DrawdownLimit).filter(
        DrawdownLimit.user_id == test_user.id
    ).first()
    
    assert retrieved is not None
    assert retrieved.max_daily_drawdown_percent == 5.0
    assert retrieved.is_active is True

def test_daily_stats_creation(db_session, test_user):
    """Test creating daily stats."""
    stats = AgentDailyStats(
        user_id=test_user.id,
        date=datetime.utcnow(),
        starting_balance=10000.0,
        current_pnl=0.0,
        is_paused=False
    )
    db_session.add(stats)
    db_session.commit()
    
    retrieved = db_session.query(AgentDailyStats).filter(
        AgentDailyStats.user_id == test_user.id
    ).first()
    
    assert retrieved is not None
    assert retrieved.starting_balance == 10000.0
    assert retrieved.current_pnl == 0.0
    assert retrieved.is_paused is False

@pytest.mark.asyncio
async def test_check_drawdown_within_limit(db_session, test_user, trading_agent):
    """Test that trading is allowed when within drawdown limit."""
    # Create limit
    limit = DrawdownLimit(
        user_id=test_user.id,
        max_daily_drawdown_percent=5.0,
        is_active=True
    )
    db_session.add(limit)
    
    # Create stats with small loss (2%)
    stats = AgentDailyStats(
        user_id=test_user.id,
        date=datetime.utcnow(),
        starting_balance=10000.0,
        current_pnl=-200.0,  # 2% loss
        is_paused=False
    )
    db_session.add(stats)
    db_session.commit()
    
    # Check if trading is allowed
    result = await trading_agent.check_drawdown_limit(db_session)
    
    assert result is True
    assert stats.is_paused is False

@pytest.mark.asyncio
async def test_check_drawdown_exceeds_limit(db_session, test_user, trading_agent):
    """Test that trading is paused when drawdown exceeds limit."""
    # Create limit
    limit = DrawdownLimit(
        user_id=test_user.id,
        max_daily_drawdown_percent=5.0,
        is_active=True
    )
    db_session.add(limit)
    
    # Create stats with large loss (6%)
    stats = AgentDailyStats(
        user_id=test_user.id,
        date=datetime.utcnow(),
        starting_balance=10000.0,
        current_pnl=-600.0,  # 6% loss
        is_paused=False
    )
    db_session.add(stats)
    db_session.commit()
    
    # Check if trading is allowed
    result = await trading_agent.check_drawdown_limit(db_session)
    
    assert result is False
    
    # Refresh stats to get updated values
    db_session.refresh(stats)
    assert stats.is_paused is True
    assert "Daily drawdown limit" in stats.pause_reason

@pytest.mark.asyncio
async def test_check_drawdown_no_limit_set(db_session, test_user, trading_agent):
    """Test that trading is allowed when no limit is set."""
    # Create stats but no limit
    stats = AgentDailyStats(
        user_id=test_user.id,
        date=datetime.utcnow(),
        starting_balance=10000.0,
        current_pnl=-1000.0,  # 10% loss
        is_paused=False
    )
    db_session.add(stats)
    db_session.commit()
    
    # Check if trading is allowed
    result = await trading_agent.check_drawdown_limit(db_session)
    
    assert result is True  # No limit set, so trading allowed

@pytest.mark.asyncio
async def test_get_or_create_daily_stats(db_session, test_user, trading_agent):
    """Test that daily stats are created if they don't exist."""
    # No stats exist initially
    stats = trading_agent._get_or_create_daily_stats(db_session)
    
    assert stats is not None
    assert stats.user_id == 1
    assert stats.starting_balance == 10000.0
    assert stats.current_pnl == 0.0
    assert stats.is_paused is False

def test_drawdown_calculation():
    """Test drawdown percentage calculation."""
    starting_balance = 10000.0
    
    # Test 5% loss
    current_pnl = -500.0
    drawdown_pct = (abs(min(0, current_pnl)) / starting_balance) * 100
    assert drawdown_pct == 5.0
    
    # Test 10% loss
    current_pnl = -1000.0
    drawdown_pct = (abs(min(0, current_pnl)) / starting_balance) * 100
    assert drawdown_pct == 10.0
    
    # Test profit (no drawdown)
    current_pnl = 500.0
    drawdown_pct = (abs(min(0, current_pnl)) / starting_balance) * 100
    assert drawdown_pct == 0.0
