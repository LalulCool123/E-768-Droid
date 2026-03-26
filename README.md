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
