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

## Schnellstart

### Voraussetzungen

#### Grundausstattung
- Docker und Docker Compose
- Mindestens 8GB RAM (für gpt-oss:20b Modell)
- 20GB freier Speicherplatz für Modelle und Daten

#### GPU-Unterstützung (empfohlen für bessere Performance)
Für optimale Leistung mit dem gpt-oss:20b Modell wird eine NVIDIA GPU mit CUDA-Unterstützung empfohlen.

**NVIDIA Container Toolkit Installation (Ubuntu/WSL2):**

1. **NVIDIA GPG-Schlüssel und Repository hinzufügen:**
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

2. **Paketlisten aktualisieren:**
```bash
sudo apt-get update
```

3. **NVIDIA Container Toolkit installieren:**
```bash
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
sudo apt-get install -y \
    nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
    libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
```

4. **Docker für NVIDIA Runtime konfigurieren:**
```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

5. **GPU-Zugriff testen:**
```bash
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

**Hinweis für WSL2-Benutzer:**
- Stellen Sie sicher, dass WSL2 mit GPU-Passthrough konfiguriert ist
- Windows 11 oder Windows 10 mit aktuellen Updates erforderlich
- NVIDIA-Treiber für Windows müssen installiert sein

#### Netzwerk-Zugriff
- Zugriff auf das FAU-Netzwerk oder VPN-Verbindung
- Internetverbindung für Modell-Downloads

### Installation

1. **Repository klonen:**
```bash
git clone https://github.com/JuliusPinsker/FAPS_Helferlein.git
cd FAPS_Helferlein
```

2. **System initialisieren:**
```bash
./setup.sh
```

3. **Services starten:**
```bash
docker-compose up -d
```

4. **Modelle herunterladen:**
```bash
./pull_models.sh
```

5. **Webinterface öffnen:**
   - Navigieren Sie zu `http://localhost:7860`
   - Führen Sie den Onboarding-Prozess durch

## Onboarding

Beim ersten Start müssen Sie die Authentifizierung konfigurieren:

### 1. NAS-Verbindung
- Automatische Verbindung zu `\\fapsroot.faps.uni-erlangen.de`
- Nur Lesezugriff (sicherheitsbedingt)

### 2. Web-Authentifizierung
Für geschützte Webressourcen:

**Wiki-Authentifizierung:**
1. Öffnen Sie `https://wiki.faps.uni-erlangen.de/` in einem neuen Tab
2. Melden Sie sich mit Ihren FAU-Zugangsdaten an
3. Kopieren Sie den Session-Cookie
4. Fügen Sie ihn in das Token-Feld ein

**Intern.FAU-Authentifizierung:**
1. Öffnen Sie `https://www.intern.fau.de/` in einem neuen Tab
2. Melden Sie sich an
3. Kopieren Sie den Session-Cookie oder Bearer-Token
4. Fügen Sie ihn in das Token-Feld ein

## Konfiguration

### Umgebungsvariablen (.env)
```bash
# LLM-Konfiguration
OLLAMA_MODEL=gpt-oss:20b

# NAS-Konfiguration
NAS_HOST=fapsroot.faps.uni-erlangen.de

# Web-URLs
WIKI_URL=https://wiki.faps.uni-erlangen.de/
INTERN_FAU_URL=https://www.intern.fau.de/

# Anwendungseinstellungen
DEFAULT_LANGUAGE=de
LOG_LEVEL=INFO
```

### Sprachen
- **Standard**: Deutsch (de)
- **Verfügbar**: Englisch (en)
- Umschaltung über die Benutzeroberfläche

## Entwicklung

### VS Code Development Container
```bash
# Mit VS Code öffnen
code .
# "Reopen in Container" auswählen
```

### Lokale Entwicklung
```bash
# Python-Abhängigkeiten installieren
pip install -r requirements.txt

# Externe Services starten
docker-compose up chromadb ollama -d

# Anwendung starten
python app.py
```

### Projektstruktur
```
├── app.py                 # Hauptanwendung (Gradio Interface)
├── src/
│   ├── config.py         # Konfigurationsmanagement
│   ├── localization.py   # Mehrsprachigkeit
│   ├── auth.py           # Authentifizierungssystem
│   ├── nas_connector.py  # NAS-Anbindung
│   ├── web_scraper.py    # Web-Scraping
│   └── rag_system.py     # RAG-Engine
├── locales/              # Übersetzungsdateien
├── docker-compose.yml    # Container-Orchestrierung
└── .devcontainer/        # VS Code Dev Container
```

## Sicherheit

- **Nur-Lese-Zugriff** auf NAS-Ressourcen
- **Token-basierte** Authentifizierung (keine Passwort-Speicherung)
- **Lokale Verarbeitung** (keine Cloud-Services)
- **Isolierte Container** für alle Services
- **CSRF-Schutz** für Web-Authentifizierung

## Fehlerbehebung

### Container starten nicht
```bash
# Logs überprüfen
docker-compose logs

# Services neu starten
docker-compose restart
```

### Modell-Download schlägt fehl
```bash
# Manueller Download
docker-compose exec ollama ollama pull gpt-oss:20b
```

### NAS-Verbindung funktioniert nicht
- Überprüfen Sie die Netzwerkverbindung zu `fapsroot.faps.uni-erlangen.de`
- Stellen Sie sicher, dass Sie im FAU-Netzwerk oder VPN sind

### Authentifizierung schlägt fehl
- Überprüfen Sie die Token-Gültigkeit
- Erneuern Sie die Session-Cookies bei Bedarf

## Support

Bei Problemen oder Fragen:
1. Überprüfen Sie die Logs in `logs/app.log`
2. Konsultieren Sie die Dokumentation
3. Erstellen Sie ein Issue im GitHub-Repository

## Lizenz

Dieses Projekt steht unter der GPL-3.0 Lizenz. Siehe [LICENSE](LICENSE) für Details.