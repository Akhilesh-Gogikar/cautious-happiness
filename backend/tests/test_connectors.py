import pytest
import asyncio
from app.connectors.aggregator import DataAggregator
from app.connectors.news import ReutersConnector, APNewsConnector, BloombergConnector
from app.connectors.social import TwitterConnector, RedditConnector, DiscordConnector
from app.connectors.vertical import NOAAConnector, CSPANConnector
from app.models import Source

@pytest.mark.asyncio
async def test_aggregator_fetch_all():
    connectors = [
        ReutersConnector(),
        APNewsConnector(),
        BloombergConnector(),
        TwitterConnector(),
        RedditConnector(),
        DiscordConnector(),
        NOAAConnector(),
        CSPANConnector()
    ]
    aggregator = DataAggregator(connectors)
    query = "US Elections"
    
    results = await aggregator.fetch_all(query)
    
    assert len(results) >= len(connectors)
    for res in results:
        assert isinstance(res, Source)
        assert res.title != ""
        assert res.url != ""
        assert res.snippet != ""

@pytest.mark.asyncio
async def test_individual_connectors():
    connectors = [
        ReutersConnector(),
        APNewsConnector(),
        BloombergConnector(),
        TwitterConnector(),
        RedditConnector(),
        DiscordConnector(),
        NOAAConnector(),
        CSPANConnector()
    ]
    query = "Fed Rate Cut"
    
    for connector in connectors:
        results = await connector.fetch_data(query)
        assert len(results) > 0
        
        # Check if the full name or part of the name (split by space or slash) is in the title
        name_parts = connector.name.replace("/", " ").split()
        assert any(part in results[0].title for part in name_parts), f"Expected one of {name_parts} in title '{results[0].title}'"
