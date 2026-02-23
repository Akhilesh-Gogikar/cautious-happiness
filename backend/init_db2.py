import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Base

async def init_db():
    url = "postgresql+asyncpg://postgres:password@db:5432/polymarket"
    engine = create_async_engine(url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database fully initialized.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
