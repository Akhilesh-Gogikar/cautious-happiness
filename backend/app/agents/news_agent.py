import json
import logging
from sqlalchemy.future import select
from sentence_transformers import SentenceTransformer
from app.db.models import NewsDocument
from app.db.session import async_session

logger = logging.getLogger("news_agent")

class NewsAgent:
    def __init__(self):
        # Using a fast local embedding model for the RAG architecture.
        # This matches the Vector(1024) dimension if we use 'mixedbread-ai/mxbai-embed-large-v1' or similar, 
        # but for demo simplicity, we'll map vectors properly or use all-MiniLM-L6-v2 and pad/project, 
        # However BAAI/bge-m3 produces 1024d embeddings.
        try:
            self.embedder = SentenceTransformer("BAAI/bge-m3")
        except Exception as e:
            logger.warning(f"Failed to load local embedder BAAI/bge-m3. Using mock embedder: {e}")
            self.embedder = None

    def _get_embedding(self, text: str) -> list[float]:
        """Generate a 1024-dimensional embedding for the given text."""
        if self.embedder:
            # Generate actual embedding
            # BAAI/bge-m3 generates 1024d vectors
            vec = self.embedder.encode(text).tolist()
            if len(vec) != 1024:
                # Fallback zero-padding if a different model was loaded
                vec = (vec + [0.0] * 1024)[:1024]
            return vec
        else:
            # Returns a mock 1024d vector
            return [0.01] * 1024

    async def ingest_news(self, title: str, content: str, category: str = "general"):
        """Ingest a news document, chunk it, embed it, and store in pgvector."""
        embedding = self._get_embedding(f"{title} {content}")
        
        async with async_session() as session:
            doc = NewsDocument(
                title=title,
                content=content,
                category=category,
                embedding=embedding
            )
            session.add(doc)
            await session.commit()
            logger.info(f"Ingested news: {title}")

    async def retrieve_context(self, query: str, limit: int = 5) -> str:
        """Retrieve relevant context for a given query using pgvector semantic search."""
        query_embedding = self._get_embedding(query)
        
        async with async_session() as session:
            # pgvector distance operator <=> (Cosine distance)
            # Find the closest documents by cosine distance
            stmt = select(NewsDocument).order_by(
                NewsDocument.embedding.cosine_distance(query_embedding)
            ).limit(limit)
            
            result = await session.execute(stmt)
            docs = result.scalars().all()
            
            context_pieces = []
            for d in docs:
                context_pieces.append(f"[{d.published_at.strftime('%Y-%m-%d')}] {d.title}: {d.content}")
                
            return "\n\n".join(context_pieces)
