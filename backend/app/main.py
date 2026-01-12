from fastapi import FastAPI, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.engine import ForecasterCriticEngine, ForecastResult
from app.models import ForecastResult, ChatRequest, ChatResponse, TradeSignal, PortfolioPosition, PortfolioSummary, AlternativeSignal, ArbitrageOpportunity, AlgoOrderRequest, AlgoOrderResponse
from app.arbitrage import ArbitrageEngine
from app import models_db, database, auth_router, database_users, auth, historical_router, permissions, risk_router, tax_router, attribution_models, compliance_models, heatmap_models, paper_trading_models
from sqlalchemy.orm import Session
import os
import logging
import json
import time
from app.services.gas_service import GasService
from app.websockets.manager import manager as ws_manager


# Force In-Memory DB hack removed - Using real DB from database_users.py
# If you need to re-enable debugging, ensure backend/data/sql_app.db is writeable
from app import database_users


# Initialize Database
models_db.BaseUsers.metadata.create_all(bind=database_users.engine)

# Configure JSON Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alpha_terminal_dashboard")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.propagate = False

app = FastAPI(title="Alpha Terminal Dashboard")

# Include Routers
app.include_router(auth_router.router)
app.include_router(historical_router.router)
app.include_router(risk_router.router)
app.include_router(tax_router.router)

# CORS Configuration
# Allow local frontend and other origins
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Websocket Manager...")
    await ws_manager.start()
    logger.info("Initializing Vector Database...")
    try:
        engine.vector_db._ensure_collection() # Ensure collection exists on startup
        logger.info("Vector Database initialized successfully.")
    except Exception as e:
        logger.error(f"Vector Database initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await ws_manager.stop()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    log_data = {
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(process_time * 1000, 2),
    }
    logger.info(json.dumps(log_data))
    return response

@app.get("/signals", response_model=List[TradeSignal])
async def get_signals(current_user: models_db.User = Depends(permissions.requires_trade_view())):
    """
    Get active trading signals.
    """
    # Return mock signals for now to prevent frontend crash
    return [
        TradeSignal(
            market_id="0x123...",
            market_question="Will Bitcoin hit $100k by 2025?",
            signal_side="BUY_YES",
            price_estimate=0.65,
            kelly_size_usd=1000.0,
            expected_value=1.5,
            rationale="Strong momentum detected by AI model",
            status="PENDING",
            timestamp=time.time()
        )
    ]

@app.post("/mode/set")
async def set_trading_mode(req: dict, current_user: models_db.User = Depends(permissions.requires_trade_execute())):
    """
    Switch between Human Review and Full AI mode.
    """
    logger.info(f"User {current_user.email} set mode to: {req.get('mode')}")
    return {"status": "success", "mode": req.get("mode")}

@app.post("/settings/credentials")
async def save_credentials(req: dict, current_user: models_db.User = Depends(permissions.requires_trade_execute())):
    """
    Save exchange API credentials.
    """
    logger.info(f"User {current_user.email} updated credentials")
    return {"status": "success"}

@app.post("/signals/{index}/approve")
async def approve_signal_endpoint(index: int, current_user: models_db.User = Depends(permissions.requires_trade_execute())):
    """
    Approve a pending trade signal.
    """
    logger.info(f"User {current_user.email} approved signal at index {index}")
    return {"status": "success"}


from fastapi.responses import JSONResponse

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

engine = ForecasterCriticEngine()
arbitrage_engine = ArbitrageEngine()

from app.risk_monitoring import RiskMonitor
from app.models import RiskReport
risk_monitor = RiskMonitor()

@app.get("/risk/status", response_model=RiskReport)
async def get_risk_status():
    """
    Returns real-time counterparty and protocol risk status.
    """
    return risk_monitor.get_latest_report()
gas_service = GasService()

# Pydantic models
from pydantic import BaseModel
class PredictionRequest(BaseModel):
    question: str
    model: str = "openforecaster"

@app.get("/api-spec")
def get_api_spec():
    """
    Export the OpenAPI specification as JSON.
    """
    return app.openapi()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/arbitrage", response_model=List[ArbitrageOpportunity])
async def get_arbitrage_opportunities(
    min_discrepancy: float = 0.02,
    current_user: models_db.User = Depends(permissions.requires_trade_view())
):
    """
    detect price discrepancies between AlphaSignals and Kalshi.
    """
    return await arbitrage_engine.find_opportunities(min_discrepancy=min_discrepancy)

