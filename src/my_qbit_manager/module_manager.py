"""Module manager for loading and running modules."""

import importlib
import logging
from pathlib import Path
from typing import Any, Dict, List

from my_qbit_manager.modules.base_module import BaseModule
from my_qbit_manager.qbit_client import QBitClient

logger = logging.getLogger(__name__)


class ModuleManager:
    """Manages loading and execution of modules."""

    def __init__(self, config: Dict[str, Any], qbit_client: QBitClient):
        """
        Initialize the module manager.

        Args:
            config: Application configuration
            qbit_client: qBittorrent client instance
        """
        self.config = config
        self.qbit_client = qbit_client
        self.modules: Dict[str, BaseModule] = {}

    def load_modules(self):
        """Load all enabled modules from configuration."""
        modules_config = self.config.get('modules', {})
        
        for module_name, module_config in modules_config.items():
            if not isinstance(module_config, dict):
                logger.warning("Invalid configuration for module '%s', skipping", module_name)
                continue
                
            if not module_config.get('enabled', False):
                logger.info("Module '%s' is disabled, skipping", module_name)
                continue

            try:
                self._load_module(module_name, module_config)
            except Exception as e:
                logger.error("Failed to load module '%s': %s", module_name, e)

    def _load_module(self, module_name: str, module_config: Dict[str, Any]):
        """
        Load a specific module.

        Args:
            module_name: Name of the module
            module_config: Module configuration
        """
        # Convert module name to class name (e.g., tracker_checker -> TrackerChecker)
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        
        try:
            # Import the module
            module_path = f"my_qbit_manager.modules.{module_name}"
            module = importlib.import_module(module_path)
            
            # Get the module class
            module_class = getattr(module, class_name)
            
            # Instantiate the module
            instance = module_class(self.qbit_client, module_config)
            
            # Store the instance
            self.modules[module_name] = instance
            
            logger.info("Loaded module: %s", module_name)
            
        except ImportError as e:
            logger.error("Could not import module '%s': %s", module_name, e)
            raise
        except AttributeError as e:
            logger.error("Module '%s' does not have class '%s': %s", module_name, class_name, e)
            raise
        except Exception as e:
            logger.error("Error instantiating module '%s': %s", module_name, e)
            raise

    def run_modules(self):
        """Run all loaded modules."""
        if not self.modules:
            logger.warning("No modules loaded to run")
            return

        logger.info("Running %d module(s)", len(self.modules))
        
        for module_name, module in self.modules.items():
            try:
                logger.info("Running module: %s", module_name)
                module.run()
                logger.info("Module '%s' completed successfully", module_name)
            except Exception as e:
                logger.error("Error running module '%s': %s", module_name, e)
                # Continue with other modules even if one fails

    def run_module(self, module_name: str):
        """
        Run a specific module by name.

        Args:
            module_name: Name of the module to run

        Raises:
            ValueError: If the module is not loaded
        """
        if module_name not in self.modules:
            raise ValueError(f"Module '{module_name}' is not loaded")

        logger.info("Running module: %s", module_name)
        self.modules[module_name].run()
        logger.info("Module '%s' completed successfully", module_name)

    def get_module(self, module_name: str) -> BaseModule:
        """
        Get a loaded module instance.

        Args:
            module_name: Name of the module

        Returns:
            Module instance

        Raises:
            ValueError: If the module is not loaded
        """
        if module_name not in self.modules:
            raise ValueError(f"Module '{module_name}' is not loaded")
        return self.modules[module_name]
