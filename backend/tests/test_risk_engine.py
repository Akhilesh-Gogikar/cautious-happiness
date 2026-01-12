import pytest
from app.risk_engine import RiskEngine
from app.models import TradeSignal, PortfolioPosition

def test_risk_exposure_limit():
    engine = RiskEngine()
    
    # Portfolio already has $400 exposure to Trump
    portfolio = [
        PortfolioPosition(
            asset_id="1", condition_id="c1", question="Will Trump win?", 
            outcome="Yes", price=0.5, size=800, svalue=400, pnl=0
        )
    ]
    
    # Propose adding $200 more to Trump (Limit is 500)
    # Total = 600 > 500 => Should Alert
    signal = TradeSignal(
        market_id="m2",
        market_question="Will Trump be elected?",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=200.0,
        expected_value=10.0,
        rationale="test",
        status="PENDING",
        timestamp=123.0
    )
    
    alerts = engine.check_portfolio_risk(signal, portfolio)
    assert len(alerts) > 0
    assert alerts[0].severity == "HIGH"
    assert "limit breach" in alerts[0].message

def test_correlation_limit():
    engine = RiskEngine()
    
    # Portfolio has $600 exposure to GOP Senate (Correlated with Trump)
    portfolio = [
        PortfolioPosition(
            asset_id="1", condition_id="c1", question="Will Republicans win Senate?", 
            outcome="Yes", price=0.5, size=1200, svalue=600, pnl=0
        )
    ]
    
    # Propose adding $300 to Trump
    # Correlation Trump <-> GOP Senate is 0.8
    # Total Correlated Exposure = 600 + 300 = 900 > 800 (Max Limit)
    signal = TradeSignal(
        market_id="m2",
        market_question="Will Trump win?",
        signal_side="BUY_YES",
        price_estimate=0.5,
        kelly_size_usd=300.0,
        expected_value=10.0,
        rationale="test",
        status="PENDING",
        timestamp=123.0
    )
    
    alerts = engine.check_portfolio_risk(signal, portfolio)
    # This might trigger two alerts: 
    # 1. Trump exposure (300 < 500, OK)
    # 2. Correlation exposure (900 > 800, WARN)
    
    assert any("correlation" in a.message.lower() for a in alerts)
