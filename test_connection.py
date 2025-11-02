#!/usr/bin/env python3

"""
Test script for qBittorrent Remote Client
"""

import os
import sys

from qbt_api import QBittorrentAPI


def test_connection():
    """Test connection to qBittorrent"""
    print("Testing qBittorrent connection...")

    # Try to load config
    try:
        from qbt_api import create_client_from_config

        client = create_client_from_config()
        print("✓ Config loaded successfully")
    except FileNotFoundError:
        print("✗ Config file not found. Please create config.json")
        print("  Copy config.example.json to config.json and edit it")
        return False
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False

    # Test authentication
    try:
        if client.login():
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")
            print("  Check your username/password in config.json")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        print("  Check if qBittorrent is running and Web UI is enabled")
        return False

    # Test API call
    try:
        version = client.get_application_version()
        print(f"✓ qBittorrent version: {version}")
    except Exception as e:
        print(f"✗ API call failed: {e}")
        return False

    # Test getting torrents
    try:
        torrents = client.get_torrents()
        print(f"✓ Found {len(torrents)} torrents")
    except Exception as e:
        print(f"✗ Failed to get torrents: {e}")
        return False

    print("\n🎉 All tests passed! qBittorrent Remote Client is ready to use.")
    return True


def manual_test():
    """Manual connection test with user input"""
    print("Manual connection test")
    print("=" * 40)

    host = input("Host (localhost): ") or "localhost"
    port = input("Port (8080): ") or "8080"
    username = input("Username (admin): ") or "admin"
    password = input("Password: ")

    try:
        port = int(port)
    except ValueError:
        print("Invalid port number")
        return False

    client = QBittorrentAPI(host=host, port=port, username=username, password=password)

    print(f"\nTesting connection to {host}:{port}...")

    try:
        if client.login():
            print("✓ Connection successful!")
            version = client.get_application_version()
            print(f"✓ qBittorrent version: {version}")
            torrents = client.get_torrents()
            print(f"✓ Found {len(torrents)} torrents")
            return True
        else:
            print("✗ Authentication failed")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_test()
    else:
        test_connection()
