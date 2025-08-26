# FAPS Wissenssystem

Ein lokales Retrieval-Augmented Generation (RAG) System zur Organisation und zum Zugriff auf Informationen aus FAPS NAS und Webressourcen.

## Funktionen

- 🔍 Durchsuche mehrere Datenquellen mit natürlicher Sprache
- 🔗 Erhalte direkte Download-Links zu relevanten Dateien auf dem NAS
- 🌐 Greife auf Informationen aus geschützten Webressourcen zu
- 🖥️ Vollständig lokale Bereitstellung für Datenschutz
- 🐳 Docker-basiertes Setup für einfache Implementierung
- 🔒 Sichere token-basierte Authentifizierung
- 🌍 Verfügbar auf Deutsch und Englisch

## Datenquellen

- **NAS**: `\\fapsroot.faps.uni-erlangen.de` (nur Lesezugriff)
- **Wiki**: `https://wiki.faps.uni-erlangen.de/`
- **Internes FAU**: `https://www.intern.fau.de/`

## Architektur

- **Frontend**: Gradio Webinterface mit FAPS Logo
- **RAG-Engine**: LlamaIndex für Dokumentenverarbeitung und Retrieval
- **Vektor-DB**: ChromaDB für Embedding-Speicherung
- **LLM**: Ollama mit gpt-oss:20b
- **Datenanbindungen**: Benutzerdefinierte Konnektoren für NAS und Webressourcen
- **Authentifizierung**: Browser-Token-basierter Zugriff für gesicherte Ressourcen

## Setup

1. Repository klonen
2. `docker-compose up` ausführen
3. Webinterface unter `http://localhost:7860` aufrufen
4. Onboarding-Prozess durchführen, um Authentifizierungs-Token einzurichten

## Onboarding

Erstbenutzer müssen einen Onboarding-Prozess abschließen:
1. Zugriff auf das Webinterface
2. Für Webressourcen, die eine Authentifizierung erfordern:
   - Bei jedem Dienst in einem separaten Browser-Tab anmelden
   - Authentifizierungs-Token durch den geführten Prozess generieren und bereitstellen
   - Token werden sicher im lokalen Speicher des Browsers gespeichert

## Konfiguration

Die Anwendung verwendet folgende Standardeinstellungen:

```
# LLM-Konfiguration
OLLAMA_MODEL=gpt-oss:20b
```

## Entwicklung

Dieses Projekt enthält eine `.devcontainer`-Konfiguration für die einfache Entwicklung in VS Code.

## Sprache

Die Standardsprache der Benutzeroberfläche ist Deutsch. Die Sprache kann über die Einstellungen auf Englisch umgestellt werden.