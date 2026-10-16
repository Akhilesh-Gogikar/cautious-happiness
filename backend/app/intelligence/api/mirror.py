from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.core.auth import get_current_active_user
from app.intelligence.application.mirror import MirrorService
from app.mirror.models import AnalysisResult, Competitor

# Every /mirror route needs a signed-in user (QA-012).
router = APIRouter(prefix="/mirror", tags=["intelligence-mirror"], dependencies=[Depends(get_current_active_user)])
mirror_service = MirrorService()


@router.get("/competitors", response_model=List[Competitor])
async def get_competitors():
    return await mirror_service.get_competitors()


@router.post("/analyze/{target_id}", response_model=AnalysisResult)
async def analyze_target(target_id: str, query: str = None):
    if not query:
        query = target_id.replace("_", " ")

    try:
        return await mirror_service.analyze_target(query, target_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
