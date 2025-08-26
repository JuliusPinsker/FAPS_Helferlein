# FAPS Knowledge Assistant

A local Retrieval-Augmented Generation (RAG) system to organize and access information from FAPS NAS and web resources.

## Features

- 🔍 Search across multiple data sources with natural language
- 🔗 Get direct download links to relevant files on the NAS
- 🌐 Access information from authenticated web resources
- 🖥️ Completely local deployment for data privacy
- 🐳 Docker-based setup for easy deployment
- 🔒 Secure token-based authentication

## Data Sources

- **NAS**: `\\fapsroot.faps.uni-erlangen.de` (read-only access)
- **Wiki**: `https://wiki.faps.uni-erlangen.de/`
- **Internal FAU**: `https://www.intern.fau.de/`

## Architecture

- **Frontend**: Gradio web interface
- **RAG Engine**: LlamaIndex for document processing and retrieval
- **Vector DB**: ChromaDB for embedding storage
- **LLM**: Ollama running gpt-oss:20b
- **Data Connectors**: Custom connectors for NAS and web resources
- **Authentication**: Browser token-based access for secured resources

## Setup

1. Clone this repository
2. Run `docker-compose up`
3. Access the web interface at `http://localhost:7860`
4. Complete the onboarding process to set up authentication tokens

## Onboarding

First-time users need to complete an onboarding process:
1. Access the web interface
2. For web resources requiring authentication:
   - Login to each service in a separate browser tab
   - Generate and provide authentication tokens through the guided process
   - Tokens are securely stored in your browser's local storage

## Configuration

The application uses the following default settings:

```
# LLM Configuration
OLLAMA_MODEL=gpt-oss:20b
```

## Development

This project includes a `.devcontainer` configuration for easy development in VS Code.