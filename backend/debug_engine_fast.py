import asyncio
import time
import os
from app.engine import ForecasterCriticEngine
from app.models import ChatRequest

# Set env for mock
os.environ["USE_MOCK_REDIS"] = "1"
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

async def test_chat():
    engine = ForecasterCriticEngine()
    req = ChatRequest(
        question="Test",
        context="Testing context",
        user_message="Hello, are you there?",
        model="llama1B3.2:latest" 
    )
    
    print("Sending request to engine (Model: llama1B3.2:latest)...")
    start = time.time()
    try:
        res = await engine.chat_with_model(req)
        end = time.time()
        print(f"Response: {res}")
        print(f"Time taken: {end - start:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
