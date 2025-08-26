#!/bin/bash

# FAPS Knowledge Assistant Setup Script

echo "🚀 Setting up FAPS Knowledge Assistant..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs config

# Pull Ollama models (if Ollama is available)
echo "🤖 Setting up Ollama models..."
if command -v docker &> /dev/null; then
    echo "Docker found. You can start the system with 'docker-compose up'"
    echo "The gpt-oss:20b model will be automatically downloaded when the container starts."
else
    echo "Docker not found. Please install Docker to run the system."
fi

# Set permissions
echo "🔒 Setting permissions..."
chmod +x setup.sh

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Run 'docker-compose up' to start all services"
echo "2. Wait for Ollama to download the gpt-oss:20b model (this may take a while)"
echo "3. Open http://localhost:7860 in your browser"
echo "4. Complete the onboarding process to configure authentication"
echo ""
echo "For development without Docker:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Start ChromaDB and Ollama separately"
echo "3. Run: python app.py"