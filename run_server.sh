#!/bin/bash

# Quick start script for USC Racing server on localhost:8000

cd "$(dirname "$0")"

echo "🚀 Starting USC Racing server on localhost:8000..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
cd backend
pip install -q -r requirements.txt

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

# Run server
echo "✅ Starting server..."
echo ""
echo "🌐 Network Access:"
echo "   Local:    http://localhost:8000"
echo "   Network:  http://${LOCAL_IP:-YOUR_IP}:8000"
echo ""
echo "📝 API docs: http://${LOCAL_IP:-localhost}:8000/docs"
echo ""
echo "💡 Connect from other devices on your network using the Network URL above"
echo ""
python main.py


