from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.engine import IntelligenceMirrorEngine, ForecastResult
from app.models import ForecastResult, ChatRequest, ChatResponse
import os
import logging
import json
import time

# ... (Logging config) ...
# (We need to be careful not to delete logging config if we replace top of file)
# This replace block is risky if I don't match exactly.
# I'll use a safer insertion point after `app = FastAPI`.


# Configure JSON Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polymarket_dashboard")

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

app = FastAPI(title="Alpha Insights: Commodity Intelligence")

# CORS Configuration
origins = ["*"] # Simplification for dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {str(exc)}")
    return {
        "error": True,
        "message": "Internal Server Error",
        "detail": str(exc),
        "path": request.url.path
    }

engine = IntelligenceMirrorEngine()

# Pydantic models
from pydantic import BaseModel
class PredictionRequest(BaseModel):
    question: str
    model: str = "lfm-thinking"

@app.get("/api-spec")
def get_api_spec():
    """
    Export the OpenAPI specification as JSON.
    """
    return app.openapi()

from app.health import get_system_health

@app.get("/health")
async def health_check():
    health_status = await get_system_health()
    status = "ok" if all(health_status.values()) else "degraded"
    return {"status": status, "details": health_status}

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

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Chat with the model about a prediction context.
    """
    if not req.user_message:
        raise HTTPException(status_code=400, detail="Message required")
    
    response_text = await engine.chat_with_model(req)
    return {"response": response_text}

from py_clob_client.client import ClobClient
from app.cache import cache_response

@app.get("/markets")
@cache_response(ttl_seconds=30)
async def get_markets():
    """
    Fetch active physical commodity instruments.
    For MVP, this returns a curated list of key physical markets.
    """
    return [
        {
            "id": "brent_crude",
            "question": "Brent Crude Oil (Spot Physical)",
            "volume_24h": 1240000,
            "last_price": 0.82, # Representing a high physical premium
            "category": "Energy"
        },
        {
            "id": "wti_crude",
            "question": "WTI Crude Oil (Cushing Delivery)",
            "volume_24h": 980000,
            "last_price": 0.55,
            "category": "Energy"
        },
        {
            "id": "ttf_gas",
            "question": "Dutch TTF Natural Gas (Physical)",
            "volume_24h": 450000,
            "last_price": 0.91,
            "category": "Energy"
        },
        {
            "id": "lme_copper",
            "question": "LME Copper Grade A (Warehouse)",
            "volume_24h": 320000,
            "last_price": 0.42,
            "category": "Metals"
        },
        {
            "id": "iron_ore",
            "question": "Iron Ore 62% Fe (Tianjin Port)",
            "volume_24h": 150000,
            "last_price": 0.28,
            "category": "Metals"
        },
        {
            "id": "soybeans",
            "question": "Soybeans (US No. 2 Yellow)",
            "volume_24h": 85000,
            "last_price": 0.64,
            "category": "Agri"
        }
    ]

# ... existing code ...
from app.intelligence import router as intelligence_router
from app.strategy import router as strategy_router

app.include_router(intelligence_router)
app.include_router(strategy_router)


from app.services.execution import ExecutionService

execution_service = ExecutionService()

@app.post("/trade/execute")
async def execute_trade():
    """
    Constructs a transaction payload for the frontend to sign.
    Delegates to ExecutionService.
    """
    return await execution_service.construct_trade_payload()

