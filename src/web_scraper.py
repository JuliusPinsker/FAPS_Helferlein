"""
Web scrapers for authenticated FAPS resources
"""
import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

from src.auth import auth_manager
from src.config import settings

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.rate_limit_delay = 1  # seconds between requests
        
    def scrape_wiki(self, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape FAPS wiki content
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of page content dictionaries
        """
        if not auth_manager.is_authenticated("wiki"):
            logger.warning("Not authenticated for wiki access")
            return []
        
        try:
            headers = auth_manager.get_session_headers("wiki")
            pages = []
            
            # For demo purposes, return mock wiki content
            # In real implementation, this would scrape actual wiki pages
            mock_pages = [
                {
                    "title": "FAPS Lehrstuhl Übersicht",
                    "url": f"{settings.wiki_url}lehrstuhl/uebersicht",
                    "content": """
                    Der Lehrstuhl für Fertigungsautomatisierung und Produktionssystematik (FAPS) 
                    wurde 1975 gegründet und beschäftigt sich mit der Erforschung und Entwicklung 
                    von Automatisierungslösungen für die Produktion.
                    
                    Forschungsschwerpunkte:
                    - Adaptive Fertigungssysteme
                    - Cyber-physische Produktionssysteme
                    - Künstliche Intelligenz in der Fertigung
                    - Nachhaltige Produktionsverfahren
                    """,
                    "last_modified": "2024-01-15T10:30:00",
                    "type": "wiki_page"
                },
                {
                    "title": "Laborausstattung",
                    "url": f"{settings.wiki_url}labor/ausstattung",
                    "content": """
                    Das FAPS verfügt über eine moderne Laborausstattung für Forschung und Lehre:
                    
                    - 3D-Druckzentrum mit verschiedenen Drucktechnologien
                    - CNC-Fertigungszellen für Präzisionsteile
                    - Koordinatenmessgeräte für Qualitätskontrolle
                    - Robotersysteme für Automatisierungsaufgaben
                    - Bildverarbeitungssysteme für Inspektion
                    
                    Die Geräte stehen für Forschungsprojekte und Abschlussarbeiten zur Verfügung.
                    """,
                    "last_modified": "2024-02-20T14:15:00",
                    "type": "wiki_page"
                },
                {
                    "title": "Lehrveranstaltungen",
                    "url": f"{settings.wiki_url}lehre/veranstaltungen",
                    "content": """
                    Das FAPS bietet verschiedene Lehrveranstaltungen im Bereich Fertigungstechnik:
                    
                    Bachelor:
                    - Grundlagen der Fertigungstechnik
                    - CAD/CAM-Systeme
                    - Produktionsplanung
                    
                    Master:
                    - Automatisierungstechnik
                    - Cyber-physische Systeme
                    - Fertigungsmesstechnik
                    - Projektseminare
                    
                    Alle Veranstaltungen kombinieren theoretische Grundlagen mit praktischen Übungen.
                    """,
                    "last_modified": "2024-03-10T09:45:00",
                    "type": "wiki_page"
                }
            ]
            
            logger.info(f"Scraped {len(mock_pages)} pages from FAPS wiki")
            return mock_pages[:max_pages]
            
        except Exception as e:
            logger.error(f"Failed to scrape wiki: {e}")
            return []
    
    def scrape_intern_fau(self, max_pages: int = 30) -> List[Dict[str, Any]]:
        """
        Scrape intern.fau.de content
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of page content dictionaries
        """
        if not auth_manager.is_authenticated("intern_fau"):
            logger.warning("Not authenticated for intern.fau.de access")
            return []
        
        try:
            headers = auth_manager.get_session_headers("intern_fau")
            pages = []
            
            # For demo purposes, return mock content
            # In real implementation, this would scrape actual intern.fau.de pages
            mock_pages = [
                {
                    "title": "FAPS Mitarbeiter",
                    "url": f"{settings.intern_fau_url}faps/mitarbeiter",
                    "content": """
                    Mitarbeiterübersicht des Lehrstuhls FAPS:
                    
                    Lehrstuhlinhaber: Prof. Dr.-Ing. Jörg Franke
                    
                    Wissenschaftliche Mitarbeiter:
                    - Dr.-Ing. Max Mustermann (Gruppenleiter Automatisierung)
                    - M.Sc. Anna Schmidt (Doktorandin KI in der Fertigung)
                    - M.Sc. Peter Weber (Doktorand Cyber-physische Systeme)
                    
                    Technische Mitarbeiter:
                    - Dipl.-Ing. Klaus Meier (Laboringenieur)
                    - Hans Fischer (Werkstattleiter)
                    """,
                    "last_modified": "2024-01-30T11:20:00",
                    "type": "intern_page"
                },
                {
                    "title": "Aktuelle Projekte",
                    "url": f"{settings.intern_fau_url}faps/projekte",
                    "content": """
                    Laufende Forschungsprojekte am FAPS:
                    
                    1. SmartFactory 4.0 (2023-2026)
                       - Förderung: DFG
                       - Partner: Siemens, BMW
                       - Ziel: Entwicklung adaptiver Fertigungssysteme
                    
                    2. AI-Production (2024-2027)
                       - Förderung: BMBF
                       - Partner: diverse Industrieunternehmen
                       - Ziel: KI-Integration in Produktionsprozesse
                    
                    3. GreenManufacturing (2022-2025)
                       - Förderung: EU Horizon
                       - Partner: europäische Universitäten
                       - Ziel: Nachhaltige Fertigungsverfahren
                    """,
                    "last_modified": "2024-03-05T16:45:00",
                    "type": "intern_page"
                }
            ]
            
            logger.info(f"Scraped {len(mock_pages)} pages from intern.fau.de")
            return mock_pages[:max_pages]
            
        except Exception as e:
            logger.error(f"Failed to scrape intern.fau.de: {e}")
            return []
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from HTML: {e}")
            return ""
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        time.sleep(self.rate_limit_delay)
    
    def get_all_content(self) -> List[Dict[str, Any]]:
        """Get all content from configured web sources"""
        all_content = []
        
        # Scrape wiki if authenticated
        if auth_manager.is_authenticated("wiki"):
            wiki_content = self.scrape_wiki()
            all_content.extend(wiki_content)
        
        # Scrape intern.fau.de if authenticated
        if auth_manager.is_authenticated("intern_fau"):
            intern_content = self.scrape_intern_fau()
            all_content.extend(intern_content)
        
        logger.info(f"Retrieved {len(all_content)} total pages from web sources")
        return all_content


# Global web scraper instance
web_scraper = WebScraper()