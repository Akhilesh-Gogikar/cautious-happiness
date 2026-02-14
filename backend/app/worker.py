from celery import Celery
import os
import asyncio
from app.engine import IntelligenceMirrorEngine

# Initialize Celery
# ... (rest of imports/init)
# Initialize Celery
# Note: In production we would use a more robust broker/backend setup
if os.getenv("CELERY_ALWAYS_EAGER"):
    celery_app = Celery(__name__, broker='memory://', backend='cache+memory://')
    celery_app.conf.task_always_eager = True
else:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    celery_app = Celery(__name__, broker=redis_url, backend=redis_url)

# Instantiate engine once (global) - careful with concurrency if not thread safe
# For simple stateless logic it's fine
engine = IntelligenceMirrorEngine()

@celery_app.task(name="run_forecast", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_forecast_task(self, question: str, model: str = "lfm-thinking"):
    """
    Wrapper to run async engine logic in a synchronous Celery worker.
    """
    # Create new event loop for this thread if needed
    # Check if loop is running (Eager mode called from async context)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Run in a separate thread to avoid "This event loop is already running"
            from concurrent.futures import ThreadPoolExecutor
            def run_in_new_loop():
                 new_loop = asyncio.new_event_loop()
                 asyncio.set_event_loop(new_loop)
                 res = new_loop.run_until_complete(engine.run_analysis(question, model))
                 new_loop.close()
                 return res
            
            with ThreadPoolExecutor() as pool:
                result = pool.submit(run_in_new_loop).result()
            return result.dict()
    except RuntimeError:
        pass # No loop, create new one below

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        # Run the async analysis
        result = loop.run_until_complete(engine.run_analysis(question, model))
        return result.dict()
    except Exception as e:
        return {"error": str(e)}
