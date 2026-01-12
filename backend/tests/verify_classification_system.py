import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add backend path
sys.path.append("/root/cautious-happiness/backend")

# Mock VectorDBClient to avoid connection error during engine init
sys.modules["app.vector_db"] = MagicMock()
sys.modules["app.vector_db"].VectorDBClient = MagicMock

from app import models_db, database_users
from app.worker import sync_and_classify_markets, engine

# Init DB
models_db.BaseUsers.metadata.create_all(bind=database_users.engine)

def test_sync_and_classification():
    print("Starting Verification...")

    # Mock ClobClient
    mock_markets = [
        {"condition_id": "0x1", "question": "Will the Fed cut rates in March?", "active": True}, # Economics
        {"condition_id": "0x2", "question": "Who will win the 2024 Election?", "active": True}, # Politics
        {"condition_id": "0x3", "question": "Will SpaceX successfully launch Starship?", "active": True}, # Science
        {"condition_id": "0x4", "question": "Will Taylor Swift break up with Kelce?", "active": True} # Other
    ]
    
    with patch("py_clob_client.client.ClobClient") as MockClob:
        instance = MockClob.return_value
        instance.get_markets.return_value = {"data": mock_markets}
        
        # Mock Engine LLM to return categories based on question keywords
        # We need to patch the global 'engine' used in worker.py, specifically its classify_market OR _call_llm
        # But classify_market calls _call_llm.
        
        async def mock_classify(question):
            if "Fed" in question: return "Economics"
            if "Election" in question: return "Politics"
            if "SpaceX" in question: return "Science"
            return "Other"

        # Patch the engine instance method in app.worker
        with patch.object(engine, 'classify_market', side_effect=mock_classify):
            
            # Run the task
            print("Running sync_and_classify_markets task...")
            sync_and_classify_markets()

    # Check DB
    db = database_users.SessionLocal()
    try:
        events = db.query(models_db.EventRegistry).all()
        print(f"Found {len(events)} events in registry.")
        
        expected = {
            "0x1": "Economics",
            "0x2": "Politics",
            "0x3": "Science",
            "0x4": "Other"
        }
        
        passed = True
        for e in events:
            print(f"- {e.question} -> {e.category}")
            if expected.get(e.market_id) != e.category:
                print(f"ERROR: Expected {expected.get(e.market_id)} but got {e.category}")
                passed = False
                
        if passed and len(events) == 4:
            print("SUCCESS: All markets correctly classified and stored.")
        else:
            print("FAILURE: Verification failed.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_sync_and_classification()
