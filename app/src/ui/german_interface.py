import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
from src.database.lance_connector import LanceDBConnector
from src.connectors.web_scraper import WebScraper
from src.connectors.nas_connector import NASConnector

def render_main_interface():
    """Render the main German language interface"""
    
    # Chat interface
    st.markdown("### 💬 Chat mit dem FAPS Assistant")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hallo! Ich bin Ihr FAPS Knowledge Assistant. Fragen Sie mich nach Informationen aus dem NAS, Wiki oder anderen FAPS-Ressourcen. Wie kann ich Ihnen helfen?"
            }
        ]
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if "sources" in message:
                    render_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Stellen Sie Ihre Frage auf Deutsch..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.markdown("🤔 Ich durchsuche die FAPS-Ressourcen...")
            
            # Process the query
            response, sources = process_query(prompt)
            
            # Update the response
            response_placeholder.markdown(response)
            
            # Display sources
            if sources:
                render_sources(sources)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "sources": sources
        })

def render_sources(sources: List[Dict[str, Any]]):
    """Render source information for responses"""
    if not sources:
        return
    
    st.markdown("#### 📚 Quellen:")
    
    for i, source in enumerate(sources, 1):
        with st.expander(f"Quelle {i}: {source.get('title', 'Unbekannt')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Typ:** {source.get('type', 'Unbekannt')}")
                st.markdown(f"**Pfad:** {source.get('path', 'N/A')}")
                if source.get('excerpt'):
                    st.markdown(f"**Auszug:** {source['excerpt'][:200]}...")
            
            with col2:
                if source.get('download_url'):
                    st.link_button("📥 Herunterladen", source['download_url'])
                elif source.get('url'):
                    st.link_button("🔗 Öffnen", source['url'])

