from duckduckgo_search import DDGS

from app.intelligence.application.mirror import MirrorService as BaseMirrorService
from app.intelligence.infrastructure.search import DuckDuckGoSearchGateway


class MirrorService(BaseMirrorService):
    def __init__(self, *args, search_gateway=None, **kwargs):
        gateway = search_gateway or DuckDuckGoSearchGateway(DDGS())
        super().__init__(*args, search_gateway=gateway, **kwargs)


__all__ = ["MirrorService", "DDGS"]
