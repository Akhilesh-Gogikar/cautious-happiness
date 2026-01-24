from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from . import models_db, auth, database_users

router = APIRouter(prefix="/agents", tags=["agents"])

# --- Pydantic Models ---

class CustomAgentCreate(BaseModel):
    name: str
    role: str = "analyst"
    system_prompt: str
    data_sources: List[str] = []
    triggers: Dict[str, Any] = {}
    output_actions: Dict[str, Any] = {}

class CustomAgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    system_prompt: Optional[str] = None
    data_sources: Optional[List[str]] = None
    triggers: Optional[Dict[str, Any]] = None
    output_actions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class CustomAgentResponse(BaseModel):
    id: int
    name: str
    role: str
    system_prompt: str
    data_sources: List[str]
    triggers: Dict[str, Any]
    output_actions: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AgentExecutionCreate(BaseModel):
    context: str
    input_data: Dict[str, Any]

class ExecutionResponse(BaseModel):
    id: int
    agent_id: int
    context: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    executed_at: datetime

    class Config:
        from_attributes = True

class DataSource(BaseModel):
    id: str
    name: str
    type: str
    description: str

# --- Endpoints ---

@router.get("/custom", response_model=List[CustomAgentResponse])
async def get_custom_agents(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """List all custom agents for the current user."""
    return current_user.custom_agents

@router.post("/custom", response_model=CustomAgentResponse)
async def create_custom_agent(
    agent_in: CustomAgentCreate,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """Create a new custom agent."""
    new_agent = models_db.CustomAgent(
        user_id=current_user.id,
        name=agent_in.name,
        role=agent_in.role,
        system_prompt=agent_in.system_prompt,
        data_sources=agent_in.data_sources,
        triggers=agent_in.triggers,
        output_actions=agent_in.output_actions
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

@router.get("/custom/{agent_id}", response_model=CustomAgentResponse)
async def get_custom_agent(
    agent_id: int,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """Get a specific custom agent."""
    agent = db.query(models_db.CustomAgent).filter(
        models_db.CustomAgent.id == agent_id,
        models_db.CustomAgent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/custom/{agent_id}", response_model=CustomAgentResponse)
async def update_custom_agent(
    agent_id: int,
    agent_in: CustomAgentUpdate,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """Update a custom agent."""
    agent = db.query(models_db.CustomAgent).filter(
        models_db.CustomAgent.id == agent_id,
        models_db.CustomAgent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    for field, value in agent_in.dict(exclude_unset=True).items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.delete("/custom/{agent_id}")
async def delete_custom_agent(
    agent_id: int,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """Delete a custom agent."""
    agent = db.query(models_db.CustomAgent).filter(
        models_db.CustomAgent.id == agent_id,
        models_db.CustomAgent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return {"status": "success", "message": "Agent deleted"}

@router.post("/custom/{agent_id}/execute", response_model=ExecutionResponse)
async def execute_custom_agent(
    agent_id: int,
    execution_in: AgentExecutionCreate,
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    """
    Execute a custom agent with a given context.
    In a real system, this would trigger an LLM call.
    For now, it records the execution and returns a mock response.
    """
    agent = db.query(models_db.CustomAgent).filter(
        models_db.CustomAgent.id == agent_id,
        models_db.CustomAgent.user_id == current_user.id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Mock LLM execution logic
    output_data = {
        "response": f"Processed input '{execution_in.input_data}' using prompt: {agent.system_prompt[:50]}...",
        "actions": ["log_entry", "notify_user"]
    }
    
    new_execution = models_db.AgentExecution(
        agent_id=agent.id,
        context=execution_in.context,
        input_data=execution_in.input_data,
        output_data=output_data
    )
    db.add(new_execution)
    db.commit()
    db.refresh(new_execution)
    return new_execution

@router.get("/data-sources", response_model=List[DataSource])
async def list_data_sources(
    current_user: models_db.User = Depends(auth.get_current_user)
):
    """List available data sources for agents."""
    return [
        DataSource(id="binance", name="Binance", type="exchange", description="Crypto spot and futures data"),
        DataSource(id="coingecko", name="CoinGecko", type="market", description="Broad market data and prices"),
        DataSource(id="yahoo", name="Yahoo Finance", type="macro", description="Stock and macro economic data"),
        DataSource(id="polymarket", name="Polymarket CLOB", type="prediction", description="Prediction market order books"),
        DataSource(id="chat_history", name="Chat History", type="database", description="Past user conversations"),
        DataSource(id="news_feed", name="Global News", type="news", description="Real-time financial news"),
    ]

@router.get("/executions", response_model=List[ExecutionResponse])
async def get_execution_history(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db),
    limit: int = 20
):
    """Get recent agent executions."""
    # This query joins executions with agents to filter by user
    executions = db.query(models_db.AgentExecution).join(models_db.CustomAgent).filter(
        models_db.CustomAgent.user_id == current_user.id
    ).order_by(models_db.AgentExecution.executed_at.desc()).limit(limit).all()
    
    return executions
