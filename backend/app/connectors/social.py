from typing import List
from app.connectors.base import DataSource
from app.models import Source

class TwitterConnector(DataSource):
    @property
    def name(self) -> str:
        return "X/Twitter"

    async def fetch_data(self, query: str) -> List[Source]:
        # Mock sentiment analysis from X
        return [
            Source(
                title=f"X: Viral trend about {query}",
                url="https://x.com/search",
                snippet=f"Social sentiment on X for {query} is currently trending bullish with high volume."
            )
        ]

class RedditConnector(DataSource):
    @property
    def name(self) -> str:
        return "Reddit"

    async def fetch_data(self, query: str) -> List[Source]:
        # Mock sentiment analysis from Reddit
        return [
            Source(
                title=f"Reddit: r/WallStreetBets discussion on {query}",
                url="https://reddit.com/r/wallstreetbets",
                snippet=f"Reddit communities are actively debating the long-term prospects of {query}."
            )
        ]

class DiscordConnector(DataSource):
    @property
    def name(self) -> str:
        return "Discord"

    async def fetch_data(self, query: str) -> List[Source]:
        # Mock sentiment from private Discord ALPHA groups
        return [
            Source(
                title=f"Discord: ALPHA signal for {query}",
                url="https://discord.com",
                snippet=f"Insider discussions in gated Discord channels suggest upcoming volatility for {query}."
            )
        ]
