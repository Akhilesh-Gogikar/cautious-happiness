from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
import time
import asyncio
from celery.result import AsyncResult
from app.worker import celery_app
from app.cache import r as redis_client
from app.health import get_system_health

# Modular Routers
from app.routers.auth import router as auth_router
from app.routers.markets import router as markets_router
from app.routers.prediction import router as prediction_router
from app.routers.trade import router as trade_router
from app.routers.chat import router as chat_router
from app.domain.intelligence import router as intelligence_router
from app.strategy import router as strategy_router
from app.mirror.router import router as mirror_router
from app.routers.scanner import router as scanner_router
from app.routers.demo import router as demo_router
from app.routers.tools import router as tools_router

# Configure Structured Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alpha_insights")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "request_id": getattr(record, "request_id", "none")
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.propagate = False

app = FastAPI(title="Alpha Insights: Unified Commodity Intelligence")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID & Logging Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Request trace: {request.method} {request.url.path} handled in {process_time:.4f}s",
        extra={"request_id": request.headers.get("X-Request-ID", "internal")}
    )
    return response

# Global Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Critical System Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal Server Error", "detail": str(exc)}
    )

# Include Routers
app.include_router(auth_router)
app.include_router(markets_router)
app.include_router(prediction_router)
app.include_router(trade_router)
app.include_router(chat_router)
app.include_router(intelligence_router)
app.include_router(strategy_router)
app.include_router(mirror_router)
app.include_router(scanner_router)
app.include_router(tools_router)
app.include_router(demo_router, prefix="/demo", tags=["demo"])

@app.get("/health")
async def health_check():
    health_status = await get_system_health()
    status = "ok" if all(health_status.values()) else "degraded"
    return {"status": status, "details": health_status}

@app.websocket("/ws/lifecycle/{task_id}")
async def websocket_lifecycle(websocket: WebSocket, task_id: str):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"task_events:{task_id}"
    await pubsub.subscribe(channel)
    
    try:
        if task_id.startswith("cached_"):
            await websocket.send_json({"event": "status", "message": "Analysis complete (Cached)"})
            await websocket.close()
            return

        result = AsyncResult(task_id, app=celery_app)
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message['data'])
                await websocket.send_json(data)
                if data.get("event") == "complete":
                    break
            
            await asyncio.sleep(0.1)
            if result.ready():
                await websocket.send_json({"event": "complete", "message": "Task finished."})
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {task_id}")
    finally:
        await pubsub.unsubscribe(channel)
        try:
            await websocket.close()
        except:
            pass
