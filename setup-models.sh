#!/bin/bash

# FAPS Chat Setup Script
# This script sets up the required Ollama models for FAPS Chat

echo "🏛️ Setting up FAPS Chat with Ollama models..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

echo "📦 Pulling required models..."

# Pull the main chat model
echo "Pulling gpt-oss:20b (this may take a while)..."
ollama pull gpt-oss:20b

# Pull the embedding model  
echo "Pulling nomic-embed-text..."
ollama pull nomic-embed-text

# Pull some additional useful models
echo "Pulling additional models..."
ollama pull llama3.1:8b
ollama pull llama3.1
ollama pull codestral
ollama pull qwen2.5

echo "✅ Model setup complete!"
echo ""
echo "🚀 You can now start FAPS Chat with:"
echo "   docker compose up"
echo ""
echo "🌐 Access FAPS Chat at: http://localhost:8501"