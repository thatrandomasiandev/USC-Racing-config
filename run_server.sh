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

# Run server
echo "✅ Starting server on http://localhost:8000"
echo "📝 API docs available at http://localhost:8000/docs"
echo ""
python main.py


