from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import hashlib
import json
from app.models import User
from app.core.auth import get_current_active_user
from app.limiter import check_rate_limit
from app.cache import r as redis_client
from app.worker import run_forecast_task
from celery.result import AsyncResult
from app.worker import celery_app

router = APIRouter(
    prefix="/prediction",
    tags=["prediction"],
)

class PredictionRequest(BaseModel):
    question: str
    model: str = "lfm-thinking"

@router.post("/predict", dependencies=[Depends(check_rate_limit)])
async def predict_market(request: PredictionRequest, current_user: User = Depends(get_current_active_user)):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")

    q_hash = hashlib.md5(request.question.encode()).hexdigest()
    cache_key = f"prediction_result:{q_hash}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {
            "task_id": f"cached_{q_hash}", 
            "status": "cached", 
            "result": json.loads(cached_data)
        }
    
    task = run_forecast_task.delay(request.question, request.model)
    return {"task_id": task.id, "status": "processing"}

@router.get("/task/{task_id}")
async def get_task_status(task_id: str, current_user: User = Depends(get_current_active_user)):
    if task_id.startswith("cached_"):
        cache_key = f"prediction_result:{task_id.replace('cached_', '')}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
             return {"id": task_id, "status": "completed", "result": json.loads(cached_data)}
        else:
             return {"id": task_id, "status": "failed", "result": None}

    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        result = task_result.get()
        return {"id": task_id, "status": "completed", "result": result}
    return {"id": task_id, "status": "processing"}
