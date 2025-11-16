"""Base module class for all qBittorrent Manager modules."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from my_qbit_manager.qbit_client import QBitClient

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """Abstract base class for all modules."""

    def __init__(self, qbit_client: QBitClient, config: Dict[str, Any]):
        """
        Initialize the module.

        Args:
            qbit_client: qBittorrent client instance
            config: Module-specific configuration
        """
        self.qbit_client = qbit_client
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def run(self):
        """
        Execute the module's main functionality.

        This method must be implemented by all subclasses.
        """
        pass

    def validate_config(self, required_fields: list):
        """
        Validate that required configuration fields are present.

        Args:
            required_fields: List of required field names

        Raises:
            ValueError: If a required field is missing
        """
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required configuration field: {field}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
