import pytest
from unittest.mock import AsyncMock, patch
from app.news_ingestor import NewsIngestor
from app.models import Source

@pytest.mark.asyncio
async def test_news_ingestor_fetch_and_store():
    # Mock VectorDBClient
    mock_vector_db = AsyncMock()
    
    # Mock DDGS inside NewsIngestor
    with patch('app.news_ingestor.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.return_value = [
            {'title': 'Test News 1', 'href': 'http://test.com/1', 'body': 'Snippet 1'},
            {'title': 'Test News 2', 'href': 'http://test.com/2', 'body': 'Snippet 2'}
        ]
        
        ingestor = NewsIngestor(mock_vector_db)
        
        sources = await ingestor.fetch_and_store("test query", max_results=2)
        
        assert len(sources) == 2
        assert sources[0].title == "Test News 1"
        
        # Verify upsert was called
        mock_vector_db.upsert_sources.assert_called_once()
        call_args = mock_vector_db.upsert_sources.call_args
        assert len(call_args[0][0]) == 2 # 2 sources passed
        assert call_args[1]['metadata'] == {"query": "test query"}

@pytest.mark.asyncio
async def test_news_ingestor_failure():
    mock_vector_db = AsyncMock()
    with patch('app.news_ingestor.DDGS') as MockDDGS:
        mock_ddgs_instance = MockDDGS.return_value
        mock_ddgs_instance.text.side_effect = Exception("DDGS Error")
        
        ingestor = NewsIngestor(mock_vector_db)
        sources = await ingestor.fetch_and_store("test query")
        
        assert len(sources) == 0
        mock_vector_db.upsert_sources.assert_not_called()
