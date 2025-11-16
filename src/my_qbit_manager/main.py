"""Main entry point for the qBittorrent Manager application."""

import logging
import sys
from pathlib import Path
from typing import Optional

from my_qbit_manager.config_manager import ConfigManager
from my_qbit_manager.module_manager import ModuleManager
from my_qbit_manager.qbit_client import QBitClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/qbit_manager.log')
    ]
)

logger = logging.getLogger(__name__)


class QBitManager:
    """Main application class for qBittorrent Manager."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the qBittorrent Manager.

        Args:
            config_path: Path to the configuration file. Defaults to config/config.yaml
        """
        self.config_path = config_path or Path("config/config.yaml")
        self.config_manager = ConfigManager(self.config_path)
        self.config = self.config_manager.load_config()
        
        logger.info("Initializing qBittorrent Manager v%s", self.config.get('version', '0.1.0'))
        
        # Initialize qBittorrent client
        self.qbit_client = QBitClient(
            host=self.config['qbittorrent']['host'],
            port=self.config['qbittorrent']['port'],
            username=self.config['qbittorrent']['username'],
            password=self.config['qbittorrent']['password'],
            use_ssl=self.config['qbittorrent'].get('use_ssl', False)
        )
        
        # Initialize module manager
        self.module_manager = ModuleManager(self.config, self.qbit_client)

    def run(self):
        """Run all enabled modules."""
        logger.info("Starting qBittorrent Manager")
        
        try:
            # Connect to qBittorrent
            if not self.qbit_client.connect():
                logger.error("Failed to connect to qBittorrent. Exiting.")
                return False
            
            logger.info("Successfully connected to qBittorrent")
            
            # Load and run enabled modules
            self.module_manager.load_modules()
            self.module_manager.run_modules()
            
            logger.info("All modules executed successfully")
            return True
            
        except Exception as e:
            logger.exception("An error occurred during execution: %s", e)
            return False
        finally:
            self.qbit_client.disconnect()
            logger.info("qBittorrent Manager finished")

    def run_specific_module(self, module_name: str):
        """
        Run a specific module by name.

        Args:
            module_name: Name of the module to run
        """
        logger.info("Running specific module: %s", module_name)
        
        try:
            if not self.qbit_client.connect():
                logger.error("Failed to connect to qBittorrent. Exiting.")
                return False
            
            self.module_manager.load_modules()
            self.module_manager.run_module(module_name)
            
            return True
            
        except Exception as e:
            logger.exception("An error occurred while running module %s: %s", module_name, e)
            return False
        finally:
            self.qbit_client.disconnect()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="qBittorrent Manager - Modular torrent management tool")
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config/config.yaml'),
        help='Path to configuration file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Run a specific module instead of all enabled modules'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='qBittorrent Manager 0.1.0'
    )
    
    args = parser.parse_args()
    
    manager = QBitManager(config_path=args.config)
    
    if args.module:
        success = manager.run_specific_module(args.module)
    else:
        success = manager.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
