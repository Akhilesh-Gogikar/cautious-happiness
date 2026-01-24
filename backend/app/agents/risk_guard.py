from typing import Any, Dict, List
from app.agents.base import BaseAgent
from app.risk_engine import RiskEngine
from app.models import TradeSignal, PortfolioPosition

class RiskGuardAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Risk-Guard", role="Risk Manager")
        self.risk_engine = RiskEngine()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "BUSY"
        query = input_data.get("query", "")
        proposed_prob = input_data.get("probability", 0.5)
        self.current_task = f"Assessing risk for {query} with p={proposed_prob}"
        self.log(f"Starting risk assessment for: {query}")

        try:
            # In a real scenario, we'd fetch the actual portfolio from a DB
            # For now, we'll use a mock portfolio or take it from input
            portfolio = input_data.get("portfolio", [])
            
            # Create a mock TradeSignal to check risk
            mock_signal = TradeSignal(
                market_id="temp_id",
                market_question=query,
                signal_side="BUY_YES" if proposed_prob > 0.5 else "BUY_NO",
                price_estimate=0.5, # Placeholder
                kelly_size_usd=100.0, # Test size
                expected_value=0.0,
                rationale="Risk check",
                status="PENDING",
                timestamp=0.0
            )

            risk_alerts = self.risk_engine.check_portfolio_risk(mock_signal, portfolio)
            
            severity = "LOW"
            if any(a.severity == "HIGH" for a in risk_alerts):
                severity = "HIGH"
            elif any(a.severity == "MEDIUM" for a in risk_alerts):
                severity = "MEDIUM"

            self.log(f"Risk assessment complete. Severity: {severity}, Alerts: {len(risk_alerts)}", level="SUCCESS")
            
            self.status = "COMPLETED"
            return {
                "agent": self.name,
                "risk_severity": severity,
                "alerts": [a.message for a in risk_alerts],
                "verdict": "REJECTED" if severity == "HIGH" else "APPROVED",
                "timestamp": self.logs[-1]["timestamp"]
            }
        except Exception as e:
            self.status = "ERROR"
            self.log(f"Risk assessment failed: {str(e)}", level="ERROR")
            return {"error": str(e)}
