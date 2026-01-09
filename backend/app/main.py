from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.engine import ForecasterCriticEngine, ForecastResult
from app.models import ForecastResult, ChatRequest, ChatResponse
from app.engine import ForecasterCriticEngine
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

app = FastAPI(title="Polymarket Hedge Fund Dashboard")

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

engine = ForecasterCriticEngine()

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
    Fetch active markets from Polymarket CLOB.
    Uses 'py-clob-client' to get real-time data.
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
        markets_data = []
        for m in resp.get('data', [])[:20]: # Limit to 20 for density
            if m.get('active') and m.get('tokens'):
                # Heuristic: Find YES token price
                yes_token = next((t for t in m['tokens'] if t['outcome'] == 'Yes'), None)
                price = yes_token.get('price', 0.5) if yes_token else 0.0
                
                markets_data.append({
                    "id": m.get('condition_id'),
                    "question": m.get('question'),
                    "volume_24h": float(m.get('volume_24h', 0) or 0), 
                    "last_price": float(price),
                    "category": m.get('tags', ['General'])[0] if m.get('tags') else 'General'
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

# Placeholder for CLOB Client Wrapper
@app.post("/trade/execute")
async def execute_trade():
    """
    Constructs a transaction payload for the frontend to sign.
    """
    # Return a mocked transaction object
    return {
        "status": "ready_to_sign",
        "tx_payload": {
            "to": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E", # Polymarket CTF Exchange
            "data": "0x...", # Hex data
            "value": "0",
            "chainId": 137 # Polygon
        }
    }
