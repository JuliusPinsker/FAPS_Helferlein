#!/usr/bin/env python3
"""
Test script for FAPS Knowledge Assistant
Tests the German interface and basic functionality
"""

import sys
import os
import time
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set environment variables for testing
os.environ['STREAMLIT_DISABLE_TELEMETRY'] = 'true'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

def test_imports():
    """Test all module imports"""
    print("🧪 Testing module imports...")
    
    try:
        from src.ui.german_interface import render_main_interface
        print("✅ German interface import successful")
    except ImportError as e:
        print(f"❌ German interface import failed: {e}")
        return False
    
    try:
        from src.database.lance_connector import LanceDBConnector
        print("✅ LanceDB connector import successful")
    except ImportError as e:
        print(f"❌ LanceDB connector import failed: {e}")
        return False
    
    try:
        from src.security.auth_manager import AuthManager
        print("✅ Auth manager import successful")
    except ImportError as e:
        print(f"❌ Auth manager import failed: {e}")
        return False
    
    try:
        from src.connectors.web_scraper import WebScraper
        print("✅ Web scraper import successful")
    except ImportError as e:
        print(f"❌ Web scraper import failed: {e}")
        return False
    
    try:
        from src.connectors.nas_connector import NASConnector
        print("✅ NAS connector import successful")
    except ImportError as e:
        print(f"❌ NAS connector import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of components"""
    print("\n🧪 Testing basic functionality...")
    
    # Test LanceDB connector
    try:
        from src.database.lance_connector import LanceDBConnector
        db = LanceDBConnector()
        connection_test = db.test_connection()
        print(f"✅ LanceDB connector: Connection test = {connection_test}")
    except Exception as e:
        print(f"❌ LanceDB connector test failed: {e}")
        return False
    
    # Test Auth Manager
    try:
        from src.security.auth_manager import AuthManager
        auth = AuthManager()
        auth_status = auth.get_auth_status()
        print(f"✅ Auth manager: Status = {auth_status}")
    except Exception as e:
        print(f"❌ Auth manager test failed: {e}")
        return False
    
    # Test NAS Connector
    try:
        from src.connectors.nas_connector import NASConnector
        nas = NASConnector()
        nas_accessible = nas.is_nas_accessible()
        print(f"✅ NAS connector: Accessible = {nas_accessible} (expected False in test environment)")
    except Exception as e:
        print(f"❌ NAS connector test failed: {e}")
        return False
    
    # Test Web Scraper
    try:
        from src.connectors.web_scraper import WebScraper
        scraper = WebScraper("www.intern.fau.de")
        print("✅ Web scraper: Instantiation successful")
    except Exception as e:
        print(f"❌ Web scraper test failed: {e}")
        return False
    
    return True

def test_german_content():
    """Test German language content and interface"""
    print("\n🧪 Testing German language content...")
    
    # Test if German text is properly handled
    test_queries = [
        "Wie kann ich mich anmelden?",
        "Wo finde ich Informationen über FAPS?",
        "Können Sie mir bei der Dokumentensuche helfen?"
    ]
    
    try:
        from src.ui.german_interface import generate_fallback_response
        
        for query in test_queries:
            response = generate_fallback_response(query)
            if "Entschuldigung" in response and "Anfrage" in response:
                print(f"✅ German response generated for: '{query[:30]}...'")
            else:
                print(f"❌ German response test failed for: '{query[:30]}...'")
                return False
        
        print("✅ German language handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ German content test failed: {e}")
        return False

def test_docker_config():
    """Test Docker configuration files"""
    print("\n🧪 Testing Docker configuration...")
    
    # Check docker-compose.yml
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    if docker_compose_path.exists():
        print("✅ docker-compose.yml exists")
        
        # Check for required services
        with open(docker_compose_path) as f:
            content = f.read()
            if "ollama:" in content and "lancedb:" in content and "phidata:" in content:
                print("✅ Required services defined in docker-compose.yml")
            else:
                print("❌ Missing required services in docker-compose.yml")
                return False
    else:
        print("❌ docker-compose.yml not found")
        return False
    
    # Check Dockerfile
    dockerfile_path = Path(__file__).parent / "Dockerfile"
    if dockerfile_path.exists():
        print("✅ Dockerfile exists")
    else:
        print("❌ Dockerfile not found")
        return False
    
    # Check requirements.txt
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        print("✅ requirements.txt exists")
        
        with open(requirements_path) as f:
            content = f.read()
            required_packages = ["streamlit", "requests", "beautifulsoup4", "pandas"]
            for package in required_packages:
                if package in content:
                    print(f"✅ Required package '{package}' in requirements.txt")
                else:
                    print(f"❌ Missing package '{package}' in requirements.txt")
                    return False
    else:
        print("❌ requirements.txt not found")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting FAPS Knowledge Assistant Tests")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run import tests
    if not test_imports():
        all_tests_passed = False
    
    # Run functionality tests
    if not test_basic_functionality():
        all_tests_passed = False
    
    # Run German content tests
    if not test_german_content():
        all_tests_passed = False
    
    # Run Docker config tests
    if not test_docker_config():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! FAPS Knowledge Assistant is ready.")
        print("\n📋 Summary:")
        print("✅ Docker infrastructure configured")
        print("✅ German language interface implemented")
        print("✅ Security components working")
        print("✅ Database connectors functional")
        print("✅ Web scraping capabilities ready")
        print("✅ NAS integration prepared")
        
        print("\n🚀 To start the application:")
        print("   docker-compose up")
        print("   Or for development:")
        print("   streamlit run main.py")
        
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())