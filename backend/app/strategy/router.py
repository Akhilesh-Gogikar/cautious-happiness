from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_active_user
from app.strategy.models import StrategyGenerationRequest, StrategyCode
from app.strategy.service import strategy_factory

# Every route here needs a signed-in user (QA-012).
router = APIRouter(
    prefix="/strategy",
    tags=["strategy"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=StrategyCode)
async def generate_strategy(request: StrategyGenerationRequest):
    """
    Generate a Python trading strategy from a natural language prompt.
    """
    strategy = await strategy_factory.generate_strategy(request)
    if not strategy:
        raise HTTPException(status_code=500, detail="Failed to generate strategy")
    return strategy
