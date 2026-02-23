import pytest
import asyncio
from app.rs_engine import ReplayContext, ReplayMode, InteractionRecorder, deterministic_replay
from app.rs_engine.wrappers import NonDeterministicError

# Clean up recorder before each test
@pytest.fixture(autouse=True)
def clean_recorder():
    InteractionRecorder().clear()
    ReplayContext.set_mode(ReplayMode.LIVE)
    yield
    InteractionRecorder().clear()
    ReplayContext.set_mode(ReplayMode.LIVE)

@pytest.mark.asyncio
async def test_deterministic_replay_basic():
    # 1. Define a simulation of an unstable API
    api_call_count = 0
    
    @deterministic_replay
    async def unstable_api(x, y):
        nonlocal api_call_count
        api_call_count += 1
        return x + y + api_call_count

    # 2. RECORD MODE
    ReplayContext.set_mode(ReplayMode.RECORD)
    
    # First call: x=1, y=2 -> 1+2+1 = 4
    result1 = await unstable_api(1, 2)
    assert result1 == 4
    assert api_call_count == 1
    
    # Second call: x=10, y=20 -> 10+20+2 = 32
    result2 = await unstable_api(10, 20)
    assert result2 == 32
    assert api_call_count == 2
    
    # 3. REPLAY MODE
    ReplayContext.set_mode(ReplayMode.REPLAY)
    
    # Replay first call: Should return 4, NOT (1+2+3=6)
    # The underlying function should NOT be called, so api_call_count stays 2
    replay1 = await unstable_api(1, 2)
    assert replay1 == 4
    assert api_call_count == 2 # verify no side effect
    
    # Replay second call
    replay2 = await unstable_api(10, 20)
    assert replay2 == 32
    assert api_call_count == 2

@pytest.mark.asyncio
async def test_replay_missing_trace_raises_error():
    @deterministic_replay
    async def my_func(a):
        return a * 2

    ReplayContext.set_mode(ReplayMode.REPLAY)
    
    with pytest.raises(NonDeterministicError):
        await my_func(5)

@pytest.mark.asyncio
async def test_live_mode_passthrough():
    @deterministic_replay
    async def simple_func(msg):
        return f"Echo: {msg}"
        
    ReplayContext.set_mode(ReplayMode.LIVE)
    
    res = await simple_func("Hello")
    assert res == "Echo: Hello"
    
    # Verify nothing was recorded
    recorder = InteractionRecorder()
    assert recorder.get_recording("simple_func", ("Hello",), {}) is None

@pytest.mark.asyncio
async def test_integration_with_mock_service():
    # Simulate a service method that would normally hit an LLM
    # We use a side effect (random or counter) to prove replay works
    
    class MockIntelligenceService:
        def __init__(self):
            self.counter = 0

        @deterministic_replay
        async def generate_forecast(self, question: str):
            self.counter += 1
            # In a real scenario, this would be an LLM response which varies
            return f"Forecast for {question} (Run {self.counter})"

    service = MockIntelligenceService()
    
    # 1. RECORD
    ReplayContext.set_mode(ReplayMode.RECORD)
    res1 = await service.generate_forecast("AI Stocks")
    assert res1 == "Forecast for AI Stocks (Run 1)"
    assert service.counter == 1
    
    # 2. REPLAY
    ReplayContext.set_mode(ReplayMode.REPLAY)
    # The underlying method should NOT be called, so counter remains 1
    # But it returns the recorded result "Run 1"
    res2 = await service.generate_forecast("AI Stocks")
    
    assert res2 == "Forecast for AI Stocks (Run 1)" # Matches recorded output!
    assert service.counter == 1 # Proves method was bypassed
    
    # 3. RECORD new query
    ReplayContext.set_mode(ReplayMode.RECORD)
    res3 = await service.generate_forecast("Oil Prices")
    assert res3 == "Forecast for Oil Prices (Run 2)" # Counter increments
    assert service.counter == 2