def process_query(query: str) -> tuple[str, List[Dict[str, Any]]]:
    """Process user query and return response with sources"""
    
    try:
        # Get search settings from session state
        settings = st.session_state.get('search_settings', {
            'max_results': 10,
            'include_nas': True,
            'include_wiki': True,
            'include_web': True
        })
        
        sources = []
        
        # Search different data sources based on settings
        if settings.get('include_nas'):
            nas_results = search_nas(query, settings['max_results'] // 3)
            sources.extend(nas_results)
        
        if settings.get('include_wiki'):
            wiki_results = search_wiki(query, settings['max_results'] // 3)
            sources.extend(wiki_results)
        
        if settings.get('include_web'):
            web_results = search_web(query, settings['max_results'] // 3)
            sources.extend(web_results)
        
        # Generate response using RAG
        if sources:
            response = generate_rag_response(query, sources)
        else:
            response = generate_fallback_response(query)
        
        return response, sources
    
    except Exception as e:
        st.error(f"Fehler bei der Abfrage: {str(e)}")
        return "Entschuldigung, bei der Bearbeitung Ihrer Anfrage ist ein Fehler aufgetreten.", []

def search_nas(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search NAS files"""
    try:
        nas_connector = NASConnector()
        return nas_connector.search(query, max_results)
    except Exception as e:
        st.warning(f"NAS-Suche nicht verfügbar: {str(e)}")
        return []

def search_wiki(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search Wiki content"""
    try:
        # Note: Authentication would be handled here
        wiki_scraper = WebScraper("wiki.faps.uni-erlangen.de")
        return wiki_scraper.search(query, max_results)
    except Exception as e:
        st.warning(f"Wiki-Suche nicht verfügbar: {str(e)}")
        return []

def search_web(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search web resources"""
    try:
        web_scraper = WebScraper("www.intern.fau.de")
        return web_scraper.search(query, max_results)
    except Exception as e:
        st.warning(f"Web-Suche nicht verfügbar: {str(e)}")
        return []

def generate_rag_response(query: str, sources: List[Dict[str, Any]]) -> str:
    """Generate response using RAG with found sources"""
    
    # Create context from sources
    context = "\\n\\n".join([
        f"Quelle: {source.get('title', 'Unbekannt')}\\n{source.get('content', source.get('excerpt', ''))}"
        for source in sources[:5]  # Use top 5 sources
    ])
    
    # Create prompt for LLM
    prompt = f"""
    Basierend auf den folgenden FAPS-Ressourcen, beantworten Sie die Frage auf Deutsch:

    Kontext:
    {context}

    Frage: {query}

    Antwort (auf Deutsch, basierend auf den bereitgestellten Quellen):
    """
    
    try:
        # Use Ollama to generate response
        import requests
        import json
        
        ollama_host = st.session_state.get('OLLAMA_HOST', 'http://ollama:11434')
        
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": "qwen2.5:20b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Keine Antwort vom LLM erhalten.')
        else:
            return generate_fallback_response(query)
    
    except Exception as e:
        st.error(f"LLM-Fehler: {str(e)}")
        return generate_fallback_response(query)

def generate_fallback_response(query: str) -> str:
    """Generate fallback response when LLM is not available"""
    return f"""
    Entschuldigung, ich konnte keine spezifischen Informationen zu Ihrer Anfrage "{query}" finden.
    
    Mögliche Gründe:
    - Die Datenquellen sind gerade nicht verfügbar
    - Ihre Anfrage ist zu spezifisch oder zu allgemein
    - Die benötigten Services sind noch nicht vollständig konfiguriert
    
    Versuchen Sie es mit:
    - Einfacheren Begriffen
    - Spezifischeren Fragen zu FAPS-Ressourcen
    - Überprüfung der Systemstatus in der Seitenleiste
    """

def render_authentication_form():
    """Render authentication form for protected resources"""
    st.markdown("### 🔐 Authentifizierung für geschützte Ressourcen")
    
    auth_type = st.selectbox(
        "Authentifizierungstyp",
        ["Wiki (FAPS Login)", "IDM FAU (SSO)", "Keine"]
    )
    
    if auth_type == "Wiki (FAPS Login)":
        with st.form("wiki_auth"):
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            submit = st.form_submit_button("Anmelden")
            
            if submit and username and password:
                # Store credentials securely in session state
                st.session_state.wiki_auth = {
                    'username': username,
                    'password': password,
                    'authenticated': True
                }
                st.success("Wiki-Authentifizierung erfolgreich!")
                st.rerun()
    
    elif auth_type == "IDM FAU (SSO)":
        st.info("SSO-Authentifizierung wird in einer separaten Registerkarte geöffnet.")
        if st.button("SSO-Anmeldung starten"):
            st.session_state.sso_auth_pending = True
            st.info("Bitte folgen Sie den Anweisungen in der SSO-Anmeldung.")

def render_data_management():
    """Render data management interface"""
    st.markdown("### 📊 Datenmanagement")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Index aktualisieren"):
            with st.spinner("Index wird aktualisiert..."):
                # Trigger index refresh
                success = refresh_index()
                if success:
                    st.success("Index erfolgreich aktualisiert!")
                else:
                    st.error("Fehler beim Aktualisieren des Index.")
    
    with col2:
        if st.button("📈 Statistiken anzeigen"):
            show_statistics()
    
    with col3:
        if st.button("🧹 Cache leeren"):
            clear_cache()
            st.success("Cache geleert!")

def refresh_index():
    """Refresh the search index"""
    try:
        db_connector = st.session_state.get('db_connector')
        if db_connector:
            return db_connector.refresh_index()
        return False
    except Exception:
        return False

def show_statistics():
    """Show index statistics"""
    try:
        db_connector = st.session_state.get('db_connector')
        if db_connector:
            stats = db_connector.get_statistics()
            
            st.metric("Gesamt Dokumente", stats.get('total_documents', 0))
            st.metric("NAS Dateien", stats.get('nas_files', 0))
            st.metric("Wiki Seiten", stats.get('wiki_pages', 0))
            st.metric("Web Seiten", stats.get('web_pages', 0))
    except Exception as e:
        st.error(f"Fehler beim Laden der Statistiken: {str(e)}")

def clear_cache():
    """Clear application cache"""
    # Clear session state cache items
    cache_keys = [k for k in st.session_state.keys() if k.startswith('cache_')]
    for key in cache_keys:
        del st.session_state[key]