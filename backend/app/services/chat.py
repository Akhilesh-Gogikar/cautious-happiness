import os
from typing import AsyncIterator
import time
from sqlalchemy import select
from app.models import ChatRequest, ChatResponse
from app.db.models import ChatMessage
from app.db.session import get_db
from app.engine import IntelligenceMirrorEngine

class ChatService:
    def __init__(self, engine: IntelligenceMirrorEngine):
        self.engine = engine

    async def process_message(self, user_id: str, request: ChatRequest) -> ChatResponse:
        # 1. Add User Message to DB
        async for session in get_db():
            user_msg = ChatMessage(
                user_id=user_id,
                role="user",
                content=request.question,
                timestamp=time.time()
            )
            session.add(user_msg)
            await session.commit()
            
            # 2. Retrieve Context & History (Last 10 messages for context)
            # In a real app, we'd vector search here too
            stmt = select(ChatMessage).where(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp.desc()).limit(11) # 10 history + 1 current (already added)
            result = await session.execute(stmt)
            history_objs = result.scalars().all()
            
            # Convert DB objects to Pydantic models for the engine
            from app.models import ChatMessage as ChatMessageModel
            # Filter out the message we just added (or include it if the engine expects it, but usually history is previous messages)
            # Actually, the engine expects 'history' to be previous messages. 
            # The current question is in request.question.
            # History_objs is descending, so history_objs[0] is the current msg (role: user, content: request.question)
            request.history = [
                ChatMessageModel(role=msg.role, content=msg.content, timestamp=msg.timestamp)
                for msg in reversed(history_objs[1:]) # Skip current, reverse to chronological
            ]
            
            # 3. Generate Response (using Engine)
            response_text = await self.engine.chat_with_model(request)
            
            # 4. Add Assistant Message to DB
            assistant_msg = ChatMessage(
                user_id=user_id,
                role="assistant",
                content=response_text,
                timestamp=time.time()
            )
            session.add(assistant_msg)
            await session.commit()
            
            return ChatResponse(response=response_text)

    async def stream_message(self, user_id: str, request: ChatRequest) -> AsyncIterator[str]:
        """Stream a chat response as Server-Sent Events while persisting final output."""
        async for session in get_db():
            user_msg = ChatMessage(
                user_id=user_id,
                role="user",
                content=request.question,
                timestamp=time.time()
            )
            session.add(user_msg)
            await session.commit()

            stmt = (
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.timestamp.desc())
                .limit(11)
            )
            result = await session.execute(stmt)
            history_objs = result.scalars().all()

            from app.models import ChatMessage as ChatMessageModel

            request.history = [
                ChatMessageModel(role=msg.role, content=msg.content, timestamp=msg.timestamp)
                for msg in reversed(history_objs[1:])
            ]

            prompt = self.engine.intelligence_service._build_chat_prompt(request)
            model = request.model if request.model != "openforecaster" else "lfm-thinking"
            provider = "llama-cpp"
            if model == "gemini-pro":
                provider = "gemini"
            elif os.getenv("OLLAMA_HOST") and model != "lfm-thinking":
                provider = "ollama"

            yield 'event: thinking\ndata: {"phase":"thinking","message":"Building reasoning graph..."}\n\n'

            chunks = []
            async for chunk in self.engine.intelligence_service.ai_stream(prompt, provider=provider, model=model):
                chunks.append(chunk)
                safe = chunk.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                yield f'event: token\ndata: {{"token":"{safe}"}}\n\n'

            response_text = "".join(chunks).strip() or "I couldn't generate a response."

            assistant_msg = ChatMessage(
                user_id=user_id,
                role="assistant",
                content=response_text,
                timestamp=time.time()
            )
            session.add(assistant_msg)
            await session.commit()

            safe_response = response_text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            yield f'event: done\ndata: {{"response":"{safe_response}"}}\n\n'
            return
