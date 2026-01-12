import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.attribution_models import TradeExecution, PositionSnapshot, AttributionMetrics
from app.attribution_service import AttributionService
from app.models import TradeSignal
from app.database_users import BaseUsers

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_attribution.db"
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
def attribution_service():
    """Create an attribution service instance."""
    return AttributionService()

@pytest.fixture
def sample_signal():
    """Create a sample trade signal."""
    return TradeSignal(
        market_id="test_market_123",
        market_question="Will Bitcoin hit $100k by 2025?",
        signal_side="BUY_YES",
        price_estimate=0.65,
        kelly_size_usd=1000.0,
        expected_value=150.0,
        rationale="Strong momentum detected",
        status="EXECUTED",
        timestamp=datetime.utcnow().timestamp(),
        tx_hash="0xtest123",
        model_used="openforecaster",
        data_sources=["RAG", "ALT_DATA"],
        strategy_type="KELLY",
        category="Economics",
        confidence_score=0.75
    )

def test_record_trade_with_attribution(db_session, attribution_service, sample_signal):
    """Test recording a trade with full attribution metadata."""
    trade = attribution_service.record_trade(
        db=db_session,
        user_id=1,
        signal=sample_signal,
        model_used="openforecaster",
        data_sources=["RAG", "ALT_DATA"],
        strategy_type="KELLY",
        category="Economics",
        entry_price=0.65,
        shares=1538.46,
        confidence_score=0.75,
        reasoning_snippet="Strong momentum detected"
    )
    
    assert trade.id is not None
    assert trade.market_id == "test_market_123"
    assert trade.model_used == "openforecaster"
    assert trade.data_sources == ["RAG", "ALT_DATA"]
    assert trade.strategy_type == "KELLY"
    assert trade.category == "Economics"
    assert trade.entry_price == 0.65
    assert trade.confidence_score == 0.75
    assert not trade.is_closed
    
    # Verify snapshot was created
    snapshots = db_session.query(PositionSnapshot).filter(
        PositionSnapshot.trade_id == trade.id
    ).all()
    assert len(snapshots) == 1

def test_calculate_pnl_single_position(db_session, attribution_service, sample_signal):
    """Test P&L calculation for a single position."""
    # Record trade
    trade = attribution_service.record_trade(
        db=db_session,
        user_id=1,
        signal=sample_signal,
        model_used="openforecaster",
        data_sources=["RAG"],
        strategy_type="KELLY",
        category="Economics",
        entry_price=0.65,
        shares=1538.46,
        confidence_score=0.75
    )
    
    # Update price
    attribution_service.update_position_prices(
        db=db_session,
        market_prices={"test_market_123": 0.75}
    )
    
    # Refresh trade
    db_session.refresh(trade)
    
    # P&L should be (0.75 - 0.65) * 1538.46 = 153.846
    assert trade.current_price == 0.75
    assert abs(trade.unrealized_pnl - 153.846) < 0.01

def test_attribution_breakdown_by_model(db_session, attribution_service):
    """Test aggregation by AI model."""
    # Create trades with different models
    for i, model in enumerate(["openforecaster", "gemini-critic", "openforecaster"]):
        signal = TradeSignal(
            market_id=f"market_{i}",
            market_question=f"Question {i}",
            signal_side="BUY_YES",
            price_estimate=0.5,
            kelly_size_usd=1000.0,
            expected_value=100.0,
            rationale="Test",
            status="EXECUTED",
            timestamp=datetime.utcnow().timestamp()
        )
        
        attribution_service.record_trade(
            db=db_session,
            user_id=1,
            signal=signal,
            model_used=model,
            data_sources=["RAG"],
            strategy_type="KELLY",
            category="Economics",
            entry_price=0.5,
            shares=2000.0
        )
    
    # Update prices to create P&L
    attribution_service.update_position_prices(
        db=db_session,
        market_prices={
            "market_0": 0.6,  # +200 P&L
            "market_1": 0.55,  # +100 P&L
            "market_2": 0.7   # +400 P&L
        }
    )
    
    # Get breakdown by model
    breakdown = attribution_service.get_attribution_by_dimension(
        db=db_session,
        user_id=1,
        dimension="model_used"
    )
    
    assert len(breakdown) == 2  # Two unique models
    
    # Find openforecaster (should have 2 trades, 600 P&L)
    openforecaster_data = next(b for b in breakdown if b["dimension_value"] == "openforecaster")
    assert openforecaster_data["total_trades"] == 2
    assert abs(openforecaster_data["total_pnl"] - 600.0) < 1.0

