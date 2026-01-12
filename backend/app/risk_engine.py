import logging
from typing import List, Dict, Optional, Tuple
from app.models import TradeSignal, PortfolioPosition, RiskAlert

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        # Hardcoded correlation matrix for prototype
        # Scale: -1.0 to 1.0
        self.correlation_matrix: Dict[str, Dict[str, float]] = {
            "Politics.Trump": {
                "Politics.GOP_Senate": 0.8,
                "Politics.TaxCuts": 0.7,
                "Economy.Renewables": -0.6
            },
            "Politics.Biden": {
                "Politics.Dem_Senate": 0.8,
                "Economy.GreenEnergy": 0.7,
                "Economy.Oil": -0.5
            },
            "Politics.GOP_Senate": {
                "Politics.Trump": 0.8,
                "Politics.TaxCuts": 0.6
            }
        }
        
        # Risk Limits (USD)
        self.exposure_limits: Dict[str, float] = {
            "Politics.Trump": 500.0,
            "Politics.Biden": 500.0,
            "Sector.Tech": 1000.0
        }
        
        # Global max correlation exposure
        # If correlation > 0.7, max combined exposure allowed
        self.max_correlated_exposure = 800.0

    def get_market_factors(self, market_question: str) -> List[str]:
        """
        Heuristic to assign factors based on market text.
        In production, this would use the Classifier agent or DB tags.
        """
        factors = []
        q_lower = market_question.lower()
        
        if "trump" in q_lower:
            factors.append("Politics.Trump")
        if "biden" in q_lower or "democrat" in q_lower:
            factors.append("Politics.Biden")
        if "senate" in q_lower and "republican" in q_lower:
            factors.append("Politics.GOP_Senate")
        if "oil" in q_lower:
            factors.append("Economy.Oil")
            
        return factors

    def calculate_current_exposure(self, portfolio: List[PortfolioPosition], factor: str) -> float:
        """
        Sum of absolute value of positions exposed to this factor.
        """
        exposure = 0.0
        for pos in portfolio:
            # Check if position relates to factor
            # Ideally position has metadata, for now use question text matching
            pos_factors = self.get_market_factors(pos.question)
            if factor in pos_factors:
                exposure += pos.svalue
        return exposure

    def check_portfolio_risk(self, proposed_trade: TradeSignal, current_portfolio: List[PortfolioPosition]) -> List[RiskAlert]:
        """
        Evaluate if adding this trade breaches risk limits.
        """
        alerts = []
        trade_factors = self.get_market_factors(proposed_trade.market_question)
        trade_size = proposed_trade.kelly_size_usd
        
        # 1. Direct Factor Exposure Check
        for factor in trade_factors:
            current_exp = self.calculate_current_exposure(current_portfolio, factor)
            projected_exp = current_exp + trade_size
            limit = self.exposure_limits.get(factor, 2000.0) # Default limit
            
            if projected_exp > limit:
                alerts.append(RiskAlert(
                    severity="HIGH",
                    message=f"Exposure limit breach for {factor}: ${projected_exp:.2f} > ${limit:.2f}",
                    factor=factor,
                    current_exposure=current_exp,
                    proposed_add=trade_size
                ))
                
        # 2. Correlation Check
        # If we enter a trade, check if we are already heavy in highly correlated assets
        for factor in trade_factors:
            # Find correlated factors
            correlations = self.correlation_matrix.get(factor, {})
            for corr_factor, corr_val in correlations.items():
                if corr_val > 0.6: # Significant positive correlation
                    corr_exposure = self.calculate_current_exposure(current_portfolio, corr_factor)
                    if corr_exposure > 0:
                         # Check combined exposure logic or specific alerts
                         # For now, just alert if we are doubling down on a correlated outcome
                         if corr_exposure + trade_size > self.max_correlated_exposure:
                             alerts.append(RiskAlert(
                                severity="MEDIUM",
                                message=f"High correlation warning: {factor} is {corr_val} correlated with {corr_factor} (Exp: ${corr_exposure:.2f}). Total correlated risk exceeds limit.",
                                factor=f"{factor} <-> {corr_factor}",
                                current_exposure=corr_exposure,
                                proposed_add=trade_size
                             ))

        return alerts
