import asyncio
import httpx
import time

async def test_llm():
    print("Testing LLM...")
    start = time.time()
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                "http://localhost:8080/completion",
                json={
                    "prompt": "What is the meaning of life?",
                    "n_predict": 50,
                    "stream": False
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    print(f"Time: {time.time() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_llm())
