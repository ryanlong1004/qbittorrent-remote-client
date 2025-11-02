#!/usr/bin/env python3

"""
Simple example showing how to use the qBittorrent API
"""

from qbittorrent_remote_client.qbt_api import create_client_from_config


def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===")

    # Method 1: Create client from config file
    try:
        client = create_client_from_config("config.json")
        print("✅ Client created from config file")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Method 2: Create client manually
    # client = QBittorrentAPI(
    #     host="localhost",
    #     port=8080,
    #     username="admin",
    #     password="your_password"
    # )

    # Login (done automatically by the client methods)
    try:
        version = client.get_application_version()
        print(f"📱 qBittorrent version: {version}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Get all torrents
    try:
        torrents = client.get_torrents()
        print(f"📊 Total torrents: {len(torrents)}")

        if torrents:
            print("\n📋 First few torrents:")
            for i, torrent in enumerate(torrents[:3]):
                print(f"  {i + 1}. {torrent['name'][:50]}...")
                print(f"     State: {torrent['state']}")
                print(f"     Progress: {torrent['progress'] * 100:.1f}%")
                print(f"     Size: {format_size(torrent['size'])}")
                print()

    except Exception as e:
        print(f"❌ Failed to get torrents: {e}")

    # Get transfer stats
    try:
        stats = client.get_global_transfer_info()
        print("📈 Transfer Statistics:")
        print(f"  Download speed: {format_size(stats['dl_info_speed'])}/s")
        print(f"  Upload speed: {format_size(stats['up_info_speed'])}/s")
        print(f"  Downloaded this session: {format_size(stats['dl_info_data'])}")
        print(f"  Uploaded this session: {format_size(stats['up_info_data'])}")
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")


def example_add_torrent():
    """Example of adding a torrent"""
    print("\n=== Add Torrent Example ===")

    # Example magnet link (Ubuntu ISO)
    magnet_link = "magnet:?xt=urn:btih:dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c" "&dn=ubuntu-20.04.3-desktop-amd64.iso"

    try:
        client = create_client_from_config("config.json")

        # Add torrent in paused state
        success = client.add_torrent_url(magnet_link, paused=True)

        if success:
            print("✅ Torrent added successfully (paused)")
            print("   You can resume it using the client or qBittorrent UI")
        else:
            print("❌ Failed to add torrent")

    except Exception as e:
        print(f"❌ Error: {e}")


def format_size(bytes_size):
    """Format bytes to human readable size"""
    if bytes_size == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


if __name__ == "__main__":
    example_basic_usage()

    # Uncomment to test adding a torrent
    # example_add_torrent()
