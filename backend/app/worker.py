from celery import Celery
import os
import asyncio
from app.intelligence.application.engine import IntelligenceMirrorEngine

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
# REMOVED GLOBAL ENGINE to avoid race conditions and resource leaks in workers
# engine = IntelligenceMirrorEngine()

def publish_event(task_id, event, message):
    from app.cache import r as redis_client
    import json
    channel = f"task_events:{task_id}"
    redis_client.publish(channel, json.dumps({"event": event, "message": message, "timestamp": os.getenv("CURRENT_TIME", "")}))

@celery_app.task(name="run_forecast", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_forecast_task(self, question: str, model: str = "lfm-thinking"):
    """
    Wrapper to run async engine logic in a synchronous Celery worker.
    """
    task_id = self.request.id
    
    async def _run_logic():
        # Instantiate engine per task for isolation
        # This ensures fresh httpx client and event loop compatibility
        local_engine = IntelligenceMirrorEngine()
        
        async def status_cb(msg):
            publish_event(task_id, "status", msg)
            
        try:
            result = await local_engine.run_analysis(question, model, status_callback=status_cb)
            publish_event(task_id, "complete", "Analysis finished.")
            return result.dict()
        except Exception as e:
            publish_event(task_id, "failed", str(e))
            return {"error": str(e)}
        finally:
            await local_engine.close()

    try:
        # Check if an event loop is already running (e.g. if worker is async or tests)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we cannot use asyncio.run() directly in this thread.
            # We must run it in a separate thread.
            from concurrent.futures import ThreadPoolExecutor
            def run_in_thread():
                return asyncio.run(_run_logic())
                
            with ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(run_in_thread).result()
    except RuntimeError:
        # No loop running in this thread
        pass

    # If no loop is running, use asyncio.run
    return asyncio.run(_run_logic())
