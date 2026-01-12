import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.tax_models import TaxLot, TaxTransaction, TaxSettings, WashSale
from app.tax_lot_service import TaxLotManager

logger = logging.getLogger(__name__)


class TaxCalculator:
    """
    Calculates tax obligations for different asset types.
    - Kalshi: Section 1256 treatment (60/40 split, mark-to-market)
    - AlphaSignals: Standard capital gains (short-term vs. long-term)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.lot_manager = TaxLotManager(db)
    
    def calculate_section_1256_gains(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict:
        """
        Calculate Section 1256 gains for Kalshi contracts.
        Applies 60% long-term / 40% short-term split regardless of holding period.
        
        Returns:
            Dict with total_gain_loss, long_term_portion, short_term_portion, transactions
        """
        transactions = self.db.query(TaxTransaction).filter(
            and_(
                TaxTransaction.user_id == user_id,
                TaxTransaction.exchange == "KALSHI",
                TaxTransaction.tax_year == tax_year,
                TaxTransaction.is_section_1256 == True
            )
        ).all()
        
        total_gain_loss = sum(t.gain_loss for t in transactions)
        long_term_portion = total_gain_loss * 0.60
        short_term_portion = total_gain_loss * 0.40
        
        return {
            "exchange": "KALSHI",
            "tax_year": tax_year,
            "total_gain_loss": total_gain_loss,
            "long_term_portion": long_term_portion,
            "short_term_portion": short_term_portion,
            "num_transactions": len(transactions),
            "transactions": [
                {
                    "transaction_id": t.id,
                    "market_question": t.market_question,
                    "transaction_date": t.transaction_date,
                    "shares": t.shares,
                    "proceeds": t.proceeds,
                    "cost_basis": t.cost_basis,
                    "gain_loss": t.gain_loss,
                    "long_term_portion": t.long_term_portion,
                    "short_term_portion": t.short_term_portion
                }
                for t in transactions
            ]
        }
    
    def mark_to_market_year_end(
        self,
        user_id: int,
        tax_year: int,
        current_prices: Dict[str, float]
    ) -> List[TaxTransaction]:
        """
        Perform year-end mark-to-market for Section 1256 contracts.
        Open positions are treated as if sold at fair market value on Dec 31.
        
        Args:
            user_id: User ID
            tax_year: Tax year
            current_prices: Dict mapping asset_id to year-end price
            
        Returns:
            List of created mark-to-market transactions
        """
        # Get all open Kalshi lots
        open_lots = self.db.query(TaxLot).filter(
            and_(
                TaxLot.user_id == user_id,
                TaxLot.exchange == "KALSHI",
                TaxLot.is_closed == False,
                TaxLot.shares_remaining > 0
            )
        ).all()
        
        mtm_transactions = []
        year_end = datetime(tax_year, 12, 31, 23, 59, 59)
        
        for lot in open_lots:
            current_price = current_prices.get(lot.asset_id)
            if current_price is None:
                logger.warning(f"No year-end price for {lot.asset_id}, skipping MTM")
                continue
            
            # Calculate unrealized gain/loss
            current_value = lot.shares_remaining * current_price
            cost_basis = lot.shares_remaining * lot.cost_basis_per_share
            gain_loss = current_value - cost_basis
            
            # Create mark-to-market transaction
            transaction = TaxTransaction(
                user_id=user_id,
                transaction_type="MARK_TO_MARKET",
                exchange="KALSHI",
                market_id=lot.market_id,
                asset_id=lot.asset_id,
                market_question=lot.market_question,
                transaction_date=year_end,
                shares=lot.shares_remaining,
                proceeds=current_value,
                cost_basis=cost_basis,
                gain_loss=gain_loss,
                holding_period_days=(year_end - lot.purchase_date).days,
                is_long_term=True,  # Section 1256 uses 60/40 regardless
                tax_year=tax_year,
                is_section_1256=True,
                long_term_portion=gain_loss * 0.60,
                short_term_portion=gain_loss * 0.40,
                lot_ids=[lot.id],
                matching_method="MTM"
            )
            
            self.db.add(transaction)
            mtm_transactions.append(transaction)
            
            logger.info(
                f"MTM: {lot.asset_id} - {lot.shares_remaining} shares, "
                f"gain/loss ${gain_loss:.2f}"
            )
        
        self.db.commit()
        return mtm_transactions
    
    def calculate_capital_gains(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict:
        """
        Calculate standard capital gains for AlphaSignals (DeFi assets).
        Separates short-term (≤365 days) and long-term (>365 days) gains.
        
        Returns:
            Dict with short_term, long_term, total, and transaction details
        """
        transactions = self.db.query(TaxTransaction).filter(
            and_(
                TaxTransaction.user_id == user_id,
                TaxTransaction.exchange == "POLYMARKET",
                TaxTransaction.tax_year == tax_year,
                TaxTransaction.transaction_type == "SALE"
            )
        ).all()
        
        short_term_gain = 0.0
        long_term_gain = 0.0
        short_term_txns = []
        long_term_txns = []
        
        for t in transactions:
            # Use adjusted gain/loss if wash sale applied
            gain_loss = t.adjusted_gain_loss if t.adjusted_gain_loss is not None else t.gain_loss
            
            txn_data = {
                "transaction_id": t.id,
                "market_question": t.market_question,
                "transaction_date": t.transaction_date,
                "shares": t.shares,
                "proceeds": t.proceeds,
                "cost_basis": t.cost_basis,
                "gain_loss": gain_loss,
                "holding_period_days": t.holding_period_days,
                "wash_sale_disallowed": t.wash_sale_disallowed
            }
            
            if t.is_long_term:
                long_term_gain += gain_loss
                long_term_txns.append(txn_data)
            else:
                short_term_gain += gain_loss
                short_term_txns.append(txn_data)
        
        return {
            "exchange": "POLYMARKET",
            "tax_year": tax_year,
            "short_term_gain": short_term_gain,
            "long_term_gain": long_term_gain,
            "total_gain": short_term_gain + long_term_gain,
            "num_short_term": len(short_term_txns),
            "num_long_term": len(long_term_txns),
            "short_term_transactions": short_term_txns,
            "long_term_transactions": long_term_txns
        }
    
    def apply_wash_sale_adjustments(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict:
        """
        Get summary of wash sale adjustments for the tax year.
        
        Returns:
            Dict with total disallowed losses and wash sale details
        """
        wash_sales = self.db.query(WashSale).filter(
            and_(
                WashSale.user_id == user_id,
                func.extract('year', WashSale.sale_date) == tax_year
            )
        ).all()
        
        total_disallowed = sum(ws.disallowed_loss for ws in wash_sales)
        
        return {
            "tax_year": tax_year,
            "total_disallowed_loss": total_disallowed,
            "num_wash_sales": len(wash_sales),
            "wash_sales": [
                {
                    "wash_sale_id": ws.id,
                    "asset_id": ws.asset_id,
                    "sale_date": ws.sale_date,
                    "repurchase_date": ws.repurchase_date,
                    "disallowed_loss": ws.disallowed_loss,
                    "adjusted_lot_id": ws.adjusted_lot_id
                }
                for ws in wash_sales
            ]
        }
    
    def generate_form_6781_data(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict:
        """
        Generate data for IRS Form 6781 (Section 1256 Contracts).
        
        Returns:
            Dict formatted for Form 6781 reporting
        """
        section_1256_data = self.calculate_section_1256_gains(user_id, tax_year)
        
        return {
            "form": "6781",
            "tax_year": tax_year,
            "part_i": {
                "description": "Section 1256 Contracts Marked to Market",
                "total_gain_loss": section_1256_data["total_gain_loss"],
                "long_term_portion": section_1256_data["long_term_portion"],
                "short_term_portion": section_1256_data["short_term_portion"]
            },
            "transactions": section_1256_data["transactions"],
            "instructions": (
                "Report 60% of gain/loss as long-term capital gain/loss on Schedule D, "
                "and 40% as short-term capital gain/loss on Schedule D."
            )
        }
    
    def generate_form_8949_data(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict:
        """
        Generate data for IRS Form 8949 / Schedule D (Capital Gains).
        
        Returns:
            Dict formatted for Form 8949 reporting
        """
        capital_gains = self.calculate_capital_gains(user_id, tax_year)
        wash_sales = self.apply_wash_sale_adjustments(user_id, tax_year)
        
        return {
            "form": "8949",
            "tax_year": tax_year,
            "part_i_short_term": {
                "description": "Short-Term Capital Gains and Losses (assets held ≤1 year)",
                "total_gain_loss": capital_gains["short_term_gain"],
                "num_transactions": capital_gains["num_short_term"],
                "transactions": capital_gains["short_term_transactions"]
            },
            "part_ii_long_term": {
                "description": "Long-Term Capital Gains and Losses (assets held >1 year)",
                "total_gain_loss": capital_gains["long_term_gain"],
                "num_transactions": capital_gains["num_long_term"],
                "transactions": capital_gains["long_term_transactions"]
            },
            "wash_sales": wash_sales,
            "instructions": (
                "Report short-term gains/losses on Schedule D Part I, "
                "and long-term gains/losses on Schedule D Part II. "
                "Wash sale losses have been disallowed and cost basis adjusted."
            )
        }
    
    def generate_tax_summary(
        self,
        user_id: int,
        tax_year: int,
        current_prices: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Generate comprehensive tax summary for the year.
        
        Returns:
            Complete tax summary with all exchanges and calculations
        """
        # Realized gains
        kalshi_data = self.calculate_section_1256_gains(user_id, tax_year)
        polymarket_data = self.calculate_capital_gains(user_id, tax_year)
        wash_sales = self.apply_wash_sale_adjustments(user_id, tax_year)
        
        # Unrealized gains (if prices provided)
        unrealized_kalshi = []
        unrealized_polymarket = []
        if current_prices:
            unrealized_kalshi = self.lot_manager.get_unrealized_gains(
                user_id, "KALSHI", current_prices
            )
            unrealized_polymarket = self.lot_manager.get_unrealized_gains(
                user_id, "POLYMARKET", current_prices
            )
        
        total_unrealized_kalshi = sum(p["unrealized_gain"] for p in unrealized_kalshi)
        total_unrealized_polymarket = sum(p["unrealized_gain"] for p in unrealized_polymarket)
        
        return {
            "tax_year": tax_year,
            "summary": {
                "kalshi": {
                    "realized_gain_loss": kalshi_data["total_gain_loss"],
                    "long_term_portion": kalshi_data["long_term_portion"],
                    "short_term_portion": kalshi_data["short_term_portion"],
                    "unrealized_gain_loss": total_unrealized_kalshi,
                    "num_transactions": kalshi_data["num_transactions"]
                },
                "polymarket": {
                    "realized_short_term": polymarket_data["short_term_gain"],
                    "realized_long_term": polymarket_data["long_term_gain"],
                    "realized_total": polymarket_data["total_gain"],
                    "unrealized_gain_loss": total_unrealized_polymarket,
                    "num_transactions": len(polymarket_data["short_term_transactions"]) + len(polymarket_data["long_term_transactions"]),
                    "wash_sale_disallowed": wash_sales["total_disallowed_loss"]
                },
                "combined": {
                    "total_realized": kalshi_data["total_gain_loss"] + polymarket_data["total_gain"],
                    "total_unrealized": total_unrealized_kalshi + total_unrealized_polymarket
                }
            },
            "kalshi_details": kalshi_data,
            "polymarket_details": polymarket_data,
            "wash_sales": wash_sales,
            "unrealized_positions": {
                "kalshi": unrealized_kalshi,
                "polymarket": unrealized_polymarket
            }
        }
    
    def get_tax_loss_harvesting_opportunities(
        self,
        user_id: int,
        current_prices: Dict[str, float],
        min_loss_threshold: float = 100.0
    ) -> List[Dict]:
        """
        Identify positions with unrealized losses for tax loss harvesting.
        
        Args:
            user_id: User ID
            current_prices: Current market prices
            min_loss_threshold: Minimum loss to consider (default $100)
            
        Returns:
            List of positions with unrealized losses
        """
        opportunities = []
        
        # Check both exchanges
        for exchange in ["KALSHI", "POLYMARKET"]:
            unrealized = self.lot_manager.get_unrealized_gains(
                user_id, exchange, current_prices
            )
            
            for position in unrealized:
                if position["unrealized_gain"] < -min_loss_threshold:
                    # Get lot details
                    cost_basis_info = self.lot_manager.get_cost_basis(
                        user_id, exchange, position["asset_id"]
                    )
                    
                    opportunities.append({
                        "exchange": exchange,
                        "asset_id": position["asset_id"],
                        "market_question": position["market_question"],
                        "shares": position["shares"],
                        "cost_basis": position["cost_basis"],
                        "current_value": position["current_value"],
                        "unrealized_loss": abs(position["unrealized_gain"]),
                        "unrealized_loss_pct": abs(position["unrealized_gain_pct"]),
                        "num_lots": position["num_lots"],
                        "lots": cost_basis_info["lots"],
                        "recommendation": (
                            "Consider selling to realize loss for tax purposes. "
                            "For AlphaSignals, avoid repurchasing within 30 days to prevent wash sale."
                        ) if exchange == "POLYMARKET" else (
                            "Section 1256 contracts are not subject to wash sale rules. "
                            "Can repurchase immediately if desired."
                        )
                    })
        
        # Sort by largest loss first
        opportunities.sort(key=lambda x: x["unrealized_loss"], reverse=True)
        
        return opportunities
