# FAPS Knowledge Assistant

Ein lokales Retrieval-Augmented Generation (RAG) System zur Organisation und zum Zugriff auf Informationen aus FAPS NAS und Webressourcen mittels phidata und LanceDB.

![FAPS Logo](faps_logo.png)

## Features

- 🔍 Durchsuchen mehrerer Datenquellen mit natürlicher Sprache
- 🔗 Direkte Download-Links zu relevanten Dateien auf dem NAS
- 🌐 Zugriff auf Informationen aus authentifizierten Webressourcen
- 🖥️ Vollständig lokale Bereitstellung für Datenschutz
- 🐳 Docker-basiertes Setup für einfache Bereitstellung

## Datenquellen

- **NAS**: `\\fapsroot.faps.uni-erlangen.de` (nur Lesezugriff)
- **Wiki**: `https://wiki.faps.uni-erlangen.de/` (erfordert Authentifizierung)
- **Internal FAU**: `https://www.intern.fau.de/` (öffentlicher Zugang)
- **IDM FAU**: `https://www.idm.fau.de/` (erfordert SSO-Authentifizierung)

## Architektur

- **Framework**: phidata für KI-Anwendungsentwicklung
- **Vector DB**: LanceDB für Embedding-Speicherung
- **LLM**: Ollama mit gpt-oss:20b Modell
- **Web Interface**: Integrierte phidata Web-UI in Deutsch
- **Datenanbindungen**: Spezifische Konnektoren für NAS und Webressourcen

## Setup

1. Dieses Repository klonen
2. Docker, Docker Compose und NVIDIA Docker-Tools installieren
3. `docker-compose up` ausführen
4. Zugriff auf die Weboberfläche unter `http://localhost:8501`

## Wichtig

Dieses System arbeitet komplett lokal und erfordert keine externen Abhängigkeiten außer Docker, Docker Compose und NVIDIA Docker-Tools.