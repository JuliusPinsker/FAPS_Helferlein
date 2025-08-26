import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import logging
import re
import time
from pathlib import Path

class WebScraper:
    """Web scraper for FAPS-related websites"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'FAPS Knowledge Assistant 1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.8,en;q=0.6',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting to be respectful to servers"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a rate-limited HTTP request"""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all relevant links from a page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Only include links from the same domain
            if urlparse(full_url).netloc == self.domain:
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def scrape_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single page and return structured data"""
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).path
            
            # Extract meta description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Extract main content
            content = self._extract_text_content(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Create excerpt (first 300 characters)
            excerpt = content[:300] + "..." if len(content) > 300 else content
            
            return {
                'id': f"web_{hash(url)}",
                'title': title_text,
                'content': content,
                'excerpt': excerpt,
                'description': description,
                'url': url,
                'source_type': 'web',
                'source_path': url,
                'links': links,
                'metadata': {
                    'domain': self.domain,
                    'scraped_at': time.time(),
                    'content_length': len(content),
                    'link_count': len(links)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scrape page {url}: {str(e)}")
            return None
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for content relevant to the query"""
        try:
            results = []
            
            if self.domain == "www.intern.fau.de":
                results = self._search_intern_fau(query, max_results)
            elif self.domain == "wiki.faps.uni-erlangen.de":
                results = self._search_wiki_faps(query, max_results)
            elif self.domain == "www.idm.fau.de":
                results = self._search_idm_fau(query, max_results)
            else:
                # Generic search
                results = self._generic_search(query, max_results)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {str(e)}")
            return []
    
    def _search_intern_fau(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search www.intern.fau.de (public access)"""
        results = []
        
        try:
            # Start with main page
            main_url = f"https://{self.domain}"
            
            # Try to find a search page or use Google site search
            search_url = f"https://www.google.com/search?q=site:{self.domain} {query}"
            
            # For now, scrape some known important pages
            important_pages = [
                f"{main_url}/",
                f"{main_url}/studium/",
                f"{main_url}/forschung/",
                f"{main_url}/personen/",
                f"{main_url}/aktuelles/"
            ]
            
            for page_url in important_pages:
                if len(results) >= max_results:
                    break
                
                page_data = self.scrape_page(page_url)
                if page_data and self._is_relevant_to_query(page_data['content'], query):
                    results.append(page_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"FAU internal search failed: {str(e)}")
            return []
    
    def _search_wiki_faps(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search FAPS Wiki (requires authentication)"""
        # This would require authentication first
        # For now, return empty list as authentication is needed
        self.logger.warning("Wiki search requires authentication")
        return []
    
    def _search_idm_fau(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search IDM FAU (requires SSO authentication)"""
        # This would require SSO authentication first
        # For now, return empty list as authentication is needed
        self.logger.warning("IDM search requires SSO authentication")
        return []
    
    def _generic_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generic search for any website"""
        results = []
        
        try:
            # Start with base URL
            base_page = self.scrape_page(f"https://{self.domain}")
            if base_page and self._is_relevant_to_query(base_page['content'], query):
                results.append(base_page)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Generic search failed: {str(e)}")
            return []
    
    def _is_relevant_to_query(self, content: str, query: str) -> bool:
        """Check if content is relevant to the search query"""
        try:
            query_terms = query.lower().split()
            content_lower = content.lower()
            
            # Simple relevance scoring
            matches = sum(1 for term in query_terms if term in content_lower)
            relevance_threshold = len(query_terms) * 0.3  # 30% of terms should match
            
            return matches >= relevance_threshold
            
        except Exception:
            return False
    
    def crawl_sitemap(self, max_pages: int = 100) -> List[Dict[str, Any]]:
        """Crawl website using sitemap or by following links"""
        try:
            crawled_pages = []
            visited_urls = set()
            urls_to_visit = [f"https://{self.domain}"]
            
            # Try to find sitemap first
            sitemap_urls = self._find_sitemap()
            if sitemap_urls:
                urls_to_visit.extend(sitemap_urls[:max_pages])
            
            while urls_to_visit and len(crawled_pages) < max_pages:
                url = urls_to_visit.pop(0)
                
                if url in visited_urls:
                    continue
                
                visited_urls.add(url)
                
                page_data = self.scrape_page(url)
                if page_data:
                    crawled_pages.append(page_data)
                    
                    # Add new links to visit (limited to avoid infinite crawling)
                    new_links = page_data.get('links', [])[:5]  # Limit links per page
                    for link in new_links:
                        if link not in visited_urls and len(urls_to_visit) < max_pages:
                            urls_to_visit.append(link)
            
            self.logger.info(f"Crawled {len(crawled_pages)} pages from {self.domain}")
            return crawled_pages
            
        except Exception as e:
            self.logger.error(f"Crawling failed: {str(e)}")
            return []
    
    def _find_sitemap(self) -> List[str]:
        """Try to find and parse sitemap.xml"""
        try:
            sitemap_urls = [
                f"https://{self.domain}/sitemap.xml",
                f"https://{self.domain}/sitemap_index.xml",
                f"https://{self.domain}/robots.txt"
            ]
            
            for sitemap_url in sitemap_urls:
                response = self._make_request(sitemap_url)
                if response:
                    if sitemap_url.endswith('robots.txt'):
                        # Parse robots.txt for sitemap
                        for line in response.text.split('\n'):
                            if line.startswith('Sitemap:'):
                                actual_sitemap = line.split(':', 1)[1].strip()
                                return self._parse_sitemap(actual_sitemap)
                    else:
                        # Parse XML sitemap
                        return self._parse_sitemap_xml(response.content)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Sitemap parsing failed: {str(e)}")
            return []
    
    def _parse_sitemap_xml(self, xml_content: bytes) -> List[str]:
        """Parse XML sitemap and extract URLs"""
        try:
            soup = BeautifulSoup(xml_content, 'xml')
            urls = []
            
            # Handle regular sitemap
            for url_tag in soup.find_all('url'):
                loc_tag = url_tag.find('loc')
                if loc_tag:
                    urls.append(loc_tag.get_text())
            
            # Handle sitemap index
            for sitemap_tag in soup.find_all('sitemap'):
                loc_tag = sitemap_tag.find('loc')
                if loc_tag:
                    # Recursively parse sub-sitemaps
                    sub_sitemap_url = loc_tag.get_text()
                    sub_urls = self._parse_sitemap(sub_sitemap_url)
                    urls.extend(sub_urls)
            
            return urls
            
        except Exception as e:
            self.logger.error(f"XML sitemap parsing failed: {str(e)}")
            return []
    
    def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse a sitemap URL and return list of URLs"""
        try:
            response = self._make_request(sitemap_url)
            if response:
                return self._parse_sitemap_xml(response.content)
            return []
        except Exception as e:
            self.logger.error(f"Sitemap URL parsing failed: {str(e)}")
            return []