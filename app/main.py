import streamlit as st
import os
from pathlib import Path
from src.ui.german_interface import render_main_interface
from src.database.lance_connector import LanceDBConnector
from src.security.auth_manager import AuthManager

# Page configuration
st.set_page_config(
    page_title="FAPS Knowledge Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "FAPS Knowledge Assistant - Ein lokales RAG-System für FAPS Ressourcen"
    }
)

# Load CSS for German UI styling
def load_css():
    css = """
    <style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        font-family: 'Arial', sans-serif;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .faps-description {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #28a745;
    }
    
    .status-offline {
        background-color: #dc3545;
    }
    
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 0.5rem;
        padding: 1rem;
        min-height: 400px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    load_css()
    
    # Header with FAPS logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Display FAPS logo
        logo_path = Path(__file__).parent / ".." / "faps_logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=200)
    
    # Main title and description
    st.markdown("""
    <div class="main-header">
        <h1>FAPS Knowledge Assistant</h1>
    </div>
    
    <div class="faps-description">
        <p>Intelligenter Assistent für FAPS-Ressourcen mit natürlicher Sprachverarbeitung</p>
        <p>Durchsuchen Sie NAS-Dateien, Wiki-Inhalte und Webressourcen mit einfachen Fragen auf Deutsch</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    if 'db_connector' not in st.session_state:
        st.session_state.db_connector = LanceDBConnector()
    
    # Sidebar for system status and configuration
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        # Check service status
        ollama_status = check_ollama_status()
        lancedb_status = check_lancedb_status()
        nas_status = check_nas_status()
        
        st.markdown(f"""
        <div class="sidebar-section">
            <p><span class="status-indicator {'status-online' if ollama_status else 'status-offline'}"></span>Ollama LLM</p>
            <p><span class="status-indicator {'status-online' if lancedb_status else 'status-offline'}"></span>LanceDB</p>
            <p><span class="status-indicator {'status-online' if nas_status else 'status-offline'}"></span>FAPS NAS</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Datenquellen")
        st.markdown("""
        - **NAS**: FAPS Dateien (nur Lesezugriff)
        - **Wiki**: wiki.faps.uni-erlangen.de
        - **FAU Internal**: www.intern.fau.de
        - **IDM FAU**: www.idm.fau.de
        """)
        
        st.markdown("### ⚙️ Einstellungen")
        
        # Language selection (fixed to German)
        st.selectbox("Sprache", ["Deutsch"], disabled=True)
        
        # Search settings
        max_results = st.slider("Max. Suchergebnisse", 5, 50, 10)
        include_nas = st.checkbox("NAS durchsuchen", True)
        include_wiki = st.checkbox("Wiki durchsuchen", True)
        include_web = st.checkbox("Web-Ressourcen durchsuchen", True)
        
        st.session_state.search_settings = {
            'max_results': max_results,
            'include_nas': include_nas,
            'include_wiki': include_wiki,
            'include_web': include_web
        }
    
    # Main interface
    render_main_interface()

def check_ollama_status():
    """Check if Ollama service is accessible"""
    try:
        import requests
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        response = requests.get(f"{ollama_host}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_lancedb_status():
    """Check if LanceDB service is accessible"""
    try:
        # Simple connection test
        return st.session_state.db_connector.test_connection()
    except:
        return False

def check_nas_status():
    """Check if NAS mount is accessible"""
    nas_path = Path("/mnt/nas")
    return nas_path.exists() and nas_path.is_dir()

if __name__ == "__main__":
    main()