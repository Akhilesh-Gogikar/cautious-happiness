import os
import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastembed import TextEmbedding
from app.models import Source

class VectorDBClient:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.collection_name = "market_news"
        self.model = TextEmbedding() # Default model: BAAI/bge-small-en-v1.5
        
        try:
            self._ensure_vector_extension()
            self._ensure_table()
        except Exception as e:
            print(f"Warning: Could not initialize PGVector: {e}")

    def _ensure_vector_extension(self):
        with self.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()

    def _ensure_table(self):
        with self.engine.connect() as conn:
            # Create table with vector column (size 384 for bge-small-en-v1.5)
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.collection_name} (
                    id BIGINT PRIMARY KEY,
                    title TEXT,
                    url TEXT,
                    snippet TEXT,
                    metadata JSONB,
                    embedding vector(384)
                )
            """))
            # Create HNSW index for speed optimization
            conn.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {self.collection_name}_embedding_idx 
                ON {self.collection_name} USING hnsw (embedding vector_cosine_ops)
            """))
            conn.commit()

    async def upsert_sources(self, sources: List[Source], metadata: Optional[Dict[str, Any]] = None):
        """
        Convert sources to embeddings and upsert to Postgres.
        """
        if not sources:
            return

        try:
            texts = [f"{s.title}: {s.snippet}" for s in sources]
            embeddings = list(self.model.embed(texts))
            
            with self.engine.connect() as conn:
                for source, vector in zip(sources, embeddings):
                    point_id = hash(source.url + source.title) % (10**18)
                    payload = metadata or {}
                    
                    conn.execute(
                        text(f"""
                            INSERT INTO {self.collection_name} (id, title, url, snippet, metadata, embedding)
                            VALUES (:id, :title, :url, :snippet, :metadata, :embedding)
                            ON CONFLICT (id) DO UPDATE SET
                                title = EXCLUDED.title,
                                url = EXCLUDED.url,
                                snippet = EXCLUDED.snippet,
                                metadata = EXCLUDED.metadata,
                                embedding = EXCLUDED.embedding
                        """),
                        {
                            "id": point_id,
                            "title": source.title,
                            "url": source.url,
                            "snippet": source.snippet,
                            "metadata": str(payload).replace("'", '"'), # Simple JSON conversion
                            "embedding": vector.tolist()
                        }
                    )
                conn.commit()
        except Exception as e:
            print(f"VectorDB Upsert Failed: {e}")

    async def search(self, query: str, limit: int = 5) -> List[Source]:
        """
        Search for relevant sources using cosine similarity.
        """
        try:
            query_vector = list(self.model.embed([query]))[0]
            
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"""
                        SELECT title, url, snippet 
                        FROM {self.collection_name}
                        ORDER BY embedding <=> :query_vector
                        LIMIT :limit
                    """),
                    {
                        "query_vector": query_vector.tolist(),
                        "limit": limit
                    }
                )
                
                sources = []
                for row in result:
                    sources.append(Source(
                        title=row.title,
                        url=row.url,
                        snippet=row.snippet
                    ))
                return sources
        except Exception as e:
            print(f"VectorDB Search Failed: {e}")
            return []
