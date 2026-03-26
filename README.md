
# E‑768 Droid – Sprachgesteuerter KI‑Roboter für den Raspberry Pi

> Offline-Spracherkennung, eigene Robotersprache, Sensorik und Bewegung in einem Projekt.  
> Ziel: Ein Droide, der hört, denkt, spricht und sich autonom bewegt.

Repository: <https://github.com/LalulCool123/E-768-Droid>

---

## 1. Überblick

E‑768‑Droid ist ein Experimentier‑Projekt für einen sprachgesteuerten Roboter auf Basis eines Raspberry Pi.

Der Droide kombiniert:

- Offline-Spracherkennung (Vosk, optional Rhino/Whisper)
- Eigene Robotersprache und Audio-Feedback (MP3-Sounds, Tonsprache)
- Aktive Sensorik (Ultraschall, Kippschutz)
- Bewegungssteuerung (Servos / Motorik)
- Eine einfache, aber erweiterbare Logik für Verhalten und Reaktionen

Das Projekt eignet sich als:

- Einstieg in Sprachsteuerung auf dem Raspberry Pi
- Grundlage für einen autonomen kleinen Roboter
- Spielwiese für eigene Ideen, Erweiterungen und Experimente

---

## 2. TL;DR – Schnellstart (für Eilige)

Auf dem Raspberry Pi:

```bash
git clone https://github.com/LalulCool123/E-768-Droid.git
cd E-768-Droid

python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren (wenn requirements.txt existiert)
# pip install -r requirements.txt

# Mindestens Vosk installieren, wenn noch nicht geschehen
pip install vosk sounddevice

# Beispiel: zentrale Logik starten (falls du server2.py dafür nutzt)
python3 server2.py
```

Dann:

- Mikrofon ins Raspberry Pi stecken
- Lautsprecher anschließen
- Servo- und Sensorskripte an deine GPIO-Pins anpassen
- Befehle in `Befehle.txt`, `woerter.txt`, `sats.txt` konfigurieren

---

## 3. Features

Hauptfunktionen (abhängig von deinem aktuellen Implementierungsstand):

- Offline-Spracherkennung in Deutsch mit Vosk:
  - Modell in `model/vosk-model-small-de-0.15`
  - Wort- und Befehlslisten in Textdateien
- Sprach- und Audioausgabe:
  - MP3-Sounds (z. B. `run.mp3`, `scan.mp3`, `Birthday.mp3`, `Sounds/`)
  - definierte „Robotersprache“ in `Roboter_Tonsprache_Tabelle.pdf`
- Hardwaresteuerung:
  - Servotest und Motorik (`Servotest.py`, `lauf.py`)
  - Ultraschall-Entfernungsmessung (`ultraschall_messung.py`)
  - Kippschutz / Lagesensor (`kippschutz.py`)
- Logik & Integration:
  - zentrale Skripte wie `server2.py` und `robot_sprache.py` als Bindeglied
  - Strukturierung von Befehlen, Sätzen und Antworten

---

## 4. Projektstruktur

Basierend auf der aktuellen Ordnerstruktur:

```text
E-768-Droid/
├── E-Sieben_de_raspberry-pi_v3_0_0/
│   └── E-7_Befehle/                  # Ältere Version / Zusatzprojekt mit Befehlen
├── Sounds/                           # MP3-Sounds & Audio-Ressourcen
├── __pycache__/                      # Automatisch erzeugte Python-Caches
├── model/
│   └── vosk-model-small-de-0.15/    # Deutsches Vosk-Spracherkennungsmodell
├── rhino/
│   └── binding/
│       └── python/                   # Rhino-Python-Bindings (Hotword/Intent, optional)
├── whisper-venv/                     # Virtuelle Umgebung für Whisper (optional)
│
├── AAA_E-7_Micro.html                # Dokumentation / Info zum Mikrofon-Setup
├── Befehle.txt                       # Liste von Sprachbefehlen
├── Birthday.mp3                      # Einzelsounds
├── LICENSE
├── README.md
├── Roboter_Tonsprache_Tabelle.pdf    # Dokument zur Robotersprache / Tonbedeutung
├── Servotest.py                      # Testskript für Servos
├── grok_image_1773002297769.jpg      # Doku-/Referenzbild
├── kippschutz.py                     # Kippschutz-Logik / Lagesensor
├── lauf.py                           # Bewegungs-/Lauf-Logik
├── robot_sprache.py                  # Sprachlogik / Roboter-Sprache
├── run.mp3
├── sats.txt                          # Sätze für Spracherkennung/-ausgabe
├── scan.mp3
├── server2.py                        # Zentrales Server-/Steuer-Skript (z. B. Hauptlogik)
├── ultraschall_messung.py            # Ultraschall-Abstandsmessung
└── woerter.txt                       # Wörterliste für Spracherkennung
```

