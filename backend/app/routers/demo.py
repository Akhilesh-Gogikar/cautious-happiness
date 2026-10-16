import threading
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.agents.orchestrator import AgentOrchestrator
from app.core.auth import get_current_active_user

# Every route here needs a signed-in user (QA-012). Router dependencies run first,
# so an anonymous request is refused before the orchestrator (and its embedder) loads.
router = APIRouter(dependencies=[Depends(get_current_active_user)])

# Single orchestrator instance for demo endpoint, built on first use: constructing
# it loads the BAAI/bge-m3 embedder (~2 GB), which must not block API startup.
_orchestrator: Optional[AgentOrchestrator] = None
_orchestrator_lock = threading.Lock()


def get_orchestrator() -> AgentOrchestrator:
    # Sync dependency, so FastAPI runs it in the threadpool rather than the event loop.
    global _orchestrator
    if _orchestrator is None:
        with _orchestrator_lock:
            if _orchestrator is None:
                _orchestrator = AgentOrchestrator()
    return _orchestrator

class DemoRequest(BaseModel):
    scenario: str

@router.post("/analyze")
async def analyze_scenario(request: DemoRequest, orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """
    Run the multi-agentic demo pipeline using Llama.cpp backend and pgvector RAG.
    Tracks global events and polymarket odds to suggest structural trades across timeframes.
    """
    try:
        response = await orchestrator.run_demo_pipeline(request.scenario)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest_news")
async def ingest_news(title: str, content: str, category: str = "geopolitics", orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """
    Utility endpoint to pump news into the RAG vector DB.
    """
    try:
        await orchestrator.news_agent.ingest_news(title, content, category)
        return {"status": "success", "message": f"Ingested news: {title}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
