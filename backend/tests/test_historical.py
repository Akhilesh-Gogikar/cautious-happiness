import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_users import BaseUsers
from app import models_db, models
from datetime import datetime

# setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_historical.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    BaseUsers.metadata.create_all(bind=engine)
    yield
    BaseUsers.metadata.drop_all(bind=engine)

def test_historical_market_model():
    """Test that we can create and retrieve historical markets"""
    db = TestingSessionLocal()
    try:
        market = models_db.HistoricalMarket(
            market_id="test_123",
            question="Will it rain tomorrow?",
            outcome="Yes",
            close_time=datetime.utcnow(),
            category="Weather",
            volume=1000.0,
            metadata_json={"test": "data"}
        )
        db.add(market)
        db.commit()
        
        # Retrieve
        retrieved = db.query(models_db.HistoricalMarket).filter(
            models_db.HistoricalMarket.market_id == "test_123"
        ).first()
        
        assert retrieved is not None
        assert retrieved.question == "Will it rain tomorrow?"
        assert retrieved.outcome == "Yes"
        assert retrieved.category == "Weather"
    finally:
        db.close()

def test_backtest_result_model():
    """Test that we can create backtest results linked to markets"""
    db = TestingSessionLocal()
    try:
        # Create user
        user = models_db.User(
            email="test@example.com",
            hashed_password="hashed",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create market
        market = models_db.HistoricalMarket(
            market_id="test_456",
            question="Will BTC hit $100k?",
            outcome="No",
            close_time=datetime.utcnow(),
            category="Crypto",
            volume=5000.0
        )
        db.add(market)
        db.commit()
        
        # Create backtest result
        result = models_db.BacktestResult(
            user_id=user.id,
            market_id=market.id,
            model_name="test_model",
            predicted_outcome=0.75,
            reasoning="Test reasoning"
        )
        db.add(result)
        db.commit()
        
        # Retrieve and verify
        retrieved = db.query(models_db.BacktestResult).first()
        assert retrieved is not None
        assert retrieved.predicted_outcome == 0.75
        assert retrieved.model_name == "test_model"
        assert retrieved.market.question == "Will BTC hit $100k?"
    finally:
        db.close()
