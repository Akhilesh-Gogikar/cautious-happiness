import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Base
from app.db.session import SQLALCHEMY_DATABASE_URL

async def init_models():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Database tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_models())
