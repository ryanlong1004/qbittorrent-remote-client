"""Tests for qbt_client.py"""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from qbt_api import QBittorrentError
from qbt_client import cli, format_eta, format_size, format_speed


class TestUtilityFunctions:
    """Test utility functions."""

    def test_format_size(self):
        """Test format_size function."""
        assert format_size(0) == "0 B"
        assert format_size(1024) == "1.0 KB"
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_format_speed(self):
        """Test format_speed function."""
        assert format_speed(1024) == "1.0 KB/s"
        assert format_speed(1024 * 1024) == "1.0 MB/s"

    def test_format_eta(self):
        """Test format_eta function."""
        assert format_eta(8640000) == "∞"
        assert format_eta(0) == "0s"
        assert format_eta(-10) == "0s"
        assert format_eta(60) == "1m"
        assert format_eta(3600) == "1h"
        assert format_eta(86400) == "1d"
        assert format_eta(90061) == "1d 1h 1m 1s"


class TestCLICommands:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test method."""
        self.runner = CliRunner()

    @patch("qbt_client.create_client_from_config")
    def test_list_command_success(self, mock_create_client, sample_torrents):
        """Test list command success."""
        mock_client = Mock()
        mock_client.get_torrents.return_value = sample_torrents
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        # Check for parts of the torrent name due to table wrapping
        assert "Test" in result.output
        assert "Torrent" in result.output
        # State might be truncated in the table
        assert "downloa" in result.output  # truncated "downloading"

    @patch("qbt_client.create_client_from_config")
    def test_list_command_error(self, mock_create_client):
        """Test list command with error."""
        mock_client = Mock()
        mock_client.get_torrents.side_effect = QBittorrentError("Connection failed")
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Error listing torrents" in result.output

    @patch("qbt_client.create_client_from_config")
    def test_list_command_with_filters(self, mock_create_client, sample_torrents):
        """Test list command with filters."""
        mock_client = Mock()
        mock_client.get_torrents.return_value = sample_torrents
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["list", "--filter", "downloading", "--category", "Movies"])

        assert result.exit_code == 0
        mock_client.get_torrents.assert_called_with(filter="downloading", category="Movies", sort="name", reverse=False)

    @patch("qbt_client.create_client_from_config")
    def test_stats_command(self, mock_create_client, sample_transfer_info):
        """Test stats command."""
        mock_client = Mock()
        mock_client.get_global_transfer_info.return_value = sample_transfer_info
        mock_client.get_application_version.return_value = "v4.6.3"
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        assert "v4.6.3" in result.output
        assert "1.0 MB/s" in result.output

    @patch("qbt_client.create_client_from_config")
    def test_status_command(
        self,
        mock_create_client,
        sample_torrents,
        sample_transfer_info,
        sample_categories,
    ):
        """Test status command."""
        mock_client = Mock()
        mock_client.get_torrents.return_value = sample_torrents
        mock_client.get_global_transfer_info.return_value = sample_transfer_info
        mock_client.get_application_version.return_value = "v4.6.3"
        mock_client.get_categories.return_value = sample_categories
        mock_client.host = "test-host"
        mock_client.port = 8080
        mock_client.base_url = "http://test-host:8080"
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["status"])

        assert result.exit_code == 0
        assert "qBittorrent Status Dashboard" in result.output
        assert "Server Information" in result.output
        assert "v4.6.3" in result.output

    @patch("qbt_client.create_client_from_config")
    def test_pause_command(self, mock_create_client):
        """Test pause command."""
        mock_client = Mock()
        mock_client.pause_torrents.return_value = True
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["pause", "abc123"])

        assert result.exit_code == 0
        mock_client.pause_torrents.assert_called_with(["abc123"])

    @patch("qbt_client.create_client_from_config")
    def test_resume_command(self, mock_create_client):
        """Test resume command."""
        mock_client = Mock()
        mock_client.resume_torrents.return_value = True
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["resume", "abc123"])

        assert result.exit_code == 0
        mock_client.resume_torrents.assert_called_with(["abc123"])

    @patch("qbt_client.create_client_from_config")
    def test_delete_command(self, mock_create_client):
        """Test delete command."""
        mock_client = Mock()
        mock_client.delete_torrents.return_value = True
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["delete", "abc123"], input="y\n")

        assert result.exit_code == 0
        mock_client.delete_torrents.assert_called_with(["abc123"], delete_files=False)

    @patch("qbt_client.create_client_from_config")
    def test_delete_command_with_files(self, mock_create_client):
        """Test delete command with files."""
        mock_client = Mock()
        mock_client.delete_torrents.return_value = True
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["delete", "--delete-files", "abc123"], input="y\n")

        assert result.exit_code == 0
        mock_client.delete_torrents.assert_called_with(["abc123"], delete_files=True)

    @patch("qbt_client.create_client_from_config")
    def test_delete_by_status_dry_run(self, mock_create_client, sample_torrents):
        """Test delete-by-status with dry run."""
        mock_client = Mock()
        mock_client.get_torrents.return_value = [sample_torrents[2]]  # error torrent
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["delete-by-status", "--dry-run", "error"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "Test Torrent 3" in result.output

    @patch("qbt_client.create_client_from_config")
    def test_delete_by_status_with_confirmation(self, mock_create_client, sample_torrents):
        """Test delete-by-status with user confirmation."""
        mock_client = Mock()
        mock_client.get_torrents.return_value = [sample_torrents[2]]  # error torrent
        mock_client.delete_torrents.return_value = True
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["delete-by-status", "--yes", "error"])

        assert result.exit_code == 0
        mock_client.delete_torrents.assert_called()

    @patch("qbt_client.create_client_from_config")
    def test_add_command_url(self, mock_create_client):
        """Test add command with URL."""
        mock_client = Mock()
        mock_client.add_torrent_url.return_value = True
        mock_create_client.return_value = mock_client

        test_url = "magnet:?xt=urn:btih:test"
        result = self.runner.invoke(cli, ["add", test_url])

        assert result.exit_code == 0
        mock_client.add_torrent_url.assert_called()

    @patch("qbt_client.create_client_from_config")
    def test_add_command_with_valid_category(self, mock_create_client):
        """Test add command with valid category."""
        mock_client = Mock()
        mock_client.get_categories.return_value = {
            "Films": {"savePath": "/movies"},
            "Music": {"savePath": "/music"},
        }
        mock_client.add_torrent_url.return_value = True
        mock_create_client.return_value = mock_client

        test_url = "magnet:?xt=urn:btih:test"
        result = self.runner.invoke(cli, ["add", test_url, "--category", "Films"])

        assert result.exit_code == 0
        assert "to category 'Films'" in result.output
        mock_client.add_torrent_url.assert_called_with(test_url, save_path="", category="Films", paused=False)

    @patch("qbt_client.create_client_from_config")
    def test_add_command_with_invalid_category(self, mock_create_client):
        """Test add command with invalid category."""
        mock_client = Mock()
        mock_client.get_categories.return_value = {
            "Films": {"savePath": "/movies"},
            "Music": {"savePath": "/music"},
        }
        mock_create_client.return_value = mock_client

        test_url = "magnet:?xt=urn:btih:test"
        result = self.runner.invoke(cli, ["add", test_url, "--category", "InvalidCategory"])

        assert result.exit_code == 0
        assert "Invalid category 'InvalidCategory'" in result.output
        assert "Available categories:" in result.output
        assert "Films" in result.output
        assert "Music" in result.output
        mock_client.add_torrent_url.assert_not_called()

    @patch("qbt_client.create_client_from_config")
    def test_add_command_category_validation_error(self, mock_create_client):
        """Test add command when category validation fails."""
        mock_client = Mock()
        mock_client.get_categories.side_effect = QBittorrentError("Cannot get categories")
        mock_client.add_torrent_url.return_value = True
        mock_create_client.return_value = mock_client

        test_url = "magnet:?xt=urn:btih:test"
        result = self.runner.invoke(cli, ["add", test_url, "--category", "Films"])

        assert result.exit_code == 0
        assert "Warning: Could not validate category" in result.output
        mock_client.add_torrent_url.assert_called_with(test_url, save_path="", category="Films", paused=False)

    @patch("qbt_client.create_client_from_config")
    def test_categories_command_success(self, mock_create_client):
        """Test categories command success."""
        mock_client = Mock()
        mock_client.get_categories.return_value = {
            "Films": {"savePath": "/movies"},
            "Music": {"savePath": "/music"},
            "Series": {"savePath": ""},
        }
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["categories"])

        assert result.exit_code == 0
        assert "Available Categories:" in result.output
        assert "Films" in result.output
        assert "Music" in result.output
        assert "Series" in result.output
        assert "/movies" in result.output
        assert "/music" in result.output
        assert "Default" in result.output  # For empty save path

    @patch("qbt_client.create_client_from_config")
    def test_categories_command_no_categories(self, mock_create_client):
        """Test categories command when no categories exist."""
        mock_client = Mock()
        mock_client.get_categories.return_value = {}
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["categories"])

        assert result.exit_code == 0
        assert "No categories found" in result.output

    @patch("qbt_client.create_client_from_config")
    def test_categories_command_error(self, mock_create_client):
        """Test categories command with error."""
        mock_client = Mock()
        mock_client.get_categories.side_effect = QBittorrentError("Connection failed")
        mock_create_client.return_value = mock_client

        result = self.runner.invoke(cli, ["categories"])

        assert result.exit_code == 0
        assert "Error getting categories" in result.output

    def test_config_file_option(self):
        """Test custom config file option."""
        with patch("qbt_client.create_client_from_config") as mock_create:
            mock_create.return_value = Mock()

            result = self.runner.invoke(cli, ["-c", "custom.json", "list"])

            mock_create.assert_called_with("custom.json")
