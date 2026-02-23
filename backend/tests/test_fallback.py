import pytest
from app.engine import IntelligenceMirrorEngine, FallbackModelOrchestrator
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_fallback_logic_secondary_success():
    orchestrator = FallbackModelOrchestrator(primary="lfm-thinking", secondaries=["lfm-40b"])
    
    mock_func = AsyncMock()
    # Primary fails, secondary succeeds
    mock_func.side_effect = [Exception("Primary failure"), "Success"]
    
    result = await orchestrator.run_with_fallback(mock_func, "arg1")
    
    assert result == "Success"
    assert mock_func.call_count == 2
    # Check that model was updated in kwargs
    assert mock_func.call_args_list[0].kwargs['model'] == "lfm-thinking"
    assert mock_func.call_args_list[1].kwargs['model'] == "lfm-40b"

@pytest.mark.asyncio
async def test_fallback_logic_all_fail():
    orchestrator = FallbackModelOrchestrator(primary="lfm-thinking", secondaries=["lfm-40b"])
    
    mock_func = AsyncMock()
    mock_func.side_effect = [Exception("1"), Exception("2")]
    
    with pytest.raises(Exception) as excinfo:
        await orchestrator.run_with_fallback(mock_func, "arg1")
    
    assert str(excinfo.value) == "2"
    assert mock_func.call_count == 2
