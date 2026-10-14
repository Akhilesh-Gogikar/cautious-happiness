from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.core.auth import get_current_active_user
from app.models import User
from app.connectors.alpaca import AlpacaConnector

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
)

class ToolCallRequest(BaseModel):
    connector: str
    name: str
    arguments: Dict[str, Any]

ALPACA_NOT_CONFIGURED = "Alpaca is not configured on the server. Set ALPACA_API_KEY and ALPACA_SECRET_KEY."


@router.get("/alpaca/status")
async def alpaca_status(current_user: User = Depends(get_current_active_user)):
    """Whether the server holds Alpaca credentials, and for paper or live trading."""
    connector = AlpacaConnector()
    return {"configured": connector.configured, "paper": connector.paper}


@router.post("/call")
async def call_tool(
    tool_req: ToolCallRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calls a backend capability connector.
    """
    if tool_req.connector == "alpaca":
        # Credentials come only from the server's environment; browsers no
        # longer hold or send them.
        connector = AlpacaConnector()
        if not connector.configured:
            raise HTTPException(status_code=503, detail=ALPACA_NOT_CONFIGURED)
        await connector.connect()
        try:
            result = await connector.call_tool(tool_req.name, tool_req.arguments)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            await connector.disconnect()
            
    raise HTTPException(status_code=404, detail=f"Connector {tool_req.connector} not found or unsupported")
