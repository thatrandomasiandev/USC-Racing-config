#!/bin/bash

# USC Racing Deployment Script
set -e

echo "🚀 Starting USC Racing deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update it with your configuration."
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Build and start containers
echo "📦 Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

echo "✅ Deployment complete!"
echo ""
echo "📊 Container status:"
docker-compose ps

echo ""
echo "🌐 Service:"
echo "   Application: http://localhost:8000"
echo "   API:         http://localhost:8000/api"
echo "   WebSocket:   ws://localhost:8000/ws"
echo ""
echo "📝 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Update:       ./deploy.sh"


