from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.mirror.service import MirrorService
from app.mirror.models import Competitor, AnalysisResult

router = APIRouter(prefix="/mirror", tags=["intelligence-mirror"])
mirror_service = MirrorService()

@router.get("/competitors", response_model=List[Competitor])
async def get_competitors():
    """
    Get list of tracked competitor algorithms/desks.
    """
    return await mirror_service.get_competitors()

@router.post("/analyze/{target_id}", response_model=AnalysisResult)
async def analyze_target(target_id: str, query: str = None):
    """
    Trigger a 'Mirror Analysis' on a specific target.
    If query is not provided, uses the target_id (or name associated with it).
    """
    # For MVP, we map target_id to a query manually if needed, or just use query.
    if not query:
        query = target_id.replace("_", " ")
        
    try:
        result = await mirror_service.analyze_target(query, target_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
