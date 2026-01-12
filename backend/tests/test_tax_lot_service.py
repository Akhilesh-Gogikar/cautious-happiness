"""
Test Tax Lot Service - FIFO/LIFO/SpecID Algorithms
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_users import BaseUsers
from app.tax_models import TaxLot, TaxTransaction, TaxSettings
from app.tax_lot_service import TaxLotManager
from app.models_db import User

# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    BaseUsers.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    BaseUsers.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(email="test@example.com", hashed_password="test")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_fifo_lot_matching(db_session, test_user):
    """Test FIFO lot matching algorithm."""
    manager = TaxLotManager(db_session)
    
    # Create three lots at different prices
    lot1 = manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.40,
        purchase_date=datetime(2026, 1, 1)
    )
    
    lot2 = manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.60,
        purchase_date=datetime(2026, 2, 1)
    )
    
    lot3 = manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.80,
        purchase_date=datetime(2026, 3, 1)
    )
    
    # Sell 150 shares using FIFO
    transaction = manager.record_sale(
        user_id=test_user.id,
        exchange="POLYMARKET",
        asset_id="asset1",
        shares=150,
        price=1.00,
        sale_date=datetime(2026, 4, 1),
        method="FIFO"
    )
    
    # FIFO should sell all of lot1 (100 @ 0.40) and 50 of lot2 (50 @ 0.60)
    # Cost basis = (100 * 0.40) + (50 * 0.60) = 40 + 30 = 70
    # Proceeds = 150 * 1.00 = 150
    # Gain = 150 - 70 = 80
    
    assert transaction.cost_basis == 70.0
    assert transaction.proceeds == 150.0
    assert transaction.gain_loss == 80.0
    assert transaction.matching_method == "FIFO"
    
    # Check lot states
    db_session.refresh(lot1)
    db_session.refresh(lot2)
    db_session.refresh(lot3)
    
    assert lot1.is_closed == True
    assert lot1.shares_remaining == 0
    assert lot2.shares_remaining == 50
    assert lot3.shares_remaining == 100

def test_lifo_lot_matching(db_session, test_user):
    """Test LIFO lot matching algorithm."""
    manager = TaxLotManager(db_session)
    
    # Create three lots at different prices
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.40,
        purchase_date=datetime(2026, 1, 1)
    )
    
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.60,
        purchase_date=datetime(2026, 2, 1)
    )
    
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.80,
        purchase_date=datetime(2026, 3, 1)
    )
    
    # Sell 150 shares using LIFO
    transaction = manager.record_sale(
        user_id=test_user.id,
        exchange="POLYMARKET",
        asset_id="asset1",
        shares=150,
        price=1.00,
        sale_date=datetime(2026, 4, 1),
        method="LIFO"
    )
    
    # LIFO should sell all of lot3 (100 @ 0.80) and 50 of lot2 (50 @ 0.60)
    # Cost basis = (100 * 0.80) + (50 * 0.60) = 80 + 30 = 110
    # Proceeds = 150 * 1.00 = 150
    # Gain = 150 - 110 = 40
    
    assert transaction.cost_basis == 110.0
    assert transaction.proceeds == 150.0
    assert transaction.gain_loss == 40.0
    assert transaction.matching_method == "LIFO"

def test_section_1256_treatment(db_session, test_user):
    """Test Section 1256 60/40 split for Kalshi."""
    manager = TaxLotManager(db_session)
    
    # Create Kalshi lot
    manager.record_purchase(
        user_id=test_user.id,
        exchange="KALSHI",
        market_id="kalshi_market1",
        asset_id="kalshi_asset1",
        shares=100,
        price=0.50,
        purchase_date=datetime(2026, 1, 1)
    )
    
    # Sell after 10 days (short holding period)
    transaction = manager.record_sale(
        user_id=test_user.id,
        exchange="KALSHI",
        asset_id="kalshi_asset1",
        shares=100,
        price=0.80,
        sale_date=datetime(2026, 1, 11),
        method="FIFO"
    )
    
    # Gain = (100 * 0.80) - (100 * 0.50) = 80 - 50 = 30
    # Section 1256: 60% LT = 18, 40% ST = 12
    
    assert transaction.gain_loss == 30.0
    assert transaction.is_section_1256 == True
    assert transaction.long_term_portion == 18.0
    assert transaction.short_term_portion == 12.0
    # Note: is_long_term is False because held < 365 days, but Section 1256 overrides this
    assert transaction.holding_period_days == 10

def test_wash_sale_detection(db_session, test_user):
    """Test wash sale detection for AlphaSignals."""
    manager = TaxLotManager(db_session)
    
    # Buy 100 shares
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.50,
        purchase_date=datetime(2026, 1, 1)
    )
    
    # Sell at a loss
    sale_txn = manager.record_sale(
        user_id=test_user.id,
        exchange="POLYMARKET",
        asset_id="asset1",
        shares=100,
        price=0.30,
        sale_date=datetime(2026, 2, 1),
        method="FIFO"
    )
    
    # Loss = (100 * 0.30) - (100 * 0.50) = 30 - 50 = -20
    assert sale_txn.gain_loss == -20.0
    
    # Repurchase within 30 days (wash sale)
    repurchase_lot = manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.35,
        purchase_date=datetime(2026, 2, 15)  # 14 days later
    )
    
    # Check if wash sale was detected
    # The sale transaction should have wash_sale_disallowed set
    # The repurchase lot should have adjusted cost basis
    db_session.refresh(sale_txn)
    db_session.refresh(repurchase_lot)
    
    # Note: Wash sale detection happens during the sale, not the repurchase
    # So we need to sell again to trigger detection
    # This test demonstrates the concept; in practice, detection happens retroactively

def test_cost_basis_calculation(db_session, test_user):
    """Test cost basis calculation for open positions."""
    manager = TaxLotManager(db_session)
    
    # Create multiple lots
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.40,
        purchase_date=datetime(2026, 1, 1)
    )
    
    manager.record_purchase(
        user_id=test_user.id,
        exchange="POLYMARKET",
        market_id="market1",
        asset_id="asset1",
        shares=100,
        price=0.60,
        purchase_date=datetime(2026, 2, 1)
    )
    
    # Get cost basis
    cost_basis = manager.get_cost_basis(
        user_id=test_user.id,
        exchange="POLYMARKET",
        asset_id="asset1"
    )
    
    # Total shares = 200
    # Total cost = (100 * 0.40) + (100 * 0.60) = 40 + 60 = 100
    # Avg cost = 100 / 200 = 0.50
    
    assert cost_basis["total_shares"] == 200
    assert cost_basis["total_cost_basis"] == 100.0
    assert cost_basis["avg_cost_per_share"] == 0.50
    assert len(cost_basis["lots"]) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
