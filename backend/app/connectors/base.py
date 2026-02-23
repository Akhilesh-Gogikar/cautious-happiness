
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

class ResourceDefinition(BaseModel):
    uri: str
    name: str
    mime_type: Optional[str] = None

class BaseConnector(ABC):
    @abstractmethod
    async def connect(self):
        """Establish connection to the data source/service."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection."""
        pass

    @abstractmethod
    async def list_tools(self) -> List[ToolDefinition]:
        """List available tools provided by this connector."""
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool."""
        pass

    @abstractmethod
    async def list_resources(self) -> List[ResourceDefinition]:
        """List available resources."""
        pass

    @abstractmethod
    async def read_resource(self, uri: str) -> str:
        """Read content of a resource."""
        pass
