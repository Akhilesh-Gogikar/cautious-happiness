import logging
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app.attribution_models import TradeExecution, PositionSnapshot, AttributionMetrics
from app.models import TradeSignal
import statistics

logger = logging.getLogger(__name__)


class AttributionService:
    """
    Service for tracking and calculating P&L attribution across models, data sources, and strategies.
    """
    
    def record_trade(
        self,
        db: Session,
        user_id: int,
        signal: TradeSignal,
        model_used: str,
        data_sources: List[str],
        strategy_type: str,
        category: str,
        entry_price: float,
        shares: float,
        confidence_score: Optional[float] = None,
        reasoning_snippet: Optional[str] = None
    ) -> TradeExecution:
        """
        Record a new trade execution with full attribution metadata.
        
        Args:
            db: Database session
            user_id: User ID
            signal: TradeSignal object
            model_used: AI model name (e.g., "openforecaster")
            data_sources: List of data sources (e.g., ["RAG", "ALT_DATA"])
            strategy_type: Strategy classification (e.g., "KELLY", "ARBITRAGE")
            category: Market category (e.g., "Economics", "Politics")
            entry_price: Actual entry price
            shares: Number of shares/tokens purchased
            confidence_score: Model confidence (0-1)
            reasoning_snippet: First 200 chars of reasoning
        """
        trade = TradeExecution(
            user_id=user_id,
            market_id=signal.market_id,
            market_question=signal.market_question,
            side=signal.signal_side,
            entry_price=entry_price,
            size_usd=signal.kelly_size_usd,
            shares=shares,
            tx_hash=signal.tx_hash,
            model_used=model_used,
            data_sources=data_sources,
            strategy_type=strategy_type,
            category=category,
            current_price=entry_price,  # Initially same as entry
            confidence_score=confidence_score,
            reasoning_snippet=reasoning_snippet[:200] if reasoning_snippet else None,
            execution_metadata={
                "expected_value": signal.expected_value,
                "rationale": signal.rationale[:500] if signal.rationale else ""
            }
        )
        
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        # Create initial snapshot
        self._create_snapshot(db, trade, entry_price)
        
        logger.info(f"Recorded trade {trade.id} with attribution: model={model_used}, strategy={strategy_type}")
        return trade
    
    def update_position_prices(self, db: Session, market_prices: Dict[str, float]):
        """
        Update current prices for open positions and recalculate P&L.
        
        Args:
            db: Database session
            market_prices: Dict mapping market_id to current price
        """
        open_trades = db.query(TradeExecution).filter(
            TradeExecution.is_closed == False
        ).all()
        
        for trade in open_trades:
            if trade.market_id in market_prices:
                new_price = market_prices[trade.market_id]
                old_price = trade.current_price
                
                # Update price and P&L
                trade.current_price = new_price
                trade.unrealized_pnl = self._calculate_pnl(
                    trade.entry_price, new_price, trade.shares, trade.side
                )
                trade.last_updated = datetime.utcnow()
                
                # Create snapshot if significant price change (>1%)
                if abs(new_price - old_price) / old_price > 0.01:
                    self._create_snapshot(db, trade, new_price)
        
        db.commit()
    
    def close_position(
        self,
        db: Session,
        trade_id: int,
        exit_price: float,
        exit_time: Optional[datetime] = None
    ) -> TradeExecution:
        """
        Close a position and record realized P&L.
        """
        trade = db.query(TradeExecution).filter(TradeExecution.id == trade_id).first()
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        trade.is_closed = True
        trade.closed_at = exit_time or datetime.utcnow()
        trade.current_price = exit_price
        trade.realized_pnl = self._calculate_pnl(
            trade.entry_price, exit_price, trade.shares, trade.side
        )
        trade.unrealized_pnl = 0.0
        
        # Create final snapshot
        self._create_snapshot(db, trade, exit_price)
        
        db.commit()
        db.refresh(trade)
        return trade
    
    def get_attribution_summary(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get overall P&L attribution summary.
        """
        query = db.query(TradeExecution).filter(TradeExecution.user_id == user_id)
        
        if start_date:
            query = query.filter(TradeExecution.executed_at >= start_date)
        if end_date:
            query = query.filter(TradeExecution.executed_at <= end_date)
        
        trades = query.all()
        
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "total_volume": 0.0,
                "win_rate": 0.0,
                "avg_pnl_per_trade": 0.0
            }
        
        total_pnl = sum((t.realized_pnl or 0.0) + t.unrealized_pnl for t in trades)
        realized_pnl = sum(t.realized_pnl or 0.0 for t in trades if t.is_closed)
        unrealized_pnl = sum(t.unrealized_pnl for t in trades if not t.is_closed)
        total_volume = sum(t.size_usd for t in trades)
        
        closed_trades = [t for t in trades if t.is_closed and t.realized_pnl is not None]
        winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0.0
        
        return {
            "total_trades": len(trades),
            "total_pnl": total_pnl,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_volume": total_volume,
            "win_rate": win_rate,
            "avg_pnl_per_trade": total_pnl / len(trades) if trades else 0.0,
            "open_positions": len([t for t in trades if not t.is_closed]),
            "closed_positions": len([t for t in trades if t.is_closed])
        }
    
    def get_attribution_by_dimension(
        self,
        db: Session,
        user_id: int,
        dimension: str,  # "model_used", "strategy_type", "category"
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get P&L breakdown by a specific dimension (model, strategy, or category).
        """
        query = db.query(TradeExecution).filter(TradeExecution.user_id == user_id)
        
        if start_date:
            query = query.filter(TradeExecution.executed_at >= start_date)
        if end_date:
            query = query.filter(TradeExecution.executed_at <= end_date)
        
        trades = query.all()
        
        # Group by dimension
        grouped = {}
        for trade in trades:
            key = getattr(trade, dimension)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(trade)
        
        # Calculate metrics for each group
        results = []
        for key, group_trades in grouped.items():
            total_pnl = sum((t.realized_pnl or 0.0) + t.unrealized_pnl for t in group_trades)
            realized_pnl = sum(t.realized_pnl or 0.0 for t in group_trades if t.is_closed)
            unrealized_pnl = sum(t.unrealized_pnl for t in group_trades if not t.is_closed)
            
            closed_trades = [t for t in group_trades if t.is_closed and t.realized_pnl is not None]
            winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
            win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0.0
            
            results.append({
                "dimension_value": key,
                "total_trades": len(group_trades),
                "total_pnl": total_pnl,
                "realized_pnl": realized_pnl,
                "unrealized_pnl": unrealized_pnl,
                "total_volume": sum(t.size_usd for t in group_trades),
                "win_rate": win_rate,
                "avg_pnl_per_trade": total_pnl / len(group_trades)
            })
        
        # Sort by total P&L descending
        results.sort(key=lambda x: x["total_pnl"], reverse=True)
        return results
    
    def get_attribution_by_data_source(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get P&L breakdown by data source.
        Note: A trade can use multiple data sources, so we attribute proportionally.
        """
        query = db.query(TradeExecution).filter(TradeExecution.user_id == user_id)
        
        if start_date:
            query = query.filter(TradeExecution.executed_at >= start_date)
        if end_date:
            query = query.filter(TradeExecution.executed_at <= end_date)
        
        trades = query.all()
        
        # Aggregate by data source (with proportional attribution)
        source_metrics = {}
        
        for trade in trades:
            sources = trade.data_sources or []
            if not sources:
                sources = ["UNKNOWN"]
            
            # Proportional attribution
            pnl_per_source = ((trade.realized_pnl or 0.0) + trade.unrealized_pnl) / len(sources)
            volume_per_source = trade.size_usd / len(sources)
            
            for source in sources:
                if source not in source_metrics:
                    source_metrics[source] = {
                        "trades": [],
                        "total_pnl": 0.0,
                        "total_volume": 0.0
                    }
                
                source_metrics[source]["trades"].append(trade)
                source_metrics[source]["total_pnl"] += pnl_per_source
                source_metrics[source]["total_volume"] += volume_per_source
        
        # Format results
        results = []
        for source, metrics in source_metrics.items():
            results.append({
                "data_source": source,
                "total_trades": len(metrics["trades"]),
                "total_pnl": metrics["total_pnl"],
                "total_volume": metrics["total_volume"],
                "avg_pnl_per_trade": metrics["total_pnl"] / len(metrics["trades"])
            })
        
        results.sort(key=lambda x: x["total_pnl"], reverse=True)
        return results
    
    def get_time_series_pnl(
        self,
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "day"  # "hour", "day", "week"
    ) -> List[Dict[str, Any]]:
        """
        Get time-series P&L data for charting.
        """
        # Get all trades for user
        query = db.query(TradeExecution).filter(TradeExecution.user_id == user_id)
        
        if start_date:
            query = query.filter(TradeExecution.executed_at >= start_date)
        if end_date:
            query = query.filter(TradeExecution.executed_at <= end_date)
        
        trades = query.order_by(TradeExecution.executed_at).all()
        
        if not trades:
            return []
        
        # Get all snapshots for these trades
        trade_ids = [t.id for t in trades]
        snapshots = db.query(PositionSnapshot).filter(
            PositionSnapshot.trade_id.in_(trade_ids)
        ).order_by(PositionSnapshot.timestamp).all()
        
        # Build time series
        time_series = []
        cumulative_pnl = 0.0
        
        # Group snapshots by time interval
        if interval == "hour":
            delta = timedelta(hours=1)
        elif interval == "day":
            delta = timedelta(days=1)
        else:  # week
            delta = timedelta(weeks=1)
        
        if not snapshots:
            return []
        
        current_time = snapshots[0].timestamp
        end_time = snapshots[-1].timestamp
        
        while current_time <= end_time:
            # Get snapshots in this interval
            interval_end = current_time + delta
            interval_snapshots = [
                s for s in snapshots
                if current_time <= s.timestamp < interval_end
            ]
            
            if interval_snapshots:
                # Sum P&L from all positions at this time
                total_pnl = sum(s.unrealized_pnl for s in interval_snapshots)
                cumulative_pnl = total_pnl  # Simplified - in reality would track cumulative
                
                time_series.append({
                    "timestamp": current_time.isoformat(),
                    "pnl": total_pnl,
                    "cumulative_pnl": cumulative_pnl,
                    "num_positions": len(set(s.trade_id for s in interval_snapshots))
                })
            
            current_time = interval_end
        
        return time_series
    
    def get_trades_with_attribution(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get list of trades with full attribution details.
        """
        query = db.query(TradeExecution).filter(TradeExecution.user_id == user_id)
        
        # Apply filters
        if filters:
            if filters.get("model_used"):
                query = query.filter(TradeExecution.model_used == filters["model_used"])
            if filters.get("strategy_type"):
                query = query.filter(TradeExecution.strategy_type == filters["strategy_type"])
            if filters.get("category"):
                query = query.filter(TradeExecution.category == filters["category"])
            if filters.get("is_closed") is not None:
                query = query.filter(TradeExecution.is_closed == filters["is_closed"])
            if filters.get("start_date"):
                query = query.filter(TradeExecution.executed_at >= filters["start_date"])
            if filters.get("end_date"):
                query = query.filter(TradeExecution.executed_at <= filters["end_date"])
        
        total = query.count()
        trades = query.order_by(TradeExecution.executed_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "trades": [self._trade_to_dict(t) for t in trades]
        }
    
    def _calculate_pnl(self, entry_price: float, current_price: float, shares: float, side: str) -> float:
        """
        Calculate P&L for a position.
        """
        if "BUY" in side:
            # Long position: profit when price goes up
            return (current_price - entry_price) * shares
        else:
            # Short position: profit when price goes down
            return (entry_price - current_price) * shares
    
    def _create_snapshot(self, db: Session, trade: TradeExecution, current_price: float):
        """
        Create a position snapshot for time-series tracking.
        """
        pnl = self._calculate_pnl(trade.entry_price, current_price, trade.shares, trade.side)
        position_value = current_price * trade.shares
        pnl_percent = (pnl / trade.size_usd * 100) if trade.size_usd > 0 else 0.0
        
        snapshot = PositionSnapshot(
            trade_id=trade.id,
            current_price=current_price,
            position_value=position_value,
            unrealized_pnl=pnl,
            pnl_percent=pnl_percent
        )
        
        db.add(snapshot)
        db.commit()
    
    def _trade_to_dict(self, trade: TradeExecution) -> Dict[str, Any]:
        """
        Convert TradeExecution to dictionary for API response.
        """
        return {
            "id": trade.id,
            "market_id": trade.market_id,
            "market_question": trade.market_question,
            "side": trade.side,
            "entry_price": trade.entry_price,
            "current_price": trade.current_price,
            "size_usd": trade.size_usd,
            "shares": trade.shares,
            "model_used": trade.model_used,
            "data_sources": trade.data_sources,
            "strategy_type": trade.strategy_type,
            "category": trade.category,
            "unrealized_pnl": trade.unrealized_pnl,
            "realized_pnl": trade.realized_pnl,
            "is_closed": trade.is_closed,
            "confidence_score": trade.confidence_score,
            "executed_at": trade.executed_at.isoformat(),
            "closed_at": trade.closed_at.isoformat() if trade.closed_at else None,
            "tx_hash": trade.tx_hash
        }