<img width="1024" height="1536" alt="Copilot_20260326_140723" src="https://github.com/user-attachments/assets/e9f47a86-057c-4935-8e99-1cf02a4b45fc" />

---

## 5. Hardware – Was du typischerweise brauchst

Mindestausstattung (Beispiel):

- Raspberry Pi (3B/4B oder ähnlich)
- Micro-SD-Karte mit Raspberry Pi OS
- USB-Mikrofon oder I2S-Mikro
- Lautsprecher (Klinke, HDMI oder USB-Audio)
- Servos oder Motoren (je nach Aufbau)
- Ultraschallsensor (z. B. HC-SR04)
- Kipp- oder Lagesensor (z. B. einfacher Neigungssensor oder IMU)
- Externe Stromversorgung für Servos, falls nötig

Je nach Roboter-Aufbau kommen hinzu:

- Chassis / Robotergestell
- Räder / Füße / Gelenke
- Spannungswandler, Breadboard, Kabel, etc.

---

## 6. Softwarevoraussetzungen

- Raspberry Pi OS (oder kompatibles Linux)
- Python 3.7+ (empfohlen 3.9+)
- Git

Python-Pakete (typische Kandidaten, bitte an dein konkretes Setup anpassen):

- `vosk` – Offline-Spracherkennung
- `sounddevice` oder `pyaudio` – Audio-Ein-/Ausgabe
- `RPi.GPIO` oder `gpiozero` – GPIO/Servosteuerung
- zusätzliche Pakete für Rhino / Whisper, falls du sie verwendest

---

## 7. Installation – Schritt für Schritt

Alle Schritte im Terminal auf dem Raspberry Pi.

### 7.1 Repository klonen

```bash
git clone https://github.com/LalulCool123/E-768-Droid.git
cd E-768-Droid
```

### 7.2 Virtuelle Umgebung (empfohlen)

```bash
python3 -m venv venv
source venv/bin/activate
```

Alternativ kannst du die vorhandene `whisper-venv/` nutzen, falls dort schon alles eingerichtet ist.

### 7.3 Python-Abhängigkeiten

Wenn `requirements.txt` vorhanden ist:

```bash
pip install -r requirements.txt
```

Falls nicht, installiere mindestens:

```bash
pip install vosk sounddevice
# und je nach Skripten:
# pip install RPi.GPIO gpiozero
# pip install pyaudio
```

### 7.4 Audio testen

Einmal prüfen, ob Audio grundsätzlich funktioniert (Beispiele):

```bash
aplay run.mp3        # Test Audio-Ausgabe
arecord -d 3 test.wav  # 3 Sekunden aufnehmen und Mikro prüfen
```

---

## 8. Konfiguration der Sprache

Die Spracherkennung ist in diesem Projekt bewusst textbasiert konfigurierbar.

### 8.1 Vosk-Modell

Verwendet wird:

```text
model/vosk-model-small-de-0.15/
```

Dieses Modell ist für deutsche Offline-Spracherkennung optimiert.  
Falls du ein anderes Modell nutzen möchtest, kannst du es hier ersetzen, z. B.:

```text
model/vosk-model-de-0.22/
```

und die Pfade im Code entsprechend anpassen.

### 8.2 Befehle, Wörter, Sätze

- `Befehle.txt`  
  Liste der Befehle, auf die der Droide reagieren soll  
  Beispiel (Beispielinhalt, bitte selbst anpassen):

  ```text
  lauf vorwärts
  dreh dich links
  dreh dich rechts
  halt
  ```

