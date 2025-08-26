#!/bin/bash

# FAPS Chat Quick Start Script
echo "🏛️ Starting FAPS Chat..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p ./data

echo "📦 Starting services with Docker Compose..."

# Start services
docker compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Access FAPS Chat at: http://localhost:8501"
    echo "🔧 Ollama API at: http://localhost:11434"
    echo ""
    echo "📋 To view logs: docker compose logs -f"
    echo "🛑 To stop: docker compose down"
    echo ""
    echo "📖 Setup models with: ./setup-models.sh"
else
    echo "❌ Failed to start services. Check logs with: docker compose logs"
    exit 1
fi