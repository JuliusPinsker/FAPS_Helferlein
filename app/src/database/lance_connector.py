import os
import lancedb
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

class LanceDBConnector:
    """Connector for LanceDB vector database operations"""
    
    def __init__(self):
        self.db_uri = os.getenv('LANCEDB_URI', '/tmp/lancedb')
        self.db = None
        self.table_name = "faps_documents"
        self.logger = logging.getLogger(__name__)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the LanceDB connection and create tables if needed"""
        try:
            # Connect to LanceDB
            if self.db_uri.startswith('http'):
                # Remote LanceDB instance
                self.db = lancedb.connect(self.db_uri)
            else:
                # Local LanceDB instance
                self.db = lancedb.connect(self.db_uri)
            
            # Create table if it doesn't exist
            self._create_table_if_not_exists()
            self.logger.info("LanceDB connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LanceDB: {str(e)}")
            raise
    
    def _create_table_if_not_exists(self):
        """Create the documents table if it doesn't exist"""
        try:
            # Check if table exists
            if self.table_name not in self.db.table_names():
                # Create sample data to define schema
                sample_data = [{
                    'id': 'sample',
                    'title': 'Sample Document',
                    'content': 'Sample content for schema definition',
                    'source_type': 'sample',
                    'source_path': '/sample/path',
                    'url': 'http://example.com',
                    'metadata': '{}',
                    'embedding': [0.0] * 384  # Default embedding dimension
                }]
                
                df = pd.DataFrame(sample_data)
                table = self.db.create_table(self.table_name, df)
                
                # Remove sample data
                table.delete("id = 'sample'")
                
                self.logger.info(f"Created table '{self.table_name}'")
            else:
                self.logger.info(f"Table '{self.table_name}' already exists")
                
        except Exception as e:
            self.logger.error(f"Failed to create table: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test if the database connection is working"""
        try:
            if self.db is None:
                return False
            
            # Try to list tables
            tables = self.db.table_names()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def add_document(self, document: Dict[str, Any]) -> bool:
        """Add a document to the vector database"""
        try:
            table = self.db.open_table(self.table_name)
            
            # Prepare document data
            doc_data = {
                'id': document.get('id', ''),
                'title': document.get('title', ''),
                'content': document.get('content', ''),
                'source_type': document.get('source_type', ''),
                'source_path': document.get('source_path', ''),
                'url': document.get('url', ''),
                'metadata': str(document.get('metadata', {})),
                'embedding': document.get('embedding', [0.0] * 384)
            }
            
            df = pd.DataFrame([doc_data])
            table.add(df)
            
            self.logger.info(f"Added document: {document.get('id', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add multiple documents to the vector database"""
        try:
            if not documents:
                return True
            
            table = self.db.open_table(self.table_name)
            
            # Prepare documents data
            docs_data = []
            for doc in documents:
                doc_data = {
                    'id': doc.get('id', ''),
                    'title': doc.get('title', ''),
                    'content': doc.get('content', ''),
                    'source_type': doc.get('source_type', ''),
                    'source_path': doc.get('source_path', ''),
                    'url': doc.get('url', ''),
                    'metadata': str(doc.get('metadata', {})),
                    'embedding': doc.get('embedding', [0.0] * 384)
                }
                docs_data.append(doc_data)
            
            df = pd.DataFrame(docs_data)
            table.add(df)
            
            self.logger.info(f"Added {len(documents)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add documents: {str(e)}")
            return False
    
    def search_similar(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        try:
            table = self.db.open_table(self.table_name)
            
            # Perform vector search
            results = table.search(query_embedding).limit(limit).to_list()
            
            # Convert results to desired format
            formatted_results = []
            for result in results:
                formatted_result = {
                    'id': result.get('id', ''),
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'source_type': result.get('source_type', ''),
                    'source_path': result.get('source_path', ''),
                    'url': result.get('url', ''),
                    'metadata': eval(result.get('metadata', '{}')),
                    'score': result.get('_distance', 0.0)
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Failed to search: {str(e)}")
            return []
    
    def search_by_text(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by text content"""
        try:
            table = self.db.open_table(self.table_name)
            
            # Perform full-text search (simplified)
            query_lower = query.lower()
            
            # This is a basic implementation - in production, you'd use proper FTS
            all_docs = table.to_pandas()
            
            # Filter documents containing query terms
            mask = (
                all_docs['title'].str.lower().str.contains(query_lower, na=False) |
                all_docs['content'].str.lower().str.contains(query_lower, na=False)
            )
            
            filtered_docs = all_docs[mask].head(limit)
            
            # Convert to desired format
            results = []
            for _, doc in filtered_docs.iterrows():
                result = {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'source_type': doc['source_type'],
                    'source_path': doc['source_path'],
                    'url': doc['url'],
                    'metadata': eval(doc['metadata']) if doc['metadata'] else {},
                    'score': 1.0  # Placeholder score for text search
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search by text: {str(e)}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            table = self.db.open_table(self.table_name)
            results = table.search().where(f"id = '{doc_id}'").to_list()
            
            if results:
                doc = results[0]
                return {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'source_type': doc['source_type'],
                    'source_path': doc['source_path'],
                    'url': doc['url'],
                    'metadata': eval(doc['metadata']) if doc['metadata'] else {}
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get document by ID: {str(e)}")
            return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            table = self.db.open_table(self.table_name)
            table.delete(f"id = '{doc_id}'")
            
            self.logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    def refresh_index(self) -> bool:
        """Refresh the search index"""
        try:
            # LanceDB handles indexing automatically
            # This method can be used to trigger re-indexing if needed
            self.logger.info("Index refresh completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh index: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            table = self.db.open_table(self.table_name)
            df = table.to_pandas()
            
            stats = {
                'total_documents': len(df),
                'nas_files': len(df[df['source_type'] == 'nas']),
                'wiki_pages': len(df[df['source_type'] == 'wiki']),
                'web_pages': len(df[df['source_type'] == 'web']),
                'source_types': df['source_type'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    def clear_all_documents(self) -> bool:
        """Clear all documents from the database"""
        try:
            table = self.db.open_table(self.table_name)
            table.delete("id IS NOT NULL")  # Delete all rows
            
            self.logger.info("Cleared all documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear documents: {str(e)}")
            return False