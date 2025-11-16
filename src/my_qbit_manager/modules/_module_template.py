"""
Template for creating new modules.

To create a new module:
1. Copy this file to a new file in the modules/ directory
2. Rename the class to match your module name (e.g., MyNewModule)
3. Implement the run() method with your logic
4. Add configuration to config.yaml
5. The module will be automatically loaded when enabled

Module naming convention:
- File: my_new_module.py
- Class: MyNewModule
- Config key: my_new_module
"""

import logging
from typing import Any, Dict

from my_qbit_manager.modules.base_module import BaseModule

logger = logging.getLogger(__name__)


class ModuleTemplate(BaseModule):
    """Template module - replace with your module description."""

    def __init__(self, qbit_client, config: Dict[str, Any]):
        """
        Initialize the module.

        Args:
            qbit_client: qBittorrent client instance
            config: Module configuration from config.yaml
        """
        super().__init__(qbit_client, config)
        
        # Load configuration with defaults
        self.example_setting = self.get_config('example_setting', 'default_value')
        self.another_setting = self.get_config('another_setting', True)
        
        # Validate required configuration (optional)
        # self.validate_config(['required_field'])

    def run(self):
        """Execute the module's main functionality."""
        self.logger.info("Starting module")
        
        try:
            # Get torrents (optionally filtered)
            torrents = self.qbit_client.get_torrents()
            self.logger.info("Found %d torrent(s) to process", len(torrents))
            
            # Process each torrent
            for torrent in torrents:
                self._process_torrent(torrent)
            
            self.logger.info("Module completed successfully")
            
        except Exception as e:
            self.logger.exception("Error in module: %s", e)
            raise

    def _process_torrent(self, torrent):
        """
        Process a single torrent.

        Args:
            torrent: Torrent object from qBittorrent API
        """
        # Example: Access torrent properties
        torrent_name = torrent.name
        torrent_hash = torrent.hash
        torrent_state = torrent.state
        
        self.logger.debug("Processing torrent: %s", torrent_name)
        
        # Your processing logic here
        # Examples:
        # - Check torrent properties
        # - Get torrent trackers
        # - Add/remove tags
        # - Modify torrent settings
        
        # Example: Add a tag
        # if some_condition:
        #     self.qbit_client.add_tag([torrent_hash], "your-tag")


# Example configuration for config.yaml:
"""
modules:
  module_template:
    enabled: false
    example_setting: "some value"
    another_setting: true
"""
