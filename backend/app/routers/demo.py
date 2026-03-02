from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()

# Single orchestrator instance for demo endpoint
orchestrator = AgentOrchestrator()

class DemoRequest(BaseModel):
    scenario: str

@router.post("/analyze")
async def analyze_scenario(request: DemoRequest):
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
async def ingest_news(title: str, content: str, category: str = "geopolitics"):
    """
    Utility endpoint to pump news into the RAG vector DB.
    """
    try:
        await orchestrator.news_agent.ingest_news(title, content, category)
        return {"status": "success", "message": f"Ingested news: {title}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
