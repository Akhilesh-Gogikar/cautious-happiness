
import asyncio
import random
import datetime
from typing import AsyncGenerator
from app.models import PnLSnapshot, PnLVelocityResponse

async def simulate_pnl_stream(market_id: str) -> AsyncGenerator[str, None]:
    """
    Simulates a real-time PnL stream for a given market.
    Yields JSON strings compatible with SSE or WebSocket text frames.
    """
    current_pnl = 0.0
    
    # Send initial history (last 60 seconds)
    # in a real scenario, we'd query the DB
    history = []
    now = datetime.datetime.utcnow()
    for i in range(60):
        t = now - datetime.timedelta(seconds=60-i)
        change = random.uniform(-5.0, 5.0)
        current_pnl += change
        history.append(PnLSnapshot(timestamp=t, pnl=current_pnl))
        
    initial_payload = PnLVelocityResponse(market_id=market_id, snapshots=history)
    yield initial_payload.json()
    
    # Stream live updates
    while True:
        await asyncio.sleep(1) # 1 update per second
        change = random.uniform(-10.0, 10.0) # Higher volatility
        current_pnl += change
        
        snapshot = PnLSnapshot(timestamp=datetime.datetime.utcnow(), pnl=current_pnl)
        payload = PnLVelocityResponse(market_id=market_id, snapshots=[snapshot])
        yield payload.json()
