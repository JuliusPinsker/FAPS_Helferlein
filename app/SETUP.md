# FAPS Knowledge Assistant - Setup Guide

## Überblick

Der FAPS Knowledge Assistant ist ein lokales RAG-System (Retrieval-Augmented Generation), das verschiedene FAPS-Datenquellen durchsucht und intelligente Antworten auf Deutsch liefert.

## Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │     Ollama      │    │    LanceDB     │
│   (Frontend)    │◄──►│   (LLM Model)   │    │ (Vector Store)  │
│   Port: 8501    │    │   Port: 11434   │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Connectors                              │
├─────────────────┬─────────────────┬─────────────────┬──────────┤
│      NAS        │      Wiki       │   FAU Internal  │   IDM    │
│   (Read-Only)   │ (Authenticated) │    (Public)     │  (SSO)   │
└─────────────────┴─────────────────┴─────────────────┴──────────┘
```

## Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- NVIDIA Docker (für GPU-Unterstützung)
- 8GB+ freier Speicher
- Internetverbindung für initiales Setup

### 1. Repository klonen

```bash
git clone https://github.com/JuliusPinsker/FAPS_Helferlein.git
cd FAPS_Helferlein
```

### 2. System starten

```bash
# Mit Docker Compose (empfohlen)
docker-compose up -d

# Logs anzeigen
docker-compose logs -f
```

### 3. Weboberfläche öffnen

Öffnen Sie http://localhost:8501 in Ihrem Browser.

## Entwicklungsumgebung

### Mit VS Code & Dev Containers

1. VS Code mit Dev Containers Extension installieren
2. Repository öffnen
3. "Reopen in Container" wählen
4. Automatisches Setup abwarten

### Lokale Entwicklung

```bash
cd app
pip install -r requirements.txt
streamlit run main.py
```

## Datenquellen konfigurieren

### NAS-Zugriff

Das System greift schreibgeschützt auf `\\fapsroot.faps.uni-erlangen.de` zu:

```yaml
# In docker-compose.yml bereits konfiguriert
volumes:
  nas_mount:
    driver: local
    driver_opts:
      type: cifs
      o: "domain=FAPS,username=guest,password=,ro,vers=3.0"
      device: "//fapsroot.faps.uni-erlangen.de"
```

### Wiki-Authentifizierung

1. In der Seitenleiste "Authentifizierung" auswählen
2. FAPS Wiki-Anmeldedaten eingeben
3. Anmeldung wird nur im Arbeitsspeicher gespeichert

### SSO für IDM FAU

1. SSO-Authentifizierung in der Seitenleiste starten
2. Weiterleitung zu sso.uni-erlangen.de folgen
3. Nach erfolgreicher Anmeldung zur App zurückkehren

## Verwendung

### Einfache Suche

```
Benutzer: "Wo finde ich Informationen über Fertigungsverfahren?"
System: Durchsucht NAS, Wiki und Webressourcen und liefert relevante Dokumente mit direkten Links.
```

### Erweiterte Funktionen

- **Multilinguale Suche**: Eingabe auf Deutsch, Antworten auf Deutsch
- **Quellenverfolgung**: Jede Antwort zeigt ihre Quellen
- **Direkte Downloads**: Links zu NAS-Dateien
- **Authentifizierte Inhalte**: Zugriff auf geschützte Wiki- und IDM-Inhalte

## System-Monitoring

### Status-Indikatoren

- 🟢 **Grün**: Service läuft und ist erreichbar
- 🔴 **Rot**: Service nicht verfügbar

### Statistiken

- Anzahl indexierter Dokumente
- Verteilung nach Datenquellen
- Systemressourcen

## Sicherheit

### Authentifizierung

- Anmeldedaten werden nur im Arbeitsspeicher gespeichert
- Automatische Session-Timeouts
- Keine persistente Speicherung von Passwörtern

### Datenschutz

- Komplett lokale Verarbeitung
- Keine externen API-Aufrufe (außer für initiale Model-Downloads)
- Kein Datenversand an Dritte

## Fehlerbehebung

### Häufige Probleme

#### Ollama startet nicht

```bash
# GPU-Support prüfen
docker run --rm --gpus all nvidia/cuda:12-base nvidia-smi

# Logs überprüfen
docker-compose logs ollama
```

#### NAS nicht erreichbar

```bash
# Netzwerk-Verbindung testen
ping fapsroot.faps.uni-erlangen.de

# Mount-Status prüfen
docker-compose exec phidata ls -la /mnt/nas
```

#### LanceDB Probleme

```bash
# Volume zurücksetzen
docker-compose down
docker volume rm faps_helferlein_lancedb_data
docker-compose up -d
```

### Debug-Modus

```bash
# Mit Debug-Logs starten
STREAMLIT_LOGGER_LEVEL=debug streamlit run main.py
```

## Konfiguration

### Umgebungsvariablen

```bash
# In .env Datei oder docker-compose.yml
OLLAMA_HOST=http://ollama:11434
LANCEDB_URI=http://lancedb:8080
UI_LANGUAGE=de
TZ=Europe/Berlin
```

### Anpassungen

#### Neue Datenquellen hinzufügen

1. Neuen Connector in `src/connectors/` erstellen
2. In `german_interface.py` integrieren
3. Indexierung in LanceDB hinzufügen

#### UI-Anpassungen

- Styling: CSS in `main.py` anpassen
- Sprache: Texte in `german_interface.py` ändern
- Logo: `faps_logo.png` ersetzen

## Performance-Optimierung

### Empfohlene Systemressourcen

- **CPU**: 8+ Cores
- **RAM**: 16GB+ (8GB für Ollama Model)
- **GPU**: NVIDIA mit 8GB+ VRAM
- **Storage**: 100GB+ freier Speicher

### Skalierung

```bash
# Mehr Worker für Streamlit
streamlit run main.py --server.maxUploadSize 1000

# LanceDB Performance tuning
# Indexing-Parameter in lance_connector.py anpassen
```

## Wartung

### Regelmäßige Updates

```bash
# Models aktualisieren
docker-compose exec ollama ollama pull qwen2.5:20b

# Index neu aufbauen
# Über die Weboberfläche: "Index aktualisieren"
```

### Backup

```bash
# LanceDB Daten sichern
docker run --rm -v faps_helferlein_lancedb_data:/data -v $(pwd):/backup alpine tar czf /backup/lancedb_backup.tar.gz /data

# Restore
docker run --rm -v faps_helferlein_lancedb_data:/data -v $(pwd):/backup alpine tar xzf /backup/lancedb_backup.tar.gz -C /
```

## Support

### Logs sammeln

```bash
# Alle Logs sammeln
docker-compose logs > faps_assistant_logs.txt

# Spezifische Services
docker-compose logs ollama > ollama_logs.txt
docker-compose logs phidata > app_logs.txt
```

### Entwicklung beitragen

1. Fork des Repositories
2. Feature-Branch erstellen
3. Tests ausführen: `python app/test_app.py`
4. Pull Request erstellen

## Lizenz

GNU General Public License v3.0 - siehe LICENSE Datei für Details.