import json
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime

class InteractionRecorder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InteractionRecorder, cls).__new__(cls)
            cls._instance.traces = {}
        return cls._instance

    def clear(self):
        self.traces = {}

    def _hash_input(self, args: tuple, kwargs: dict) -> str:
        """
        Create a deterministic hash of the input arguments.
        Arguments must be serializable or support __str__.
        """
        # Convert args/kwargs to a stable string representation
        # TODO: Better serialization for complex objects (Pydantic models)
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.sha256(key_str.encode()).hexdigest()

    def record(self, func_name: str, args: tuple, kwargs: dict, result: Any):
        if func_name not in self.traces:
            self.traces[func_name] = {}
        
        input_hash = self._hash_input(args, kwargs)
        
        # We store the result. If result is an object, we might need to serialize it.
        # For this prototype, we assume the result is pickle-able or we rely on the test to handle it.
        # In a real system, we'd json-serialize here.
        self.traces[func_name][input_hash] = {
            "output": result,
            "timestamp": datetime.now().isoformat()
        }

    def get_recording(self, func_name: str, args: tuple, kwargs: dict) -> Optional[Any]:
        if func_name not in self.traces:
            return None
        
        input_hash = self._hash_input(args, kwargs)
        record = self.traces[func_name].get(input_hash)
        
        if record:
            return record["output"]
        return None

    def export_traces(self) -> dict:
        return self.traces

    def load_traces(self, traces: dict):
        self.traces = traces
