import logging
from typing import List
from app.models import Source
from app.vector_db import VectorDBClient
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class NewsIngestor:
    def __init__(self, vector_db: VectorDBClient):
        self.vector_db = vector_db
        self.ddgs = DDGS()

    async def fetch_and_store(self, query: str, max_results: int = 5) -> List[Source]:
        """
        Search for news and store them in the vector database.
        """
        logger.info(f"Ingesting news for: {query}")
        try:
            # DDGS can be flaky, wrap in try/except specifically
            try:
                results = self.ddgs.text(query, max_results=max_results)
            except Exception as e:
                logger.error(f"DDGS Search failed: {e}")
                return []

            sources = []
            if results:
                for r in results:
                    sources.append(Source(
                        title=r.get('title', 'Unknown'),
                        url=r.get('href', '#'),
                        snippet=r.get('body', '')
                    ))
            
            if sources:
                try:
                    await self.vector_db.upsert_sources(sources, metadata={"query": query})
                    logger.info(f"Upserted {len(sources)} sources to Vector DB.")
                except Exception as e:
                    logger.error(f"Vector DB Upsert failed: {e}")
            
            return sources
        except Exception as e:
            logger.error(f"Ingestion process failed: {e}")
            return []
