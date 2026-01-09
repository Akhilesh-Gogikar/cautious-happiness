import os
import redis
import json
import functools
import asyncio
from typing import Callable, Any

# Initialize Redis
if os.getenv("USE_MOCK_REDIS"):
    try:
        from fakeredis import FakeRedis
        r = FakeRedis(decode_responses=True)
    except ImportError:
        print("fakeredis not found, using simple dict mock")
        class SimpleMockRedis:
            def __init__(self): self.store = {}
            def get(self, key): return self.store.get(key)
            def setex(self, key, time, value): self.store[key] = value
        r = SimpleMockRedis()
else:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    r = redis.from_url(redis_url)

def cache_response(ttl_seconds: int = 60):
    """
    Async decorator to cache FastAPI response in Redis.
    Key is generated from function name + args.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Simple key generation
            key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
            cache_key = ":".join(key_parts)
            
            # Check cache
            try:
                cached = r.get(cache_key)
                if cached:
                    # Return cached data
                    return json.loads(cached)
            except Exception as e:
                print(f"Redis Read Error: {e}")

            # Run function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                r.setex(cache_key, ttl_seconds, json.dumps(result))
            except Exception as e:
                print(f"Redis Write Error: {e}")
                
            return result
        return wrapper
    return decorator
