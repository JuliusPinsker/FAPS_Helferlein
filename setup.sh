#!/bin/bash

# FAPS Wissenssystem Setup Script
# Vollständig containerisierte Lösung - KEINE lokalen Python-Abhängigkeiten erforderlich

set -e

echo "🚀 FAPS Wissenssystem Setup wird gestartet..."

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen für farbige Ausgaben
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Überprüfe Docker Installation
echo "📋 Überprüfe Systemvoraussetzungen..."

if ! command -v docker &> /dev/null; then
    print_error "Docker ist nicht installiert. Bitte installieren Sie Docker zuerst."
    echo "Installation: https://docs.docker.com/engine/install/"
    exit 1
fi
print_status "Docker ist installiert"

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose ist nicht installiert."
    echo "Installation: https://docs.docker.com/compose/install/"
    exit 1
fi
print_status "Docker Compose ist verfügbar"

# Überprüfe NVIDIA GPU Support (optional)
if command -v nvidia-smi &> /dev/null; then
    print_status "NVIDIA GPU erkannt"
    
    # Teste Docker GPU Support
    echo "🧪 Teste Docker GPU Support..."
    if docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi &> /dev/null; then
        print_status "Docker GPU Support ist aktiv"
    else
        print_warning "Docker GPU Support ist nicht konfiguriert."
        print_info "Führen Sie die GPU-Setup-Anweisungen aus dem README aus."
        print_info "System wird im CPU-Modus fortfahren."
    fi
else
    print_warning "Keine NVIDIA GPU erkannt. System läuft im CPU-Modus."
fi

# Erstelle erforderliche Verzeichnisse
echo "📁 Erstelle Verzeichnisstruktur..."
mkdir -p data/{vectors,cache,uploads}
mkdir -p logs
mkdir -p config
mkdir -p locales/{de,en}
print_status "Verzeichnisse erstellt"

# Erstelle .env Datei falls nicht vorhanden
if [ ! -f .env ]; then
    echo "📝 Erstelle .env Konfigurationsdatei..."
    cat > .env << EOF
# LLM-Konfiguration
OLLAMA_MODEL=gpt-oss:20b
OLLAMA_HOST=ollama
OLLAMA_PORT=11434

# ChromaDB-Konfiguration
CHROMA_HOST=chromadb
CHROMA_PORT=8000

# NAS-Konfiguration
NAS_HOST=fapsroot.faps.uni-erlangen.de

# Web-URLs
WIKI_URL=https://wiki.faps.uni-erlangen.de/
INTERN_FAU_URL=https://www.intern.fau.de/

# Anwendungseinstellungen
DEFAULT_LANGUAGE=de
LOG_LEVEL=INFO
DEBUG=false

# Gradio-Konfiguration
GRADIO_HOST=0.0.0.0
GRADIO_PORT=7860
EOF
    print_status ".env Datei erstellt"
else
    print_status ".env Datei bereits vorhanden"
fi

# Überprüfe Docker Images
echo "🐳 Baue Docker Images..."
if docker-compose build; then
    print_status "Docker Images erfolgreich gebaut"
else
    print_error "Fehler beim Bauen der Docker Images"
    print_info "Überprüfen Sie die Logs für Details"
    exit 1
fi

echo ""
print_info "🎯 WICHTIG: Dieses System ist vollständig containerisiert!"
print_info "   → Keine lokalen Python-Installationen erforderlich"
print_info "   → Alle Abhängigkeiten werden in Docker-Containern verwaltet"
print_info "   → Führen Sie NIEMALS 'pip install' auf Ihrem Host-System aus"
echo ""

# Starte Services
echo "� Starte Services..."
if docker-compose up -d; then
    print_status "Services erfolgreich gestartet"
else
    print_error "Fehler beim Starten der Services"
    exit 1
fi

# Warte auf Services
echo "⏳ Warte auf Service-Initialisierung..."
sleep 15

# Überprüfe Service-Status
echo "🔍 Überprüfe Service-Status..."

# ChromaDB
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null; then
    print_status "ChromaDB ist bereit (Port 8000)"
else
    print_warning "ChromaDB ist noch nicht bereit"
fi

# Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_status "Ollama ist bereit (Port 11434)"
else
    print_warning "Ollama ist noch nicht bereit"
fi

# App (Gradio)
if curl -s http://localhost:7860 > /dev/null; then
    print_status "Web-Interface ist bereit (Port 7860)"
else
    print_warning "Web-Interface ist noch nicht bereit"
    print_info "Überprüfen Sie 'docker-compose logs app' für Details"
fi

echo ""
echo "🎉 Setup abgeschlossen!"
echo ""
echo "📱 Nächste Schritte:"
echo "1. Öffnen Sie http://localhost:7860 in Ihrem Browser"
echo "2. Führen Sie den Onboarding-Prozess durch"
echo "3. Laden Sie das gpt-oss:20b Modell herunter: ./pull_models.sh"
echo ""
echo "🔧 Nützliche Befehle:"
echo "   docker-compose ps              # Service-Status anzeigen"
echo "   docker-compose logs app        # App-Logs anzeigen"
echo "   docker-compose restart         # Services neu starten"
echo "   docker-compose down            # Services stoppen"
echo ""
echo "📚 Weitere Informationen finden Sie im README.md"
echo ""
print_info "🐳 Alles läuft in Containern - keine lokalen Python-Änderungen erforderlich!"