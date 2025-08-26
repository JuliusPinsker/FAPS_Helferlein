import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import mimetypes
import time
from datetime import datetime

class NASConnector:
    """Connector for FAPS NAS with read-only access"""
    
    def __init__(self):
        self.nas_mount_path = Path("/mnt/nas")
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {
            '.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx',
            '.md', '.rtf', '.odt', '.ods', '.odp', '.csv'
        }
        
        # Verify NAS access
        self._verify_nas_access()
    
    def _verify_nas_access(self) -> bool:
        """Verify that NAS is accessible and read-only"""
        try:
            if not self.nas_mount_path.exists():
                self.logger.warning(f"NAS mount path {self.nas_mount_path} does not exist")
                return False
            
            if not self.nas_mount_path.is_dir():
                self.logger.error(f"NAS mount path {self.nas_mount_path} is not a directory")
                return False
            
            # Test read access
            try:
                list(self.nas_mount_path.iterdir())
                self.logger.info("NAS read access verified")
            except PermissionError:
                self.logger.error("No read access to NAS")
                return False
            
            # Verify read-only (try to create a test file)
            test_file = self.nas_mount_path / ".test_write_access"
            try:
                test_file.touch()
                test_file.unlink()  # Clean up
                self.logger.warning("NAS appears to have write access - this should be read-only!")
                return False
            except (PermissionError, OSError):
                self.logger.info("NAS is properly configured as read-only")
                return True
            
        except Exception as e:
            self.logger.error(f"NAS access verification failed: {str(e)}")
            return False
    
    def is_nas_accessible(self) -> bool:
        """Check if NAS is currently accessible"""
        try:
            return self.nas_mount_path.exists() and self.nas_mount_path.is_dir()
        except Exception:
            return False
    
    def list_files(self, directory: str = "", recursive: bool = True, max_files: int = 1000) -> List[Dict[str, Any]]:
        """List files in NAS directory with metadata"""
        try:
            if not self.is_nas_accessible():
                self.logger.error("NAS is not accessible")
                return []
            
            search_path = self.nas_mount_path / directory.lstrip('/')
            
            if not search_path.exists():
                self.logger.warning(f"Directory {search_path} does not exist")
                return []
            
            files = []
            file_count = 0
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in search_path.glob(pattern):
                if file_count >= max_files:
                    break
                
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    file_info = self._get_file_metadata(file_path)
                    if file_info:
                        files.append(file_info)
                        file_count += 1
            
            self.logger.info(f"Listed {len(files)} files from NAS directory: {directory}")
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list NAS files: {str(e)}")
            return []
    
    def _get_file_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from a file"""
        try:
            stat = file_path.stat()
            
            # Calculate relative path from NAS mount
            relative_path = file_path.relative_to(self.nas_mount_path)
            
            # Generate unique ID based on path
            file_id = f"nas_{hashlib.md5(str(relative_path).encode()).hexdigest()}"
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                'id': file_id,
                'title': file_path.name,
                'filename': file_path.name,
                'path': str(relative_path),
                'full_path': str(file_path),
                'size': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'modified_timestamp': stat.st_mtime,
                'extension': file_path.suffix.lower(),
                'mime_type': mime_type,
                'source_type': 'nas',
                'source_path': str(relative_path),
                'download_url': self._generate_download_url(relative_path),
                'metadata': {
                    'directory': str(relative_path.parent),
                    'basename': file_path.stem,
                    'is_readable': os.access(file_path, os.R_OK)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metadata for {file_path}: {str(e)}")
            return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _generate_download_url(self, relative_path: Path) -> str:
        """Generate secure download URL for a file"""
        # In a real implementation, this would generate a secure, time-limited URL
        # For now, we'll create a local file path reference
        return f"/nas/download/{relative_path}"
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search files by name and content (where possible)"""
        try:
            if not self.is_nas_accessible():
                return []
            
            query_lower = query.lower()
            results = []
            
            # Get all files
            all_files = self.list_files(recursive=True, max_files=5000)
            
            # Search by filename first
            for file_info in all_files:
                if len(results) >= max_results:
                    break
                
                # Check filename match
                if query_lower in file_info['filename'].lower():
                    # Add content preview if possible
                    content_preview = self._extract_content_preview(Path(file_info['full_path']))
                    if content_preview:
                        file_info['content'] = content_preview
                        file_info['excerpt'] = content_preview[:300] + "..." if len(content_preview) > 300 else content_preview
                    
                    results.append(file_info)
            
            # If we need more results, search by content in text files
            if len(results) < max_results:
                for file_info in all_files:
                    if len(results) >= max_results:
                        break
                    
                    if file_info in results:
                        continue
                    
                    # Only search content for text-based files
                    if file_info['extension'] in ['.txt', '.md', '.csv']:
                        content = self._extract_text_content(Path(file_info['full_path']))
                        if content and query_lower in content.lower():
                            file_info['content'] = content
                            file_info['excerpt'] = content[:300] + "..." if len(content) > 300 else content
                            results.append(file_info)
            
            self.logger.info(f"Found {len(results)} files matching query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"NAS search failed: {str(e)}")
            return []
    
    def _extract_content_preview(self, file_path: Path) -> Optional[str]:
        """Extract content preview from file"""
        try:
            extension = file_path.suffix.lower()
            
            if extension in ['.txt', '.md', '.csv']:
                return self._extract_text_content(file_path)
            elif extension == '.pdf':
                return self._extract_pdf_content(file_path)
            elif extension in ['.doc', '.docx']:
                return self._extract_word_content(file_path)
            elif extension in ['.xls', '.xlsx']:
                return self._extract_excel_content(file_path)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Content extraction failed for {file_path}: {str(e)}")
            return None
    
    def _extract_text_content(self, file_path: Path) -> Optional[str]:
        """Extract text from plain text files"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        # Limit content size for performance
                        return content[:10000] if len(content) > 10000 else content
                except UnicodeDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Text extraction failed for {file_path}: {str(e)}")
            return None
    
    def _extract_pdf_content(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF files"""
        try:
            # This would require PyPDF2 or similar library
            # For now, return placeholder
            return f"PDF content from {file_path.name} (content extraction not implemented)"
        except Exception as e:
            self.logger.error(f"PDF extraction failed for {file_path}: {str(e)}")
            return None
    
    def _extract_word_content(self, file_path: Path) -> Optional[str]:
        """Extract text from Word documents"""
        try:
            # This would require python-docx library
            # For now, return placeholder
            return f"Word document content from {file_path.name} (content extraction not implemented)"
        except Exception as e:
            self.logger.error(f"Word extraction failed for {file_path}: {str(e)}")
            return None
    
    def _extract_excel_content(self, file_path: Path) -> Optional[str]:
        """Extract text from Excel files"""
        try:
            # This would require openpyxl library
            # For now, return placeholder
            return f"Excel content from {file_path.name} (content extraction not implemented)"
        except Exception as e:
            self.logger.error(f"Excel extraction failed for {file_path}: {str(e)}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific file"""
        try:
            full_path = self.nas_mount_path / file_path.lstrip('/')
            
            if not full_path.exists():
                return None
            
            return self._get_file_metadata(full_path)
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return None
    
    def get_directory_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get directory structure of the NAS"""
        try:
            if not self.is_nas_accessible():
                return {}
            
            def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
                if current_depth >= max_depth:
                    return {}
                
                tree = {
                    'name': path.name,
                    'path': str(path.relative_to(self.nas_mount_path)),
                    'type': 'directory',
                    'children': {}
                }
                
                try:
                    for item in path.iterdir():
                        if item.is_dir():
                            tree['children'][item.name] = build_tree(item, current_depth + 1)
                        elif item.suffix.lower() in self.supported_extensions:
                            tree['children'][item.name] = {
                                'name': item.name,
                                'path': str(item.relative_to(self.nas_mount_path)),
                                'type': 'file',
                                'size': item.stat().st_size
                            }
                except PermissionError:
                    tree['error'] = 'Permission denied'
                
                return tree
            
            return build_tree(self.nas_mount_path)
            
        except Exception as e:
            self.logger.error(f"Failed to get directory structure: {str(e)}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get NAS usage statistics"""
        try:
            if not self.is_nas_accessible():
                return {}
            
            total_files = 0
            total_size = 0
            file_types = {}
            
            all_files = self.list_files(recursive=True, max_files=10000)
            
            for file_info in all_files:
                total_files += 1
                total_size += file_info['size']
                
                ext = file_info['extension']
                if ext in file_types:
                    file_types[ext] += 1
                else:
                    file_types[ext] = 1
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_human': self._format_file_size(total_size),
                'file_types': file_types,
                'is_accessible': True,
                'mount_path': str(self.nas_mount_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get NAS statistics: {str(e)}")
            return {'is_accessible': False, 'error': str(e)}