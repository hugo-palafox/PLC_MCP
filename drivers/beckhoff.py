import pyads
import logging
from typing import Any, Dict, List, Optional
from .base import BasePLC

logger = logging.getLogger("plc-bridge.beckhoff")

class TwinCATDriver(BasePLC):
    """
    Beckhoff TwinCAT ADS Driver.
    Optimized for symbol handling and large GVLs.
    """

    def __init__(self, ams_net_id: str, ams_port: int = pyads.PORT_TC3PLC1):
        self.ams_net_id = ams_net_id
        self.ams_port = ams_port
        self.plc: Optional[pyads.Connection] = None
        self._symbol_cache: Dict[str, Any] = {}

    def connect(self) -> bool:
        try:
            self.plc = pyads.Connection(self.ams_net_id, self.ams_port)
            self.plc.open()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        if self.plc:
            self.plc.close()
            self.plc = None

    @property
    def is_connected(self) -> bool:
        return self.plc is not None and self.plc.is_open

    def read_tag(self, tag_path: str) -> Any:
        if not self.is_connected:
            raise ConnectionError("PLC not connected")
        return self.plc.read_by_name(tag_path)

    def read_tags(self, tag_paths: List[str]) -> Dict[str, Any]:
        """
        Batch read tags using pyads Sum Read for efficiency.
        Prevents bottlenecks in large GVLs.
        """
        if not self.is_connected:
            raise ConnectionError("PLC not connected")
        
        try:
            # Use pyads.Connection.read_list for optimized batch requests
            return self.plc.read_list(tag_paths)
        except Exception as e:
            logger.error(f"Batch read failed: {e}")
            # Fallback to individual reads if batch fails
            results = {}
            for path in tag_paths:
                try:
                    results[path] = self.read_tag(path)
                except Exception:
                    results[path] = None
            return results

    def list_all_tags(self, force_refresh: bool = False) -> List[Dict[str, str]]:
        """
        Retrieves all symbols from the TwinCAT PLC.
        Uses caching to avoid expensive re-uploads.
        """
        if not self.is_connected:
            raise ConnectionError("PLC not connected")
        
        if not self._symbol_cache or force_refresh:
            logger.info("Uploading symbols from PLC (this may take a moment for large projects)...")
            symbols = self.plc.get_all_symbols()
            self._symbol_cache = {
                s.name: {"name": s.name, "type": str(s.symbol_type), "comment": s.comment} 
                for s in symbols
            }
        
        return list(self._symbol_cache.values())

    def _get_plc_type(self, type_str: str) -> int:
        """
        Convert type string to pyads PLCTYPE constant.
        
        Args:
            type_str: String representation of PLC type (e.g., 'DINT', 'REAL')
        
        Returns:
            pyads PLCTYPE constant
        """
        type_map = {
            'BOOL': pyads.PLCTYPE_BOOL,
            'SINT': pyads.PLCTYPE_SINT,
            'USINT': pyads.PLCTYPE_USINT,
            'INT': pyads.PLCTYPE_INT,
            'UINT': pyads.PLCTYPE_UINT,
            'DINT': pyads.PLCTYPE_DINT,
            'UDINT': pyads.PLCTYPE_UDINT,
            'LINT': pyads.PLCTYPE_LINT,
            'ULINT': pyads.PLCTYPE_ULINT,
            'REAL': pyads.PLCTYPE_REAL,
            'LREAL': pyads.PLCTYPE_LREAL,
            'STRING': pyads.PLCTYPE_STRING,
        }
        return type_map.get(type_str.upper(), pyads.PLCTYPE_DINT)

    def read_array(self, tag_path: str, plc_type: int, array_size: int) -> List[Any]:
        """
        Read an array from the PLC.
        
        Args:
            tag_path: Path to array (e.g., "Global.PartsPerHour")
            plc_type: pyads.PLCTYPE_* constant
            array_size: Number of elements in the array
        
        Returns:
            List of values from the array
        
        Example:
            >>> driver.read_array("Global.PartsPerHour", pyads.PLCTYPE_DINT, 25)
            [120, 135, 142, ...]  # 25 values
        """
        if not self.is_connected:
            raise ConnectionError("PLC not connected")
        
        try:
            # Read entire array in one operation
            array_data = self.plc.read_by_name(tag_path, plc_type * array_size)
            return list(array_data) if hasattr(array_data, '__iter__') else [array_data]
        except Exception as e:
            logger.error(f"Array read failed for {tag_path}: {e}")
            raise
