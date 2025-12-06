"""Configuration management for qBittorrent Manager."""

import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration from YAML files and environment variables."""

    def __init__(self, config_path: Path):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file and merge with environment variables.
        
        Environment variables take priority over config.yaml for qBittorrent settings.

        Returns:
            Dictionary containing the merged configuration

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the configuration file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        logger.info("Loading configuration from %s", self.config_path)

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Override qBittorrent settings with environment variables (takes priority)
        self._apply_env_overrides()

        # Validate configuration
        self._validate_config()

        logger.info("Configuration loaded successfully")
        return self.config

    def _apply_env_overrides(self):
        """
        Apply environment variable overrides to qBittorrent configuration.
        
        Environment variables ALWAYS take priority over config.yaml values.
        Only qBittorrent settings can be overridden via environment variables.
        """
        # Ensure qbittorrent section exists
        if 'qbittorrent' not in self.config:
            self.config['qbittorrent'] = {}
        
        qbit_config = self.config['qbittorrent']
        overrides_applied = []
        
        # qBittorrent connection settings - env vars always take priority
        if os.getenv('QBIT_HOST'):
            qbit_config['host'] = os.getenv('QBIT_HOST')
            overrides_applied.append('host')
        
        if os.getenv('QBIT_PORT'):
            qbit_config['port'] = int(os.getenv('QBIT_PORT'))
            overrides_applied.append('port')
        
        if os.getenv('QBIT_USERNAME'):
            qbit_config['username'] = os.getenv('QBIT_USERNAME')
            overrides_applied.append('username')
        
        if os.getenv('QBIT_PASSWORD'):
            qbit_config['password'] = os.getenv('QBIT_PASSWORD')
            overrides_applied.append('password')
        
        if os.getenv('QBIT_USE_SSL'):
            qbit_config['use_ssl'] = os.getenv('QBIT_USE_SSL').lower() == 'true'
            overrides_applied.append('use_ssl')

        if overrides_applied:
            logger.info("Environment variable overrides applied for qBittorrent settings: %s", 
                       ', '.join(overrides_applied))
        else:
            logger.debug("No environment variable overrides found")

    def _validate_config(self):
        """
        Validate the configuration structure.

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Check required sections
        if 'qbittorrent' not in self.config:
            raise ValueError("Missing 'qbittorrent' section in configuration")

        if 'modules' not in self.config:
            raise ValueError("Missing 'modules' section in configuration")

        # Check required qBittorrent settings
        qbit_config = self.config['qbittorrent']
        required_fields = ['host', 'port', 'username', 'password']
        
        for field in required_fields:
            if field not in qbit_config:
                raise ValueError(f"Missing required qBittorrent configuration: {field}")

        logger.debug("Configuration validation successful")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'qbittorrent.host')
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

    def reload(self):
        """Reload configuration from file."""
        self.load_config()