- `woerter.txt`  
  Wörterliste für die Spracherkennung (z. B. Vokabular, das besonders wichtig ist).

- `sats.txt`  
  Sätze, die der Droide selbst sagen kann oder als Muster für die Erkennung dienen.

Du kannst hier ganz einfach neue Befehle hinzufügen, indem du sie als neue Zeile einträgst und im Python-Code darauf reagierst.

---

## 9. Architektur – Wie der Droide denkt (Konzept)

Eine mögliche Daten- und Steuerfluss-Sicht (Beispiel):

```text
Mikrofon
  ↓
Audio-Stream
  ↓
Vosk (Offline-Spracherkennung)
  ↓
Text (z. B. "lauf vorwärts")
  ↓
Befehl-Parser / Logik (server2.py / robot_sprache.py)
  ↓
- Motorik (lauf.py / Servotest.py)
- Sensorabfragen (ultraschall_messung.py / kippschutz.py)
- Audioantwort (robot_sprache.py / Sounds/)
```

Aus dieser Sicht lassen sich drei Ebenen unterscheiden:

1. Wahrnehmung:
   - Audio-Eingang, Sensoren (Ultraschall, Kipp)
2. Entscheidung:
   - Matching von Text auf Befehle
   - Zustandslogik (z. B. „falls fast gekippt → Bewegung stoppen“)
3. Aktion:
   - Servos/Bewegung
   - Audio-Feedback / Roboter-Sprache

---

## 10. Wichtige Skripte im Detail

Da sich der Code weiterentwickelt, ist dies eine generische Beschreibung, wie du sie nutzen kannst:

### 10.1 `server2.py` – Zentrale Steuerlogik (empfohlen als Einstieg)

Typische Aufgaben für dieses Skript könnten sein:

- Haupt-Loop des Roboters
- Starten der Spracherkennung
- Auswerten von erkannten Befehlen
- Weiterleitung an Bewegungs- und Sensorfunktionen

Start (Beispiel):

```bash
python3 server2.py
```

### 10.2 `robot_sprache.py` – Robotersprache und Audio-Feedback

Mögliche Aufgaben:

- Ausgeben von Text über Sprachsynthese oder Tonausgabe
- Abspielen von MP3-Sounds (z. B. in `Sounds/`)
- Umsetzung der „Tonsprache“ aus `Roboter_Tonsprache_Tabelle.pdf`

Start:

```bash
python3 robot_sprache.py
```

### 10.3 `lauf.py` – Bewegungslogik

Mögliche Funktionen:

- Vorwärts-/Rückwärtsbewegung
- Drehungen
- ggf. komplexere Bewegungsmuster

Start:

```bash
python3 lauf.py
```

Bevor du dies ausführst, prüfe die im Skript eingestellten GPIO-Pins und die Servoverkabelung.

### 10.4 `Servotest.py` – Servotest

Zum schnellen Testen der Servos ohne Sprachlogik:

```bash
python3 Servotest.py
```

Hier kannst du sehen, ob die Hardware korrekt angeschlossen ist (Drehrichtung, Winkel, etc.).

### 10.5 `ultraschall_messung.py` – Abstandsmessung

Testet den Ultraschallsensor (z. B. HC-SR04):

```bash
python3 ultraschall_messung.py
```

Typische Ausgabe wäre z. B. Distanz in Zentimetern.  
Nutze das, um Hinderniserkennung in deine Logik zu integrieren.

### 10.6 `kippschutz.py` – Kippschutz

Überwacht einen Kipp- oder Lagesensor.  
Sinnvoll, um den Roboter rechtzeitig anzuhalten oder Alarm auszugeben, wenn er zu kippen droht.

Start:

```bash
python3 kippschutz.py
```

---

## 11. Pseudo-Code: Beispiel-Hauptschleife

So könnte eine zentrale Loop (z. B. in `server2.py`) aussehen – als Idee:

