#!/bin/bash

echo "🚀 Setting up qBittorrent Remote Client"
echo "======================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create config file if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "⚙️  Creating config file..."
    cp config.example.json config.json
    echo "✅ Config file created (config.json)"
    echo "📝 Please edit config.json with your qBittorrent details"
else
    echo "✅ Config file already exists"
fi

# Make scripts executable
chmod +x qbt_client.py
chmod +x test_connection.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your qBittorrent Web UI details"
echo "2. Test the connection: python3 test_connection.py"
echo "3. Start using the client: python3 qbt_client.py --help"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"