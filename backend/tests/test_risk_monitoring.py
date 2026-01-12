import pytest
from app.risk_monitoring import RiskMonitor
from app.models import RiskLevel

def test_risk_monitor_report():
    monitor = RiskMonitor()
    report = monitor.get_latest_report()
    
    assert report.overall_health in [RiskLevel.NORMAL, RiskLevel.WARNING, RiskLevel.CRITICAL]
    assert len(report.components) == 3
    
    component_names = [c.name for c in report.components]
    assert "POLYGON_BRIDGE" in component_names
    assert "POLYMARKET_CONTRACTS" in component_names
    assert "USDC_STABILITY" in component_names

def test_bridge_health():
    monitor = RiskMonitor()
    status = monitor.check_bridge_health()
    assert status.name == "POLYGON_BRIDGE"
    assert status.level in [RiskLevel.NORMAL, RiskLevel.WARNING]

def test_stablecoin_peg():
    monitor = RiskMonitor()
    status = monitor.check_stablecoin_peg()
    assert status.name == "USDC_STABILITY"
    assert status.level in [RiskLevel.NORMAL, RiskLevel.WARNING, RiskLevel.CRITICAL]
