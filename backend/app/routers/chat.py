from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models import User, ChatRequest, ChatResponse
from app.core.auth import get_current_active_user
from app.services.chat import ChatService
from app.intelligence.application.engine import IntelligenceMirrorEngine

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

# In a full DI refactor, these would be injected
engine = IntelligenceMirrorEngine()
chat_service = ChatService(engine)

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, current_user: User = Depends(get_current_active_user)):
    if not req.question:
         raise HTTPException(status_code=400, detail="Question required")

    return await chat_service.process_message(current_user.username, req)


@router.post("/stream")
async def chat_stream_endpoint(req: ChatRequest, current_user: User = Depends(get_current_active_user)):
    if not req.question:
         raise HTTPException(status_code=400, detail="Question required")

    return StreamingResponse(
        chat_service.stream_message(current_user.username, req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
