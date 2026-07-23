# Anleitung zum Testen der neuen Funktionen

## Schritt 1: Website öffnen
Öffne in deinem Browser:
```
http://localhost:8081/index.html
```

## Schritt 2: Landing Page
Du solltest sehen:
- ✅ Das Frequency-Logo
- ✅ "Finde deine Frequenz" Heading
- ✅ Zwei Buttons:
  - 🎧 Ich bin Schüler:in
  - 📡 Ich bin Lehrkraft

## Schritt 3: Lehrkraft-Workflow testen
1. Klicke auf **"Ich bin Lehrkraft"**
2. Du solltest zum **Login-Screen** weitergeleitet werden

### Login-Screen:
- Benutzername-Eingabefeld
- Passwort-Eingabefeld
- "Anmelden" Button
- Link: "Noch kein Konto? Registrieren"

### Demo-Modus aktivieren:
Da das Backend nicht läuft, funktioniert der Login im **Demo-Modus**:
- Beliebiger Benutzername (z.B. "Demo Lehrkraft")
- Beliebiges Passwort mit mindestens 6 Zeichen
- Klick auf "Anmelden"

### Erwartetes Ergebnis:
Du solltest zum **Gruppen-Dashboard** weitergeleitet werden mit:
- "Deine Gruppen" Überschrift
- "+ Neue Gruppe" Button
- Leere Gruppen-Liste (da neu)
- Bereich "Gruppe von einem anderen Gerät öffnen"

## Schritt 4: Registrieren testen
Auf dem Login-Screen:
1. Klick auf "Registrieren"
2. Du solltest zum **Register-Screen** weitergeleitet werden
3. Fülle die Felder aus:
   - Benutzername (beliebig)
   - Passwort (mindestens 6 Zeichen)
   - Passwort wiederholen (muss gleich sein)
4. Klick auf "Registrieren"
5. Im Demo-Modus funktioniert das ebenfalls, du kommst zum Dashboard

## Schritt 5: Gruppe erstellen
Im Gruppen-Dashboard:
1. Klick auf **"+ Neue Gruppe"**
2. Du solltest zum **"Neue Gruppe anlegen" Screen** geleitet werden
3. Fülle aus:
   - Gruppenname (z.B. "Klasse 9b")
   - Ziel-Level (z.B. "B1")
   - Wähle mindestens eine Grammatikstruktur
4. Klick auf "Gruppe erstellen"
5. Du solltest zur Gruppen-Detail-Seite geleitet werden

## Schritt 6: Logout testen
Oben rechts in der Navigation sollte ein **"Abmelden" Button** sichtbar sein:
1. Klick darauf
2. Du solltest zur Landing Page zurückgeleitet werden
3. Login-Daten sollten gelöscht sein

## Neue Funktionen, die sichtbar sein sollten:

✅ **Login/Register Screens** (NEU!)
- Nur für Lehrkräfte
- Mit Fehlerbehandlung
- Links zwischen Login und Register

✅ **Abmelden-Button** (NEU!)
- Oben rechts in der Navigation
- Löscht alle Session-Daten

✅ **Demo-Modus** (NEU!)
- Funktioniert ohne Backend
- Ermöglicht Testen aller Features
- Speichert Gruppen im localStorage

✅ **Teacher-spezifische Gruppen** (NEU!)
- Jede Lehrkraft kann nur ihre eigenen Gruppen sehen
- Gruppen werden dem Teacher zugeordnet

## Troubleshooting

Falls die Landing Page nicht angezeigt wird:
1. Browser-Konsole öffnen (F12)
2. Auf Fehler prüfen
3. Seite neu laden (Ctrl+R)

Falls die Login-Buttons nicht funktionieren:
1. Öffne die Browser-Konsole
2. Gib ein: `state.teacherId` (sollte `null` sein)
3. Gib ein: `typeof submitLogin` (sollte "function" sein)

## Backend starten (optional)

Wenn du das Backend starten möchtest:
```bash
pip install -r requirements.txt
python backend.py
```

Dann funktioniert die echte Persistenz statt Demo-Modus.
