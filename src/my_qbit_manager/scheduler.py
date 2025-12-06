"""Scheduler for running modules based on their individual schedules."""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from my_qbit_manager.module_manager import ModuleManager

logger = logging.getLogger(__name__)


class ModuleScheduler:
    """Manages scheduling and execution of modules based on their individual schedules."""

    def __init__(self, module_manager: ModuleManager, config: Dict[str, Any]):
        """
        Initialize the scheduler.

        Args:
            module_manager: ModuleManager instance
            config: Application configuration
        """
        self.module_manager = module_manager
        self.config = config
        self.module_schedules: Dict[str, Dict[str, Any]] = {}
        self.last_run: Dict[str, datetime] = {}

    def initialize_schedules(self):
        """Initialize schedules for all enabled modules."""
        modules_config = self.config.get('modules', {})
        
        for module_name, module_config in modules_config.items():
            if not isinstance(module_config, dict):
                continue
                
            if not module_config.get('enabled', False):
                continue
            
            schedule_config = module_config.get('schedule', {})
            
            # Default: run once immediately if no schedule specified
            if not schedule_config or not schedule_config.get('enabled', False):
                logger.info("Module '%s' has no schedule - will run once", module_name)
                self.module_schedules[module_name] = {
                    'enabled': False,
                    'interval_minutes': None,
                    'run_on_start': True
                }
            else:
                interval = schedule_config.get('interval_minutes', 60)
                run_on_start = schedule_config.get('run_on_start', True)
                
                self.module_schedules[module_name] = {
                    'enabled': True,
                    'interval_minutes': interval,
                    'run_on_start': run_on_start
                }
                
                logger.info("Module '%s' scheduled to run every %d minutes", 
                          module_name, interval)

    def should_run_module(self, module_name: str) -> bool:
        """
        Check if a module should run now.

        Args:
            module_name: Name of the module

        Returns:
            True if the module should run, False otherwise
        """
        if module_name not in self.module_schedules:
            return False
        
        schedule = self.module_schedules[module_name]
        
        # Check if module has never run
        if module_name not in self.last_run:
            return schedule.get('run_on_start', True)
        
        # If scheduling is disabled, only run once
        if not schedule.get('enabled', False):
            return False
        
        # Check if enough time has passed since last run
        interval_minutes = schedule.get('interval_minutes', 60)
        last_run_time = self.last_run[module_name]
        next_run_time = last_run_time + timedelta(minutes=interval_minutes)
        
        return datetime.now() >= next_run_time

    def run_module_if_scheduled(self, module_name: str):
        """
        Run a module if its schedule indicates it should run.

        Args:
            module_name: Name of the module to potentially run
        """
        if not self.should_run_module(module_name):
            return
        
        try:
            logger.info("Running scheduled module: %s", module_name)
            self.module_manager.run_module(module_name)
            self.last_run[module_name] = datetime.now()
            logger.info("Module '%s' completed successfully", module_name)
        except Exception as e:
            logger.error("Error running module '%s': %s", module_name, e)
            # Still update last_run to prevent rapid retries
            self.last_run[module_name] = datetime.now()

    def run_scheduler_loop(self, check_interval_seconds: int = 60):
        """
        Run the scheduler in a continuous loop.

        Args:
            check_interval_seconds: How often to check if modules should run
        """
        logger.info("Starting scheduler loop (checking every %d seconds)", 
                   check_interval_seconds)
        
        # Load modules
        self.module_manager.load_modules()
        
        # Initialize schedules
        self.initialize_schedules()
        
        if not self.module_schedules:
            logger.warning("No modules scheduled to run")
            return
        
        logger.info("Scheduler initialized with %d module(s)", len(self.module_schedules))
        
        try:
            while True:
                # Check each module's schedule
                for module_name in list(self.module_schedules.keys()):
                    self.run_module_if_scheduled(module_name)
                
                # Wait before next check
                time.sleep(check_interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.exception("Scheduler error: %s", e)
            raise

    def run_all_once(self):
        """Run all enabled modules once and exit."""
        logger.info("Running all enabled modules once")
        
        # Load modules
        self.module_manager.load_modules()
        
        # Initialize schedules to get enabled modules
        self.initialize_schedules()
        
        if not self.module_schedules:
            logger.warning("No modules to run")
            return
        
        # Run each enabled module
        for module_name in self.module_schedules.keys():
            try:
                logger.info("Running module: %s", module_name)
                self.module_manager.run_module(module_name)
                logger.info("Module '%s' completed successfully", module_name)
            except Exception as e:
                logger.error("Error running module '%s': %s", module_name, e)
                # Continue with other modules

    def get_schedule_info(self) -> Dict[str, Any]:
        """
        Get information about module schedules.

        Returns:
            Dictionary with schedule information for each module
        """
        info = {}
        
        for module_name, schedule in self.module_schedules.items():
            last_run = self.last_run.get(module_name)
            
            module_info = {
                'enabled': schedule.get('enabled', False),
                'interval_minutes': schedule.get('interval_minutes'),
                'last_run': last_run.isoformat() if last_run else None,
            }
            
            if schedule.get('enabled', False) and last_run:
                interval = schedule.get('interval_minutes', 60)
                next_run = last_run + timedelta(minutes=interval)
                module_info['next_run'] = next_run.isoformat()
                module_info['next_run_in_minutes'] = int((next_run - datetime.now()).total_seconds() / 60)
            
            info[module_name] = module_info
        
        return info
