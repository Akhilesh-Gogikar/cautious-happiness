from __future__ import annotations

import asyncio
from typing import Any

from duckduckgo_search import DDGS


class DuckDuckGoSearchGateway:
    """Thin adapter around DDGS so services do not construct search clients directly."""

    def __init__(self, client: DDGS | None = None):
        self.client = client or DDGS()

    async def search_text(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        results = await asyncio.to_thread(self.client.text, query, max_results=max_results)
        return list(results or [])
