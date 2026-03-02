import os
import httpx
from redis import Redis
from app.cache import r as redis_client

from app.db.session import engine
from sqlalchemy import text

async def check_ollama(host: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{host}/health")
            return resp.status_code == 200
    except:
        return False

def check_redis() -> bool:
    try:
        return redis_client.ping()
    except:
        return False

async def check_db() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except:
        return False

async def get_system_health():
    ollama_host = os.getenv("LLAMA_CPP_HOST", "http://text-gen-cpp:8080")
    
    return {
        "ollama": await check_ollama(ollama_host),
        "redis": check_redis(),
        "database": await check_db(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }
