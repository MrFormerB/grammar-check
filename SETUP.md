# Grammar Check – Englisch-Level-Check mit Persistenz

## Problem behoben

Das Haupt-Problem war, dass angelegte Gruppen nicht abgespeichert wurden. Die Ursache war:
- Der ursprüngliche Code verwendete `window.storage` (Claude Artifacts Storage API), die nur in Claude funktioniert
- Es gab kein echtes Backend für persistente Datenspeicherung
- Jede Lehrkraft musste sich nicht anmelden, sodass Gruppen nicht zwischen Geräten synchronisiert werden konnten

## Lösung

### Backend (Python Flask)
- **backend.py**: Ein einfacher Flask-Server mit SQLite-Datenbank
- Funktionen:
  - Benutzerregistrierung und Login für Lehrkräfte
  - Passwort-Hashing mit PBKDF2
  - Persistente Speicherung von Gruppen
  - REST-API für Frontend-Kommunikation

### Frontend (HTML/JavaScript)
- **index.html** (angepasst):
  - Neue Storage-Funktionen, die mit dem Backend kommunizieren
  - Login/Register Screens für Lehrkräfte
  - Authentifizierungs-Token-Management
  - Logout-Funktion
  - Teacher-spezifische Gruppe-Keys (`teacher:{id}:myGroups`)

## Installation und Start

### Schritt 1: Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### Schritt 2: Backend starten
```bash
python backend.py
```
Der Backend läuft dann unter `http://localhost:5000`

### Schritt 3: Frontend öffnen
Öffne die `index.html` Datei in einem Browser

## Funktionsweise

1. **Lehrkraft klickt auf "Ich bin Lehrkraft"**
   - Wird auf Login-Screen weitergeleitet (falls nicht eingeloggt)

2. **Login/Registrierung**
   - Benutzer erstellt ein neues Konto oder meldet sich an
   - Authentifizierungs-Token wird in localStorage gespeichert

3. **Gruppen erstellen**
   - Gruppen werden mit teacher-ID im Speicher gespeichert
   - Gruppen-Daten werden auf dem Backend persistiert

4. **Geräteübergreifender Zugriff**
   - Von jedem Gerät kann sich die Lehrkraft mit denselben Anmeldedaten einloggen
   - Die Gruppen werden vom Backend geladen

## API-Endpunkte

### Authentifizierung
- `POST /api/auth/register` - Neue Lehrkraft registrieren
- `POST /api/auth/login` - Lehrkraft anmelden

### Speicherung
- `GET /api/storage/get?key=...&shared=true/false` - Daten abrufen
- `POST /api/storage/set` - Daten speichern
- `GET /api/storage/list?prefix=...&shared=true/false` - Schlüssel auflisten

### Info
- `GET /api/teacher/info` - Informationen über die aktuelle Lehrkraft (mit Authorization)
- `GET /health` - Health-Check

## Sicherheit

- Passwörter werden mit PBKDF2 gehasht (100.000 Iterationen)
- Session-Tokens werden als sichere Hex-Strings generiert
- Alle sensiblen Operationen erfordern Authentifizierung

## Zukünftige Verbesserungen

- HTTPS/TLS für Produktivumgebung
- Datenbank-Verschlüsselung
- Benutzer-Management für Administratoren
- Audit-Logging
- Rate-Limiting
