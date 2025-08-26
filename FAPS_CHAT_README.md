# FAPS Chat 🏛️

A secure, local ChatGPT-like interface for FAPS (Friedrich-Alexander-Universität) sensitive documents. Built with the Agno framework and powered by Ollama for complete data privacy.

## Features

- 🔒 **Local Processing**: All data processing happens locally using Ollama
- 📄 **Document Ingestion**: Support for FAPS document sources
- 🛡️ **Data Privacy**: No external API calls, complete data security
- 🤖 **AI-Powered**: Uses advanced language models for document Q&A
- 🏛️ **FAPS Branding**: Customized interface for FAPS users

## Quick Start

### Prerequisites

- Docker and Docker Compose
- **Ollama running locally** (install from https://ollama.ai)
- At least 16GB RAM (for larger models)
- 50GB+ free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JuliusPinsker/FAPS_Helferlein.git
   cd FAPS_Helferlein
   ```

2. **Ensure Ollama is running locally**
   ```bash
   # Install Ollama if not already installed
   # Visit https://ollama.ai for installation instructions
   
   # Start Ollama (if not already running)
   ollama serve
   ```

3. **Setup required models**
   ```bash
   ./setup-models.sh
   ```

4. **Start FAPS Chat**
   ```bash
   docker compose up
   ```

5. **Access the interface**
   - FAPS Chat: http://localhost:8501

### Models

FAPS Chat uses the following Ollama models:

- **gpt-oss:20b**: Main chat model for conversations
- **nomic-embed-text**: Embedding model for document search
- **Additional models**: llama3.1, codestral, qwen2.5

## Usage

1. **Select Model**: Choose from available Ollama models in the sidebar
2. **Chat Interface**: Ask questions about your documents
3. **Document Sources**: Currently supports local document upload
4. **Secure Processing**: All processing happens locally

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   FAPS Chat     │    │   Ollama     │    │   Document      │
│   (Streamlit)   │◄──►│   (External) │◄──►│   Storage       │
│   Port: 8501    │    │   Port: 11434│    │   Local Files   │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## Configuration

### Environment Variables

- `OLLAMA_HOST`: Ollama service endpoint (default: `host.docker.internal:11434` for external Ollama)
- `AGNO_TELEMETRY`: Disable telemetry (set to `false`)

### Model Configuration

Edit `cookbook/examples/streamlit_apps/universal_agent_interface/utils.py` to modify available models.

## Data Sources (Planned)

- ✅ Local document upload
- ⏳ FAU Internal Portal
- ⏳ FAPS Wiki  
- ⏳ IDM Portal
- ⏳ Network Drives

## Development

### Local Development

1. **Install dependencies**
   ```bash
   cd cookbook/examples/streamlit_apps/universal_agent_interface
   pip install -r requirements.txt
   ```

2. **Ensure Ollama is running locally**
   ```bash
   ollama serve
   ```

3. **Run Streamlit app**
   ```bash
   streamlit run app.py
   ```

### Adding New Models

1. Pull the model with Ollama:
   ```bash
   ollama pull model-name
   ```

2. Add to the model options in `utils.py`:
   ```python
   model_options = {
       "model-name": "ollama:model-name",
       # ... other models
   }
   ```

## Security

- ✅ Local processing only
- ✅ No external API calls
- ✅ Data never leaves your infrastructure
- ✅ Configurable access controls

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running locally
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### Model Download Issues

```bash
# Check available models
ollama list

# Re-run setup script
./setup-models.sh
```

### Memory Issues

- Ensure sufficient RAM for chosen models
- Use smaller models like `llama3.1:8b` if needed
- Monitor resource usage with `docker stats`

## Support

For technical support and questions:

- Create issues in this repository
- Check the Agno documentation: https://docs.agno.com
- FAPS-specific questions: Contact your system administrator

## License

This project inherits the license from the Agno framework.