import asyncio
import os
from app.engine import ForecasterCriticEngine
from app.models import Source

async def verify_rag():
    print("Starting RAG Verification...")
    
    # Initialize Engine
    engine = ForecasterCriticEngine()
    
    # Test Question
    question = "What is the latest status of the Artemis II mission?"
    
    print(f"\n1. Running analysis for: {question}")
    result = await engine.run_analysis(question)
    
    print(f"\nResult Probability: {result.adjusted_forecast}")
    print(f"Sources used ({len(result.news_summary)}):")
    for s in result.news_summary:
        print(f"- {s.title} ({s.url})")
    
    print("\n2. Checking Vector DB directly for stored snippets...")
    retrieved = await engine.vector_db.search("Artemis crew", limit=3)
    print(f"Retrieved from Vector DB ({len(retrieved)}):")
    for s in retrieved:
        print(f"- {s.title}: {s.snippet[:100]}...")

    if len(retrieved) > 0:
        print("\nSUCCESS: RAG Pipeline is working (Ingestion -> Search -> Retrieval confirmed).")
    else:
        print("\nFAILURE: No snippets retrieved from Vector DB.")

if __name__ == "__main__":
    # We need to mock environment variables if running locally without docker
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    try:
        asyncio.run(verify_rag())
    except Exception as e:
        print(f"Verification Script Error: {e}")