```python
# Pseudo-Code – Beispielstruktur, nicht 1:1 dein Code

from sprecher import SagWas
from befehle import parse_befehl
from lauf import bewege
from ultraschall_messung import entfernung
from kippschutz import ist_stabil
from vosk_wrapper import hoere_zu

def main():
    SagWas("Systemstart. E-7 ist bereit.")

    while True:
        text = hoere_zu()  # wartet auf gesprochene Eingabe
        
        if not ist_stabil():
            SagWas("Achtung, ich kippe! Bewegung stoppen.")
            bewege("stopp")
            continue

        befehl = parse_befehl(text)

        if befehl == "lauf vorwärts":
            if entfernung() < 20:
                SagWas("Zu nah am Hindernis. Ich stoppe.")
                bewege("stopp")
            else:
                SagWas("Laufe vorwärts.")
                bewege("vorwärts")

        elif befehl == "halt":
            SagWas("Stoppe.")
            bewege("stopp")

        elif befehl == "tanz":
            SagWas("Starte E-7 Tanzmodus.")
            bewege("tanz")

        # usw.

if __name__ == "__main__":
    main()
```

Dieser Pseudo-Code dient als Inspiration, wie du deine Module kombinieren kannst.

---

## 12. Erweiterung – Eigene Befehle und Verhaltensweisen

Ein möglicher Workflow, um den Droiden „klüger“ zu machen:

1. Neuen Befehl in `Befehle.txt` eintragen, z. B.:

   ```text
   mach einen tanz
   ```

2. Logik für diesen Befehl in deiner zentralen Steuerung hinzufügen (z. B. in `server2.py`):

   ```python
   elif befehl == "mach einen tanz":
       SagWas("Okay, Tanzmodus aktiviert.")
       bewege("tanz")
   ```

3. Optional: Neue Sounds in `Sounds/` ablegen und in `robot_sprache.py` einbauen.

4. Sensorik kombinieren:
   - Beispiel: Roboter tanzt nur, wenn er stabil steht und nichts im Weg ist.

So wird der Droide Schritt für Schritt zu deinem persönlichen, individuellen Projekt.

---

## 13. Fehlerbehebung (FAQ)

**Der Droide hört nichts / Spracherkennung reagiert nicht**

- Prüfe, ob das Mikrofon korrekt erkannt wird:
  - `arecord -l`
- Testaufnahme machen:
  - `arecord -d 3 test.wav`
- Prüfe, ob das richtige Audio-Device im Code verwendet wird.

**Ich bekomme Fehler zu `vosk`**

- Prüfe, ob `vosk` installiert ist:

  ```bash
  pip show vosk
  ```

- Falls nicht:

  ```bash
  pip install vosk
  ```

**Servos zucken wild oder bewegen sich gar nicht**

- Eigene Stromversorgung für Servos nutzen (nicht direkt über Pi-5V, wenn möglich)
- GND von Servo und Raspberry Pi verbinden
- GPIO-Pin-Nummern im Skript und in der Hardware abgleichen

**Ultraschallsensor liefert nur 0 oder riesige Werte**

- Trigger- und Echo-Pin korrekt angeschlossen?
- Echo-Pin über Spannungsteiler, wenn du 5V-Sensor verwendest
- Times und Delays im Script prüfen

---

## 14. Roadmap / Ideen

Mögliche nächste Schritte für das Projekt:

- Zustandsmaschine oder Behavior-Tree einbauen
- KI-Komponente für adaptives Verhalten (z. B. aus Fehlern lernen)
- Web-Dashboard, um Status, Sensorwerte und Logs live zu sehen
- Mehrere Droiden, die miteinander kommunizieren
- Integration von Whisper für robustere Erkennung (über `whisper-venv/`)
- Übergang auf eine echte mobile Plattform (Fahrroboter, humanoider Aufbau)

---

## 15. Lizenz

Die Lizenz findest du in der Datei [`LICENSE`](./LICENSE).  
Bitte beachte die dort genannten Bedingungen für Nutzung, Weitergabe und Änderungen.

---

## 16. Autor / Kontakt

- Projekt: E‑768-Droid – Sprachgesteuerter KI-Roboter
- Repository: <https://github.com/LalulCool123/E-768-Droid>
- Autor / Maintainer: (Edrio/Rahul Kavlak)
- Kontakt:
  - GitHub-Issues im Repository
  - optional: Rahul.Kavlak@gmx.de

---
```
