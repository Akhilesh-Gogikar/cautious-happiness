from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.models import Source
import random

class PhysicalDataInterface(ABC):
    """
    Abstract interface for retrieving physical commodity data.
    Implementations could be: Mock, SatelliteAPI, ShippingAPI, etc.
    """
    @abstractmethod
    async def search_physical_data(self, question: str) -> List[Source]:
        pass

class MockPhysicalDataProvider(PhysicalDataInterface):
    """
    Provides realistic mock data for physical commodities to simulate
    high-value institutional intelligence feeds.
    """
    async def search_physical_data(self, question: str) -> List[Source]:
        q_lower = question.lower()
        sources = []
        
        # Simulate latency
        # await asyncio.sleep(0.5) 

        if "oil" in q_lower or "crude" in q_lower or "brent" in q_lower:
            sources.extend([
                Source(
                    title="Orbital Insight - Cushing Storage Levels",
                    url="internal://satellite/cushing_terminals",
                    snippet=f"Floating roof analysis indicates 62% capacity utilization at Cushing. 48h change: -1.2M barrels. Trend: Drawdown accelerating."
                ),
                Source(
                    title="Vortexa - Global Floating Storage",
                    url="internal://shipping/global_float",
                    snippet="Global clean tanker utilization at 88%. Dirty tanker rates (VLCC) showing divergence on China routes. Total floating storage: 85M bbls (Low)."
                )
            ])
            
        elif "gas" in q_lower or "lng" in q_lower:
             sources.extend([
                Source(
                    title="Copernicus Sentinel-5P Methane",
                    url="internal://satellite/methane_leaks",
                    snippet="High resolution scan of Permian basin shows 3% increase in venting events. Supply side constraints likely underreported."
                ),
                Source(
                    title="GIE AGSI+ Storage Data",
                    url="https://agsi.gie.eu/",
                    snippet="EU Storage levels at 92% capacity. Injection rates slowing down due to maintenance at Norwegian terminals."
                )
            ])
             
        elif "copper" in q_lower or "metal" in q_lower:
             sources.extend([
                Source(
                    title="Satellite - Escondida Mine Activity",
                    url="internal://satellite/chile_mining",
                    snippet="Thermal analysis of smelter stacks indicates 85% operating capacity, down from 95% last week. Potential undeclared maintenance."
                ),
                Source(
                    title="LME Warehouse Inventory (Live)",
                    url="internal://lme/warehouse",
                    snippet="On-warrant stocks in Rotterdam down 4500 tonnes. Cancelled warrants rising (22%)."
                )
            ])
            
        elif "crop" in q_lower or "sovbean" in q_lower or "corn" in q_lower:
             sources.extend([
                Source(
                    title="NDVI Crop Health - Brazil Mato Grosso",
                    url="internal://satellite/ndvi_brazil",
                    snippet="Vegetation index 15% below 5-year average in Southern Mato Grosso. Soil moisture critical. Early harvest yields likely impacted."
                )
             ])
        
        # Fallback generic "Physical" signal if specific keyword not matched
        if not sources:
            sources.append(Source(
                title="Global Supply Chain Pressure Index",
                url="internal://fed/gscpi",
                snippet="Index is at +0.5 standard deviations. Shipping costs normalizing but container throughput in LA/LB port remains congested."
            ))
            
        return sources
