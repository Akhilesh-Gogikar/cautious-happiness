from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.core.auth import get_current_active_user
from app.services.execution import ExecutionService

router = APIRouter(
    prefix="/trade",
    tags=["trade"],
)

execution_service = ExecutionService()

@router.post("/execute")
async def execute_trade(current_user: User = Depends(get_current_active_user)):
    """
    Constructs a transaction payload for the frontend to sign.
    """
    if current_user.role not in ["admin", "trader"]:
         raise HTTPException(status_code=403, detail="Insufficient privileges")

    return await execution_service.construct_trade_payload()
