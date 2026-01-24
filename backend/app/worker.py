from celery import Celery
import os
import asyncio
from app.engine import ForecasterCriticEngine

# Initialize Celery
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
engine = ForecasterCriticEngine()

@celery_app.task(name="run_forecast", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def run_forecast_task(self, question: str, model: str = "qwen2.5"):
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
        print(f"Worker Error: {e}")
        return {"error": str(e)}

@celery_app.task(name="process_algo_orders")
def process_algo_orders_task():
    """
    Periodic task to process all active algo orders.
    """
    from app.database_users import SessionLocal
    from app.models_db import AlgoOrder
    from app.execution import AlgoOrderManager
    from app.market_client import MockMarketClient, RealMarketClient
    import os

    db = SessionLocal()
    try:
        # 1. Setup Market Client
        api_key = os.getenv("POLYMARKET_API_KEY")
        if api_key:
            market_client = RealMarketClient(
                api_key, 
                os.getenv("POLYMARKET_SECRET", ""), 
                os.getenv("POLYMARKET_PASSPHRASE", "")
            )
        else:
            market_client = MockMarketClient()

        manager = AlgoOrderManager(market_client)

        # 2. Find all active orders
        active_orders = db.query(AlgoOrder).filter(AlgoOrder.status == "ACTIVE").all()
        
        # 3. Process each
        # In a real app, we might want to run these in parallel or use subtasks
        for order in active_orders:
            # We need a new event loop or run sync
            # Since market_client place_order is currently sync in mock/real, 
            # and AlgoOrderManager methods are async, we use the loop trick.
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(manager.execute_step(order.id, db))
            
    finally:
        db.close()

# To enable periodic execution, we'd normally add to beat_schedule
# For this demo, we'll assume it's triggered or we'll trigger it once to show it works.
celery_app.conf.beat_schedule = {
    'process-algo-orders-every-minute': {
        'task': 'process_algo_orders',
        'schedule': 60.0,
    },
    'sync-markets-every-5-minutes': {
        'task': 'sync_and_classify_markets',
        'schedule': 300.0,
    },
}

@celery_app.task(name="sync_and_classify_markets")
def sync_and_classify_markets():
    """
    Fetch new markets and classify them.
    """
    from app.database_users import SessionLocal
    from app.models_db import EventRegistry
    from py_clob_client.client import ClobClient
    import os

    db = SessionLocal()
    try:
        # 1. Fetch Active Markets
        # Public Read-Only is fine for fetching markets if no keys
        client = ClobClient("https://clob.polymarket.com", chain_id=137) 
        
        # simplified fetch
        resp = client.get_markets(next_cursor="")
        markets = resp.get('data', [])[:50] # Increased limit for better coverage

        # 2. Loop and Classify
        for m in markets:
            m_id = m.get('condition_id')
            question = m.get('question')
            
            if not m_id or not question:
                continue

            # Check DB
            existing = db.query(EventRegistry).filter(EventRegistry.market_id == m_id).first()
            if not existing:
                # Classify using the global engine instance
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Reuse loop if running? No, worker is sync.
                if loop.is_running():
                     # This shouldn't happen in standard celery worker unless using certain pools
                     # Fallback to creating a new loop in a thread if strictly needed, 
                     # but here standard helper usually works.
                     pass 

                category = loop.run_until_complete(engine.classify_market(question))
                
                new_event = EventRegistry(
                    market_id=m_id,
                    question=question,
                    category=category
                )
                db.add(new_event)
                db.commit()
                print(f"Synced & Classified: {question} -> {category}")

    except Exception as e:
        print(f"Sync logic failed: {e}")
    finally:
        db.close()

@celery_app.task(name="autonomous_explorer")
def autonomous_explorer():
    """
    Background loop that:
    1. Finds a market that hasn't been updated recently.
    2. Runs the full analysis pipeline (Calibrated Probability).
    3. (Optionally) Executes trades via the Engine's enabled execution logic.
    """
    from app.database_users import SessionLocal
    from app.models_db import EventRegistry
    from sqlalchemy import func
    import datetime

    db = SessionLocal()
    try:
        import time
        
        # Process up to 3 markets per task execution to ensure continuous-like operation
        for _ in range(3):
            # Find oldest updated market
            market = db.query(EventRegistry).order_by(EventRegistry.last_updated.asc()).with_for_update(skip_locked=True).first()
            
            if not market:
                print("Explorer: No markets found in registry.")
                break

            print(f"Explorer: Analyzing '{market.question}' (Last updated: {market.last_updated})")
            
            # Determine model to use
            model = os.getenv("MODEL_NAME", "openforecaster")
            
            # Since worker is sync, we use the async-to-sync trick
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run Analysis
            result = loop.run_until_complete(engine.run_analysis(market.question, model=model))
            
            # Update timestamp
            market.last_updated = datetime.datetime.utcnow()
            db.commit()
            
            print(f"Explorer: Analysis Complete. Reasoning snippet: {result.reasoning[:100]}...")
            
            # Small pause to be nice to CPUs
            time.sleep(1)

    except Exception as e:
        print(f"Explorer Failed: {e}")
    finally:
        db.close()

@celery_app.task(name="fetch_rss_feeds")
def fetch_rss_feeds():
    """
    Task to fetch and filter RSS feeds for proposed trades.
    """
    from app.services.rss_service import RssService
    import asyncio
    
    service = RssService()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(service.fetch_and_filter_feeds())

# Update Schedule
celery_app.conf.beat_schedule = {
    'process-algo-orders-every-minute': {
        'task': 'process_algo_orders',
        'schedule': 60.0,
    },
    'sync-markets-every-5-minutes': {
        'task': 'sync_and_classify_markets',
        'schedule': 120.0,
    },
    'autonomous-explorer-every-30-seconds': {
        'task': 'autonomous_explorer',
        'schedule': 15.0,
    },
    'fetch-rss-every-minute': {
        'task': 'fetch_rss_feeds',
        'schedule': 60.0,
    },
}