def test_attribution_breakdown_by_source(db_session, attribution_service):
    """Test aggregation by data source."""
    # Create trade with multiple sources
    signal = TradeSignal(
        market_id="market_1",
        market_question="Test question",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=1000.0,
        expected_value=100.0,
        rationale="Test",
        status="EXECUTED",
        timestamp=datetime.utcnow().timestamp()
    )
    
    attribution_service.record_trade(
        db=db_session,
        user_id=1,
        signal=signal,
        model_used="openforecaster",
        data_sources=["RAG", "ALT_DATA", "SOCIAL"],
        strategy_type="KELLY",
        category="Economics",
        entry_price=0.5,
        shares=2000.0
    )
    
    # Update price
    attribution_service.update_position_prices(
        db=db_session,
        market_prices={"market_1": 0.65}  # +300 P&L
    )
    
    # Get breakdown by source
    breakdown = attribution_service.get_attribution_by_data_source(
        db=db_session,
        user_id=1
    )
    
    # Should have 3 sources, each with proportional attribution (100 each)
    assert len(breakdown) == 3
    for source_data in breakdown:
        assert abs(source_data["total_pnl"] - 100.0) < 1.0

def test_time_series_pnl(db_session, attribution_service):
    """Test time-series data generation."""
    # Create a trade
    signal = TradeSignal(
        market_id="market_1",
        market_question="Test question",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=1000.0,
        expected_value=100.0,
        rationale="Test",
        status="EXECUTED",
        timestamp=datetime.utcnow().timestamp()
    )
    
    trade = attribution_service.record_trade(
        db=db_session,
        user_id=1,
        signal=signal,
        model_used="openforecaster",
        data_sources=["RAG"],
        strategy_type="KELLY",
        category="Economics",
        entry_price=0.5,
        shares=2000.0
    )
    
    # Create multiple snapshots
    for i in range(3):
        snapshot = PositionSnapshot(
            trade_id=trade.id,
            timestamp=datetime.utcnow() + timedelta(hours=i),
            current_price=0.5 + (i * 0.05),
            position_value=(0.5 + (i * 0.05)) * 2000.0,
            unrealized_pnl=(i * 0.05) * 2000.0,
            pnl_percent=(i * 0.05) / 0.5 * 100
        )
        db_session.add(snapshot)
    db_session.commit()
    
    # Get time series
    timeseries = attribution_service.get_time_series_pnl(
        db=db_session,
        user_id=1,
        interval="hour"
    )
    
    assert len(timeseries) > 0

def test_close_position(db_session, attribution_service, sample_signal):
    """Test closing a position and recording realized P&L."""
    # Record trade
    trade = attribution_service.record_trade(
        db=db_session,
        user_id=1,
        signal=sample_signal,
        model_used="openforecaster",
        data_sources=["RAG"],
        strategy_type="KELLY",
        category="Economics",
        entry_price=0.65,
        shares=1538.46
    )
    
    # Close position at higher price
    closed_trade = attribution_service.close_position(
        db=db_session,
        trade_id=trade.id,
        exit_price=0.75
    )
    
    assert closed_trade.is_closed
    assert closed_trade.closed_at is not None
    assert closed_trade.current_price == 0.75
    assert abs(closed_trade.realized_pnl - 153.846) < 0.01
    assert closed_trade.unrealized_pnl == 0.0

def test_attribution_summary(db_session, attribution_service):
    """Test overall attribution summary calculation."""
    # Create multiple trades
    for i in range(3):
        signal = TradeSignal(
            market_id=f"market_{i}",
            market_question=f"Question {i}",
            signal_side="BUY_YES",
            price_estimate=0.5,
            kelly_size_usd=1000.0,
            expected_value=100.0,
            rationale="Test",
            status="EXECUTED",
            timestamp=datetime.utcnow().timestamp()
        )
        
        attribution_service.record_trade(
            db=db_session,
            user_id=1,
            signal=signal,
            model_used="openforecaster",
            data_sources=["RAG"],
            strategy_type="KELLY",
            category="Economics",
            entry_price=0.5,
            shares=2000.0
        )
    
    # Update prices
    attribution_service.update_position_prices(
        db=db_session,
        market_prices={
            "market_0": 0.6,
            "market_1": 0.55,
            "market_2": 0.7
        }
    )
    
    # Get summary
    summary = attribution_service.get_attribution_summary(
        db=db_session,
        user_id=1
    )
    
    assert summary["total_trades"] == 3
    assert summary["open_positions"] == 3
    assert summary["closed_positions"] == 0
    assert abs(summary["total_pnl"] - 700.0) < 1.0  # 200 + 100 + 400
    assert summary["total_volume"] == 3000.0
