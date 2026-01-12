import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.trading_agent import TradingAgent
from app.models import TradeSignal
from app.models_db import WhitelistedAddress, User, UserProfile
from app.database_users import SessionLocal, engine, BaseUsers
from app.market_client import MockMarketClient
from app.engine import ForecasterCriticEngine
from datetime import datetime, timedelta

# Setup test database
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    BaseUsers.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    BaseUsers.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user with profile."""
    user = User(
        email="trader@example.com",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    profile = UserProfile(
        user_id=user.id,
        full_name="Test Trader",
        role="trader",
        preferences={"default_wallet_address": "0x1234567890abcdef"}
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def trading_agent():
    """Create a trading agent with mock dependencies."""
    with patch('app.engine.DDGS'), \
         patch('app.engine.VectorDBClient'), \
         patch('app.engine.NewsIngestor'), \
         patch('app.engine.SentimentDetector'), \
         patch('app.engine.AlternativeDataClient'), \
         patch('app.engine.DataAggregator'), \
         patch('app.engine.TwitterConnector'), \
         patch('app.engine.RedditConnector'), \
         patch('app.engine.DiscordConnector'), \
         patch('app.engine.ReutersConnector'), \
         patch('app.engine.APNewsConnector'), \
         patch('app.engine.BloombergConnector'), \
         patch('app.engine.NOAAConnector'), \
         patch('app.engine.CSPANConnector'):
        
        market_client = MockMarketClient()
        engine = ForecasterCriticEngine()
        agent = TradingAgent(market_client, engine)
        return agent

@pytest.mark.asyncio
async def test_trade_execution_blocked_for_non_whitelisted(trading_agent, db_session, test_user):
    """Test that trade execution is blocked when wallet is not whitelisted."""
    signal = TradeSignal(
        market_id="test_market_1",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=1000.0,
        expected_value=100.0,
        rationale="Test trade",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0xnotwhitelisted"
    )
    
    # Execute signal - should be rejected
    await trading_agent.execute_signal(signal, db_session)
    
    # Verify trade was rejected
    assert signal.status == "REJECTED"
    assert signal.compliance_status == "REJECTED"
    assert "not whitelisted" in signal.compliance_message.lower()
    assert "REJECTED" in signal.rationale

@pytest.mark.asyncio
async def test_trade_execution_succeeds_for_whitelisted(trading_agent, db_session, test_user):
    """Test that trade execution proceeds when wallet is whitelisted and compliant."""
    # Add whitelisted wallet
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0x1234567890abcdef",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    signal = TradeSignal(
        market_id="test_market_2",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=500.0,  # Below large order threshold
        expected_value=50.0,
        rationale="Test trade",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0x1234567890abcdef"
    )
    
    # Execute signal - should succeed
    await trading_agent.execute_signal(signal, db_session)
    
    # Verify trade was approved and executed
    assert signal.compliance_status == "APPROVED"
    assert "passed" in signal.compliance_message.lower()
    assert signal.status in ["EXECUTED", "FAILED"]  # May fail for other reasons, but not compliance

@pytest.mark.asyncio
async def test_trade_uses_default_wallet_from_profile(trading_agent, db_session, test_user):
    """Test that trade uses default wallet from user profile if not specified."""
    # Add whitelisted wallet matching user's default
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0x1234567890abcdef",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    signal = TradeSignal(
        market_id="test_market_3",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=500.0,
        expected_value=50.0,
        rationale="Test trade",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp()
        # No wallet_address specified
    )
    
    # Execute signal - should use default wallet
    await trading_agent.execute_signal(signal, db_session)
    
    # Verify default wallet was used
    assert signal.wallet_address == "0x1234567890abcdef"
    assert signal.compliance_status == "APPROVED"

@pytest.mark.asyncio
async def test_trade_blocked_for_expired_kyc(trading_agent, db_session, test_user):
    """Test that trade is blocked when KYC has expired."""
    # Add whitelisted wallet with expired KYC
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xexpired",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow() - timedelta(days=400),
        expiry_date=datetime.utcnow() - timedelta(days=30),  # Expired
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    signal = TradeSignal(
        market_id="test_market_4",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=500.0,
        expected_value=50.0,
        rationale="Test trade",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0xexpired"
    )
    
    # Execute signal - should be rejected
    await trading_agent.execute_signal(signal, db_session)
    
    # Verify trade was rejected
    assert signal.status == "REJECTED"
    assert signal.compliance_status == "REJECTED"
    assert "expired" in signal.compliance_message.lower()

@pytest.mark.asyncio
async def test_compliance_check_logged_to_audit(trading_agent, db_session, test_user):
    """Test that all compliance checks are logged to audit trail."""
    from app.models_db import ComplianceCheck
    
    signal = TradeSignal(
        market_id="test_market_5",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=500.0,
        expected_value=50.0,
        rationale="Test trade",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0xauditlog"
    )
    
    # Execute signal - will be rejected (not whitelisted)
    await trading_agent.execute_signal(signal, db_session)
    
    # Verify audit log was created
    logs = db_session.query(ComplianceCheck).filter(
        ComplianceCheck.wallet_address == "0xauditlog"
    ).all()
    
    assert len(logs) >= 1
    assert logs[0].check_type == "PRE_TRADE"
    assert logs[0].check_result == "REJECTED"
    assert logs[0].user_id == test_user.id

@pytest.mark.asyncio
async def test_multiple_wallets_per_user(trading_agent, db_session, test_user):
    """Test that users can have multiple whitelisted wallets."""
    # Add multiple wallets
    wallet1 = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xwallet1",
        custody_provider="fireblocks",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    wallet2 = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xwallet2",
        custody_provider="coinbase",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add_all([wallet1, wallet2])
    db_session.commit()
    
    # Test trade with wallet1
    signal1 = TradeSignal(
        market_id="test_market_6",
        market_question="Will BTC hit $100k?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=500.0,
        expected_value=50.0,
        rationale="Test trade 1",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0xwallet1"
    )
    await trading_agent.execute_signal(signal1, db_session)
    assert signal1.compliance_status == "APPROVED"
    
    # Test trade with wallet2
    signal2 = TradeSignal(
        market_id="test_market_7",
        market_question="Will ETH hit $10k?",
        signal_side="BUY_YES",
        price_estimate=0.55,
        kelly_size_usd=300.0,
        expected_value=30.0,
        rationale="Test trade 2",
        status="PENDING",
        timestamp=datetime.utcnow().timestamp(),
        wallet_address="0xwallet2"
    )
    await trading_agent.execute_signal(signal2, db_session)
    assert signal2.compliance_status == "APPROVED"
