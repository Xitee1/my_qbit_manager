"""qBittorrent client wrapper."""

import logging
from typing import List, Optional

import qbittorrentapi
from qbittorrentapi import Client

logger = logging.getLogger(__name__)


class QBitClient:
    """Wrapper for qBittorrent API client."""

    def __init__(self, host: str, port: int, username: str, password: str, use_ssl: bool = False):
        """
        Initialize qBittorrent client.

        Args:
            host: qBittorrent host address
            port: qBittorrent port
            username: qBittorrent username
            password: qBittorrent password
            use_ssl: Whether to use HTTPS
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.client: Optional[Client] = None

    def connect(self) -> bool:
        """
        Connect to qBittorrent.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            protocol = 'https' if self.use_ssl else 'http'
            url = f"{protocol}://{self.host}:{self.port}"
            
            logger.info("Connecting to qBittorrent at %s", url)
            
            self.client = Client(
                host=url,
                username=self.username,
                password=self.password
            )
            
            # Test connection
            self.client.auth_log_in()
            version = self.client.app.version
            
            logger.info("Successfully connected to qBittorrent v%s", version)
            return True
            
        except qbittorrentapi.LoginFailed as e:
            logger.error("Failed to login to qBittorrent: %s", e)
            return False
        except Exception as e:
            logger.error("Failed to connect to qBittorrent: %s", e)
            return False

    def disconnect(self):
        """Disconnect from qBittorrent."""
        if self.client:
            try:
                self.client.auth_log_out()
                logger.info("Disconnected from qBittorrent")
            except Exception as e:
                logger.warning("Error during disconnect: %s", e)

    def get_torrents(self, category: Optional[str] = None, tag: Optional[str] = None) -> List:
        """
        Get list of torrents.

        Args:
            category: Filter by category (optional)
            tag: Filter by tag (optional)

        Returns:
            List of torrent objects
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            torrents = self.client.torrents_info(category=category, tag=tag)
            logger.debug("Retrieved %d torrents", len(torrents))
            return torrents
        except Exception as e:
            logger.error("Failed to get torrents: %s", e)
            raise

    def get_torrent_trackers(self, torrent_hash: str) -> List:
        """
        Get trackers for a specific torrent.

        Args:
            torrent_hash: Hash of the torrent

        Returns:
            List of tracker objects
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            trackers = self.client.torrents_trackers(torrent_hash=torrent_hash)
            return trackers
        except Exception as e:
            logger.error("Failed to get trackers for torrent %s: %s", torrent_hash, e)
            raise

    def add_tag(self, torrent_hashes: List[str], tag: str):
        """
        Add a tag to torrents.

        Args:
            torrent_hashes: List of torrent hashes
            tag: Tag to add
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            self.client.torrents_add_tags(tags=tag, torrent_hashes=torrent_hashes)
            logger.info("Added tag '%s' to %d torrent(s)", tag, len(torrent_hashes))
        except Exception as e:
            logger.error("Failed to add tag: %s", e)
            raise

    def remove_tag(self, torrent_hashes: List[str], tag: str):
        """
        Remove a tag from torrents.

        Args:
            torrent_hashes: List of torrent hashes
            tag: Tag to remove
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            self.client.torrents_remove_tags(tags=tag, torrent_hashes=torrent_hashes)
            logger.info("Removed tag '%s' from %d torrent(s)", tag, len(torrent_hashes))
        except Exception as e:
            logger.error("Failed to remove tag: %s", e)
            raise
