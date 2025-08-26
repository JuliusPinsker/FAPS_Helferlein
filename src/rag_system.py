"""
RAG (Retrieval-Augmented Generation) system using LlamaIndex and ChromaDB
"""
import logging
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import chromadb

from src.config import settings
from src.nas_connector import NASConnector
from src.web_scraper import web_scraper

logger = logging.getLogger(__name__)


class RAGSystem:
    def __init__(self):
        self.chroma_client = None
        self.vector_store = None
        self.index = None
        self.query_engine = None
        self.nas_connector = NASConnector()
        self._setup_llm()
        self._setup_vector_store()
        
    def _setup_llm(self):
        """Setup Ollama LLM and embeddings"""
        try:
            ollama_url = f"http://{settings.ollama_host}:{settings.ollama_port}"
            
            # Setup LLM
            llm = Ollama(
                model=settings.ollama_model,
                base_url=ollama_url,
                request_timeout=60.0
            )
            
            # Setup embeddings (using a smaller model for embeddings)
            embed_model = OllamaEmbedding(
                model_name="nomic-embed-text",
                base_url=ollama_url,
                ollama_additional_kwargs={"mirostat": 0},
            )
            
            # Configure global settings
            Settings.llm = llm
            Settings.embed_model = embed_model
            Settings.chunk_size = 1024
            Settings.chunk_overlap = 20
            
            logger.info("LLM and embeddings configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup LLM: {e}")
            # Use mock implementations for development
            self._setup_mock_llm()
    
    def _setup_mock_llm(self):
        """Setup mock LLM for development when Ollama is not available"""
        logger.warning("Using mock LLM - Ollama not available")
        
        from llama_index.core.base.llms.base import BaseLLM
        from llama_index.core.base.embeddings.base import BaseEmbedding
        from llama_index.core.llms.callbacks import llm_completion_callback
        from typing import Any, List
        
        class MockLLM(BaseLLM):
            def complete(self, prompt, **kwargs):
                from llama_index.core.base.llms.types import CompletionResponse
                return CompletionResponse(text=f"Mock response for: {prompt[:100]}...")
            
            def chat(self, messages, **kwargs):
                from llama_index.core.base.llms.types import ChatResponse, ChatMessage
                return ChatResponse(message=ChatMessage(content="Mock chat response about FAPS knowledge system."))
            
            @property
            def metadata(self):
                return {"model_name": "mock"}
        
        class MockEmbedding(BaseEmbedding):
            def _get_text_embedding(self, text: str) -> List[float]:
                # Return a simple mock embedding
                return [0.1] * 384
            
            def _get_query_embedding(self, query: str) -> List[float]:
                return [0.1] * 384
                
            async def _aget_text_embedding(self, text: str) -> List[float]:
                return self._get_text_embedding(text)
        
        Settings.llm = MockLLM()
        Settings.embed_model = MockEmbedding()
    
    def _setup_vector_store(self):
        """Setup ChromaDB vector store"""
        try:
            # Initialize ChromaDB client
            chroma_url = f"http://{settings.chroma_host}:{settings.chroma_port}"
            self.chroma_client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
            
            # Create or get collection
            collection_name = "faps_knowledge"
            try:
                collection = self.chroma_client.create_collection(collection_name)
                logger.info(f"Created new ChromaDB collection: {collection_name}")
            except Exception:
                collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"Using existing ChromaDB collection: {collection_name}")
            
            # Setup vector store
            self.vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Create or load index
            self.index = VectorStoreIndex.from_vector_store(self.vector_store)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            logger.info("Vector store configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup vector store: {e}")
            # Create a simple in-memory index for development
            self._setup_mock_vector_store()
    
    def _setup_mock_vector_store(self):
        """Setup mock vector store for development"""
        logger.warning("Using mock vector store - ChromaDB not available")
        
        # Create simple in-memory index with mock documents
        mock_documents = [
            Document(
                text="FAPS ist der Lehrstuhl für Fertigungsautomatisierung und Produktionssystematik.",
                metadata={"source": "mock", "type": "info"}
            ),
            Document(
                text="Der Lehrstuhl wurde 1975 gegründet und beschäftigt sich mit Automatisierung.",
                metadata={"source": "mock", "type": "info"}
            )
        ]
        
        try:
            self.index = VectorStoreIndex.from_documents(mock_documents)
            self.query_engine = self.index.as_query_engine()
            logger.info("Mock vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to create mock vector store: {e}")
            # Create minimal fallback
            self.index = None
            self.query_engine = None
    
    def index_documents(self, force_refresh: bool = False) -> bool:
        """
        Index all documents from configured sources
        
        Args:
            force_refresh: Whether to force re-indexing of all documents
            
        Returns:
            bool: Success status
        """
        try:
            # If no query engine is available, skip indexing
            if not self.query_engine:
                logger.warning("No query engine available - skipping document indexing")
                return False
                
            documents = []
            
            # Index NAS files
            nas_files = self.nas_connector.list_files()
            for file_info in nas_files:
                content = self.nas_connector.get_file_content(file_info["path"])
                if content:
                    doc = Document(
                        text=content,
                        metadata={
                            "source": "nas",
                            "file_path": file_info["path"],
                            "file_name": file_info["name"],
                            "file_type": file_info["type"],
                            "download_url": file_info["download_url"],
                            "modified": file_info["modified"]
                        }
                    )
                    documents.append(doc)
            
            # Index web content
            web_content = web_scraper.get_all_content()
            for page in web_content:
                doc = Document(
                    text=page["content"],
                    metadata={
                        "source": "web",
                        "title": page["title"],
                        "url": page["url"],
                        "type": page["type"],
                        "last_modified": page["last_modified"]
                    }
                )
                documents.append(doc)
            
            if documents:
                # Add documents to index
                if hasattr(self.index, 'insert'):
                    for doc in documents:
                        self.index.insert(doc)
                else:
                    # Rebuild index with new documents
                    self.index = VectorStoreIndex.from_documents(documents, vector_store=self.vector_store)
                    self.query_engine = self.index.as_query_engine(
                        similarity_top_k=5,
                        response_mode="compact"
                    )
                
                logger.info(f"Indexed {len(documents)} documents successfully")
                return True
            else:
                logger.warning("No documents found to index")
                return False
                
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            return False
    
    def query(self, question: str, language: str = "de") -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            language: Response language (de/en)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            if not self.query_engine:
                return {
                    "response": "System not initialized",
                    "sources": [],
                    "error": "RAG system not properly initialized"
                }
            
            # Add language instruction to the query
            if language == "de":
                enhanced_query = f"Beantworte die folgende Frage auf Deutsch: {question}"
            else:
                enhanced_query = f"Answer the following question in English: {question}"
            
            # Execute query
            response = self.query_engine.query(enhanced_query)
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    source_info = {
                        "content": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                        "metadata": node.metadata,
                        "score": getattr(node, 'score', 0.0)
                    }
                    sources.append(source_info)
            
            return {
                "response": str(response),
                "sources": sources,
                "query": question,
                "language": language,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "response": "Es ist ein Fehler aufgetreten." if language == "de" else "An error occurred.",
                "sources": [],
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the RAG system components"""
        status = {
            "vector_store": bool(self.vector_store),
            "index": bool(self.index),
            "query_engine": bool(self.query_engine),
            "nas_connected": self.nas_connector.test_connection(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if self.chroma_client:
                collections = self.chroma_client.list_collections()
                status["collections"] = len(collections)
        except Exception:
            status["collections"] = 0
        
        return status
    
    def refresh_index(self) -> bool:
        """Refresh the document index with latest content"""
        return self.index_documents(force_refresh=True)


# Global RAG system instance - Initialize lazily
rag_system = None

def get_rag_system():
    """Get or create the RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system