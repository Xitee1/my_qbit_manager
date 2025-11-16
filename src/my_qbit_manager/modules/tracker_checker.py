"""Tracker checker module for identifying torrents with non-working trackers."""

import logging
from typing import Any, Dict, List, Set

from my_qbit_manager.modules.base_module import BaseModule

logger = logging.getLogger(__name__)


class TrackerChecker(BaseModule):
    """Module to check for non-working trackers and tag affected torrents."""

    # Tracker statuses that indicate a tracker is not working
    NON_WORKING_STATUSES = [
        2,  # Not contacted yet
        3,  # Working (but we'll check the msg)
        4,  # Not working
    ]

    def __init__(self, qbit_client, config: Dict[str, Any]):
        """
        Initialize the tracker checker module.

        Args:
            qbit_client: qBittorrent client instance
            config: Module configuration
        """
        super().__init__(qbit_client, config)
        
        # Module configuration with defaults
        self.categories = self.get_config('categories', [])
        self.tag = self.get_config('tag', 'broken-tracker')
        self.remove_tag_when_fixed = self.get_config('remove_tag_when_fixed', True)
        self.check_message_for_errors = self.get_config('check_message_for_errors', True)
        
        # Error keywords to look for in tracker messages
        self.error_keywords = self.get_config('error_keywords', [
            'not registered',
            'not found',
            'unregistered',
            'torrent not found',
            'invalid passkey',
            'passkey',
        ])

    def run(self):
        """Execute the tracker checker module."""
        self.logger.info("Starting tracker checker module")
        
        try:
            # Get torrents based on category filter
            if self.categories:
                self.logger.info("Checking torrents in categories: %s", ', '.join(self.categories))
                all_torrents = []
                for category in self.categories:
                    torrents = self.qbit_client.get_torrents(category=category)
                    all_torrents.extend(torrents)
            else:
                self.logger.info("Checking all torrents (no category filter)")
                all_torrents = self.qbit_client.get_torrents()
            
            self.logger.info("Found %d torrent(s) to check", len(all_torrents))
            
            # Track torrents with broken and working trackers
            torrents_with_broken_trackers: Set[str] = set()
            torrents_with_working_trackers: Set[str] = set()
            
            # Check each torrent
            for torrent in all_torrents:
                has_broken_tracker = self._check_torrent_trackers(torrent)
                
                if has_broken_tracker:
                    torrents_with_broken_trackers.add(torrent.hash)
                else:
                    torrents_with_working_trackers.add(torrent.hash)
            
            # Apply tags
            self._apply_tags(torrents_with_broken_trackers, torrents_with_working_trackers)
            
            self.logger.info("Tracker checker module completed")
            self.logger.info("Summary: %d torrent(s) with broken trackers, %d with working trackers",
                           len(torrents_with_broken_trackers),
                           len(torrents_with_working_trackers))
            
        except Exception as e:
            self.logger.exception("Error in tracker checker module: %s", e)
            raise

    def _check_torrent_trackers(self, torrent) -> bool:
        """
        Check if a torrent has any non-working trackers.

        Args:
            torrent: Torrent object

        Returns:
            True if the torrent has broken trackers, False otherwise
        """
        try:
            trackers = self.qbit_client.get_torrent_trackers(torrent.hash)
            
            for tracker in trackers:
                # Skip trackers with tier -1 (internal trackers like DHT, PEX, LSD)
                if tracker.get('tier', 0) == -1:
                    continue
                
                # Check tracker status
                status = tracker.get('status', 0)
                msg = tracker.get('msg', '').lower()
                
                # Status 4 means not working
                if status == 4:
                    self.logger.debug("Torrent '%s' has broken tracker: %s (status: %d, msg: %s)",
                                    torrent.name, tracker.get('url', 'unknown'), status, msg)
                    return True
                
                # Check message for error keywords if enabled
                if self.check_message_for_errors and msg:
                    for keyword in self.error_keywords:
                        if keyword.lower() in msg:
                            self.logger.debug("Torrent '%s' has tracker with error message: %s (msg: %s)",
                                            torrent.name, tracker.get('url', 'unknown'), msg)
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error("Error checking trackers for torrent '%s': %s", torrent.name, e)
            return False

    def _apply_tags(self, broken_hashes: Set[str], working_hashes: Set[str]):
        """
        Apply or remove tags based on tracker status.

        Args:
            broken_hashes: Set of torrent hashes with broken trackers
            working_hashes: Set of torrent hashes with working trackers
        """
        # Add tag to torrents with broken trackers
        if broken_hashes:
            try:
                self.qbit_client.add_tag(list(broken_hashes), self.tag)
                self.logger.info("Tagged %d torrent(s) with '%s'", len(broken_hashes), self.tag)
            except Exception as e:
                self.logger.error("Failed to add tags: %s", e)
        
        # Remove tag from torrents with working trackers (if configured)
        if self.remove_tag_when_fixed and working_hashes:
            try:
                self.qbit_client.remove_tag(list(working_hashes), self.tag)
                self.logger.info("Removed tag '%s' from %d torrent(s) with working trackers",
                               self.tag, len(working_hashes))
            except Exception as e:
                self.logger.error("Failed to remove tags: %s", e)
