import functools
from .context import ReplayContext, ReplayMode
from .recorder import InteractionRecorder

class NonDeterministicError(Exception):
    pass

def deterministic_replay(func):
    """
    Decorator to make a function deterministic via the Replay Engine.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        mode = ReplayContext.get_mode()
        recorder = InteractionRecorder()
        func_name = func.__qualname__ # Use qualname to distinguish methods

        if mode == ReplayMode.REPLAY:
            result = recorder.get_recording(func_name, args, kwargs)
            if result is None:
                raise NonDeterministicError(
                    f"No recording found for {func_name} with these args in REPLAY mode."
                )
            return result

        # LIVE or RECORD mode
        result = await func(*args, **kwargs)

        if mode == ReplayMode.RECORD:
            recorder.record(func_name, args, kwargs, result)

        return result
    return wrapper
