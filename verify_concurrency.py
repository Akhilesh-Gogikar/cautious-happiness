import asyncio
import httpx
import time

async def call_model(i):
    start = time.time()
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "http://localhost:8081/completion",
                json={
                    "prompt": "Explain the concept of market liquidity in one sentence.",
                    "n_predict": 50,
                    "stream": False
                }
            )
            end = time.time()
            if response.status_code == 200:
                print(f"Request {i} finished successfully in {end - start:.2f}s")
            else:
                print(f"Request {i} failed with status {response.status_code} in {end - start:.2f}s")
            return response.status_code
        except Exception as e:
            end = time.time()
            print(f"Request {i} exception: {e} after {end - start:.2f}s")
            return str(e)

async def main():
    print("Starting concurrent requests to openforecaster-cpp (Parallel=2)...")
    start_total = time.time()
    # Test with 2 concurrent requests first
    results = await asyncio.gather(*[call_model(i) for i in range(2)])
    end_total = time.time()
    print(f"Total time for 2 concurrent requests: {end_total - start_total:.2f}s")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
