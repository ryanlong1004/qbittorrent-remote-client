"""Tests for qbt_api.py"""

import json
import pytest
import requests
from unittest.mock import patch, mock_open

from qbt_api import (
    QBittorrentAPI,
    QBittorrentError,
    QBittorrentAuthenticationError,
    QBittorrentConnectionError,
    QBittorrentAPIError,
    load_config,
    create_client_from_config,
)


class TestQBittorrentAPI:
    """Test cases for QBittorrentAPI class."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        client = QBittorrentAPI()

        assert client.host == "localhost"
        assert client.port == 8080
        assert client.username == "admin"
        assert client.timeout == 30
        assert "http://localhost:8080" in client.base_url
        assert not client._authenticated

    def test_init_custom_values(self, mock_config):
        """Test initialization with custom values."""
        client = QBittorrentAPI(**mock_config)

        assert client.host == "test-host"
        assert client.port == 8080
        assert client.username == "test-user"
        assert client.timeout == 30
        assert "http://test-host:8080" in client.base_url

    def test_init_https(self):
        """Test initialization with HTTPS."""
        client = QBittorrentAPI(use_https=True)
        assert "https://" in client.base_url

    def test_init_base_path(self):
        """Test initialization with base path."""
        client = QBittorrentAPI(base_path="/qbittorrent")
        assert "/qbittorrent/api/v2" in client.base_url

    def test_login_success(self, qbt_client, mock_session):
        """Test successful login."""
        mock_session.post(f"{qbt_client.base_url}/auth/login", text="Ok.")

        result = qbt_client.login()
        assert result is True
        assert qbt_client._authenticated is True

    def test_login_failure(self, qbt_client, mock_session):
        """Test failed login."""
        mock_session.post(f"{qbt_client.base_url}/auth/login", text="Fails.")

        with pytest.raises(QBittorrentAuthenticationError):
            qbt_client.login()

    def test_login_connection_error(self, qbt_client, mock_session):
        """Test login with connection error."""
        mock_session.post(
            f"{qbt_client.base_url}/auth/login",
            exc=requests.ConnectionError("Connection failed"),
        )

        with pytest.raises(QBittorrentConnectionError):
            qbt_client.login()

    def test_logout_success(self, qbt_client, mock_session):
        """Test successful logout."""
        qbt_client._authenticated = True
        mock_session.post(f"{qbt_client.base_url}/auth/logout")

        result = qbt_client.logout()
        assert result is True
        assert qbt_client._authenticated is False

    def test_get_torrents_success(self, qbt_client, mock_session, sample_torrents):
        """Test successful get_torrents."""
        qbt_client._authenticated = True
        mock_session.get(f"{qbt_client.base_url}/torrents/info", json=sample_torrents)

        result = qbt_client.get_torrents()
        assert len(result) == 3
        assert result[0]["name"] == "Test Torrent 1"

    def test_get_torrents_with_filters(self, qbt_client, mock_session, sample_torrents):
        """Test get_torrents with filters."""
        qbt_client._authenticated = True
        mock_session.get(f"{qbt_client.base_url}/torrents/info", json=sample_torrents)

        result = qbt_client.get_torrents(filter="downloading", category="Movies")
        assert mock_session.last_request.qs == {
            "filter": ["downloading"],
            "category": ["Movies"],
        }

    def test_get_global_transfer_info(self, qbt_client, mock_session, sample_transfer_info):
        """Test get_global_transfer_info."""
        qbt_client._authenticated = True
        mock_session.get(f"{qbt_client.base_url}/transfer/info", json=sample_transfer_info)

        result = qbt_client.get_global_transfer_info()
        assert result["dl_info_speed"] == 1024000
        assert result["global_ratio"] == 0.5

    def test_get_application_version(self, qbt_client, mock_session):
        """Test get_application_version."""
        mock_session.get(f"{qbt_client.base_url}/app/version", text='"v4.6.3"')

        result = qbt_client.get_application_version()
        assert result == "v4.6.3"

    def test_get_categories(self, qbt_client, mock_session, sample_categories):
        """Test get_categories."""
        qbt_client._authenticated = True
        mock_session.get(f"{qbt_client.base_url}/torrents/categories", json=sample_categories)

        result = qbt_client.get_categories()
        assert "Movies" in result
        assert result["Movies"]["savePath"] == "/downloads/movies"

    def test_pause_torrents(self, qbt_client, mock_session):
        """Test pause_torrents."""
        qbt_client._authenticated = True
        mock_session.post(f"{qbt_client.base_url}/torrents/pause")

        result = qbt_client.pause_torrents(["hash1", "hash2"])
        assert result is True

    def test_resume_torrents(self, qbt_client, mock_session):
        """Test resume_torrents."""
        qbt_client._authenticated = True
        mock_session.post(f"{qbt_client.base_url}/torrents/resume")

        result = qbt_client.resume_torrents("hash1")
        assert result is True

    def test_delete_torrents(self, qbt_client, mock_session):
        """Test delete_torrents."""
        qbt_client._authenticated = True
        mock_session.post(f"{qbt_client.base_url}/torrents/delete")

        result = qbt_client.delete_torrents(["hash1"], delete_files=True)
        assert result is True

    def test_ensure_authenticated_when_not_authenticated(self, qbt_client, mock_session):
        """Test _ensure_authenticated when not authenticated."""
        mock_session.post(f"{qbt_client.base_url}/auth/login", text="Ok.")

        qbt_client._ensure_authenticated()
        assert qbt_client._authenticated is True

    def test_api_error_handling(self, qbt_client, mock_session):
        """Test API error handling."""
        qbt_client._authenticated = True
        mock_session.get(f"{qbt_client.base_url}/torrents/info", status_code=500)

        with pytest.raises(QBittorrentAPIError):
            qbt_client.get_torrents()


class TestConfigFunctions:
    """Test configuration loading functions."""

    def test_load_config_success(self):
        """Test successful config loading."""
        config_data = {"host": "example.com", "port": 9090, "username": "user"}

        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("os.path.exists", return_value=True):
                result = load_config("test.json")

        assert result == config_data

    def test_load_config_file_not_found(self):
        """Test config loading when file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                load_config("nonexistent.json")

    def test_create_client_from_config(self):
        """Test creating client from config."""
        config_data = {
            "host": "example.com",
            "port": 9090,
            "username": "user",
            "password": "pass",
        }

        with patch("qbt_api.load_config", return_value=config_data):
            client = create_client_from_config("test.json")

        assert client.host == "example.com"
        assert client.port == 9090
        assert client.username == "user"
