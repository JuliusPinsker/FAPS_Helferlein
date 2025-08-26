#!/usr/bin/env python3
"""
Test script to validate the FAPS Knowledge Assistant components
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        import src.config
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        import src.localization
        print("✅ Localization module imported successfully")
    except Exception as e:
        print(f"❌ Localization import failed: {e}")
        return False
    
    try:
        import src.auth
        print("✅ Authentication module imported successfully")
    except Exception as e:
        print(f"❌ Authentication import failed: {e}")
        return False
    
    try:
        import src.nas_connector
        print("✅ NAS connector module imported successfully")
    except Exception as e:
        print(f"❌ NAS connector import failed: {e}")
        return False
    
    try:
        import src.web_scraper
        print("✅ Web scraper module imported successfully")
    except Exception as e:
        print(f"❌ Web scraper import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of core components"""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from src.config import settings
        print(f"✅ Settings loaded: {settings.default_language}")
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False
    
    try:
        from src.localization import localization
        text = localization.get_text("app_title")
        print(f"✅ Localization working: '{text}'")
    except Exception as e:
        print(f"❌ Localization test failed: {e}")
        return False
    
    try:
        from src.auth import auth_manager
        services = auth_manager.list_services()
        print(f"✅ Authentication manager initialized: {len(services)} services")
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False
    
    try:
        from src.nas_connector import NASConnector
        nas = NASConnector()
        # Test connection (will use mock data)
        status = nas.test_connection()
        print(f"✅ NAS connector initialized: connection status = {status}")
    except Exception as e:
        print(f"❌ NAS connector test failed: {e}")
        return False
    
    return True

def test_mock_data():
    """Test that mock data is available for development"""
    print("\n📊 Testing mock data availability...")
    
    try:
        from src.nas_connector import NASConnector
        nas = NASConnector()
        files = nas.list_files()
        print(f"✅ NAS mock files: {len(files)} files available")
        
        if files:
            content = nas.get_file_content(files[0]["path"])
            if content:
                print(f"✅ File content retrieval working: {len(content)} characters")
            else:
                print("⚠️ File content is empty")
    except Exception as e:
        print(f"❌ NAS mock data test failed: {e}")
        return False
    
    try:
        from src.web_scraper import web_scraper
        # Mock authentication for testing
        from src.auth import auth_manager
        auth_manager.store_token("wiki", "mock_token")
        auth_manager.store_token("intern_fau", "mock_token")
        
        content = web_scraper.get_all_content()
        print(f"✅ Web scraper mock data: {len(content)} pages")
    except Exception as e:
        print(f"❌ Web scraper mock data test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 FAPS Knowledge Assistant - Component Test Suite")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_basic_functionality():
        success = False
    
    if not test_mock_data():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! The system is ready for development.")
        print("\nNext steps:")
        print("1. Run 'docker-compose up' to start the full system")
        print("2. Open http://localhost:7860 to access the web interface")
        print("3. Complete the authentication setup for live data sources")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()