"""
Main Gradio application for FAPS Knowledge Assistant
"""
import gradio as gr
import logging
import os
from typing import List, Tuple, Dict, Any
from datetime import datetime

from src.config import settings
from src.localization import localization
from src.auth import auth_manager
from src.rag_system import get_rag_system
from src.nas_connector import NASConnector

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)


class FAPSKnowledgeApp:
    def __init__(self):
        self.chat_history = []
        self.nas_connector = NASConnector()
        
    def search_knowledge(self, question: str, language: str = "de") -> Tuple[str, str]:
        """
        Search the knowledge base and return response with sources
        
        Args:
            question: User question
            language: Response language
            
        Returns:
            Tuple of (response, sources_html)
        """
        if not question.strip():
            no_query_msg = localization.get_text("no_results") if language == "de" else "Please enter a question."
            return no_query_msg, ""
        
        try:
            # Query the RAG system
            rag_system = get_rag_system()
            result = rag_system.query(question, language)
            
            response = result.get("response", "")
            sources = result.get("sources", [])
            
            # Format sources as HTML
            sources_html = self._format_sources(sources, language)
            
            # Add to chat history
            self.chat_history.append({
                "question": question,
                "response": response,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "language": language
            })
            
            return response, sources_html
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            error_msg = localization.get_text("error_occurred") if language == "de" else "An error occurred."
            return error_msg, ""
    
    def _format_sources(self, sources: List[Dict], language: str) -> str:
        """Format sources as HTML"""
        if not sources:
            return ""
        
        sources_title = localization.get_text("sources_title") if language == "de" else "Sources"
        html = f"<h3>{sources_title}</h3><ul>"
        
        for source in sources:
            metadata = source.get("metadata", {})
            content_preview = source.get("content", "")[:150] + "..."
            
            if metadata.get("source") == "nas":
                # NAS file source
                file_name = metadata.get("file_name", "Unknown file")
                download_url = metadata.get("download_url", "#")
                html += f'<li><strong>{file_name}</strong><br>'
                html += f'<small>{content_preview}</small><br>'
                html += f'<a href="{download_url}" target="_blank">Download</a></li>'
            elif metadata.get("source") == "web":
                # Web page source
                title = metadata.get("title", "Unknown page")
                url = metadata.get("url", "#")
                html += f'<li><strong>{title}</strong><br>'
                html += f'<small>{content_preview}</small><br>'
                html += f'<a href="{url}" target="_blank">View page</a></li>'
            else:
                html += f'<li><small>{content_preview}</small></li>'
        
        html += "</ul>"
        return html
    
    def change_language(self, language: str):
        """Change the application language"""
        localization.set_language(language)
        return self._get_ui_texts(language)
    
    def _get_ui_texts(self, language: str) -> Dict[str, str]:
        """Get all UI texts for the current language"""
        return {
            "title": localization.get_text("app_title"),
            "description": localization.get_text("app_description"),
            "search_placeholder": localization.get_text("search_placeholder"),
            "search_button": localization.get_text("search_button"),
            "clear_button": localization.get_text("clear_button"),
            "language_label": localization.get_text("language_label"),
            "setup_title": localization.get_text("setup_title"),
            "response_title": localization.get_text("response_title"),
            "sources_title": localization.get_text("sources_title")
        }
    
    def setup_authentication(self, service: str, token: str) -> str:
        """Setup authentication for a service"""
        try:
            if auth_manager.store_token(service, token):
                success_msg = "Token gespeichert" if localization.current_language == "de" else "Token saved"
                return f"✅ {success_msg}"
            else:
                error_msg = "Fehler beim Speichern" if localization.current_language == "de" else "Error saving token"
                return f"❌ {error_msg}"
        except Exception as e:
            logger.error(f"Authentication setup failed: {e}")
            return f"❌ Error: {str(e)}"
    
    def test_nas_connection(self) -> str:
        """Test NAS connection"""
        try:
            if self.nas_connector.test_connection():
                success_msg = "NAS verbunden" if localization.current_language == "de" else "NAS connected"
                return f"✅ {success_msg}"
            else:
                error_msg = "NAS nicht erreichbar" if localization.current_language == "de" else "NAS not reachable"
                return f"❌ {error_msg}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_system_status(self) -> str:
        """Get system status information"""
        try:
            rag_system = get_rag_system()
            status = rag_system.get_system_status()
            nas_status = self.nas_connector.test_connection()
            auth_status = auth_manager.list_services()
            
            status_html = "<h3>System Status</h3>"
            status_html += f"<p>Vector Store: {'✅' if status['vector_store'] else '❌'}</p>"
            status_html += f"<p>Query Engine: {'✅' if status['query_engine'] else '❌'}</p>"
            status_html += f"<p>NAS Connection: {'✅' if nas_status else '❌'}</p>"
            
            status_html += "<h4>Authentication Status</h4>"
            for service, info in auth_status.items():
                status_html += f"<p>{info['name']}: {'✅' if info['authenticated'] else '❌'}</p>"
            
            return status_html
            
        except Exception as e:
            return f"Error getting status: {str(e)}"
    
    def refresh_index(self) -> str:
        """Refresh the document index"""
        try:
            rag_system = get_rag_system()
            if rag_system.refresh_index():
                success_msg = "Index aktualisiert" if localization.current_language == "de" else "Index refreshed"
                return f"✅ {success_msg}"
            else:
                error_msg = "Fehler beim Aktualisieren" if localization.current_language == "de" else "Error refreshing index"
                return f"❌ {error_msg}"
        except Exception as e:
            return f"❌ Error: {str(e)}"


