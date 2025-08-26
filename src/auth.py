"""
Authentication system for secure token-based access to web resources
"""
import json
import logging
from typing import Dict, Optional, Any
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AuthenticationManager:
    def __init__(self):
        self.tokens = {}
        self.session_cache = {}
    
    def store_token(self, service: str, token: str, expiry: Optional[str] = None) -> bool:
        """
        Store authentication token for a service
        
        Args:
            service: Service name (e.g., 'wiki', 'intern_fau')
            token: Authentication token or session cookie
            expiry: Optional expiry date/time
            
        Returns:
            bool: Success status
        """
        try:
            self.tokens[service] = {
                "token": token,
                "expiry": expiry,
                "created": datetime.now().isoformat()
            }
            logger.info(f"Token stored for service: {service}")
            return True
        except Exception as e:
            logger.error(f"Failed to store token for {service}: {e}")
            return False
    
    def get_token(self, service: str) -> Optional[str]:
        """Get stored token for a service"""
        token_data = self.tokens.get(service)
        if not token_data:
            return None
        
        # Check if token has expired
        if token_data.get("expiry"):
            try:
                expiry = datetime.fromisoformat(token_data["expiry"])
                if datetime.now() > expiry:
                    logger.warning(f"Token for {service} has expired")
                    del self.tokens[service]
                    return None
            except ValueError:
                logger.warning(f"Invalid expiry format for {service} token")
        
        return token_data["token"]
    
    def validate_token(self, service: str, token: str) -> bool:
        """
        Validate token against the service
        
        Args:
            service: Service name
            token: Token to validate
            
        Returns:
            bool: True if token is valid
        """
        try:
            if service == "wiki":
                return self._validate_wiki_token(token)
            elif service == "intern_fau":
                return self._validate_intern_fau_token(token)
            else:
                logger.warning(f"Unknown service for token validation: {service}")
                return False
        except Exception as e:
            logger.error(f"Token validation failed for {service}: {e}")
            return False
    
    def _validate_wiki_token(self, token: str) -> bool:
        """Validate wiki authentication token"""
        try:
            # For demo purposes, always return True
            # In real implementation, this would make a test request to the wiki
            logger.info("Validating wiki token (demo mode)")
            return True
        except Exception as e:
            logger.error(f"Wiki token validation failed: {e}")
            return False
    
    def _validate_intern_fau_token(self, token: str) -> bool:
        """Validate intern.fau.de authentication token"""
        try:
            # For demo purposes, always return True
            # In real implementation, this would make a test request to intern.fau.de
            logger.info("Validating intern.fau.de token (demo mode)")
            return True
        except Exception as e:
            logger.error(f"Intern.FAU token validation failed: {e}")
            return False
    
    def is_authenticated(self, service: str) -> bool:
        """Check if user is authenticated for a service"""
        token = self.get_token(service)
        if not token:
            return False
        return self.validate_token(service, token)
    
    def get_session_headers(self, service: str) -> Dict[str, str]:
        """Get HTTP headers with authentication for a service"""
        token = self.get_token(service)
        if not token:
            return {}
        
        headers = {
            "User-Agent": "FAPS Knowledge Assistant 1.0"
        }
        
        if service == "wiki":
            # For wiki, token might be a session cookie
            headers["Cookie"] = token
        elif service == "intern_fau":
            # For intern.fau.de, token might be a bearer token or cookie
            if token.startswith("Bearer "):
                headers["Authorization"] = token
            else:
                headers["Cookie"] = token
        
        return headers
    
    def clear_token(self, service: str) -> bool:
        """Clear stored token for a service"""
        try:
            if service in self.tokens:
                del self.tokens[service]
                logger.info(f"Token cleared for service: {service}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear token for {service}: {e}")
            return False
    
    def get_token_info(self, service: str) -> Optional[Dict[str, Any]]:
        """Get information about stored token"""
        token_data = self.tokens.get(service)
        if not token_data:
            return None
        
        info = {
            "service": service,
            "has_token": bool(token_data.get("token")),
            "created": token_data.get("created"),
            "expiry": token_data.get("expiry"),
            "is_valid": self.is_authenticated(service)
        }
        
        return info
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all configured services and their authentication status"""
        services = {
            "wiki": {
                "name": "FAPS Wiki",
                "url": "https://wiki.faps.uni-erlangen.de/",
                "authenticated": self.is_authenticated("wiki")
            },
            "intern_fau": {
                "name": "Intern.FAU",
                "url": "https://www.intern.fau.de/",
                "authenticated": self.is_authenticated("intern_fau")
            }
        }
        
        return services


# Global authentication manager instance
auth_manager = AuthenticationManager()