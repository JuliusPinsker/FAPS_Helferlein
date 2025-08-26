#!/usr/bin/env python3
"""
Demo script to show FAPS Knowledge Assistant interface
(requires gradio: pip install gradio)
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_interface():
    """Create a demo version of the interface for testing"""
    
    try:
        import gradio as gr
    except ImportError:
        print("❌ Gradio not installed. Run: pip install gradio")
        sys.exit(1)
    
    # Import our modules
    from src.localization import localization
    from src.auth import auth_manager
    from src.nas_connector import NASConnector
    
    # Initialize components
    nas = NASConnector()
    
    def demo_search(question, language):
        """Demo search function with mock responses"""
        if not question.strip():
            return "Bitte stellen Sie eine Frage." if language == "de" else "Please ask a question.", ""
        
        # Mock response based on question content
        if "FAPS" in question or "Lehrstuhl" in question:
            if language == "de":
                response = f"FAPS ist der Lehrstuhl für Fertigungsautomatisierung und Produktionssystematik an der FAU. Die Frage '{question}' bezieht sich auf unsere Kernkompetenzen in der Automatisierung und Fertigungstechnik."
            else:
                response = f"FAPS is the Chair of Manufacturing Automation and Production Systems at FAU. Your question '{question}' relates to our core competencies in automation and manufacturing technology."
        else:
            if language == "de":
                response = f"Vielen Dank für Ihre Frage: '{question}'. Das System sucht in den verfügbaren Datenquellen und würde hier eine relevante Antwort basierend auf NAS-Dateien und Webinhalten liefern."
            else:
                response = f"Thank you for your question: '{question}'. The system searches available data sources and would provide a relevant answer based on NAS files and web content here."
        
        # Mock sources
        sources_html = """
        <h3>Quellen / Sources</h3>
        <ul>
            <li><strong>Forschungsprojekt_2024.pdf</strong><br>
                <small>FAPS Forschungsprojekt: Automatisierung in der Produktion...</small><br>
                <a href="smb://fapsroot.faps.uni-erlangen.de/Forschung/Projekte/Forschungsprojekt_2024.pdf">Download</a>
            </li>
            <li><strong>FAPS Lehrstuhl Übersicht</strong><br>
                <small>Der Lehrstuhl für Fertigungsautomatisierung und Produktionssystematik...</small><br>
                <a href="https://wiki.faps.uni-erlangen.de/lehrstuhl/uebersicht">View page</a>
            </li>
        </ul>
        """
        
        return response, sources_html
    
    def demo_test_nas():
        """Demo NAS connection test"""
        return "✅ NAS verbunden (Demo-Modus)"
    
    def demo_save_token(service, token):
        """Demo token saving"""
        if token.strip():
            return f"✅ Token für {service} gespeichert (Demo-Modus)"
        else:
            return "❌ Bitte geben Sie einen Token ein"
    
    # Custom CSS with FAPS branding
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
    .demo-notice {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        color: #856404;
    }
    """
    
    # Create interface
    with gr.Blocks(css=css, title="FAPS Wissenssystem (Demo)") as demo:
        # Header
        gr.HTML("""
            <div class="logo-container">
                <h1>🏭 FAPS Wissenssystem</h1>
                <p>Lokales RAG-System für FAPS Datenquellen</p>
            </div>
            <div class="demo-notice">
                <strong>Demo-Modus:</strong> Dies ist eine Funktionsdemonstration mit Mock-Daten. 
                Für den Vollbetrieb starten Sie das System mit Docker: <code>docker-compose up</code>
            </div>
        """)
        
        # Language selection
        language_dropdown = gr.Dropdown(
            choices=[("Deutsch", "de"), ("English", "en")],
            value="de",
            label="Sprache / Language"
        )
        
        # Main interface
        with gr.Tab("Suche / Search"):
            with gr.Row():
                with gr.Column(scale=4):
                    question_input = gr.Textbox(
                        label="Frage / Question",
                        placeholder="Stellen Sie Ihre Frage über FAPS...",
                        lines=2
                    )
                with gr.Column(scale=1):
                    search_button = gr.Button("🔍 Suchen", variant="primary")
                    clear_button = gr.Button("🗑️ Löschen")
            
            with gr.Row():
                with gr.Column(scale=2):
                    response_output = gr.Textbox(
                        label="Antwort / Response",
                        lines=8,
                        interactive=False
                    )
                with gr.Column(scale=1):
                    sources_output = gr.HTML(label="Quellen / Sources")
        
        # Setup tab
        with gr.Tab("Einrichtung / Setup"):
            gr.Markdown("### Demo-Modus Einstellungen")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### NAS Verbindung")
                    nas_test_button = gr.Button("NAS testen")
                    nas_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    gr.Markdown("#### Authentifizierung")
                    service_dropdown = gr.Dropdown(
                        choices=[("Wiki", "wiki"), ("Intern.FAU", "intern_fau")],
                        label="Service",
                        value="wiki"
                    )
                    token_input = gr.Textbox(
                        label="Token (Demo)",
                        placeholder="demo_token_123",
                        type="password"
                    )
                    save_button = gr.Button("Token speichern")
                    auth_status = gr.Textbox(label="Status", interactive=False)
        
        # System info
        with gr.Tab("System Info"):
            gr.HTML(f"""
                <h3>System Information</h3>
                <ul>
                    <li><strong>Modus:</strong> Demo (Mock-Daten)</li>
                    <li><strong>Sprache:</strong> {localization.current_language}</li>
                    <li><strong>NAS Host:</strong> fapsroot.faps.uni-erlangen.de</li>
                    <li><strong>Verfügbare Services:</strong> Wiki, Intern.FAU</li>
                    <li><strong>LLM Model:</strong> gpt-oss:20b (nicht verfügbar im Demo)</li>
                </ul>
                
                <h3>Vollversion starten</h3>
                <p>Für die vollständige Funktionalität:</p>
                <ol>
                    <li>Docker starten: <code>docker-compose up</code></li>
                    <li>Modelle laden: <code>./pull_models.sh</code></li>
                    <li>Interface öffnen: <a href="http://localhost:7860">http://localhost:7860</a></li>
                </ol>
            """)
        
        # Event handlers
        search_button.click(
            fn=demo_search,
            inputs=[question_input, language_dropdown],
            outputs=[response_output, sources_output]
        )
        
        clear_button.click(
            fn=lambda: ("", "", ""),
            outputs=[question_input, response_output, sources_output]
        )
        
        nas_test_button.click(
            fn=demo_test_nas,
            outputs=[nas_status]
        )
        
        save_button.click(
            fn=demo_save_token,
            inputs=[service_dropdown, token_input],
            outputs=[auth_status]
        )
        
        question_input.submit(
            fn=demo_search,
            inputs=[question_input, language_dropdown],
            outputs=[response_output, sources_output]
        )
    
    return demo

if __name__ == "__main__":
    print("🚀 Starting FAPS Knowledge Assistant Demo...")
    
    demo = demo_interface()
    
    print("📱 Demo interface will open at: http://localhost:7860")
    print("🔧 This is a demonstration with mock data")
    print("🐳 For full functionality, use: docker-compose up")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )