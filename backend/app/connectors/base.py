from abc import ABC, abstractmethod
from typing import List
from app.models import Source

class DataSource(ABC):
    @abstractmethod
    async def fetch_data(self, query: str) -> List[Source]:
        """
        Fetch data from the source and return a list of Source objects.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the data source.
        """
        pass
