"""
qBittorrent Remote Client

A Python-based command-line tool for remotely managing qBittorrent instances via the Web API.
"""

__version__ = "0.1.0"
__author__ = "rlong"
__email__ = "rlong@example.com"

from .qbt_api import QBittorrentAPI, QBittorrentError, create_client_from_config
from .qbt_client import main

__all__ = ["QBittorrentAPI", "QBittorrentError", "create_client_from_config", "main"]
