import math
import time
import random
from typing import Any, Dict, List
from .base import BasePLC

class MockDriver(BasePLC):
    """
    Mock PLC Driver for offline testing and UI simulation.
    Generates sine waves for floats and toggles for booleans.
    """

    def __init__(self):
        self._connected = False
        self._start_time = time.time()
        # Simulated tag database (Matching live OEE GVL)
        self._tags = {
            "Global.bMachineRunning": "BOOL",
            "Global.bMachineInFault": "BOOL",
            "Global.bMachineInChangeover": "BOOL",
            "Global.nTotalPartsProduced": "UDINT",
            "Global.nGoodPartsProduced": "UDINT",
            "Global.nRejectedParts": "UDINT",
            "Global.fOEE_Overall": "REAL",
            "Global.fActualRunTime": "REAL",
            "Global.nShiftTarget": "UDINT"
        }

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _get_simulated_value(self, tag_path: str) -> Any:
        elapsed = time.time() - self._start_time
        
        if ".f" in tag_path:  # Simulate float/sine wave
            # Percentage or time data
            if "OEE" in tag_path:
                return round(75.0 + 10.0 * math.sin(elapsed * 0.1), 2)
            return round(elapsed * 0.8, 2)
        
        if ".b" in tag_path:  # Simulate boolean/toggle
            if "Running" in tag_path: return True
            return bool(int(elapsed / 10) % 2 == 0)
        
        if ".n" in tag_path:  # Simulate counter
            if "Target" in tag_path: return 1000
            return int(elapsed * 2)
            
        return random.randint(0, 100)

    def read_tag(self, tag_path: str) -> Any:
        if not self.is_connected:
            raise ConnectionError("Mock PLC not connected")
        return self._get_simulated_value(tag_path)

    def read_tags(self, tag_paths: List[str]) -> Dict[str, Any]:
        return {path: self.read_tag(path) for path in tag_paths}

    def list_all_tags(self) -> List[Dict[str, str]]:
        return [{"name": name, "type": type_info, "comment": "Mock Data"} 
                for name, type_info in self._tags.items()]
