import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.tax_models import TaxLot, TaxTransaction, TaxSettings, WashSale, TaxTransactionLot
from app.models_db import User

logger = logging.getLogger(__name__)


class TaxLotManager:
    """
    Manages tax lot tracking and cost basis calculations.
    Supports FIFO, LIFO, and Specific Identification methods.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_purchase(
        self,
        user_id: int,
        exchange: str,
        market_id: str,
        asset_id: str,
        shares: float,
        price: float,
        purchase_date: datetime,
        market_question: Optional[str] = None,
        trade_execution_id: Optional[int] = None
    ) -> TaxLot:
        """
        Create a new tax lot for a purchase.
        
        Args:
            user_id: User ID
            exchange: "KALSHI" or "POLYMARKET"
            market_id: Market/condition ID
            asset_id: Specific asset/token ID
            shares: Number of shares purchased
            price: Price per share
            purchase_date: Date of purchase
            market_question: Optional market question text
            trade_execution_id: Optional link to TradeExecution record
            
        Returns:
            Created TaxLot instance
        """
        total_cost = shares * price
        
        lot = TaxLot(
            user_id=user_id,
            exchange=exchange.upper(),
            market_id=market_id,
            asset_id=asset_id,
            market_question=market_question,
            purchase_date=purchase_date,
            shares_purchased=shares,
            shares_remaining=shares,
            cost_basis_per_share=price,
            total_cost_basis=total_cost,
            is_closed=False,
            trade_execution_id=trade_execution_id
        )
        
        self.db.add(lot)
        self.db.commit()
        self.db.refresh(lot)
        
        logger.info(f"Created tax lot {lot.id}: {shares} shares @ ${price} on {exchange}")
        return lot
    
    def record_sale(
        self,
        user_id: int,
        exchange: str,
        asset_id: str,
        shares: float,
        price: float,
        sale_date: datetime,
        method: Optional[str] = None,
        specific_lot_ids: Optional[List[int]] = None,
        market_id: Optional[str] = None,
        market_question: Optional[str] = None,
        trade_execution_id: Optional[int] = None
    ) -> TaxTransaction:
        """
        Record a sale and match against existing lots.
        
        Args:
            user_id: User ID
            exchange: "KALSHI" or "POLYMARKET"
            asset_id: Asset being sold
            shares: Number of shares sold
            price: Sale price per share
            sale_date: Date of sale
            method: "FIFO", "LIFO", or "SPECID" (if None, uses user's default)
            specific_lot_ids: Required if method="SPECID"
            market_id: Optional market ID
            market_question: Optional market question
            trade_execution_id: Optional link to TradeExecution record
            
        Returns:
            Created TaxTransaction instance
        """
        # Get user's default method if not specified
        if method is None:
            method = self._get_user_method(user_id, exchange, sale_date.year)
        
        # Get open lots for this asset
        open_lots = self._get_open_lots(user_id, exchange, asset_id)
        
        if not open_lots:
            raise ValueError(f"No open lots found for {asset_id} on {exchange}")
        
        # Match lots based on method
        if method == "FIFO":
            matched_lots = self._match_fifo(open_lots, shares)
        elif method == "LIFO":
            matched_lots = self._match_lifo(open_lots, shares)
        elif method == "SPECID":
            if not specific_lot_ids:
                raise ValueError("specific_lot_ids required for SPECID method")
            matched_lots = self._match_specid(open_lots, shares, specific_lot_ids)
        else:
            raise ValueError(f"Invalid method: {method}")
        
        # Calculate total cost basis and proceeds
        total_cost_basis = sum(lot['cost_basis'] for lot in matched_lots)
        proceeds = shares * price
        gain_loss = proceeds - total_cost_basis
        
        # Calculate holding period (use weighted average)
        total_days = sum(
            (sale_date - lot['lot'].purchase_date).days * lot['shares']
            for lot in matched_lots
        )
        avg_holding_days = int(total_days / shares)
        is_long_term = avg_holding_days > 365
        
        # Determine if Section 1256 (Kalshi)
        is_section_1256 = exchange.upper() == "KALSHI"
        long_term_portion = None
        short_term_portion = None
        
        if is_section_1256:
            # 60/40 split for Section 1256 contracts
            long_term_portion = gain_loss * 0.60
            short_term_portion = gain_loss * 0.40
        
        # Create transaction
        transaction = TaxTransaction(
            user_id=user_id,
            transaction_type="SALE",
            exchange=exchange.upper(),
            market_id=market_id,
            asset_id=asset_id,
            market_question=market_question,
            transaction_date=sale_date,
            shares=shares,
            proceeds=proceeds,
            cost_basis=total_cost_basis,
            gain_loss=gain_loss,
            holding_period_days=avg_holding_days,
            is_long_term=is_long_term,
            tax_year=sale_date.year,
            is_section_1256=is_section_1256,
            long_term_portion=long_term_portion,
            short_term_portion=short_term_portion,
            lot_ids=[lot['lot'].id for lot in matched_lots],
            matching_method=method,
            trade_execution_id=trade_execution_id
        )
        
        self.db.add(transaction)
        self.db.flush()  # Get transaction ID
        
        # Create association records and update lots
        for match in matched_lots:
            lot = match['lot']
            shares_used = match['shares']
            cost_basis_used = match['cost_basis']
            
            # Create association record
            assoc = TaxTransactionLot(
                transaction_id=transaction.id,
                lot_id=lot.id,
                shares_from_lot=shares_used,
                cost_basis_from_lot=cost_basis_used
            )
            self.db.add(assoc)
            
            # Update lot
            lot.shares_remaining -= shares_used
            if lot.shares_remaining <= 0.0001:  # Handle floating point precision
                lot.shares_remaining = 0
                lot.is_closed = True
                lot.closed_at = sale_date
        
        # Check for wash sales (AlphaSignals only)
        if exchange.upper() == "POLYMARKET" and gain_loss < 0:
            wash_sale_adjustment = self._detect_wash_sales(
                user_id, asset_id, sale_date, abs(gain_loss), transaction.id
            )
            if wash_sale_adjustment > 0:
                transaction.wash_sale_disallowed = wash_sale_adjustment
                transaction.adjusted_gain_loss = gain_loss + wash_sale_adjustment
        
        self.db.commit()
        self.db.refresh(transaction)
        
        logger.info(
            f"Recorded sale: {shares} shares @ ${price}, "
            f"cost basis ${total_cost_basis:.2f}, "
            f"gain/loss ${gain_loss:.2f} ({method})"
        )
        
        return transaction
    
    def get_cost_basis(
        self,
        user_id: int,
        exchange: str,
        asset_id: str,
        method: Optional[str] = None
    ) -> Dict:
        """
        Calculate current cost basis for an asset.
        
        Returns:
            Dict with total_shares, total_cost_basis, avg_cost_per_share
        """
        open_lots = self._get_open_lots(user_id, exchange, asset_id)
        
        if not open_lots:
            return {
                "total_shares": 0,
                "total_cost_basis": 0,
                "avg_cost_per_share": 0,
                "lots": []
            }
        
        total_shares = sum(lot.shares_remaining for lot in open_lots)
        total_cost = sum(
            lot.shares_remaining * lot.cost_basis_per_share
            for lot in open_lots
        )
        avg_cost = total_cost / total_shares if total_shares > 0 else 0
        
        return {
            "total_shares": total_shares,
            "total_cost_basis": total_cost,
            "avg_cost_per_share": avg_cost,
            "lots": [
                {
                    "lot_id": lot.id,
                    "purchase_date": lot.purchase_date,
                    "shares": lot.shares_remaining,
                    "cost_per_share": lot.cost_basis_per_share,
                    "total_cost": lot.shares_remaining * lot.cost_basis_per_share
                }
                for lot in open_lots
            ]
        }
    
    def get_unrealized_gains(
        self,
        user_id: int,
        exchange: str,
        current_prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Calculate unrealized gains for all open positions.
        
        Args:
            user_id: User ID
            exchange: "KALSHI" or "POLYMARKET"
            current_prices: Dict mapping asset_id to current price
            
        Returns:
            List of dicts with unrealized gain/loss info
        """
        open_lots = self.db.query(TaxLot).filter(
            and_(
                TaxLot.user_id == user_id,
                TaxLot.exchange == exchange.upper(),
                TaxLot.is_closed == False
            )
        ).all()
        
        # Group by asset_id
        assets = {}
        for lot in open_lots:
            if lot.asset_id not in assets:
                assets[lot.asset_id] = {
                    "asset_id": lot.asset_id,
                    "market_question": lot.market_question,
                    "total_shares": 0,
                    "total_cost_basis": 0,
                    "lots": []
                }
            
            cost = lot.shares_remaining * lot.cost_basis_per_share
            assets[lot.asset_id]["total_shares"] += lot.shares_remaining
            assets[lot.asset_id]["total_cost_basis"] += cost
            assets[lot.asset_id]["lots"].append(lot)
        
        # Calculate unrealized gains
        results = []
        for asset_id, data in assets.items():
            current_price = current_prices.get(asset_id, 0)
            current_value = data["total_shares"] * current_price
            unrealized_gain = current_value - data["total_cost_basis"]
            
            results.append({
                "asset_id": asset_id,
                "market_question": data["market_question"],
                "shares": data["total_shares"],
                "cost_basis": data["total_cost_basis"],
                "current_price": current_price,
                "current_value": current_value,
                "unrealized_gain": unrealized_gain,
                "unrealized_gain_pct": (unrealized_gain / data["total_cost_basis"] * 100) if data["total_cost_basis"] > 0 else 0,
                "num_lots": len(data["lots"])
            })
        
        return results
    
    # Private helper methods
    
    def _get_user_method(self, user_id: int, exchange: str, tax_year: int) -> str:
        """Get user's preferred accounting method for an exchange."""
        settings = self.db.query(TaxSettings).filter(
            and_(
                TaxSettings.user_id == user_id,
                TaxSettings.tax_year == tax_year
            )
        ).first()
        
        if not settings:
            # Create default settings
            settings = TaxSettings(
                user_id=user_id,
                tax_year=tax_year,
                kalshi_method="FIFO",
                polymarket_method="FIFO",
                enable_wash_sale_detection=True
            )
            self.db.add(settings)
            self.db.commit()
        
        return settings.kalshi_method if exchange.upper() == "KALSHI" else settings.polymarket_method
    
    def _get_open_lots(self, user_id: int, exchange: str, asset_id: str) -> List[TaxLot]:
        """Get all open lots for an asset."""
        return self.db.query(TaxLot).filter(
            and_(
                TaxLot.user_id == user_id,
                TaxLot.exchange == exchange.upper(),
                TaxLot.asset_id == asset_id,
                TaxLot.is_closed == False,
                TaxLot.shares_remaining > 0
            )
        ).order_by(TaxLot.purchase_date.asc()).all()
    
    def _match_fifo(self, lots: List[TaxLot], shares_to_sell: float) -> List[Dict]:
        """
        Match lots using First-In-First-Out.
        
        Returns:
            List of dicts with 'lot', 'shares', 'cost_basis'
        """
        matched = []
        remaining = shares_to_sell
        
        # Lots are already sorted by purchase_date ascending
        for lot in lots:
            if remaining <= 0:
                break
            
            shares_from_lot = min(lot.shares_remaining, remaining)
            cost_basis = shares_from_lot * lot.cost_basis_per_share
            
            matched.append({
                "lot": lot,
                "shares": shares_from_lot,
                "cost_basis": cost_basis
            })
            
            remaining -= shares_from_lot
        
        if remaining > 0.0001:  # Handle floating point precision
            raise ValueError(f"Insufficient shares: need {shares_to_sell}, have {shares_to_sell - remaining}")
        
        return matched
    
    def _match_lifo(self, lots: List[TaxLot], shares_to_sell: float) -> List[Dict]:
        """
        Match lots using Last-In-First-Out.
        
        Returns:
            List of dicts with 'lot', 'shares', 'cost_basis'
        """
        matched = []
        remaining = shares_to_sell
        
        # Reverse order for LIFO (most recent first)
        for lot in reversed(lots):
            if remaining <= 0:
                break
            
            shares_from_lot = min(lot.shares_remaining, remaining)
            cost_basis = shares_from_lot * lot.cost_basis_per_share
            
            matched.append({
                "lot": lot,
                "shares": shares_from_lot,
                "cost_basis": cost_basis
            })
            
            remaining -= shares_from_lot
        
        if remaining > 0.0001:
            raise ValueError(f"Insufficient shares: need {shares_to_sell}, have {shares_to_sell - remaining}")
        
        return matched
    
    def _match_specid(
        self,
        lots: List[TaxLot],
        shares_to_sell: float,
        lot_ids: List[int]
    ) -> List[Dict]:
        """
        Match specific lots by ID.
        
        Returns:
            List of dicts with 'lot', 'shares', 'cost_basis'
        """
        matched = []
        remaining = shares_to_sell
        
        # Create lookup dict
        lot_dict = {lot.id: lot for lot in lots}
        
        for lot_id in lot_ids:
            if remaining <= 0:
                break
            
            if lot_id not in lot_dict:
                raise ValueError(f"Lot {lot_id} not found or already closed")
            
            lot = lot_dict[lot_id]
            shares_from_lot = min(lot.shares_remaining, remaining)
            cost_basis = shares_from_lot * lot.cost_basis_per_share
            
            matched.append({
                "lot": lot,
                "shares": shares_from_lot,
                "cost_basis": cost_basis
            })
            
            remaining -= shares_from_lot
        
        if remaining > 0.0001:
            raise ValueError(f"Specified lots insufficient: need {shares_to_sell}, have {shares_to_sell - remaining}")
        
        return matched
    
    def _detect_wash_sales(
        self,
        user_id: int,
        asset_id: str,
        sale_date: datetime,
        loss_amount: float,
        transaction_id: int
    ) -> float:
        """
        Detect wash sales: repurchase within 30 days of a loss sale.
        
        Returns:
            Amount of loss to disallow
        """
        # Get user's wash sale setting
        settings = self.db.query(TaxSettings).filter(
            and_(
                TaxSettings.user_id == user_id,
                TaxSettings.tax_year == sale_date.year
            )
        ).first()
        
        if not settings or not settings.enable_wash_sale_detection:
            return 0.0
        
        # Check for purchases within 30 days before or after sale
        wash_sale_start = sale_date - timedelta(days=30)
        wash_sale_end = sale_date + timedelta(days=30)
        
        repurchase_lots = self.db.query(TaxLot).filter(
            and_(
                TaxLot.user_id == user_id,
                TaxLot.asset_id == asset_id,
                TaxLot.exchange == "POLYMARKET",  # Wash sales only apply to AlphaSignals
                TaxLot.purchase_date >= wash_sale_start,
                TaxLot.purchase_date <= wash_sale_end,
                TaxLot.purchase_date != sale_date  # Exclude same-day
            )
        ).order_by(TaxLot.purchase_date.asc()).first()
        
        if repurchase_lots:
            # Wash sale detected - disallow the loss
            wash_sale = WashSale(
                user_id=user_id,
                asset_id=asset_id,
                sale_transaction_id=transaction_id,
                sale_date=sale_date,
                repurchase_date=repurchase_lots.purchase_date,
                disallowed_loss=loss_amount,
                adjusted_lot_id=repurchase_lots.id
            )
            self.db.add(wash_sale)
            
            # Adjust the repurchase lot's cost basis
            repurchase_lots.cost_basis_per_share += (loss_amount / repurchase_lots.shares_purchased)
            repurchase_lots.total_cost_basis += loss_amount
            repurchase_lots.notes = f"Wash sale adjustment: +${loss_amount:.2f}"
            
            logger.warning(
                f"Wash sale detected: ${loss_amount:.2f} loss disallowed, "
                f"adjusted lot {repurchase_lots.id}"
            )
            
            return loss_amount
        
        return 0.0