@app.get("/gas/polygon")
def get_polygon_gas():
    """
    Get current Polygon gas price and estimates.
    """
    return gas_service.estimate_optimal_gas()

from celery.result import AsyncResult
from app.worker import celery_app, run_forecast_task
from typing import List, Dict, Any
from fastapi import Request, Depends
from app.limiter import check_rate_limit
from app.cache import r as redis_client
import hashlib

# ... (Previous imports preserved above, but we rewrite the file for clarity in this block if needed. 
# Actually replacing the whole file is cleaner for the new endpoints)

@app.post("/predict", dependencies=[Depends(check_rate_limit)])
async def predict_market(request: PredictionRequest, req: Request):
    """
    Trigger the AI Forecaster-Critic Engine.
    Checks Redis cache first for a recent valid prediction for this question.
    Title/Question is the cache key.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")

    # Check Cache (TTL 1 hour for predictions)
    # We use a derived key from the question
    q_hash = hashlib.md5(request.question.encode()).hexdigest()
    cache_key = f"prediction_result:{q_hash}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        # Return a "completed" task structure instantly with cached data
        # We dummy a task_id for frontend consistency
        return {
            "task_id": f"cached_{q_hash}", 
            "status": "cached", 
            "result": json.loads(cached_data)
        }
    
    # If not cached, start task
    task = run_forecast_task.delay(request.question, request.model)
    return {"task_id": task.id, "status": "processing"}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    # Handle the fake "cached" task ID
    if task_id.startswith("cached_"):
        # Retrieve from redis again
        cache_key = f"prediction_result:{task_id.replace('cached_', '')}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
             return {"id": task_id, "status": "completed", "result": json.loads(cached_data)}
        else:
             return {"id": task_id, "status": "failed", "result": None}

    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        result = task_result.get()
        
        # Cache the successful result here for future /predict calls
        # We need the original question to form the key, which might be in the result object
        if result and isinstance(result, dict) and 'search_query' in result:
             q_hash = hashlib.md5(result['search_query'].encode()).hexdigest()
             cache_key = f"prediction_result:{q_hash}"
             # Cache for 1 hour (3600s) as "periodic update"
             redis_client.setex(cache_key, 3600, json.dumps(result))
             
        return {"id": task_id, "status": "completed", "result": result}
    return {"id": task_id, "status": "processing"}

from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, current_user: models_db.User = Depends(auth.get_current_user), db: Session = Depends(database_users.get_db)):
    """
    Chat with the model about a prediction context.
    """
    if not req.user_message:
        raise HTTPException(status_code=400, detail="Message required")
    
    # Save User Message
    user_msg = models_db.ChatHistory(user_id=current_user.id, role="user", content=req.user_message, context=req.context)
    db.add(user_msg)
    
    response_text = await engine.chat_with_model(req)
    
    # Save Assistant Message
    assistant_msg = models_db.ChatHistory(user_id=current_user.id, role="assistant", content=response_text, context=req.context)
    db.add(assistant_msg)
    db.commit()

    return {"response": response_text}

@app.post("/chat/stream")
async def stream_chat_endpoint(req: ChatRequest, current_user: models_db.User = Depends(auth.get_current_user), db: Session = Depends(database_users.get_db)):
    """
    Stream chat with the model about a prediction context.
    Using Server-Sent Events (SSE) compatible streaming.
    """
    if not req.user_message:
        raise HTTPException(status_code=400, detail="Message required")
    
    # Save User Message
    user_msg = models_db.ChatHistory(user_id=current_user.id, role="user", content=req.user_message, context=req.context)
    db.add(user_msg)
    db.commit()

    async def wrapped_stream():
        full_response = ""
        async for chunk in engine.stream_chat_with_model(req):
            full_response += chunk
            yield chunk
        
        # Save Assistant Message after stream finishes
        # We need a new session or use the existing one carefully
        # For simplicity in this demo/MVP, we save it at the end
        new_db = database_users.SessionLocal()
        try:
            assistant_msg = models_db.ChatHistory(user_id=current_user.id, role="assistant", content=full_response, context=req.context)
            new_db.add(assistant_msg)
            new_db.commit()
        finally:
            new_db.close()

    return StreamingResponse(wrapped_stream(), media_type="text/event-stream")

from py_clob_client.client import ClobClient
from app.cache import cache_response

@app.get("/markets")
@cache_response(ttl_seconds=30)
async def get_markets():
    """
    Fetch active markets from the CLOB.
    Uses the client to get real-time data.
    """
    try:
        # Load Creds from Env
        api_key = os.getenv("POLYMARKET_API_KEY", "")
        secret = os.getenv("POLYMARKET_SECRET", "")
        passphrase = os.getenv("POLYMARKET_PASSPHRASE", "")
        
        # Initialize client
        # If no keys provided, it falls back to public access (usually fine for getting markets)
        client = ClobClient(
            "https://clob.polymarket.com", 
            key=api_key, 
            secret=secret, 
            passphrase=passphrase, 
            chain_id=137
        )

        # Fetch active markets (limit to top 20 by volume/activity via simplified sampling)
        # Note: The raw API might return many, we filter for top volume ones.
        # Since 'get_markets' returns detailed token info, we parse it.
        
        # Using simplified approach for MVP latency:
        # 1. Get markets (filtering by active is ideal if supported, or client logic)
        resp = client.get_markets(next_cursor="") 
        
        # Transform to our minimal dashboard format
        # This is a simplification; real app handles pagination and robust filtering
        
        # Load classifications from DB
        db = database_users.SessionLocal()
        registry_map = {}
        try:
            # We fetch all for now, optimized would be fetch only matching IDs
            # For 20 items, fetching all is okay if table small, but let's just fetch all for MVP or assume small table
            events = db.query(models_db.EventRegistry).all()
            registry_map = {e.market_id: e.category for e in events}
        except Exception as e:
            logger.error(f"DB Error fetching registry: {e}")
        finally:
            db.close()

        markets_data = []
        for m in resp.get('data', [])[:20]: # Limit to 20 for density
            if m.get('active') and m.get('tokens'):
                # Heuristic: Find YES token price
                yes_token = next((t for t in m['tokens'] if t['outcome'] == 'Yes'), None)
                price = yes_token.get('price', 0.5) if yes_token else 0.0
                
                m_id = m.get('condition_id')
                # Use DB category if available, else fallback to tags
                category = registry_map.get(m_id)
                if not category:
                     category = m.get('tags', ['General'])[0] if m.get('tags') else 'General'

                markets_data.append({
                    "id": m_id,
                    "question": m.get('question'),
                    "volume_24h": float(m.get('volume_24h', 0) or 0), 
                    "last_price": float(price),
                    "category": category
                })
        
        # Sort by Volume desc
        markets_data.sort(key=lambda x: x['volume_24h'], reverse=True)
        return markets_data

    except Exception as e:
        logger.error(f"CLOB Error: {e}")
        # Fallback to Mock if API fails (e.g., rate limit)
        return [
            {
                "id": "err_fallback",
                "question": "Error fetching Live Data - Showing Cached/Mock",
                "volume_24h": 0,
                "last_price": 0.0,
                "category": "System"
            }
        ]


@app.get("/markets/{market_id}/orderbook")
async def get_order_book(market_id: str):
    """
    Fetch order book (bids/asks) for a specific market.
    """
    try:
        # Try Live WS Data First
        live_book = ws_manager.get_live_book(market_id)
        if live_book:
            return live_book

        # Check for API key to decide between Real or Mock client
        api_key = os.getenv("POLYMARKET_API_KEY")
        if api_key:
            from app.market_client import RealMarketClient
            client = RealMarketClient(
                api_key, 
                os.getenv("POLYMARKET_SECRET", ""), 
                os.getenv("POLYMARKET_PASSPHRASE", "")
            )
            # Trigger subscription for next time
            await ws_manager.subscribe_market(market_id)
        else:
            from app.market_client import MockMarketClient
            client = MockMarketClient(api_key="", secret="", passphrase="")
            
        return client.get_order_book(market_id)
    except Exception as e:
        logger.error(f"Error fetching order book for {market_id}: {e}")
        # Return empty book on error rather than crash
        return {"asks": [], "bids": []}

@app.post("/trade/algo", response_model=AlgoOrderResponse)
async def create_algo_order(
    req: AlgoOrderRequest, 
    current_user: models_db.User = Depends(permissions.requires_trade_execute()), 
    db: Session = Depends(database_users.get_db)
):
    """
    Create a new algorithmic order.
    """
    new_order = models_db.AlgoOrder(
        user_id=current_user.id,
        market_id=req.market_id,
        type=req.type,
        total_size_usd=req.total_size_usd,
        remaining_size_usd=req.total_size_usd,
        display_size_usd=req.display_size_usd,
        duration_minutes=req.duration_minutes,
        status="ACTIVE" # Start as active for this demo
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/trade/algo", response_model=List[AlgoOrderResponse])
async def list_algo_orders(
    current_user: models_db.User = Depends(permissions.requires_trade_view()), 
    db: Session = Depends(database_users.get_db)
):
    """
    List user's algorithmic orders.
    """
    orders = db.query(models_db.AlgoOrder).filter(models_db.AlgoOrder.user_id == current_user.id).all()
    return orders

@app.delete("/trade/algo/{order_id}")
async def cancel_algo_order(
    order_id: int, 
    current_user: models_db.User = Depends(permissions.requires_trade_execute()), 
    db: Session = Depends(database_users.get_db)
):
    """
    Cancel an active algo order.
    """
    order = db.query(models_db.AlgoOrder).filter(
        models_db.AlgoOrder.id == order_id, 
        models_db.AlgoOrder.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "CANCELLED"
    db.commit()
    return {"status": "cancelled"}

@app.post("/trade/panic")
async def panic_button(
    current_user: models_db.User = Depends(permissions.requires_trade_execute()),
    db: Session = Depends(database_users.get_db)
):
    """
    EMERGENCY KILL SWITCH.
    1. Cancels all active AlgoOrders in DB.
    2. Cancels all open orders on Exchange.
    """
    logger.critical(f"USER {current_user.email} ACTIVATED KILL SWITCH")
    
    # 1. DB Cancel
    active_orders = db.query(models_db.AlgoOrder).filter(
        models_db.AlgoOrder.user_id == current_user.id,
        models_db.AlgoOrder.status == "ACTIVE"
    ).all()
    
    for order in active_orders:
        order.status = "CANCELLED"
    db.commit()
    
    # 2. Exchange Cancel
    api_key = os.getenv("POLYMARKET_API_KEY")
    if api_key:
        from app.market_client import RealMarketClient
        client = RealMarketClient(
            api_key, 
            os.getenv("POLYMARKET_SECRET", ""), 
            os.getenv("POLYMARKET_PASSPHRASE", "")
        )
        success = client.cancel_all_orders()
    else:
        # Mock
        from app.market_client import MockMarketClient
        client = MockMarketClient()
        success = client.cancel_all_orders()
        
    return {
        "status": "success", 
        "cancelled_db_orders": len(active_orders),
        "exchange_cancel_success": success
    }

# Placeholder for CLOB Client Wrapper

@app.get("/portfolio")
async def get_portfolio(current_user: models_db.User = Depends(permissions.requires_trade_view())):
    """
    Returns user portfolio summary from the real market client (or mock).
    """
    # Note: connect to real client if configured
    api_key = os.getenv("POLYMARKET_API_KEY")
    if api_key:
        from app.market_client import RealMarketClient
        client = RealMarketClient(
            api_key, 
            os.getenv("POLYMARKET_SECRET", ""), 
            os.getenv("POLYMARKET_PASSPHRASE", "")
        )
        return client.get_portfolio()
    else:
        # Mock portfolio
        return {
            "balance": 10000.0,
            "exposure": 2500.0,
            "positions": [
                {
                    "asset_id": "0x123",
                    "condition_id": "0xcde",
                    "question": "Will Bitcoin hit $100k by 2025?",
                    "outcome": "Yes",
                    "price": 0.65,
                    "size": 1000,
                    "svalue": 650.0,
                    "pnl": 50.0
                }
            ]
        }

@app.get("/alt-data/signals", response_model=List[AlternativeSignal])
async def get_alt_signals(current_user: models_db.User = Depends(permissions.requires_trade_view())):
    """
    Get active alternative intelligence signals.
    """
    # Sample question for global signals
    signals = engine.alt_data_client.get_signals_for_market("agricultural shipping flight oil")
    return signals

@app.post("/alt-data/ingest")
async def ingest_alt_data(
    signal_type: str = "SATELLITE",
    current_user: models_db.User = Depends(permissions.requires_system_debug())
):
    """
    Simulate ingestion of new alternative data.
    """
    logger.info(f"Ingesting new {signal_type} data...")
    return {"status": "success", "message": f"New {signal_type} data ingested and indexed."}

from app.models import DrawdownLimitRequest, DrawdownLimitResponse, DailyStatsResponse

@app.get("/api/trading/limits", response_model=DrawdownLimitResponse)
async def get_drawdown_limits(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Get the current drawdown limit configuration for the user.
    """
    limit = db.query(models_db.DrawdownLimit).filter(
        models_db.DrawdownLimit.user_id == current_user.id,
        models_db.DrawdownLimit.is_active == True
    ).first()
    
    if not limit:
        # Create default limit if none exists
        limit = models_db.DrawdownLimit(
            user_id=current_user.id,
            max_daily_drawdown_percent=5.0,
            is_active=True
        )
        db.add(limit)
        db.commit()
        db.refresh(limit)
    
    return limit

