from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import hashlib
import json
from celery.result import AsyncResult

from app.cache import r as redis_client
from app.core.auth import get_current_active_user
from app.limiter import check_rate_limit
from app.models import User
from app.worker import celery_app, run_forecast_task

router = APIRouter(
    prefix="/prediction",
    tags=["prediction"],
)
compat_router = APIRouter(tags=["prediction-compat"])


class PredictionRequest(BaseModel):
    question: str
    model: str = "lfm-thinking"


async def _predict_market(
    request: PredictionRequest,
    current_user: User = Depends(get_current_active_user),
):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")

    q_hash = hashlib.md5(request.question.encode()).hexdigest()
    cache_key = f"prediction_result:{q_hash}"

    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {
            "task_id": f"cached_{q_hash}",
            "status": "cached",
            "result": json.loads(cached_data),
        }

    task = run_forecast_task.delay(request.question, request.model)
    return {"task_id": task.id, "status": "processing"}


async def _get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
):
    if task_id.startswith("cached_"):
        cache_key = f"prediction_result:{task_id.replace('cached_', '')}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return {"id": task_id, "status": "completed", "result": json.loads(cached_data)}
        return {"id": task_id, "status": "failed", "result": None}

    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        result = task_result.get()
        return {"id": task_id, "status": "completed", "result": result}
    return {"id": task_id, "status": "processing"}


router.add_api_route(
    "/predict",
    _predict_market,
    methods=["POST"],
    dependencies=[Depends(check_rate_limit)],
)
compat_router.add_api_route(
    "/predict",
    _predict_market,
    methods=["POST"],
    dependencies=[Depends(check_rate_limit)],
)
router.add_api_route("/task/{task_id}", _get_task_status, methods=["GET"])
compat_router.add_api_route("/task/{task_id}", _get_task_status, methods=["GET"])
