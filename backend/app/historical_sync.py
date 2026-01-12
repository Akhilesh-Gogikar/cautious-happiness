import os
import requests
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database_users import SessionLocal
from app.models_db import HistoricalMarket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("historical_sync")

POLYMARKET_GAMMA_API = "https://gamma-api.polymarket.com/events"

def fetch_settled_markets(limit=50):
    """
    Fetches settled markets from AlphaSignals Gamma API.
    """
    params = {
        "closed": "true",
        "limit": limit,
        "offset": 0
    }
    try:
        response = requests.get(POLYMARKET_GAMMA_API, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching settled markets from AlphaSignals: {e}")
        return []

def sync_historical_markets(limit=50):
    db: Session = SessionLocal()
    try:
        markets = fetch_settled_markets(limit)
        logger.info(f"Fetched {len(markets)} settled markets.")
        
        sync_count = 0
        for m in markets:
            # AlphaSignals 'events' may contain multiple 'markets'
            # For simplicity, we assume an event is a market or has a primary market
            market_id = str(m.get('id'))
            
            # Check if already exists
            existing = db.query(HistoricalMarket).filter(HistoricalMarket.market_id == market_id).first()
            if existing:
                continue
                
            # Basic parsing of outcome and close time
            # Note: Gamma API structure might vary, this is a best-effort based on common patterns
            close_time_str = m.get('closed_time') or m.get('end_date')
            close_time = None
            if close_time_str:
                try:
                    # Try common ISO formats
                    close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
                except ValueError:
                    logger.warning(f"Could not parse date: {close_time_str}")

            # Heuristic for outcome: often in 'mutually_exclusive' or 'tokens'
            # Here we just store the raw metadata and a placeholder outcome
            # Proper resolution data might require fetching the specific market token status
            outcome = "Resolved" # Placeholder
            
            new_market = HistoricalMarket(
                market_id=market_id,
                question=m.get('title') or m.get('question'),
                outcome=outcome,
                close_time=close_time,
                category=m.get('category', 'General'),
                volume=float(m.get('volume', 0) or 0),
                metadata_json=m
            )
            db.add(new_market)
            sync_count += 1
            
        db.commit()
        logger.info(f"Successfully synced {sync_count} new historical markets.")
        return sync_count
    except Exception as e:
        logger.error(f"Error syncing historical markets: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    sync_historical_markets(limit=100)
