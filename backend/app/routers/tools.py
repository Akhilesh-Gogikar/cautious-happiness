import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.core.auth import get_current_active_user
from app.models import User
from app.connectors.alpaca import AlpacaConnector

logger = logging.getLogger("alpha_insights")

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
)

# Reading the account is open to every signed-in user; any other Alpaca tool
# (placing orders, and whatever is added later) needs a trading role.
ALPACA_READ_TOOLS = {"get_account", "list_positions"}
TRADING_ROLES = {"admin", "trader"}

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
        trading = tool_req.name not in ALPACA_READ_TOOLS
        if trading and current_user.role not in TRADING_ROLES:
            logger.warning(f"Alpaca {tool_req.name} refused for {current_user.username} (role {current_user.role})")
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        if trading:
            logger.info(f"Alpaca {tool_req.name} by {current_user.username} (role {current_user.role}): {tool_req.arguments}")

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
