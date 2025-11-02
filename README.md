# qBittorrent Remote Client

A Python-based command-line tool for remotely managing qBittorrent instances via the Web API.

## Features

- Connect to remote qBittorrent instances
- List torrents with detailed information
- Add torrents from magnet links or torrent files
- Pause, resume, and delete torrents
- Get transfer statistics
- Configurable connection settings

## Setup

1. Enable Web UI in qBittorrent:

   - Go to Tools → Preferences → Web UI
   - Check "Web User Interface"
   - Set username/password
   - Note the port (default: 8080)

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure connection:
   ```bash
   cp config.example.json config.json
   # Edit config.json with your qBittorrent details
   ```

## Usage

```bash
# List all torrents
python qbt_client.py list

# Add torrent from magnet link
python qbt_client.py add "magnet:?xt=urn:btih:..."

# Add torrent from file
python qbt_client.py add /path/to/file.torrent

# Pause torrents
python qbt_client.py pause <hash1> <hash2>

# Resume torrents
python qbt_client.py resume <hash1> <hash2>

# Delete torrents
python qbt_client.py delete <hash1> --delete-files

# Delete all torrents with specific status (with preview)
python qbt_client.py delete-by-status error --dry-run

# Delete all torrents with specific status
python qbt_client.py delete-by-status missingFiles --delete-files

# Get statistics
python qbt_client.py stats

# Interactive mode
python qbt_client.py interactive
```

## Configuration

Edit `config.json` to match your qBittorrent setup:

```json
{
  "host": "localhost",
  "port": 8080,
  "username": "admin",
  "password": "your_password",
  "use_https": false
}
```
