"""
Configuration management for FAPS Knowledge Assistant
"""
import os
from typing import Optional

try:
    from pydantic import BaseSettings
    HAS_PYDANTIC = True
except ImportError:
    # Fallback for development without pydantic
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
            env_file = ".env"
            case_sensitive = False
    HAS_PYDANTIC = False


class Settings(BaseSettings):
    # ChromaDB settings
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    
    # Ollama settings
    ollama_host: str = "ollama"
    ollama_port: int = 11434
    ollama_model: str = "gpt-oss:20b"
    
    # NAS settings
    nas_host: str = "fapsroot.faps.uni-erlangen.de"
    nas_share_path: str = "/"
    
    # Web scraping settings
    wiki_url: str = "https://wiki.faps.uni-erlangen.de/"
    intern_fau_url: str = "https://www.intern.fau.de/"
    
    # Application settings
    default_language: str = "de"
    log_level: str = "INFO"
    data_dir: str = "./data"
    config_dir: str = "./config"
    
    # Gradio settings
    gradio_server_name: str = "0.0.0.0"
    gradio_server_port: int = 7860
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self):
        # Load from environment or use defaults
        self.chroma_host = os.getenv("CHROMA_HOST", "chromadb")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        self.ollama_host = os.getenv("OLLAMA_HOST", "ollama")
        self.ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        self.nas_host = os.getenv("NAS_HOST", "fapsroot.faps.uni-erlangen.de")
        self.nas_share_path = os.getenv("NAS_SHARE_PATH", "/")
        self.wiki_url = os.getenv("WIKI_URL", "https://wiki.faps.uni-erlangen.de/")
        self.intern_fau_url = os.getenv("INTERN_FAU_URL", "https://www.intern.fau.de/")
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "de")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.data_dir = os.getenv("DATA_DIR", "./data")
        self.config_dir = os.getenv("CONFIG_DIR", "./config")
        self.gradio_server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
        self.gradio_server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))


settings = Settings()