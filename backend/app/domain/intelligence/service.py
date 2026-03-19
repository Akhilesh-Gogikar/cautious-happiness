from duckduckgo_search import DDGS

from app.intelligence.application.forecasting import IntelligenceService as BaseIntelligenceService
from app.intelligence.infrastructure.search import DuckDuckGoSearchGateway


class IntelligenceService(BaseIntelligenceService):
    def __init__(self, *args, search_gateway=None, **kwargs):
        gateway = search_gateway or DuckDuckGoSearchGateway(DDGS())
        super().__init__(*args, search_gateway=gateway, **kwargs)


__all__ = ["IntelligenceService", "DDGS"]
