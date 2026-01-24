from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import datetime
import uuid

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.status = "IDLE"  # IDLE, BUSY, ERROR, COMPLETED
        self.current_task: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []
        self.data_store: Dict[str, Any] = {}

    def log(self, message: str, level: str = "INFO"):
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        # In a real system, we would stream this to a WebSocket or Redis Pub/Sub
        print(f"[{self.name}] {level}: {message}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point for agent logic."""
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "current_task": self.current_task,
            "log_count": len(self.logs)
        }
