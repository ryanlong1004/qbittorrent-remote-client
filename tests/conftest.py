"""Pytest configuration and fixtures."""

import pytest
import requests_mock

from qbittorrent_remote_client.qbt_api import QBittorrentAPI


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "host": "test-host",
        "port": 8080,
        "username": "test-user",
        "password": "test-pass",
        "use_https": False,
        "timeout": 30,
        "verify_ssl": True,
        "base_path": "",
    }


@pytest.fixture
def qbt_client(mock_config):
    """Create a QBittorrentAPI client for testing."""
    return QBittorrentAPI(**mock_config)


@pytest.fixture
def mock_session():
    """Mock requests session."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def sample_torrents():
    """Sample torrent data for testing."""
    return [
        {
            "hash": "abc123",
            "name": "Test Torrent 1",
            "size": 1073741824,  # 1GB
            "state": "downloading",
            "dlspeed": 1024000,  # 1MB/s
            "upspeed": 512000,  # 512KB/s
            "progress": 0.5,
            "eta": 1800,  # 30 minutes
            "category": "Movies",
            "ratio": 1.5,
        },
        {
            "hash": "def456",
            "name": "Test Torrent 2",
            "size": 2147483648,  # 2GB
            "state": "pausedDL",
            "dlspeed": 0,
            "upspeed": 0,
            "progress": 0.8,
            "eta": 8640000,  # infinity
            "category": "TV",
            "ratio": 0.8,
        },
        {
            "hash": "ghi789",
            "name": "Test Torrent 3",
            "size": 536870912,  # 512MB
            "state": "error",
            "dlspeed": 0,
            "upspeed": 0,
            "progress": 0.0,
            "eta": 8640000,
            "category": "",
            "ratio": 0.0,
        },
    ]


@pytest.fixture
def sample_transfer_info():
    """Sample transfer info data for testing."""
    return {
        "dl_info_speed": 1024000,  # 1MB/s
        "up_info_speed": 512000,  # 512KB/s
        "dl_info_data": 10737418240,  # 10GB
        "up_info_data": 5368709120,  # 5GB
        "alltime_dl": 107374182400,  # 100GB
        "alltime_ul": 53687091200,  # 50GB
        "global_ratio": 0.5,
    }


@pytest.fixture
def sample_categories():
    """Sample categories data for testing."""
    return {
        "Movies": {"name": "Movies", "savePath": "/downloads/movies"},
        "TV": {"name": "TV", "savePath": "/downloads/tv"},
    }
