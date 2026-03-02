import asyncio
import argparse
from app.agents.orchestrator import AgentOrchestrator

async def run_scenario(scenario: str):
    print(f"--- Running Demo Pipeline Validation ---")
    print(f"Scenario: {scenario}\n")
    
    orchestrator = AgentOrchestrator()
    
    # 1. Ingest dummy RAG Data for context
    print("[1] Ingesting Mock News data into pgvector...")
    await orchestrator.news_agent.ingest_news(
        title="US imposes strict naval blockade on Strait of Hormuz",
        content="In response to escalating conflicts in Iran, the US Navy has deployed carrier strike groups "
                "to effectively blockade the Strait of Hormuz. Global oil shipments are severely delayed. "
                "European energy markets are panicking, while defense contractors see record highs.",
        category="geopolitics"
    )
    
    # 2. Run the pipeline
    print("\n[2] Executing Demo Pipeline Orchestrator...")
    result = await orchestrator.run_demo_pipeline(scenario)
    
    print("\n[3] Pipeline Result:")
    import json
    print(json.dumps(result, indent=2))
    
    assert result["status"] == "success", "Expected success status"
    assert "trade_recommendations" in result, "Expected trade recommendations"
    
    recs = result["trade_recommendations"]
    print("\nValidation Complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Demo Pipeline Agentic flow")
    parser.add_argument("--scenario", type=str, default="War in Iran ongoing and Strait of Hormuz completely blocked", help="Target scenario to analyze")
    args = parser.add_argument()
    
    asyncio.run(run_scenario(args.scenario))
