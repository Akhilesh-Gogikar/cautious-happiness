import sys
import os
import asyncio
import logging
import datetime
import pytest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database_users import SessionLocal, engine, BaseUsers
from app.models_db import AlgoOrder, User
from app.execution import AlgoOrderManager
from app.market_client import MockMarketClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_db():
    # Create tables if they don't exist
    BaseUsers.metadata.create_all(bind=engine)
    db = SessionLocal()
    return db

def teardown_db(db):
    db.close()

@pytest.mark.asyncio
async def test_twap_execution():
    logger.info("--- Testing TWAP Execution ---")
    db = setup_db()
    
    # Create a dummy user if not exists
    user = db.query(User).filter(User.email == "test_algo@example.com").first()
    if not user:
        user = User(email="test_algo@example.com", hashed_password="pw")
        db.add(user)
        db.commit()
    
    # Create a TWAP order
    # $1000 total, 10 minutes -> $100 per chunk
    order = AlgoOrder(
        user_id=user.id,
        market_id="0xTEST_MARKET",
        type="TWAP",
        total_size_usd=1000.0,
        remaining_size_usd=1000.0,
        duration_minutes=10,
        status="ACTIVE"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    logger.info(f"Created TWAP Order ID: {order.id}")

    # Initialize Manager with Mock Client
    client = MockMarketClient()
    manager = AlgoOrderManager(client)

    # Execute Step 1
    logger.info("Executing Step 1...")
    await manager.execute_step(order.id, db)
    
    # Refetch
    db.refresh(order)
    logger.info(f"After Step 1: Remaining = ${order.remaining_size_usd}")
    
    assert order.remaining_size_usd < 1000.0, "Should have executed some amount"
    assert order.last_executed_at is not None, "Should have timestamp"

    # Execute Step 2 (Should be blocked if too soon, effectively < 55s)
    logger.info("Executing Step 2 (Immediate - should skip)...")
    prev_remaining = order.remaining_size_usd
    await manager.execute_step(order.id, db)
    db.refresh(order)
    assert order.remaining_size_usd == prev_remaining, "Should not execute again immediately"

    # Simulate Time Passing (manually update last_executed_at)
    logger.info("Simulating time passing (1 min)...")
    order.last_executed_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=1, seconds=1)
    db.commit()

    logger.info("Executing Step 3...")
    await manager.execute_step(order.id, db)
    db.refresh(order)
    logger.info(f"After Step 3: Remaining = ${order.remaining_size_usd}")
    
    assert order.remaining_size_usd < prev_remaining, "Should have executed next chunk"

    # Cleanup
    db.delete(order)
    db.commit()
    logger.info("--- TWAP Test Passed ---")

@pytest.mark.asyncio
async def test_iceberg_execution():
    logger.info("--- Testing Iceberg Execution ---")
    db = setup_db()
    
    # Reuse user
    user = db.query(User).filter(User.email == "test_algo@example.com").first()

    # Create Iceberg
    # Total $500, Display $50
    order = AlgoOrder(
        user_id=user.id,
        market_id="0xTEST_ICEBERG",
        type="ICEBERG",
        total_size_usd=500.0,
        remaining_size_usd=500.0,
        display_size_usd=50.0,
        status="ACTIVE"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    client = MockMarketClient()
    manager = AlgoOrderManager(client)

    logger.info("Executing Iceberg Step 1...")
    await manager.execute_step(order.id, db)
    db.refresh(order)
    logger.info(f"Remaining: ${order.remaining_size_usd}")
    
    assert order.remaining_size_usd == 450.0, "Should have executed exactly display size ($50)"

    db.delete(order)
    db.commit()
    logger.info("--- Iceberg Test Passed ---")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_twap_execution())
    loop.run_until_complete(test_iceberg_execution())
