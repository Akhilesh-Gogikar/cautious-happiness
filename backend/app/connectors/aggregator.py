import asyncio
import logging
from typing import List
from app.connectors.base import DataSource
from app.models import Source

logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self, sources: List[DataSource]):
        self.sources = sources

    async def fetch_all(self, query: str) -> List[Source]:
        """
        Fetch data from all registered sources in parallel.
        """
        tasks = [source.fetch_data(query) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated_sources = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching data from {self.sources[i].name}: {result}")
            else:
                aggregated_sources.extend(result)
        
        return aggregated_sources
