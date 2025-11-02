#!/bin/bash

# qBittorrent Missing Files Cleanup Script
# Runs daily to remove torrents with missing files

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment and run cleanup
.venv/bin/python qbt_client.py delete-by-status missingFiles --yes

# Log the execution
echo "$(date): Cleaned up missing files torrents" >> cleanup.log