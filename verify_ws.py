import asyncio
import websockets
import json

async def test_pnl_ws():
    uri = "ws://localhost:8000/ws/pnl/test-market"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            for _ in range(3):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received data: {data}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_pnl_ws())
