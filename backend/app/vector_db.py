import os
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from fastembed import TextEmbedding
from app.models import Source

class VectorDBClient:
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", 6333))
        self.client = QdrantClient(host=self.host, port=self.port)
        self.collection_name = "market_news"
        self.model = TextEmbedding() # Default model: BAAI/bge-small-en-v1.5
        
        try:
            self._ensure_collection()
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant on init: {e}")

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            # We need to know the embedding dimension. BGE-small is 384.
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=384,
                    distance=rest.Distance.COSINE
                )
            )

    async def upsert_sources(self, sources: List[Source], metadata: Optional[Dict[str, Any]] = None):
        """
        Convert sources to embeddings and upsert to Qdrant.
        """
        if not sources:
            return

        texts = [f"{s.title}: {s.snippet}" for s in sources]
        embeddings = list(self.model.embed(texts))
        
        points = []
        for i, (source, vector) in enumerate(zip(sources, embeddings)):
            payload = {
                "title": source.title,
                "url": source.url,
                "snippet": source.snippet
            }
            if metadata:
                payload.update(metadata)
                
            points.append(rest.PointStruct(
                id=hash(source.url + source.title) % (10**18), # Simple unique ID if none provided
                vector=vector.tolist(),
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query: str, limit: int = 5) -> List[Source]:
        """
        Search for relevant sources.
        """
        query_vector = list(self.model.embed([query]))[0]
        
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit
        )
        
        results = []
        for hit in hits:
            results.append(Source(
                title=hit.payload.get("title", ""),
                url=hit.payload.get("url", ""),
                snippet=hit.payload.get("snippet", "")
            ))
        return results
