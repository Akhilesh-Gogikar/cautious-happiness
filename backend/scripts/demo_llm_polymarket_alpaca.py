"""Demo runner: LLM + Polymarket signal discovery + Alpaca order plan generation.

Usage:
  python backend/scripts/demo_llm_polymarket_alpaca.py --scenario "Middle East supply shock"

Notes:
- Default mode is dry-run (recommended).
- This script builds candidate orders from LLM output and optionally submits to Alpaca paper trading.
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

async def build_orders_from_recommendations(recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    timeframe_to_symbol = {
        "week": "USO",
        "month": "XLE",
        "quarter": "GLD",
        "half_year": "TLT",
        "year": "ITA",
    }

    orders = []
    for timeframe, ideas in recommendations.get("timeframes", {}).items():
        if not ideas:
            continue

        idea = ideas[0]
        side = "buy"
        trade_text = str(idea.get("trade", "")).lower()
        if "short" in trade_text or "sell" in trade_text:
            side = "sell"

        orders.append(
            {
                "timeframe": timeframe,
                "symbol": timeframe_to_symbol.get(timeframe, "SPY"),
                "qty": 1,
                "side": side,
                "reasoning": idea.get("reasoning", ""),
            }
        )

    return orders


async def run_demo(scenario: str, execute: bool):
    from app.agents.orchestrator import AgentOrchestrator
    from app.connectors.alpaca import AlpacaConnector

    orchestrator = AgentOrchestrator()
    demo_result = await orchestrator.run_demo_pipeline(scenario)

    recommendations = demo_result.get("trade_recommendations", {})
    orders = await build_orders_from_recommendations(recommendations)

    print("=== Scenario Analysis ===")
    print(recommendations.get("scenario_analysis", "No analysis returned."))
    print("\n=== Proposed Orders ===")
    print(json.dumps(orders, indent=2))

    if not execute:
        print("\nDry run only. No Alpaca orders submitted.")
        return

    connector = AlpacaConnector()
    await connector.connect()
    if not connector.client:
        raise RuntimeError("Alpaca connector inactive. Set ALPACA_API_KEY / ALPACA_SECRET_KEY.")

    print("\nSubmitting orders to Alpaca...")
    for order in orders:
        result = await connector.call_tool(
            "place_market_order",
            {"symbol": order["symbol"], "qty": order["qty"], "side": order["side"]},
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True, help="Scenario for demo analysis")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually place orders on Alpaca (paper trading recommended)",
    )
    args = parser.parse_args()

    asyncio.run(run_demo(args.scenario, args.execute))
