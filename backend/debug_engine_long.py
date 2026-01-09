import asyncio
import time
import os
import httpx
from app.models import ChatRequest

# Set env for mock
os.environ["USE_MOCK_REDIS"] = "1"
os.environ["OLLAMA_HOST"] = "http://localhost:11434"

async def test_chat():
    # Manual implementation to override engine timeout
    request = ChatRequest(
        question="Test",
        context="Testing context",
        user_message="Hello, are you there?",
        model="llama1B3.2:latest" 
    )
    
    prompt = f"""
    [INST] You are an intelligent market analyst.
    
    Context of the conversation (previous forecast):
    {request.context}
    
    User Question: {request.user_message}
    
    Answer the user's question based on the context provided. Be concise and professional.
    [/INST]
    """
    
    print("Sending request to Ollama (Model: llama1B3.2:latest, Timeout: 300s)...")
    start = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": request.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300.0 # 5 minutes
            )
            end = time.time()
            if response.status_code == 200:
                print(f"Response: {response.json().get('response', '')[:50]}...")
            else:
                print(f"Error Code: {response.status_code}")
                print(f"Error Body: {response.text}")
            
            print(f"Time taken: {end - start:.2f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
