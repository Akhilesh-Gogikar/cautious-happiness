import pytest
from unittest.mock import MagicMock
from app.trading_agent import TradingAgent
from app.models import TradeSignal, PortfolioPosition, PortfolioSummary
from app.models_db import ExposureLimit, EventRegistry, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_users import BaseUsers
import app.models_db # Import all to register models

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
BaseUsers.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    session = SessionLocal()
    # Create test user
    user = User(id=1, email="test@example.com")
    session.add(user)
    session.commit()
    yield session
    session.close()
    BaseUsers.metadata.drop_all(bind=engine)
    BaseUsers.metadata.create_all(bind=engine)

@pytest.fixture
def mock_market_client():
    client = MagicMock()
    return client

@pytest.fixture
def agent(mock_market_client):
    # Mock engine as well since TradingAgent init requires it, or pass None if typed allows
    # TradingAgent(market_client, engine)
    return TradingAgent(mock_market_client, MagicMock())

def test_no_limits(db_session, agent):
    # No limits in DB
    signal = TradeSignal(
        market_id="mkt_1",
        market_question="Q1",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=100.0,
        expected_value=1.1,
        rationale="test",
        timestamp=123.0
    )
    
    # Mock Portfolio
    agent.market_client.get_portfolio.return_value = PortfolioSummary(
        balance=1000, exposure=0, positions=[]
    )
    
    assert agent.check_exposure_limits(db_session, signal) == True

def test_market_cap_breach(db_session, agent):
    # Limit: Max $100 per market
    limit = ExposureLimit(user_id=1, scope_type="PER_MARKET_CAP", scope_value="ALL", max_exposure_usd=100.0)
    db_session.add(limit)
    db_session.commit()

    # Existing position: $80 in mkt_1
    pos1 = PortfolioPosition(asset_id="a1", condition_id="mkt_1", question="Q", outcome="Yes", price=0.5, size=160, svalue=80.0, pnl=0)
    agent.market_client.get_portfolio.return_value = PortfolioSummary(
        balance=1000, exposure=80, positions=[pos1]
    )

    # Signal: Buy $30 more in mkt_1 -> Total $110 > $100
    signal = TradeSignal(
        market_id="mkt_1",
        market_question="Q1",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=30.0,
        expected_value=1.1,
        rationale="test",
        timestamp=123.0
    )
    
    # Need to register market in EventRegistry so it knows it exists (though logic defaults uncategorized)
    # The logic checks exposure_per_market directly by ID, so category lookup failure won't impact market cap check directly
    assert agent.check_exposure_limits(db_session, signal) == False

def test_market_cap_ok(db_session, agent):
    # Limit: Max $100 per market
    limit = ExposureLimit(user_id=1, scope_type="PER_MARKET_CAP", scope_value="ALL", max_exposure_usd=100.0)
    db_session.add(limit)
    db_session.commit()

    # Existing position: $80 in mkt_1
    pos1 = PortfolioPosition(asset_id="a1", condition_id="mkt_1", question="Q", outcome="Yes", price=0.5, size=160, svalue=80.0, pnl=0)
    agent.market_client.get_portfolio.return_value = PortfolioSummary(
        balance=1000, exposure=80, positions=[pos1]
    )

    # Signal: Buy $10 more -> Total $90 <= $100
    signal = TradeSignal(
        market_id="mkt_1",
        market_question="Q1",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=10.0,
        expected_value=1.1,
        rationale="test",
        timestamp=123.0
    )
    
    assert agent.check_exposure_limits(db_session, signal) == True

def test_category_cap_breach(db_session, agent):
    # Limit: Max $100 in Politics
    limit = ExposureLimit(user_id=1, scope_type="CATEGORY_CAP", scope_value="Politics", max_exposure_usd=100.0)
    
    # Register markets
    m1 = EventRegistry(market_id="mkt_1", category="Politics")
    m2 = EventRegistry(market_id="mkt_2", category="Politics")
    db_session.add_all([limit, m1, m2])
    db_session.commit()

    # Existing: $80 in mkt_1 (Politics)
    pos1 = PortfolioPosition(asset_id="a1", condition_id="mkt_1", question="Q", outcome="Yes", price=0.5, size=160, svalue=80.0, pnl=0)
    agent.market_client.get_portfolio.return_value = PortfolioSummary(
        balance=1000, exposure=80, positions=[pos1]
    )

    # Signal: Buy $30 in mkt_2 (Politics) -> Total Politics $110 > $100
    signal = TradeSignal(
        market_id="mkt_2",
        market_question="Q2",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=30.0,
        expected_value=1.1,
        rationale="test",
        timestamp=123.0
    )

    assert agent.check_exposure_limits(db_session, signal) == False

def test_exchange_cap_breach(db_session, agent):
    # Limit: Max $100 in AlphaSignals
    limit = ExposureLimit(user_id=1, scope_type="EXCHANGE_CAP", scope_value="AlphaSignals", max_exposure_usd=100.0)
    db_session.add(limit)
    db_session.commit()

    # Existing: $80
    pos1 = PortfolioPosition(asset_id="a1", condition_id="mkt_1", question="Q", outcome="Yes", price=0.5, size=160, svalue=80.0, pnl=0)
    agent.market_client.get_portfolio.return_value = PortfolioSummary(
        balance=1000, exposure=80, positions=[pos1]
    )

    # Signal: Buy $30 -> Total $110 > $100
    # Assuming code defaults to AlphaSignals per my implementation
    signal = TradeSignal(
        market_id="mkt_2",
        market_question="Q2",
        signal_side="BUY_YES", # Fixed typo
        price_estimate=0.5,
        kelly_size_usd=30.0,
        expected_value=1.1,
        rationale="test",
        timestamp=123.0
    )
    
    # Register mkt_2 category just in case (optional)
    m2 = EventRegistry(market_id="mkt_2", category="Other")
    db_session.add(m2)
    db_session.commit()

    assert agent.check_exposure_limits(db_session, signal) == False
