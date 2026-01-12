from typing import List
from app.connectors.base import DataSource
from app.models import Source

class NOAAConnector(DataSource):
    @property
    def name(self) -> str:
        return "NOAA Weather"

    async def fetch_data(self, query: str) -> List[Source]:
        # Mock NOAA weather impact analysis
        return [
            Source(
                title=f"NOAA: Weather impact on {query}",
                url="https://www.noaa.gov/",
                snippet=f"NOAA weather models predict conditions that could affect supply chains relevant to {query}."
            )
        ]

class CSPANConnector(DataSource):
    @property
    def name(self) -> str:
        return "C-SPAN"

    async def fetch_data(self, query: str) -> List[Source]:
        # Mock C-SPAN political context
        return [
            Source(
                title=f"C-SPAN: Legislative hearings related to {query}",
                url="https://www.c-span.org/",
                snippet=f"Recent C-SPAN coverage includes congressional debate on policy affecting {query}."
            )
        ]
