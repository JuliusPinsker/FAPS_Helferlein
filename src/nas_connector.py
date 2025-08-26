"""
NAS connector for read-only access to FAPS network storage
"""
import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import tempfile
from urllib.parse import quote

from src.config import settings

logger = logging.getLogger(__name__)


class NASConnector:
    def __init__(self):
        self.nas_host = settings.nas_host
        self.nas_share_path = settings.nas_share_path
        self.cache_dir = os.path.join(settings.data_dir, "nas_cache")
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def test_connection(self) -> bool:
        """Test connection to NAS"""
        try:
            # For now, simulate connection test
            # In real implementation, this would try to connect to the SMB share
            logger.info(f"Testing connection to {self.nas_host}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NAS: {e}")
            return False
    
    def list_files(self, path: str = "", recursive: bool = True) -> List[Dict[str, Any]]:
        """
        List files in the NAS directory
        Returns list of file metadata dictionaries
        """
        try:
            # For development/demo purposes, return mock data
            # In real implementation, this would connect to SMB share and list actual files
            mock_files = [
                {
                    "name": "Forschungsprojekt_2024.pdf",
                    "path": "/Forschung/Projekte/Forschungsprojekt_2024.pdf",
                    "size": 2048576,
                    "modified": "2024-01-15T10:30:00",
                    "type": "pdf",
                    "download_url": self._generate_download_url("/Forschung/Projekte/Forschungsprojekt_2024.pdf")
                },
                {
                    "name": "Lehrstuhl_Präsentation.pptx",
                    "path": "/Präsentationen/Lehrstuhl_Präsentation.pptx",
                    "size": 5242880,
                    "modified": "2024-02-20T14:15:00",
                    "type": "pptx",
                    "download_url": self._generate_download_url("/Präsentationen/Lehrstuhl_Präsentation.pptx")
                },
                {
                    "name": "Anleitung_Laborgeräte.docx",
                    "path": "/Dokumentation/Anleitung_Laborgeräte.docx",
                    "size": 1048576,
                    "modified": "2024-03-10T09:45:00",
                    "type": "docx",
                    "download_url": self._generate_download_url("/Dokumentation/Anleitung_Laborgeräte.docx")
                }
            ]
            
            # Filter by path if specified
            if path:
                mock_files = [f for f in mock_files if f["path"].startswith(path)]
            
            logger.info(f"Listed {len(mock_files)} files from NAS path: {path}")
            return mock_files
            
        except Exception as e:
            logger.error(f"Failed to list files from NAS: {e}")
            return []
    
    def _generate_download_url(self, file_path: str) -> str:
        """Generate a download URL for a file"""
        # Encode the file path for URL safety
        encoded_path = quote(file_path)
        return f"smb://{self.nas_host}{encoded_path}"
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file for indexing
        Returns text content or None if file cannot be read
        """
        try:
            # Check cache first
            cache_key = file_path.replace("/", "_").replace("\\", "_")
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.txt")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # For demo purposes, return mock content
            # In real implementation, this would connect to SMB and extract text
            mock_content = self._get_mock_content(file_path)
            
            # Cache the content
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(mock_content)
            
            return mock_content
            
        except Exception as e:
            logger.error(f"Failed to get content for file {file_path}: {e}")
            return None
    
    def _get_mock_content(self, file_path: str) -> str:
        """Generate mock content for demo purposes"""
        filename = os.path.basename(file_path)
        
        if "Forschungsprojekt" in filename:
            return """
            Forschungsprojekt: Automatisierung in der Produktion
            
            Dieses Dokument beschreibt die aktuellen Forschungsaktivitäten am FAPS 
            im Bereich der Produktionsautomatisierung. Schwerpunkte sind:
            
            - Entwicklung adaptiver Fertigungssysteme
            - Integration von KI in Produktionsprozesse
            - Qualitätssicherung durch maschinelles Lernen
            - Nachhaltige Produktionsverfahren
            
            Das Projekt läuft von 2024 bis 2026 und wird in Kooperation mit 
            verschiedenen Industriepartnern durchgeführt.
            """
        elif "Laborgeräte" in filename:
            return """
            Anleitung für Laborgeräte am FAPS
            
            Diese Anleitung beschreibt die korrekte Verwendung der Laborausstattung:
            
            1. 3D-Drucker
               - Einschalten und Kalibrierung
               - Material-Setup
               - Druckparameter einstellen
            
            2. CNC-Maschinen
               - Sicherheitshinweise
               - Werkzeugwechsel
               - Programmierung
            
            3. Messgeräte
               - Koordinatenmessgerät
               - Oberflächenmessgerät
               - Härteprüfgerät
            
            Bitte beachten Sie alle Sicherheitsvorschriften.
            """
        elif "Präsentation" in filename:
            return """
            FAPS Lehrstuhl Präsentation
            
            Überblick über den Lehrstuhl für Fertigungsautomatisierung 
            und Produktionssystematik (FAPS):
            
            - Geschichte und Entwicklung des Lehrstuhls
            - Aktuelle Forschungsschwerpunkte
            - Lehrveranstaltungen und Studiengänge
            - Industriekooperationen
            - Laborausstattung und Infrastruktur
            - Team und Mitarbeiter
            - Publikationen und Erfolge
            
            Der Lehrstuhl wurde 1975 gegründet und ist seitdem führend 
            in der Fertigungstechnik-Forschung.
            """
        else:
            return f"Inhalt der Datei: {filename}\n\nDiese Datei enthält wichtige Informationen im Zusammenhang mit FAPS."
    
    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file"""
        files = self.list_files()
        for file_info in files:
            if file_info["path"] == file_path:
                return file_info
        return None