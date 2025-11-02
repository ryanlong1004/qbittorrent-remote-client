# qBittorrent Remote Client

[![CI/CD Pipeline](https://github.com/ryanlong1004/qbittorrent-remote-client/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ryanlong1004/qbittorrent-remote-client/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/ryanlong1004/qbittorrent-remote-client/branch/main/graph/badge.svg)](https://codecov.io/gh/ryanlong1004/qbittorrent-remote-client)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![GitHub issues](https://img.shields.io/github/issues/ryanlong1004/qbittorrent-remote-client)](https://github.com/ryanlong1004/qbittorrent-remote-client/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/ryanlong1004/qbittorrent-remote-client)](https://github.com/ryanlong1004/qbittorrent-remote-client/pulls)

A Python-based command-line tool for remotely managing qBittorrent instances via the Web API.

## Project Status

🚀 **Active Development** - This project is actively maintained with comprehensive CI/CD pipeline

- ✅ **Tests**: 34/37 passing (92% pass rate) with 72% code coverage
- ✅ **CI/CD**: Multi-Python testing (3.9-3.12) with automated quality checks
- ✅ **Security**: Automated vulnerability scanning with Bandit
- ✅ **Code Quality**: Black formatting, isort imports, mypy type checking
- ✅ **Branch Protection**: Main branch protected with required status checks
- ✅ **Documentation**: Comprehensive README with usage examples

## Features

- 🖥️ **Comprehensive Status Dashboard** - Real-time monitoring with rich formatted display
- 📋 **List and Filter Torrents** - View torrents with detailed information and filtering
- ➕ **Add Torrents** - From magnet links, URLs, or torrent files
- ⏸️ **Control Torrents** - Pause, resume, and delete operations
- 🗑️ **Bulk Operations** - Delete torrents by status (error, missingFiles, etc.)
- 📊 **Transfer Statistics** - Global transfer info and session statistics
- 🔄 **Auto-refresh Mode** - Real-time monitoring with configurable refresh intervals
- 🎯 **Interactive Mode** - Interactive shell for quick operations
- ⚡ **Automation Ready** - CLI flags for scripting and automation

## Status Dashboard

Get a comprehensive overview of your qBittorrent instance:

```bash
# One-time status check
python qbt_client.py status

# Auto-refresh every 5 seconds for monitoring
python qbt_client.py status --refresh 5
```

The dashboard shows:

- 🖥️ Server information (version, connection, protocol)
- 📊 Transfer statistics (speeds, session/all-time totals)
- 📚 Torrent overview (counts, sizes, active transfers)
- 📈 Status breakdown with color-coded percentages
- 🚀 Most active torrents with progress and speeds

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

## Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/ryanlong1004/qbittorrent-remote-client.git
cd qbittorrent-remote-client

# Set up development environment
make dev-setup

# Run tests
make test

# Run tests with coverage
make test-cov

# Run all CI checks locally
make ci
```

## Testing

This project includes a comprehensive test suite with:

- **Unit Tests** - Complete coverage of API and CLI functionality
- **Integration Tests** - End-to-end testing scenarios
- **Code Quality** - Automated linting, formatting, and security checks
- **CI/CD Pipeline** - GitHub Actions workflow for continuous testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/test_qbt_api.py

# Run tests matching pattern
pytest -k "test_status"
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
