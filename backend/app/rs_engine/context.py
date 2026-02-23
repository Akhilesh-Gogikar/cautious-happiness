import json
from enum import Enum
from .recorder import InteractionRecorder

class ReplayMode(Enum):
    LIVE = "live"       # Normal execution, nothing recorded
    RECORD = "record"   # Execute and record
    REPLAY = "replay"   # Replay from recording, fail if missing

class ReplayContext:
    _mode: ReplayMode = ReplayMode.LIVE
    _recorder = InteractionRecorder()

    @classmethod
    def set_mode(cls, mode: ReplayMode):
        cls._mode = mode

    @classmethod
    def get_mode(cls) -> ReplayMode:
        return cls._mode

    @classmethod
    def load_from_file(cls, filepath: str):
        try:
            with open(filepath, 'r') as f:
                # This assumes purely JSON serializable data for now.
                # For complex objects, we'd need a custom deserializer.
                # Since we are mocking mostly Pydantic/Dicts, simple JSON might suffice 
                # if we serialized correctly. 
                # For the Prototype, specific tests will inject the data directly.
                pass 
        except FileNotFoundError:
            pass

    @classmethod
    def save_to_file(cls, filepath: str):
        # Placeholder for persistent storage
        pass
