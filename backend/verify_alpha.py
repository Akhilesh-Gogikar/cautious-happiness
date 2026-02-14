import asyncio
import os
from app.engine import IntelligenceMirrorEngine

async def verify_engine():
    print("--- Alpha Insights: Manual Verification ---")
    engine = IntelligenceMirrorEngine()
    
    question = "Brent Crude Oil Physical Supply Divergence"
    print(f"Testing Question: {question}")
    
    # Mocking sources to avoid external dependency for local check
    from app.models import Source
    sources = [
        Source(title="Brent Physical Premium Rises", url="http://example.com/1", snippet="Market observers note a rising premium for physical Brent over paper contracts due to North Sea maintenance."),
        Source(title="Algo Trading Spikes in Energy", url="http://example.com/2", snippet="High-frequency algorithms are driving volatility in crude futures following geopolitical noise.")
    ]
    
    print("\n1. Generating Intelligence Mirror...")
    # Note: This still hits Ollama if not caught. We expect it might fail if Ollama is not running, 
    # but we want to see the prompt construction and parsing logic flow.
    try:
        mirror_score, reasoning = await engine.generate_forecast_with_reasoning(question, sources)
        print(f"Mirror Confidence Score: {mirror_score}")
        print(f"Reasoning snippet: {reasoning[:200]}...")
    except Exception as e:
        print(f"Mirror Generation Failed (Expected if Ollama offline): {e}")

    print("\n2. Auditing Intelligence (Critic)...")
    try:
        critique, adj_score = await engine.critique_forecast(question, sources, 0.75, "High algo noise detected.")
        print(f"Audit Critique: {critique}")
        print(f"Adjusted Mirror Score: {adj_score}")
    except Exception as e:
        print(f"Audit Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_engine())
