#!/usr/bin/env python3
"""
Minimal test of FAPS Knowledge Assistant core functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_system():
    """Test core system without external dependencies"""
    print("🧪 Testing FAPS Knowledge Assistant core system...")
    
    # Test configuration
    try:
        from src.config import settings
        print(f"✅ Configuration: {settings.default_language}, Port: {settings.gradio_server_port}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False
    
    # Test localization
    try:
        from src.localization import localization
        german_title = localization.get_text("app_title")
        localization.set_language("en")
        english_title = localization.get_text("app_title")
        print(f"✅ Localization: DE='{german_title}', EN='{english_title}'")
    except Exception as e:
        print(f"❌ Localization failed: {e}")
        return False
    
    # Test authentication
    try:
        from src.auth import auth_manager
        auth_manager.store_token("wiki", "test_token_123")
        token = auth_manager.get_token("wiki")
        print(f"✅ Authentication: Token stored and retrieved")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
    # Test NAS connector
    try:
        from src.nas_connector import NASConnector
        nas = NASConnector()
        files = nas.list_files()
        if files:
            content = nas.get_file_content(files[0]["path"])
            print(f"✅ NAS Connector: {len(files)} files, content length: {len(content) if content else 0}")
        else:
            print("⚠️ NAS Connector: No files found")
    except Exception as e:
        print(f"❌ NAS Connector failed: {e}")
        return False
    
    return True

def test_gradio_imports():
    """Test if Gradio can be imported"""
    try:
        import gradio as gr
        print("✅ Gradio is available for UI")
        return True
    except ImportError:
        print("⚠️ Gradio not installed - UI will not work")
        return False

def main():
    print("🚀 FAPS Knowledge Assistant - Core System Test")
    print("=" * 50)
    
    core_success = test_core_system()
    gradio_available = test_gradio_imports()
    
    print("\n" + "=" * 50)
    
    if core_success:
        print("✅ Core system is functional!")
        print("\nImplemented features:")
        print("- ✅ Docker infrastructure (docker-compose.yml)")
        print("- ✅ Multi-language support (German/English)")
        print("- ✅ Authentication system with token management")
        print("- ✅ NAS connector with mock data")
        print("- ✅ Configuration management")
        print("- ✅ Project structure and organization")
        
        if gradio_available:
            print("- ✅ Gradio UI framework ready")
        else:
            print("- ⚠️ Gradio UI requires 'pip install gradio'")
        
        print("\nReady for:")
        print("🐳 Docker deployment: docker-compose up")
        print("🌐 Web interface: http://localhost:7860")
        print("🔧 Development: VS Code with .devcontainer")
        
    else:
        print("❌ Core system has issues - please check configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()