def create_interface():
    """Create the Gradio interface"""
    app = FAPSKnowledgeApp()
    
    # Custom CSS for FAPS branding
    css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .logo-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #003366, #0066cc);
        color: white;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    .status-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(css=css, title="FAPS Wissenssystem") as interface:
        # Header with FAPS logo
        with gr.Row():
            gr.HTML("""
                <div class="logo-container">
                    <img src="/file/faps_logo.png" alt="FAPS Logo" style="height: 80px; margin-bottom: 10px;">
                    <h1>FAPS Wissenssystem</h1>
                    <p>Lokales RAG-System für FAPS Datenquellen</p>
                </div>
            """)
        
        # Language selection
        with gr.Row():
            language_dropdown = gr.Dropdown(
                choices=[("Deutsch", "de"), ("English", "en")],
                value="de",
                label="Sprache / Language",
                interactive=True
            )
        
        # Main search interface
        with gr.Tab("Suche / Search"):
            with gr.Row():
                with gr.Column(scale=4):
                    question_input = gr.Textbox(
                        label="Frage / Question",
                        placeholder="Stellen Sie Ihre Frage...",
                        lines=2
                    )
                with gr.Column(scale=1):
                    search_button = gr.Button("Suchen", variant="primary")
                    clear_button = gr.Button("Löschen")
            
            with gr.Row():
                with gr.Column(scale=2):
                    response_output = gr.Textbox(
                        label="Antwort / Response",
                        lines=10,
                        interactive=False
                    )
                with gr.Column(scale=1):
                    sources_output = gr.HTML(
                        label="Quellen / Sources"
                    )
        
        # Setup and configuration
        with gr.Tab("Einrichtung / Setup"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### NAS Verbindung / NAS Connection")
                    nas_test_button = gr.Button("NAS testen / Test NAS")
                    nas_status_output = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Authentifizierung / Authentication")
                    service_dropdown = gr.Dropdown(
                        choices=[("Wiki", "wiki"), ("Intern.FAU", "intern_fau")],
                        label="Service",
                        value="wiki"
                    )
                    token_input = gr.Textbox(
                        label="Token",
                        type="password",
                        placeholder="Authentication token..."
                    )
                    save_token_button = gr.Button("Token speichern / Save Token")
                    auth_status_output = gr.Textbox(label="Status", interactive=False)
        
        # System status and maintenance
        with gr.Tab("System"):
            with gr.Row():
                with gr.Column():
                    status_button = gr.Button("Status abrufen / Get Status")
                    refresh_button = gr.Button("Index aktualisieren / Refresh Index")
                with gr.Column():
                    system_status_output = gr.HTML(label="System Status")
                    maintenance_output = gr.Textbox(label="Maintenance", interactive=False)
        
        # Event handlers
        search_button.click(
            fn=app.search_knowledge,
            inputs=[question_input, language_dropdown],
            outputs=[response_output, sources_output]
        )
        
        clear_button.click(
            fn=lambda: ("", ""),
            outputs=[question_input, response_output]
        )
        
        save_token_button.click(
            fn=app.setup_authentication,
            inputs=[service_dropdown, token_input],
            outputs=[auth_status_output]
        )
        
        nas_test_button.click(
            fn=app.test_nas_connection,
            outputs=[nas_status_output]
        )
        
        status_button.click(
            fn=app.get_system_status,
            outputs=[system_status_output]
        )
        
        refresh_button.click(
            fn=app.refresh_index,
            outputs=[maintenance_output]
        )
        
        # Submit on Enter
        question_input.submit(
            fn=app.search_knowledge,
            inputs=[question_input, language_dropdown],
            outputs=[response_output, sources_output]
        )
    
    return interface


if __name__ == "__main__":
    # Initialize the RAG system
    logger.info("Initializing FAPS Knowledge Assistant...")
    
    # Index documents on startup (skip if services are not available)
    logger.info("Indexing documents...")
    try:
        rag_system = get_rag_system()
        rag_system.index_documents()
        logger.info("Document indexing completed")
    except Exception as e:
        logger.warning(f"Document indexing failed (will work in demo mode): {e}")
    
    # Create and launch the interface
    interface = create_interface()
    
    logger.info(f"Starting Gradio server on {settings.gradio_server_name}:{settings.gradio_server_port}")
    
    interface.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        share=False,
        debug=False
    )