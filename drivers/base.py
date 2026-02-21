from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

class BasePLC(ABC):
    """
    Abstract Base Class for PLC Drivers.
    Enforces a Read-Only interface for safety.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the PLC."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection."""
        pass

    @abstractmethod
    def read_tag(self, tag_path: str) -> Any:
        """Read a single tag value."""
        pass

    @abstractmethod
    def read_tags(self, tag_paths: List[str]) -> Dict[str, Any]:
        """Read multiple tags efficiently."""
        pass

    @abstractmethod
    def list_all_tags(self) -> List[Dict[str, str]]:
        """Browse and list available tags/symbols."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the driver is currently connected."""
        pass
