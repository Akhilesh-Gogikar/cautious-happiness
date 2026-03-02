from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

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

@router.post("/call")
async def call_tool(
    request: Request,
    tool_req: ToolCallRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Calls a backend capability connector dynamically via headers.
    """
    if tool_req.connector == "alpaca":
        api_key = request.headers.get("x-alpaca-api-key")
        secret_key = request.headers.get("x-alpaca-secret")
        
        connector = AlpacaConnector(api_key=api_key, secret_key=secret_key)
        await connector.connect()
        try:
            result = await connector.call_tool(tool_req.name, tool_req.arguments)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            await connector.disconnect()
            
    raise HTTPException(status_code=404, detail=f"Connector {tool_req.connector} not found or unsupported")
