#!/bin/bash

# Script to pull the required Ollama models

echo "🤖 Pulling Ollama models for FAPS Knowledge Assistant..."

# Pull the main LLM model
echo "Pulling gpt-oss:20b model (this may take a while)..."
docker-compose exec ollama ollama pull gpt-oss:20b

# Pull the embedding model
echo "Pulling nomic-embed-text model..."
docker-compose exec ollama ollama pull nomic-embed-text

echo "✅ Model download completed!"
echo "The system is now ready to use."