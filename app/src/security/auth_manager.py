import streamlit as st
import hashlib
import secrets
import time
from typing import Dict, Optional, Any
import logging
from datetime import datetime, timedelta

class AuthManager:
    """Secure authentication manager for FAPS resources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session_timeout = 3600  # 1 hour in seconds
        
        # Initialize session state for authentication
        if 'auth_sessions' not in st.session_state:
            st.session_state.auth_sessions = {}
    
    def create_session_token(self) -> str:
        """Create a secure session token"""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    def authenticate_wiki(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate against FAPS Wiki"""
        try:
            # Store credentials securely in session state (memory only)
            session_token = self.create_session_token()
            
            # In a real implementation, this would validate against the wiki
            # For now, we'll store the credentials for the session
            auth_session = {
                'type': 'wiki',
                'username': username,
                'password': password,  # In production, this should be encrypted
                'token': session_token,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=self.session_timeout),
                'authenticated': True
            }
            
            st.session_state.auth_sessions['wiki'] = auth_session
            
            self.logger.info(f"Wiki authentication session created for user: {username}")
            
            return {
                'success': True,
                'token': session_token,
                'message': 'Wiki-Authentifizierung erfolgreich'
            }
            
        except Exception as e:
            self.logger.error(f"Wiki authentication failed: {str(e)}")
            return {
                'success': False,
                'message': f'Wiki-Authentifizierung fehlgeschlagen: {str(e)}'
            }
    
    def authenticate_sso(self, redirect_url: str = None) -> Dict[str, Any]:
        """Initiate SSO authentication for IDM FAU"""
        try:
            # Generate SSO session
            session_token = self.create_session_token()
            
            # In a real implementation, this would redirect to SSO provider
            sso_session = {
                'type': 'sso',
                'token': session_token,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=self.session_timeout),
                'status': 'pending',
                'redirect_url': redirect_url or 'https://sso.uni-erlangen.de'
            }
            
            st.session_state.auth_sessions['sso'] = sso_session
            
            return {
                'success': True,
                'token': session_token,
                'redirect_url': sso_session['redirect_url'],
                'message': 'SSO-Authentifizierung initiiert'
            }
            
        except Exception as e:
            self.logger.error(f"SSO authentication failed: {str(e)}")
            return {
                'success': False,
                'message': f'SSO-Authentifizierung fehlgeschlagen: {str(e)}'
            }
    
    def complete_sso_authentication(self, token: str, sso_response: Dict[str, Any]) -> Dict[str, Any]:
        """Complete SSO authentication with response data"""
        try:
            if 'sso' not in st.session_state.auth_sessions:
                return {'success': False, 'message': 'Keine SSO-Session gefunden'}
            
            session = st.session_state.auth_sessions['sso']
            
            if session['token'] != token:
                return {'success': False, 'message': 'Ungültiger Session-Token'}
            
            if datetime.now() > session['expires_at']:
                return {'success': False, 'message': 'Session abgelaufen'}
            
            # Update session with SSO response
            session.update({
                'authenticated': True,
                'status': 'completed',
                'user_info': sso_response,
                'expires_at': datetime.now() + timedelta(seconds=self.session_timeout)
            })
            
            self.logger.info("SSO authentication completed successfully")
            
            return {
                'success': True,
                'message': 'SSO-Authentifizierung erfolgreich abgeschlossen'
            }
            
        except Exception as e:
            self.logger.error(f"SSO completion failed: {str(e)}")
            return {
                'success': False,
                'message': f'SSO-Abschluss fehlgeschlagen: {str(e)}'
            }
    
    def is_authenticated(self, auth_type: str) -> bool:
        """Check if user is authenticated for a specific service"""
        try:
            if auth_type not in st.session_state.auth_sessions:
                return False
            
            session = st.session_state.auth_sessions[auth_type]
            
            # Check if session is still valid
            if datetime.now() > session['expires_at']:
                self.logout(auth_type)
                return False
            
            return session.get('authenticated', False)
            
        except Exception as e:
            self.logger.error(f"Authentication check failed: {str(e)}")
            return False
    
    def get_auth_session(self, auth_type: str) -> Optional[Dict[str, Any]]:
        """Get authentication session data"""
        try:
            if not self.is_authenticated(auth_type):
                return None
            
            return st.session_state.auth_sessions.get(auth_type)
            
        except Exception as e:
            self.logger.error(f"Failed to get auth session: {str(e)}")
            return None
    
    def refresh_session(self, auth_type: str) -> bool:
        """Refresh an authentication session"""
        try:
            if auth_type not in st.session_state.auth_sessions:
                return False
            
            session = st.session_state.auth_sessions[auth_type]
            session['expires_at'] = datetime.now() + timedelta(seconds=self.session_timeout)
            
            self.logger.info(f"Session refreshed for {auth_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Session refresh failed: {str(e)}")
            return False
    
    def logout(self, auth_type: str = None) -> bool:
        """Logout from specific service or all services"""
        try:
            if auth_type:
                # Logout from specific service
                if auth_type in st.session_state.auth_sessions:
                    del st.session_state.auth_sessions[auth_type]
                    self.logger.info(f"Logged out from {auth_type}")
            else:
                # Logout from all services
                st.session_state.auth_sessions.clear()
                self.logger.info("Logged out from all services")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Logout failed: {str(e)}")
            return False
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get overall authentication status"""
        try:
            status = {
                'wiki': self.is_authenticated('wiki'),
                'sso': self.is_authenticated('sso'),
                'active_sessions': len(st.session_state.auth_sessions),
                'last_activity': None
            }
            
            # Find most recent activity
            if st.session_state.auth_sessions:
                latest_activity = max(
                    session['created_at'] 
                    for session in st.session_state.auth_sessions.values()
                )
                status['last_activity'] = latest_activity
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get auth status: {str(e)}")
            return {}
    
    def cleanup_expired_sessions(self):
        """Clean up expired authentication sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for auth_type, session in st.session_state.auth_sessions.items():
                if current_time > session['expires_at']:
                    expired_sessions.append(auth_type)
            
            for auth_type in expired_sessions:
                del st.session_state.auth_sessions[auth_type]
                self.logger.info(f"Cleaned up expired session: {auth_type}")
            
            return len(expired_sessions)
            
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {str(e)}")
            return 0
    
    def encrypt_credentials(self, credentials: Dict[str, str]) -> str:
        """Encrypt credentials for secure storage (if needed)"""
        # This is a placeholder for credential encryption
        # In production, use proper encryption libraries
        import json
        return json.dumps(credentials)  # This should be encrypted
    
    def decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, str]:
        """Decrypt credentials from secure storage"""
        # This is a placeholder for credential decryption
        # In production, use proper decryption libraries
        import json
        return json.loads(encrypted_credentials)  # This should be decrypted
    
    def validate_session_security(self) -> Dict[str, Any]:
        """Validate session security and return recommendations"""
        security_status = {
            'secure': True,
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Check session timeout
            if self.session_timeout > 7200:  # 2 hours
                security_status['warnings'].append('Session timeout ist sehr lang')
                security_status['recommendations'].append('Verkürzen Sie das Session-Timeout')
            
            # Check number of active sessions
            active_sessions = len(st.session_state.auth_sessions)
            if active_sessions > 5:
                security_status['warnings'].append('Viele aktive Sessions')
                security_status['recommendations'].append('Alte Sessions bereinigen')
            
            # Clean up expired sessions
            cleaned = self.cleanup_expired_sessions()
            if cleaned > 0:
                security_status['recommendations'].append(f'{cleaned} abgelaufene Sessions bereinigt')
            
            return security_status
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {str(e)}")
            return {
                'secure': False,
                'warnings': ['Sicherheitsvalidierung fehlgeschlagen'],
                'recommendations': ['System-Administrator kontaktieren']
            }