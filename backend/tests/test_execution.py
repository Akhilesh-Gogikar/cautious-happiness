import pytest
from app.services.execution import ExecutionService

@pytest.mark.asyncio
async def test_construct_trade_payload():
    service = ExecutionService()
    result = await service.construct_trade_payload()
    
    assert result["status"] == "ready_to_sign"
    assert "tx_payload" in result
    assert result["tx_payload"]["chainId"] == 137