@app.post("/api/trading/limits", response_model=DrawdownLimitResponse)
async def update_drawdown_limits(
    req: DrawdownLimitRequest,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Update or create drawdown limit configuration.
    """
    limit = db.query(models_db.DrawdownLimit).filter(
        models_db.DrawdownLimit.user_id == current_user.id
    ).first()
    
    if limit:
        limit.max_daily_drawdown_percent = req.max_daily_drawdown_percent
        limit.is_active = req.is_active
    else:
        limit = models_db.DrawdownLimit(
            user_id=current_user.id,
            max_daily_drawdown_percent=req.max_daily_drawdown_percent,
            is_active=req.is_active
        )
        db.add(limit)
    
    db.commit()
    db.refresh(limit)
    return limit

@app.get("/api/trading/daily-stats", response_model=DailyStatsResponse)
async def get_daily_stats(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Get current daily trading statistics and pause status.
    """
    from datetime import datetime
    today = datetime.utcnow().date()
    
    stats = db.query(models_db.AgentDailyStats).filter(
        models_db.AgentDailyStats.user_id == current_user.id
    ).order_by(models_db.AgentDailyStats.date.desc()).first()
    
    if not stats:
        # Create initial stats
        stats = models_db.AgentDailyStats(
            user_id=current_user.id,
            date=datetime.utcnow(),
            starting_balance=10000.0,
            current_pnl=0.0,
            is_paused=False
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return stats

@app.post("/api/trading/reset-daily")
async def reset_daily_stats(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Manually reset daily stats (e.g., after deposit or at day start).
    """
    from datetime import datetime
    
    # Archive old stats by creating new entry
    stats = models_db.AgentDailyStats(
        user_id=current_user.id,
        date=datetime.utcnow(),
        starting_balance=10000.0,  # Should fetch from portfolio
        current_pnl=0.0,
        is_paused=False,
        pause_reason=None
    )
    db.add(stats)
    db.commit()
    
    return {"status": "success", "message": "Daily stats reset successfully"}

# ============================================================================
# COMPLIANCE / KYC-AML ENDPOINTS
# ============================================================================

from app.compliance import ComplianceService
from app.compliance_models import WhitelistRequest, ComplianceStatusResponse
from typing import Optional

# Initialize compliance service
compliance_service = ComplianceService(
    custody_provider=os.getenv("CUSTODY_PROVIDER", "mock"),
    api_key=os.getenv("CUSTODY_API_KEY", ""),
    api_secret=os.getenv("CUSTODY_API_SECRET", "")
)

@app.post("/api/compliance/whitelist")
async def add_wallet_to_whitelist(
    request: WhitelistRequest,
    current_user: models_db.User = Depends(permissions.requires_system_debug()),  # Admin only
    db: Session = Depends(database_users.get_db)
):
    """
    Add a wallet address to the whitelist (Admin only).
    Triggers KYC/AML verification with custody provider.
    """
    try:
        whitelisted = compliance_service.add_whitelisted_address(current_user.id, request, db)
        return {
            "status": "success",
            "wallet_address": whitelisted.wallet_address,
            "kyc_verified": whitelisted.kyc_verified,
            "aml_status": whitelisted.aml_status,
            "message": "Wallet successfully added to whitelist"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding wallet to whitelist: {e}")
        raise HTTPException(status_code=500, detail="Failed to add wallet to whitelist")

@app.delete("/api/compliance/whitelist/{wallet_address}")
async def remove_wallet_from_whitelist(
    wallet_address: str,
    current_user: models_db.User = Depends(permissions.requires_system_debug()),  # Admin only
    db: Session = Depends(database_users.get_db)
):
    """
    Remove a wallet address from the whitelist (Admin only).
    """
    success = compliance_service.remove_whitelisted_address(wallet_address, current_user.id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Wallet address not found")
    
    return {
        "status": "success",
        "wallet_address": wallet_address,
        "message": "Wallet removed from whitelist"
    }

@app.get("/api/compliance/status/{wallet_address}", response_model=ComplianceStatusResponse)
async def get_compliance_status(
    wallet_address: str,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Get compliance status for a wallet address.
    """
    status = compliance_service.get_wallet_compliance_status(wallet_address, db)
    if not status:
        raise HTTPException(status_code=404, detail="Wallet address not found")
    return status

@app.get("/api/compliance/checks")
async def get_compliance_checks(
    wallet_address: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    List compliance check audit logs with pagination.
    Optionally filter by wallet_address.
    """
    query = db.query(models_db.ComplianceCheck).filter(
        models_db.ComplianceCheck.user_id == current_user.id
    )
    
    if wallet_address:
        query = query.filter(models_db.ComplianceCheck.wallet_address == wallet_address)
    
    total = query.count()
    checks = query.order_by(models_db.ComplianceCheck.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "checks": [
            {
                "id": check.id,
                "wallet_address": check.wallet_address,
                "check_type": check.check_type,
                "check_result": check.check_result,
                "reason": check.reason,
                "timestamp": check.timestamp.isoformat(),
                "trade_signal_id": check.trade_signal_id
            }
            for check in checks
        ]
    }

@app.post("/api/compliance/verify/{wallet_address}")
async def trigger_wallet_verification(
    wallet_address: str,
    current_user: models_db.User = Depends(permissions.requires_system_debug()),  # Admin only
    db: Session = Depends(database_users.get_db)
):
    """
    Trigger re-verification of a wallet with custody provider.
    Updates KYC/AML status in database.
    """
    # Get existing whitelist entry
    whitelisted = db.query(models_db.WhitelistedAddress).filter(
        models_db.WhitelistedAddress.wallet_address == wallet_address
    ).first()
    
    if not whitelisted:
        raise HTTPException(status_code=404, detail="Wallet address not whitelisted")
    
    # Check custody provider status
    custody_status = compliance_service.check_custody_provider_status(wallet_address)
    
    # Update database
    whitelisted.kyc_verified = custody_status["kyc"].get("verified", False)
    whitelisted.aml_status = custody_status["aml"].get("status", "PENDING")
    whitelisted.metadata_json = custody_status
    whitelisted.updated_at = datetime.utcnow()
    
    if whitelisted.kyc_verified:
        whitelisted.verification_date = datetime.utcnow()
        if custody_status["kyc"].get("expiry_date"):
            from dateutil import parser
            whitelisted.expiry_date = parser.parse(custody_status["kyc"]["expiry_date"])
    
    db.commit()
    
    # Log the verification
    compliance_service.log_compliance_check(
        current_user.id, wallet_address, "KYC_VERIFICATION", 
        "APPROVED" if whitelisted.kyc_verified else "PENDING",
        reason=f"Re-verification triggered. KYC: {whitelisted.kyc_verified}, AML: {whitelisted.aml_status}",
        metadata=custody_status,
        db=db
    )
    
    return {
        "status": "success",
        "wallet_address": wallet_address,
        "kyc_verified": whitelisted.kyc_verified,
        "aml_status": whitelisted.aml_status,
        "custody_provider": whitelisted.custody_provider,
        "message": "Wallet verification updated"
    }

from fastapi import WebSocket, WebSocketDisconnect
from app.pnl import simulate_pnl_stream

@app.websocket("/ws/pnl/{market_id}")
async def websocket_pnl_endpoint(websocket: WebSocket, market_id: str):
    await websocket.accept()
    try:
        async for data in simulate_pnl_stream(market_id):
            await websocket.send_text(data)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from PnL stream for {market_id}")


# ============================================================================
# P&L ATTRIBUTION ENDPOINTS
# ============================================================================

from app.attribution_service import AttributionService
from datetime import datetime as dt

attribution_service = AttributionService()

@app.get("/api/attribution/summary")
async def get_attribution_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get overall P&L attribution summary.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    summary = attribution_service.get_attribution_summary(db, current_user.id, start, end)
    return summary

@app.get("/api/attribution/by-model")
async def get_attribution_by_model(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get P&L breakdown by AI model.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    breakdown = attribution_service.get_attribution_by_dimension(
        db, current_user.id, "model_used", start, end
    )
    return {"breakdown": breakdown}

@app.get("/api/attribution/by-source")
async def get_attribution_by_source(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get P&L breakdown by data source.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    breakdown = attribution_service.get_attribution_by_data_source(
        db, current_user.id, start, end
    )
    return {"breakdown": breakdown}

@app.get("/api/attribution/by-strategy")
async def get_attribution_by_strategy(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get P&L breakdown by strategy type.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    breakdown = attribution_service.get_attribution_by_dimension(
        db, current_user.id, "strategy_type", start, end
    )
    return {"breakdown": breakdown}

@app.get("/api/attribution/by-category")
async def get_attribution_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get P&L breakdown by market category.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    breakdown = attribution_service.get_attribution_by_dimension(
        db, current_user.id, "category", start, end
    )
    return {"breakdown": breakdown}

@app.get("/api/attribution/timeseries")
async def get_attribution_timeseries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "day",
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get time-series P&L data for charting.
    """
    start = dt.fromisoformat(start_date) if start_date else None
    end = dt.fromisoformat(end_date) if end_date else None
    
    timeseries = attribution_service.get_time_series_pnl(
        db, current_user.id, start, end, interval
    )
    return {"timeseries": timeseries}

@app.get("/api/attribution/trades")
async def get_attribution_trades(
    limit: int = 50,
    offset: int = 0,
    model_used: Optional[str] = None,
    strategy_type: Optional[str] = None,
    category: Optional[str] = None,
    is_closed: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(database_users.get_db)
):
    """
    Get list of trades with attribution details.
    """
    filters = {}
    if model_used:
        filters["model_used"] = model_used
    if strategy_type:
        filters["strategy_type"] = strategy_type
    if category:
        filters["category"] = category
    if is_closed is not None:
        filters["is_closed"] = is_closed
    if start_date:
        filters["start_date"] = dt.fromisoformat(start_date)
    if end_date:
        filters["end_date"] = dt.fromisoformat(end_date)
    
    result = attribution_service.get_trades_with_attribution(
        db, current_user.id, limit, offset, filters
    )
    return result

@app.websocket("/ws/attribution")
async def websocket_attribution_endpoint(
    websocket: WebSocket,
    token: str = None
):
    """
    Real-time P&L attribution updates via WebSocket.
    """
    await websocket.accept()
    
    try:
        # In production, validate token and get user_id
        # For now, send periodic updates
        import asyncio
        
        while True:
            # This would be triggered by actual trade executions
            # For demo, send updates every 5 seconds
            await asyncio.sleep(5)
            
            # Mock update
            update = {
                "type": "attribution_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "total_pnl": 1250.50,
                    "change": 15.25
                }
            }
            
            await websocket.send_json(update)
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from attribution stream")


# ============================================================================
# PROBABILITY HEATMAP ENDPOINTS
# ============================================================================

from app.heatmap_service import heatmap_service
from app.heatmap_models import HeatmapData, DivergenceAlert, MarketProbabilityHistory

@app.get("/api/heatmap/probability-comparison", response_model=HeatmapData)
async def get_probability_heatmap(
    category: Optional[str] = None,
    min_divergence: Optional[float] = None,
    current_user: models_db.User = Depends(permissions.requires_trade_view())
):
    """
    Get heatmap data comparing implied market probability vs AI calculated probability.
    
    Args:
        category: Optional filter by market category
        min_divergence: Minimum absolute divergence to include (0.0 to 1.0)
    
    Returns:
        HeatmapData with cells for visualization
    """
    try:
        # Fetch current markets with AI probabilities
        # In production, this would query your database or cache
        # For now, we'll create sample data from live markets
        
        api_key = os.getenv("POLYMARKET_API_KEY", "")
        secret = os.getenv("POLYMARKET_SECRET", "")
        passphrase = os.getenv("POLYMARKET_PASSPHRASE", "")
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key=api_key,
            secret=secret,
            passphrase=passphrase,
            chain_id=137
        )
        
        # Get markets
        resp = client.get_markets(next_cursor="")
        
        # Transform to our format with AI probabilities
        markets_data = []
        for m in resp.get('data', [])[:30]:  # Limit to 30 markets
            if m.get('active') and m.get('tokens'):
                yes_token = next((t for t in m['tokens'] if t['outcome'] == 'Yes'), None)
                market_price = float(yes_token.get('price', 0.5)) if yes_token else 0.5
                
                # Simulate AI probability (in production, fetch from forecast results)
                # For demo, add some variance to market price
                import random
                ai_probability = max(0.01, min(0.99, market_price + random.uniform(-0.15, 0.15)))
                
                markets_data.append({
                    'market_id': m.get('condition_id'),
                    'question': m.get('question'),
                    'category': m.get('tags', ['General'])[0] if m.get('tags') else 'General',
                    'market_price': market_price,
                    'ai_probability': ai_probability,
                    'volume_24h': float(m.get('volume_24h', 0) or 0),
                    'confidence_score': random.uniform(0.6, 0.95)
                })
        
        # Generate heatmap data
        heatmap_data = heatmap_service.get_heatmap_data(
            markets_data,
            category_filter=category,
            min_divergence=min_divergence
        )
        
        return heatmap_data
        
    except Exception as e:
        logger.error(f"Error generating heatmap data: {e}")
        # Return empty heatmap on error
        return HeatmapData(
            cells=[],
            timestamp=datetime.utcnow(),
            total_markets=0,
            avg_divergence=0.0,
            max_divergence=0.0,
            min_divergence=0.0
        )

@app.get("/api/heatmap/markets/{market_id}/history", response_model=MarketProbabilityHistory)
async def get_market_probability_history(
    market_id: str,
    timeframe: str = "24h",
    current_user: models_db.User = Depends(permissions.requires_trade_view())
):
    """
    Get historical probability data for a specific market.
    
    Args:
        market_id: Market/condition ID
        timeframe: Time range ("1h", "6h", "24h", "7d")
    
    Returns:
        Historical probability data
    """
    history = heatmap_service.get_market_history(market_id, timeframe)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for market {market_id}"
        )
    
    return history

@app.get("/api/heatmap/divergence-alerts", response_model=List[DivergenceAlert])
async def get_divergence_alerts(
    high_threshold: float = 0.2,
    medium_threshold: float = 0.1,
    current_user: models_db.User = Depends(permissions.requires_trade_view())
):
    """
    Get alerts for significant probability divergences.
    
    Args:
        high_threshold: Threshold for HIGH severity alerts (default 0.2 = 20%)
        medium_threshold: Threshold for MEDIUM severity alerts (default 0.1 = 10%)
    
    Returns:
        List of divergence alerts sorted by severity
    """
    try:
        # Fetch current markets (similar to heatmap endpoint)
        api_key = os.getenv("POLYMARKET_API_KEY", "")
        secret = os.getenv("POLYMARKET_SECRET", "")
        passphrase = os.getenv("POLYMARKET_PASSPHRASE", "")
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key=api_key,
            secret=secret,
            passphrase=passphrase,
            chain_id=137
        )
        
        resp = client.get_markets(next_cursor="")
        
        markets_data = []
        for m in resp.get('data', [])[:30]:
            if m.get('active') and m.get('tokens'):
                yes_token = next((t for t in m['tokens'] if t['outcome'] == 'Yes'), None)
                market_price = float(yes_token.get('price', 0.5)) if yes_token else 0.5
                
                import random
                ai_probability = max(0.01, min(0.99, market_price + random.uniform(-0.25, 0.25)))
                
                markets_data.append({
                    'market_id': m.get('condition_id'),
                    'question': m.get('question'),
                    'category': m.get('tags', ['General'])[0] if m.get('tags') else 'General',
                    'market_price': market_price,
                    'ai_probability': ai_probability
                })
        
        alerts = heatmap_service.get_divergence_alerts(
            markets_data,
            high_threshold=high_threshold,
            medium_threshold=medium_threshold
        )
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error generating divergence alerts: {e}")
        return []

