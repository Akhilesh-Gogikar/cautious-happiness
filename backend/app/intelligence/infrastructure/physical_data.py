from __future__ import annotations

import math
import time
from abc import ABC, abstractmethod
from typing import List

from app.models import Source


class PhysicalDataInterface(ABC):
    """Abstract interface for retrieving physical commodity data."""

    @abstractmethod
    async def search_physical_data(self, question: str) -> List[Source]:
        raise NotImplementedError


class MockPhysicalDataProvider(PhysicalDataInterface):
    """Provides realistic mock data for physical commodities."""

    async def search_physical_data(self, question: str) -> List[Source]:
        q_lower = question.lower()
        sources: list[Source] = []
        current_time = time.time()

        if "oil" in q_lower or "crude" in q_lower or "brent" in q_lower:
            cushing_util = 62.0 + math.sin(current_time / 3600.0) * 5.0
            drawdown = -1.2 + math.cos(current_time / 1800.0) * 0.5
            trend = "Drawdown accelerating" if drawdown < 0 else "Building up"

            clean_util = 88.0 + math.sin(current_time / 7200.0) * 4.0
            float_storage = 85.0 + math.cos(current_time / 86400.0) * 10.0

            sources.extend([
                Source(
                    title="Orbital Insight - Cushing Storage Levels",
                    url="internal://satellite/cushing_terminals",
                    snippet=f"Floating roof analysis indicates {cushing_util:.1f}% capacity utilization at Cushing. 48h change: {drawdown:.1f}M barrels. Trend: {trend}.",
                ),
                Source(
                    title="Vortexa - Global Floating Storage",
                    url="internal://shipping/global_float",
                    snippet=f"Global clean tanker utilization at {clean_util:.1f}%. Dirty tanker rates (VLCC) showing divergence on China routes. Total floating storage: {float_storage:.1f}M bbls.",
                ),
            ])
        elif "gas" in q_lower or "lng" in q_lower:
            leaks = 3.0 + math.sin(current_time / 1800.0) * 2.0
            eu_storage = 92.0 + math.cos(current_time / 86400.0) * 5.0

            sources.extend([
                Source(
                    title="Copernicus Sentinel-5P Methane",
                    url="internal://satellite/methane_leaks",
                    snippet=f"High resolution scan of Permian basin shows {leaks:.1f}% increase in venting events. Supply side constraints likely underreported.",
                ),
                Source(
                    title="GIE AGSI+ Storage Data",
                    url="https://agsi.gie.eu/",
                    snippet=f"EU Storage levels at {eu_storage:.1f}% capacity. Injection rates slowing down due to maintenance at Norwegian terminals.",
                ),
            ])
        elif "copper" in q_lower or "metal" in q_lower:
            smelter = 85.0 + (math.sin(current_time / 3600.0) * 10.0)
            warrants = 4500 + int(math.cos(current_time / 7200.0) * 500)
            cancelled = 22.0 + math.sin(current_time / 3600.0) * 4.0

            sources.extend([
                Source(
                    title="Satellite - Escondida Mine Activity",
                    url="internal://satellite/chile_mining",
                    snippet=f"Thermal analysis of smelter stacks indicates {smelter:.1f}% operating capacity, down from 95% last week. Potential undeclared maintenance.",
                ),
                Source(
                    title="LME Warehouse Inventory (Live)",
                    url="internal://lme/warehouse",
                    snippet=f"On-warrant stocks in Rotterdam down {warrants} tonnes. Cancelled warrants rising ({cancelled:.1f}%).",
                ),
            ])
        elif "crop" in q_lower or "sovbean" in q_lower or "corn" in q_lower:
            ndvi = 15.0 + math.sin(current_time / 86400.0) * 5.0
            sources.append(
                Source(
                    title="NDVI Crop Health - Brazil Mato Grosso",
                    url="internal://satellite/ndvi_brazil",
                    snippet=f"Vegetation index {ndvi:.1f}% below 5-year average in Southern Mato Grosso. Soil moisture critical. Early harvest yields likely impacted.",
                )
            )

        if not sources:
            gscpi = 0.5 + math.sin(current_time / 86400.0) * 0.3
            sources.append(
                Source(
                    title="Global Supply Chain Pressure Index",
                    url="internal://fed/gscpi",
                    snippet=f"Index is at {gscpi:+.2f} standard deviations. Shipping costs normalizing but container throughput in LA/LB port remains congested.",
                )
            )

        return sources
