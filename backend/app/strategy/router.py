from fastapi import APIRouter, HTTPException
from app.strategy.models import StrategyGenerationRequest, StrategyCode
from app.strategy.service import strategy_factory

router = APIRouter(
    prefix="/strategy",
    tags=["strategy"],
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
