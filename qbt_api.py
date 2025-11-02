import requests
import json
import os
from typing import Dict, List, Union


class QBittorrentAPI:
    """
    A Python wrapper for the qBittorrent Web API.

    Provides methods to interact with a remote qBittorrent instance
    via HTTP requests to the Web API endpoints.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        username: str = "admin",
        password: str = "",
        use_https: bool = False,
        timeout: int = 30,
        verify_ssl: bool = True,
        base_path: str = "",
    ):
        """
        Initialize the qBittorrent API client.

        Args:
            host: qBittorrent host address
            port: qBittorrent Web UI port
            username: Web UI username
            password: Web UI password
            use_https: Whether to use HTTPS
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            base_path: Base path for the qBittorrent Web UI (e.g., "/qbittorrent")
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        protocol = "https" if use_https else "http"
        # Ensure base_path starts with / if provided and doesn't end with /
        if base_path and not base_path.startswith("/"):
            base_path = "/" + base_path
        if base_path.endswith("/"):
            base_path = base_path.rstrip("/")

        self.base_url = f"{protocol}://{host}:{port}{base_path}/api/v2"

        self.session = requests.Session()
        self.session.verify = verify_ssl

        self._authenticated = False

    def login(self) -> bool:
        """
        Authenticate with the qBittorrent Web API.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                data={"username": self.username, "password": self.password},
                timeout=self.timeout,
            )

            if response.text == "Ok.":
                self._authenticated = True
                return True
            else:
                self._authenticated = False
                return False

        except requests.RequestException as e:
            print(f"Login failed: {e}")
            self._authenticated = False
            return False

    def logout(self) -> bool:
        """Logout from the qBittorrent Web API."""
        try:
            response = self.session.post(f"{self.base_url}/auth/logout", timeout=self.timeout)
            self._authenticated = False
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _ensure_authenticated(self):
        """Ensure we're authenticated before making API calls."""
        if not self._authenticated:
            if not self.login():
                raise Exception("Authentication failed. Please check your credentials.")

    def get_torrents(
        self,
        filter_type: str = "all",
        category: str = "",
        sort: str = "name",
        reverse: bool = False,
    ) -> List[Dict]:
        """
        Get list of torrents.

        Args:
            filter_type: Filter type (all, downloading, seeding, completed, paused, etc.)
            category: Filter by category
            sort: Sort field
            reverse: Reverse sort order

        Returns:
            List of torrent dictionaries
        """
        self._ensure_authenticated()

        params = {
            "filter": filter_type,
            "category": category,
            "sort": sort,
            "reverse": reverse,
        }

        try:
            response = self.session.get(f"{self.base_url}/torrents/info", params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get torrents: {e}")

    def add_torrent_url(self, url: str, save_path: str = "", category: str = "", paused: bool = False) -> bool:
        """
        Add torrent from URL (magnet link or HTTP).

        Args:
            url: Magnet link or torrent file URL
            save_path: Download path
            category: Torrent category
            paused: Add in paused state

        Returns:
            True if successful
        """
        self._ensure_authenticated()

        data = {
            "urls": url,
            "savepath": save_path,
            "category": category,
            "paused": paused,
        }

        try:
            response = self.session.post(f"{self.base_url}/torrents/add", data=data, timeout=self.timeout)
            return response.text == "Ok."
        except requests.RequestException as e:
            raise Exception(f"Failed to add torrent: {e}")

    def add_torrent_file(
        self,
        file_path: str,
        save_path: str = "",
        category: str = "",
        paused: bool = False,
    ) -> bool:
        """
        Add torrent from file.

        Args:
            file_path: Path to torrent file
            save_path: Download path
            category: Torrent category
            paused: Add in paused state

        Returns:
            True if successful
        """
        self._ensure_authenticated()

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Torrent file not found: {file_path}")

        data = {"savepath": save_path, "category": category, "paused": paused}

        try:
            with open(file_path, "rb") as f:
                files = {"torrents": f}
                response = self.session.post(
                    f"{self.base_url}/torrents/add",
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
            return response.text == "Ok."
        except requests.RequestException as e:
            raise Exception(f"Failed to add torrent file: {e}")

    def pause_torrents(self, hashes: Union[str, List[str]]) -> bool:
        """Pause torrents by hash."""
        return self._torrent_action("pause", hashes)

    def resume_torrents(self, hashes: Union[str, List[str]]) -> bool:
        """Resume torrents by hash."""
        return self._torrent_action("resume", hashes)

    def delete_torrents(self, hashes: Union[str, List[str]], delete_files: bool = False) -> bool:
        """Delete torrents by hash."""
        self._ensure_authenticated()

        if isinstance(hashes, str):
            hashes = [hashes]

        data = {"hashes": "|".join(hashes), "deleteFiles": delete_files}

        try:
            response = self.session.post(f"{self.base_url}/torrents/delete", data=data, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException as e:
            raise Exception(f"Failed to delete torrents: {e}")

    def _torrent_action(self, action: str, hashes: Union[str, List[str]]) -> bool:
        """Perform action on torrents."""
        self._ensure_authenticated()

        if isinstance(hashes, str):
            hashes = [hashes]

        data = {"hashes": "|".join(hashes)}

        try:
            response = self.session.post(f"{self.base_url}/torrents/{action}", data=data, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException as e:
            raise Exception(f"Failed to {action} torrents: {e}")

    def get_global_transfer_info(self) -> Dict:
        """Get global transfer information."""
        self._ensure_authenticated()

        try:
            response = self.session.get(f"{self.base_url}/transfer/info", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get transfer info: {e}")

    def get_application_version(self) -> str:
        """Get qBittorrent application version."""
        try:
            response = self.session.get(f"{self.base_url}/app/version", timeout=self.timeout)
            response.raise_for_status()
            return response.text.strip('"')
        except requests.RequestException as e:
            raise Exception(f"Failed to get version: {e}")


def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_client_from_config(config_path: str = "config.json") -> QBittorrentAPI:
    """Create QBittorrentAPI client from config file."""
    config = load_config(config_path)
    return QBittorrentAPI(**config)
