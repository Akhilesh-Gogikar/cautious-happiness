from typing import Dict, List, Optional
from app.agents.base import BaseAgent

class AgentRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.agents: Dict[str, BaseAgent] = {}
        return cls._instance

    def register(self, agent: BaseAgent):
        self.agents[agent.id] = agent
        print(f"Registered agent: {agent.name} ({agent.role})")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict]:
        return [agent.get_status() for agent in self.agents.values()]

    def get_agents_by_role(self, role: str) -> List[BaseAgent]:
        return [a for a in self.agents.values() if a.role == role]

registry = AgentRegistry()
