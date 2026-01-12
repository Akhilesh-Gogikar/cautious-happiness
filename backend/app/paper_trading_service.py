import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np

from app.models_db import PaperTradingSession, PaperTrade, PaperPosition
from app.paper_trading_client import PaperTradingClient
from app.paper_trading_models import (
    PaperSessionResponse, PaperTradeResponse, PaperPositionResponse,
    PaperPerformanceResponse, SessionComparisonResponse
)

logger = logging.getLogger(__name__)


class PaperTradingService:
    """Service layer for paper trading operations."""
    
    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        model_name: str,
        model_version: str = "default",
        initial_balance: float = 10000.0,
        description: Optional[str] = None
    ) -> PaperTradingSession:
        """
        Create a new paper trading session.
        
        Args:
            db: Database session
            user_id: User ID
            model_name: Name of the LLM model being tested
            model_version: Version/weight identifier
            initial_balance: Starting virtual balance
            description: Optional session description
        
        Returns:
            Created PaperTradingSession
        """
        session = PaperTradingSession(
            user_id=user_id,
            model_name=model_name,
            model_version=model_version,
            initial_balance=initial_balance,
            current_balance=initial_balance,
            metadata_json={'description': description} if description else {}
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created paper trading session {session.id} for user {user_id}")
        return session
    
    @staticmethod
    def end_session(db: Session, session_id: int) -> PaperTradingSession:
        """
        End a paper trading session and finalize metrics.
        
        Args:
            db: Database session
            session_id: Session ID to end
        
        Returns:
            Updated PaperTradingSession
        """
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if session.status != "ACTIVE":
            raise ValueError(f"Session {session_id} is not active")
        
        # Calculate final metrics
        performance = PaperTradingService.get_session_performance(db, session_id)
        
        session.status = "COMPLETED"
        session.end_time = datetime.utcnow()
        session.total_pnl = performance['total_pnl']
        session.win_rate = performance['win_rate']
        session.max_drawdown = performance['max_drawdown']
        session.sharpe_ratio = performance.get('sharpe_ratio')
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Ended paper trading session {session_id}")
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[PaperTradingSession]:
        """Get a paper trading session by ID."""
        return db.query(PaperTradingSession).filter(
            PaperTradingSession.id == session_id
        ).first()
    
    @staticmethod
    def get_active_session(db: Session, user_id: int) -> Optional[PaperTradingSession]:
        """Get the active paper trading session for a user."""
        return db.query(PaperTradingSession).filter(
            PaperTradingSession.user_id == user_id,
            PaperTradingSession.status == "ACTIVE"
        ).first()
    
    @staticmethod
    def record_trade(
        db: Session,
        session_id: int,
        market_id: str,
        market_question: str,
        side: str,
        entry_price: float,
        shares: float,
        execution_strategy: str = "SINGLE"
    ) -> PaperTrade:
        """
        Record a paper trade.
        
        Args:
            db: Database session
            session_id: Paper trading session ID
            market_id: Market ID
            market_question: Market question text
            side: Trade side (BUY_YES, BUY_NO, SELL)
            entry_price: Entry price
            shares: Number of shares
            execution_strategy: Execution strategy used
        
        Returns:
            Created PaperTrade
        """
        trade = PaperTrade(
            session_id=session_id,
            market_id=market_id,
            market_question=market_question,
            side=side,
            entry_price=entry_price,
            shares=shares,
            execution_strategy=execution_strategy
        )
        
        db.add(trade)
        
        # Update session trade count
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.id == session_id
        ).first()
        if session:
            session.num_trades += 1
        
        db.commit()
        db.refresh(trade)
        
        return trade
    
    @staticmethod
    def update_position(
        db: Session,
        session_id: int,
        market_id: str,
        shares: float,
        avg_entry_price: float,
        current_price: float
    ) -> PaperPosition:
        """
        Update or create a paper position.
        
        Args:
            db: Database session
            session_id: Paper trading session ID
            market_id: Market ID
            shares: Current shares held
            avg_entry_price: Average entry price
            current_price: Current market price
        
        Returns:
            Updated/created PaperPosition
        """
        position = db.query(PaperPosition).filter(
            PaperPosition.session_id == session_id,
            PaperPosition.market_id == market_id
        ).first()
        
        unrealized_pnl = (current_price - avg_entry_price) * shares
        
        if position:
            position.shares = shares
            position.avg_entry_price = avg_entry_price
            position.current_price = current_price
            position.unrealized_pnl = unrealized_pnl
            position.last_updated = datetime.utcnow()
        else:
            position = PaperPosition(
                session_id=session_id,
                market_id=market_id,
                shares=shares,
                avg_entry_price=avg_entry_price,
                current_price=current_price,
                unrealized_pnl=unrealized_pnl
            )
            db.add(position)
        
        db.commit()
        db.refresh(position)
        
        return position
    
    @staticmethod
    def get_session_performance(db: Session, session_id: int) -> Dict:
        """
        Calculate comprehensive performance metrics for a session.
        
        Args:
            db: Database session
            session_id: Paper trading session ID
        
        Returns:
            Dictionary with performance metrics
        """
        session = db.query(PaperTradingSession).filter(
            PaperTradingSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Get all trades
        trades = db.query(PaperTrade).filter(
            PaperTrade.session_id == session_id
        ).all()
        
        # Get current positions
        positions = db.query(PaperPosition).filter(
            PaperPosition.session_id == session_id
        ).all()
        
        # Calculate metrics
        num_trades = len(trades)
        realized_pnl = sum(t.realized_pnl for t in trades if t.status == "CLOSED")
        unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        total_pnl = realized_pnl + unrealized_pnl
        
        # Win rate
        closed_trades = [t for t in trades if t.status == "CLOSED"]
        winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0.0
        
        # Total value
        total_exposure = sum(p.shares * p.current_price for p in positions)
        total_value = session.current_balance + total_exposure
        
        # Total return
        total_return_pct = ((total_value - session.initial_balance) / session.initial_balance * 100)
        
        # Average trade P&L
        avg_trade_pnl = (realized_pnl / len(closed_trades)) if closed_trades else None
        
        # Sharpe ratio (simplified - would need daily returns for proper calculation)
        sharpe_ratio = None
        if closed_trades and len(closed_trades) > 1:
            pnls = [t.realized_pnl for t in closed_trades]
            mean_pnl = np.mean(pnls)
            std_pnl = np.std(pnls)
            if std_pnl > 0:
                sharpe_ratio = (mean_pnl / std_pnl) * np.sqrt(252)  # Annualized
        
        # Max drawdown (simplified - based on cumulative P&L)
        max_drawdown = 0.0
        if closed_trades:
            cumulative_pnl = 0.0
            peak = 0.0
            for trade in sorted(closed_trades, key=lambda t: t.entry_time):
                cumulative_pnl += trade.realized_pnl
                peak = max(peak, cumulative_pnl)
                drawdown = peak - cumulative_pnl
                max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'session_id': session_id,
            'initial_balance': session.initial_balance,
            'current_balance': session.current_balance,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_return_pct': total_return_pct,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'num_positions': len(positions),
            'total_exposure': total_exposure,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade_pnl': avg_trade_pnl
        }
    
    @staticmethod
    def compare_sessions(db: Session, session_ids: List[int]) -> Dict:
        """
        Compare performance across multiple paper trading sessions.
        
        Args:
            db: Database session
            session_ids: List of session IDs to compare
        
        Returns:
            Dictionary with comparison data
        """
        sessions = []
        performances = []
        
        for session_id in session_ids:
            session = PaperTradingService.get_session(db, session_id)
            if session:
                sessions.append(session)
                performance = PaperTradingService.get_session_performance(db, session_id)
                performances.append(performance)
        
        if not sessions:
            return {'sessions': [], 'comparison_metrics': {}}
        
        # Calculate comparison metrics
        comparison = {
            'best_total_return': max(performances, key=lambda p: p['total_return_pct']),
            'best_win_rate': max(performances, key=lambda p: p['win_rate']),
            'best_sharpe': max(
                [p for p in performances if p['sharpe_ratio'] is not None],
                key=lambda p: p['sharpe_ratio'],
                default=None
            ),
            'lowest_drawdown': min(performances, key=lambda p: p['max_drawdown']),
            'most_trades': max(performances, key=lambda p: p['num_trades']),
            'avg_return': np.mean([p['total_return_pct'] for p in performances]),
            'avg_win_rate': np.mean([p['win_rate'] for p in performances])
        }
        
        return {
            'sessions': sessions,
            'performances': performances,
            'comparison_metrics': comparison
        }
