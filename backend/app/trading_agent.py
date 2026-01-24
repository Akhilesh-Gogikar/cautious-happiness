import logging
import time
from typing import List, Optional
from app.market_client import MarketClient
from app.paper_trading_client import PaperTradingClient
from app.execution import SlippageAwareKelly
from app.models import TradeSignal, ForecastResult, OrderBook, PortfolioPosition
from app.engine import ForecasterCriticEngine
from app.pricing import PriceConverter
from app import models_db, database_users
from app.models_db import ExposureLimit, EventRegistry
from app.compliance import ComplianceService
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.sor import SmartOrderRouter
logger = logging.getLogger(__name__)

class TradingAgent:
    def __init__(self, market_client: MarketClient, engine: ForecasterCriticEngine, trading_mode: str = "REAL"):
        """
        Initialize TradingAgent with support for paper and real trading.
        
        Args:
            market_client: Real market client (RealMarketClient or MockMarketClient)
            engine: Forecaster/Critic engine
            trading_mode: "REAL" or "PAPER"
        """
        self.trading_mode = trading_mode  # "REAL" or "PAPER"
        self.real_client = market_client if trading_mode == "REAL" else None
        self.paper_client = None
        self.paper_session_id = None
        
        # Active client points to either real or paper
        self.market_client = market_client
        
        self.engine = engine
        self.kelly = SlippageAwareKelly(bankroll=10000.0) # Default bankroll, should be configurable
        self.mode = "HUMAN_REVIEW" # or "FULL_AI"
        self.signal_queue: List[TradeSignal] = []
        self.sor = SmartOrderRouter(self.market_client)
        
        # Initialize compliance service
        custody_provider = os.getenv("CUSTODY_PROVIDER", "mock")
        self.compliance = ComplianceService(custody_provider=custody_provider)
        
        logger.info(f"TradingAgent initialized in {trading_mode} mode")

    def set_mode(self, mode: str):
        """Set execution mode (HUMAN_REVIEW or FULL_AI)."""
        if mode not in ["HUMAN_REVIEW", "FULL_AI"]:
            raise ValueError("Invalid mode")
        self.mode = mode
        logger.info(f"Trading Mode set to: {self.mode}")
    
    def set_trading_mode(self, trading_mode: str, db: Optional[Session] = None):
        """
        Switch between REAL and PAPER trading modes.
        
        Args:
            trading_mode: "REAL" or "PAPER"
            db: Database session (required for paper mode)
        """
        if trading_mode not in ["REAL", "PAPER"]:
            raise ValueError("Invalid trading mode. Must be 'REAL' or 'PAPER'")
        
        if trading_mode == self.trading_mode:
            logger.info(f"Already in {trading_mode} mode")
            return
        
        if trading_mode == "PAPER":
            if not db:
                raise ValueError("Database session required for paper trading mode")
            
            # End any existing paper session
            if self.paper_client and self.paper_session_id:
                self.end_paper_session(db)
            
            # Start new paper session
            self.start_paper_session(db)
            
        elif trading_mode == "REAL":
            # End paper session if active
            if self.paper_client and self.paper_session_id and db:
                self.end_paper_session(db)
            
            self.market_client = self.real_client
            self.sor = SmartOrderRouter(self.market_client)
        
        self.trading_mode = trading_mode
        logger.info(f"Switched to {trading_mode} trading mode")
    
    def start_paper_session(self, db: Session, model_name: str = "default", initial_balance: float = 10000.0):
        """
        Start a new paper trading session.
        
        Args:
            db: Database session
            model_name: Name of the model being tested
            initial_balance: Starting virtual balance
        """
        from app.paper_trading_service import PaperTradingService
        
        # Create database session record
        user_id = 1  # TODO: Get from context/session
        session = PaperTradingService.create_session(
            db=db,
            user_id=user_id,
            model_name=model_name,
            initial_balance=initial_balance
        )
        
        # Create paper trading client
        self.paper_client = PaperTradingClient(
            initial_balance=initial_balance,
            session_id=session.id
        )
        self.paper_session_id = session.id
        
        # Switch active client to paper
        self.market_client = self.paper_client
        self.sor = SmartOrderRouter(self.market_client)
        
        logger.info(f"Started paper trading session {session.id} with ${initial_balance}")
        return session
    
    def end_paper_session(self, db: Session):
        """
        End the current paper trading session.
        
        Args:
            db: Database session
        """
        if not self.paper_session_id:
            logger.warning("No active paper trading session to end")
            return
        
        from app.paper_trading_service import PaperTradingService
        
        # Finalize session in database
        session = PaperTradingService.end_session(db, self.paper_session_id)
        
        logger.info(f"Ended paper trading session {self.paper_session_id}")
        
        # Reset paper trading state
        self.paper_client = None
        self.paper_session_id = None
        
        return session

    def update_bankroll(self, amount: float):
        self.kelly.bankroll = amount

    async def analyze_and_propose(self, market_id: str, question: str) -> Optional[TradeSignal]:
        """
        Full pipeline: Forecast -> Kelly -> Signal
        """
        logger.info(f"Analyzing market: {question}")
        
        # 1. Forecast
        # We need a way to call the async engine. Assuming engine methods are async.
        # The engine usually takes a ChatRequest or just string. 
        # Let's use the public helper from main `engine.run_forecast_flow` if available 
        # or call agents directly. The `ForecasterCriticEngine` in `engine.py` has `run_main_flow`.
        
        # We'll assume strict YES/NO market for now.
        
        # Hack: The engine implementation in `engine.py` might need to be called carefully. 
        # Let's assume we can use the `run_forecast_task` (celery) logic or call engine directly.
        # Start simple: trigger engine.
        
        # Note: In a real app, this is heavy.
        # Note: In a real app, this is heavy.
        result_text = "No Analysis"
        try:
             # run_analysis returns a ForecastResult object, not text.
             result_obj = await self.engine.run_analysis(question)
             # The result_obj has .adjusted_forecast (float) and .reasoning (str)
             
             prob_yes = result_obj.adjusted_forecast
             result_text = result_obj.reasoning
             
             # Determine direction based on probability
             # If > 0.5, we assume "YES" is the prediction with that confidence.
             # If < 0.5, we might interpret it as "NO is likely" (prob NO = 1 - prob YES), 
             # but our Kelly assumes we are buying "YES" tokens with `prob_yes` chance of winning.
             # So we can just use `prob_yes` directly.
             
             is_yes = prob_yes > 0.5
        except Exception as e:
             logger.error(f"Engine analysis failed: {e}")
             return None 
        # We need to parse this text to get a number. 
        # This is the tricky part of "Text to Float".
        # For now, let's assume the engine output contains "Confidence: X%"
        
        # logic moved above
        pass
        
        # Direction?
        # If text says "Prediction: YES", prob = confidence
        # If "Prediction: NO", prob = 1 - confidence
        
        # logic moved above
            
        # prob_yes = confidence if is_yes else (1.0 - confidence)
        
        # 2. Market Data
        try:
            order_book = self.market_client.get_order_book(market_id)
        except NotImplementedError:
             logger.warning("Market data source not ready.")
             return None
        
        # 3. Execution Logic (Kelly)
        # We are buying YES tokens.
        # If we think NO, we buy NO tokens? Or Sell Yes? 
        # The exchange splits YES/NO. Buying NO is buying NO token.
        # Our `SlippageAwareKelly` assumes we are buying an asset.
        
        target_token_prob = prob_yes if is_yes else (1.0 - prob_yes)
        # We need the order book for the token we want to buy.
        # `get_order_book` needs to know WHICH token.
        # Simplified: `market_client` returns orderbook for YES token by default?
        # We need to extend `market_client` to handle TokenID.
        
        # For prototype: Assume we only buy YES for now. 
        if not is_yes:
            logger.info("Shorting/Buying NO not yet fully implemented in auto-execution. Skipping.")
            return None
            
        size_usd, shares, vwap = self.kelly.optimal_allocation(target_token_prob, order_book)
        
        if size_usd <= 0:
            logger.info(f"No positive expected value found (Prob: {prob_yes}, VWAP: {vwap}).")
            return None
            
        signal = TradeSignal(
            market_id=market_id,
            market_question=question,
            signal_side="BUY_YES",
            price_estimate=vwap,
            kelly_size_usd=size_usd,
            expected_value=size_usd * (target_token_prob / vwap - 1), # Simple EV approx
            rationale=f"Model confidence {prob_yes:.2f} > Price {vwap:.2f}. {result_text[:100]}...",
            timestamp=time.time()
        )
        
        # 3.5 Price Limits for potential Limit Orders
        limits = PriceConverter.convert_to_limits(prob_yes)
        signal.rationale += f" | Proposed Limits: Bid ${limits['bid']} / Ask ${limits['ask']}"
        
        # 4. Act
        if self.mode == "FULL_AI":
            # Check Drawdown Limit
            db = database_users.SessionLocal()
            try:
                if await self.check_drawdown_limit(db):
                    await self.execute_signal(signal, db)
                else:
                    signal.status = "PAUSED"
                    signal.rationale += " | Execution skipped: Drawdown limit reached."
                    logger.warning(f"Drawdown limit reached for agent. Skipping trade.")
            finally:
                db.close()
        else:
            self.signal_queue.append(signal)
            logger.info("Signal added to review queue.")
            
        return signal

    async def execute_signal(self, signal: TradeSignal, db: Optional[Session] = None):
        logger.info(f"EXECUTING Trade {signal.market_id}: ${signal.kelly_size_usd}")
        
        # Import attribution service
        from app.attribution_service import AttributionService
        attribution_service = AttributionService()
        
        # 1. Compliance Check - KYC/AML Whitelisting
        if db:
            # Get wallet address from signal or user profile
            wallet_address = signal.wallet_address
            if not wallet_address:
                # Try to get default wallet from user profile
                user_id = 1  # TODO: Get from context/session
                user = db.query(models_db.User).filter(models_db.User.id == user_id).first()
                if user and user.profile and user.profile.preferences:
                    wallet_address = user.profile.preferences.get("default_wallet_address")
            
            if not wallet_address:
                logger.error("No wallet address provided for trade execution")
                signal.status = "REJECTED"
                signal.compliance_status = "REJECTED"
                signal.compliance_message = "No wallet address configured. Please add a whitelisted wallet."
                signal.rationale += " [REJECTED: No Wallet Address]"
                return
            
            # Validate wallet compliance
            user_id = 1  # TODO: Get from context/session
            compliance_result = self.compliance.validate_wallet_address(wallet_address, user_id, db)
            
            signal.wallet_address = wallet_address
            signal.compliance_status = "APPROVED" if compliance_result.is_approved else "REJECTED"
            signal.compliance_message = compliance_result.reason
            
            if not compliance_result.is_approved:
                logger.warning(f"Trade signal {signal.market_id} rejected due to compliance: {compliance_result.reason}")
                signal.status = "REJECTED"
                signal.rationale += f" [REJECTED: {compliance_result.reason}]"
                return
            
            logger.info(f"Compliance check passed for wallet: {wallet_address}")
        
        # 2. Risk Management (Kelly + Snipe checks done in analyze_and_propose or separate, but Exposure is hard stop)
        # We need a DB session to check exposure limits
        if db:
            if not self.check_exposure_limits(db, signal):
                logger.warning(f"Trade signal {signal.market_id} rejected due to exposure limits.")
                signal.status = "REJECTED"
                signal.rationale += " [REJECTED: Exposure Limit Breached]"
                return
        
        LARGE_ORDER_THRESHOLD = 1000.0
        success = False
        
        if signal.kelly_size_usd > LARGE_ORDER_THRESHOLD:
            logger.info(f"Order size ${signal.kelly_size_usd} > ${LARGE_ORDER_THRESHOLD}. Routing via SOR (TWAP).")
            # Fire and forget / Background task? 
            # In this simple implementation, we await it, which blocks other signals.
            # Ideally use asyncio.create_task for non-blocking if safe.
            # But we want to confirm execution for status.
            try:
                await self.sor.execute_twap(signal.market_id, "BUY", signal.kelly_size_usd, duration_minutes=5)
                success = True # SOR doesn't return bool yet, assuming success if no exception
            except Exception as e:
                logger.error(f"SOR Execution failed: {e}")
                success = False
        else:
            order_id = self.market_client.place_order(signal.market_id, signal.kelly_size_usd, "BUY", wallet_address=signal.wallet_address)
            success = bool(order_id)
        
        if db:
            # Record PnL (Mock: assuming we know the entry price and immediate outcome for stats)
            # In a real app, PnL is tracked over time. 
            # For this 'hard stop', we track realized losses or current exposure.
            # Simplified: we assume every trade has a potential max loss of its size.
            stats = self._get_or_create_daily_stats(db)
            # We don't have real PnL yet, but we can track 'exposure' or 'potential drawdown'
            # Or if we're simulating a loss for the demo:
            # stats.current_pnl -= signal.kelly_size_usd * 0.05 # Simulate 5% slippage/loss
            db.commit()

        if success:
            signal.status = "EXECUTED"
            signal.tx_hash = "0xMOCKED_HASH"
            
            # Record trade with attribution metadata
            if db:
                try:
                    user_id = 1  # TODO: Get from context/session
                    
                    # Determine data sources used
                    data_sources = []
                    if hasattr(signal, 'data_sources') and signal.data_sources:
                        data_sources = signal.data_sources
                    else:
                        # Default attribution based on available data
                        data_sources = ["RAG"]  # Assume RAG was used
                    
                    # Record the trade execution
                    trade_execution = attribution_service.record_trade(
                        db=db,
                        user_id=user_id,
                        signal=signal,
                        model_used=signal.model_used or "openforecaster",
                        data_sources=data_sources,
                        strategy_type=signal.strategy_type or "KELLY",
                        category=signal.category or "General",
                        entry_price=signal.price_estimate,
                        shares=signal.kelly_size_usd / signal.price_estimate,
                        confidence_score=signal.confidence_score,
                        reasoning_snippet=signal.rationale
                    )
                    
                    logger.info(f"Recorded trade execution {trade_execution.id} with attribution")
                except Exception as e:
                    logger.error(f"Failed to record trade attribution: {e}")
        else:
            signal.status = "FAILED"

    async def check_drawdown_limit(self, db: Session) -> bool:
        """
        Check if the agent is allowed to trade based on daily drawdown.
        """
        stats = self._get_or_create_daily_stats(db)
        if stats.is_paused:
            return False

        limit = db.query(models_db.DrawdownLimit).filter(
            models_db.DrawdownLimit.user_id == stats.user_id,
            models_db.DrawdownLimit.is_active == True
        ).first()

        if not limit:
            return True # No limit set

        # Calculate current drawdown percentage
        if stats.starting_balance > 0:
            # Drawdown = (Max Balance - Current Balance) / Max Balance
            # Here simplified to: (Loss) / Starting Balance
            drawdown_pct = (abs(min(0, stats.current_pnl)) / stats.starting_balance) * 100
            
            if drawdown_pct >= limit.max_daily_drawdown_percent:
                stats.is_paused = True
                stats.pause_reason = f"Daily drawdown limit of {limit.max_daily_drawdown_percent}% reached ({drawdown_pct:.2f}%)."
                db.commit()
                return False

        return True

    def _get_or_create_daily_stats(self, db: Session) -> models_db.AgentDailyStats:
        # For simplicity, assume user_id=1 for now if not provided
        user_id = 1 
        today = datetime.utcnow().date()
        stats = db.query(models_db.AgentDailyStats).filter(
            models_db.AgentDailyStats.user_id == user_id,
            models_db.AgentDailyStats.date >= datetime.combine(today, datetime.min.time()),
            models_db.AgentDailyStats.date <= datetime.combine(today, datetime.max.time())
        ).first()

        if not stats:
            # Initialize with default bankroll
            initial_balance = 10000.0 # Should come from portfolio/wallet
            stats = models_db.AgentDailyStats(
                user_id=user_id,
                date=datetime.utcnow(),
                starting_balance=initial_balance,
                current_pnl=0.0,
                is_paused=False
            )
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        return stats

    def get_queue(self):
        return self.signal_queue

    def approve_signal(self, signal_index: int):
        if 0 <= signal_index < len(self.signal_queue):
            signal = self.signal_queue[signal_index]
            # In async context we'd await, but this might be called from synchronous endpoint 
            # so we might need a background task or careful handling. 
            # For MVP, we'll mark it pending execution or execute if we can.
            
            # Since we are in a class that might be run by FastAPI, we might need to be async.
            # We'll set status APPROVED and let a worker pick it up, or execute immediately if we can.
            
            # Hack: execute sync for now (mocked client is sync-ish or fast)
            # Real client needs async.
            
            # self.execute_signal(signal) -> needs await.
            # We'll just set flag.
            signal.status = "APPROVED" 
            return True
        return False

    def check_exposure_limits(self, db: Session, signal: TradeSignal) -> bool:
        """
        Checks if executing the signal would breach any user-defined exposure limits.
        Returns True if safe to proceed, False if limit breached.
        """
        user_id = 1 # TODO: Pass actual user_id when multi-user enabled.
        
        # 1. Fetch Limits
        limits = db.query(ExposureLimit).filter(
            ExposureLimit.user_id == user_id, 
            ExposureLimit.is_active == True
        ).all()
        
        if not limits:
            return True # No limits configured

        # 2. Fetch Current Portfolio
        try:
            portfolio = self.market_client.get_portfolio()
            positions = portfolio.positions
        except Exception as e:
            logger.error(f"Failed to fetch portfolio for exposure check: {e}")
            return False 

        # 3. Calculate Exposures
        proposed_usd = signal.kelly_size_usd
        
        # Identify Category of the Proposed Trade
        registry_entry = db.query(EventRegistry).filter(EventRegistry.market_id == signal.market_id).first()
        proposed_category = registry_entry.category if registry_entry else "Uncategorized"
        
        # Current Exposures
        exposure_per_market = {}
        exposure_per_category = {}
        exposure_per_exchange = {} 
        
        # Initialize with Proposed Trade
        exposure_per_market[signal.market_id] = proposed_usd
        exposure_per_category[proposed_category] = exposure_per_category.get(proposed_category, 0.0) + proposed_usd
        exposure_per_exchange["AlphaSignals"] = exposure_per_exchange.get("AlphaSignals", 0.0) + proposed_usd 
        
        # Add Existing Positions
        known_market_ids = [p.condition_id for p in positions]
        market_cats = {}
        if known_market_ids:
            records = db.query(EventRegistry).filter(EventRegistry.market_id.in_(known_market_ids)).all()
            for r in records:
                market_cats[r.market_id] = r.category

        for p in positions:
            val = p.svalue 
            exposure_per_market[p.condition_id] = exposure_per_market.get(p.condition_id, 0.0) + val
            cat = market_cats.get(p.condition_id, "Uncategorized")
            exposure_per_category[cat] = exposure_per_category.get(cat, 0.0) + val
            exposure_per_exchange["AlphaSignals"] = exposure_per_exchange.get("AlphaSignals", 0.0) + val

        # 4. Check Constraints
        for limit in limits:
            if limit.scope_type == "PER_MARKET_CAP":
                if limit.scope_value and limit.scope_value != "ALL":
                    if limit.scope_value == signal.market_id:
                        if exposure_per_market.get(signal.market_id, 0.0) > limit.max_exposure_usd:
                            logger.warning(f"Exposure Limit (Specific Market) Hit: {signal.market_id}")
                            return False
                else: 
                    if exposure_per_market.get(signal.market_id, 0.0) > limit.max_exposure_usd:
                        logger.warning(f"Exposure Limit (Per Market Cap) Hit: {exposure_per_market[signal.market_id]} > {limit.max_exposure_usd}")
                        return False
            
            elif limit.scope_type == "CATEGORY_CAP":
                target_cat = limit.scope_value
                if target_cat and exposure_per_category.get(target_cat, 0.0) > limit.max_exposure_usd:
                     if target_cat == proposed_category:
                        logger.warning(f"Exposure Limit (Category: {target_cat}) Hit")
                        return False

            elif limit.scope_type == "EXCHANGE_CAP":
                 target_ex = limit.scope_value
                 # Assuming AlphaSignals for now
                 if target_ex == "AlphaSignals" and exposure_per_exchange["AlphaSignals"] > limit.max_exposure_usd:
                     logger.warning("Exposure Limit (AlphaSignals) Hit")
                     return False

        return True
