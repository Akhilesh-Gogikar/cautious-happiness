import os
import httpx
from redis import Redis
from app.cache import r as redis_client

async def check_ollama(host: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(host)
            return resp.status_code == 200
    except:
        return False

def check_redis() -> bool:
    try:
        return redis_client.ping()
    except:
        return False

async def get_system_health():
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    
    return {
        "ollama": await check_ollama(ollama_host),
        "redis": check_redis(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }
