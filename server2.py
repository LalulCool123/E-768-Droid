# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import threading
import pygame
import time
import random

app = Flask(__name__)
CORS(app)

running_scripts = {}

# pygame einmal global initialisieren
pygame.mixer.init()
mixer_lock = threading.Lock()

def speak_with_robot_voice(text):
    try:
        if not text.strip():
            print("Warnung: Leertext für Sprachausgabe")
            return

        thread_id = threading.get_ident()
        tmp_raw = f"/tmp/robot_raw_{thread_id}.wav"
        tmp_fx = f"/tmp/robot_voice_{thread_id}.wav"

        # pico2wave erzeugt Datei
        ret = os.system(f'pico2wave -l=de-DE -w={tmp_raw} "{text}"')
        if ret != 0 or not os.path.exists(tmp_raw) or os.path.getsize(tmp_raw) == 0:
            print("Fehler: pico2wave hat keine gültige WAV erzeugt")
            return

        # sox Effekt anwenden
        ret_sox = os.system(f"sox {tmp_raw} {tmp_fx} pitch +100 tempo 0.9 echo 0.8 0.7 100 0.3 reverb")
        if ret_sox != 0 or not os.path.exists(tmp_fx) or os.path.getsize(tmp_fx) == 0:
            print("Fehler: sox konnte die Datei nicht bearbeiten")
            return

        with mixer_lock:
            pygame.mixer.music.load(tmp_fx)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

        # Temporäre Dateien löschen
        try:
            os.remove(tmp_raw)
            os.remove(tmp_fx)
        except Exception:
            pass

    except Exception as e:
        print(f"Fehler bei Sprachausgabe: {e}")

def play_mp3(file_path):
    try:
        with mixer_lock:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    except Exception as e:
        print(f"Fehler beim Abspielen von MP3: {e}")

def generate_sentence_from_wordlist(user_input=None):
    if not os.path.exists("woerter.txt"):
        return "Ich weiß noch nicht genug, um sinnvoll zu antworten."

    try:
        with open("woerter.txt", "r", encoding="utf-8") as f:
            words = list(set(word.strip().lower() for word in f if word.strip()))

        subjects = ["Ich", "Das System", "Wir", "Ein Droide", "Mein Programm"]
        verbs = [w for w in words if w in [
            "mache", "starte", "spiele", "höre", "erkenne", "schalte", "berechne", "lese", "lerne", "finde", "kaufe"
        ]]
        objects = [w for w in words if w not in verbs and len(w) > 2]

        if not verbs or not objects:
            return "Ich habe noch nicht genug gelernt, um sinnvoll zu antworten."

        # Frageerkennung
        question_words = ["wer", "was", "wie", "warum", "wann", "wo", "welche", "wieso"]
        is_question = False
        if user_input:
            tokens = user_input.lower().split()
            if tokens and tokens[0] in question_words:
                is_question = True

        if is_question:
            antworten_auf_fragen = [
                "Das ist eine gute Frage, die ich noch nicht beantworten kann.",
                "Ich arbeite daran, das herauszufinden.",
                "Dazu weiß ich im Moment leider nichts.",
                "Vielleicht kann ich dir später mehr sagen.",
                "Ich lerne noch und gebe bald eine Antwort."
            ]
            return random.choice(antworten_auf_fragen)

        sentence_type = random.choice(["kurz", "normal", "lang"])

        s = random.choice(subjects)
        v = random.choice(verbs)
        o = random.choice(objects)

        if sentence_type == "kurz":
            return f"{s} {v} {o}."
        elif sentence_type == "normal":
            return f"{s} {v} gerade {o}."
        else:
            additions = [
                f"{s} {v} {o}, weil ich es wichtig finde.",
                f"{s} {v} {o}, um dir zu helfen.",
                f"Manchmal {v} ich {o}, wenn es notwendig ist.",
                f"Ich versuche gerade, {o} zu {v}.",
                f"{s} habe gerade begonnen, {o} zu {v}."
            ]
            return random.choice(additions)

    except Exception as e:
        print(f"Fehler beim Generieren eines Satzes: {e}")
        return "Fehler beim Denken."

def load_commands(filename="Befehle.txt"):
    commands = {}
    if not os.path.exists(filename):
        return commands
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, value = line.split(":", 1)
            commands[key.strip().lower()] = value.strip()
    return commands

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data or 'intent' not in data:
        return jsonify({"error": "No intent provided"}), 400

    user_input = data['intent'].lower().replace("e7", "").strip()
    print(f"Eingehende Anfrage: {user_input}")

    # Wörter extrahieren und speichern
    words = user_input.split()
    try:
        with open("woerter.txt", "a", encoding="utf-8") as f:
            for word in words:
                f.write(word + "\n")
    except Exception as e:
        print(f"Fehler beim Schreiben in woerter.txt: {e}")

    commands = load_commands()

    if user_input in ["stop", "stoff", "shop", "stopp", "aufhören"]:
        stopped = []
        for script, proc in running_scripts.items():
            try:
                proc.terminate()
                stopped.append(script)
            except Exception as e:
                print(f"Fehler beim Stoppen von {script}: {e}")
        running_scripts.clear()
        return jsonify({"status": "Alle Skripte gestoppt", "stopped": stopped})

    matched_key = None
    for key in commands:
        if key in user_input:
            matched_key = key
            break

    if matched_key:
        value = commands[matched_key]

        if value.endswith(".py"):
            script_path = os.path.join(os.path.dirname(__file__), value)
            try:
                output = subprocess.check_output(["python3", script_path], text=True).strip()
                threading.Thread(target=speak_with_robot_voice, args=(output,), daemon=True).start()
                return jsonify({"response": output})
            except Exception as e:
                print(f"Fehler beim Ausführen von {value}: {e}")
                return jsonify({"error": str(e)}), 500

        elif value.endswith(".mp3"):
            mp3_path = os.path.join(os.path.dirname(__file__), value)
            threading.Thread(target=play_mp3, args=(mp3_path,), daemon=True).start()
            return jsonify({"response": f"Spiele Sound: {value}"})

        else:
            threading.Thread(target=speak_with_robot_voice, args=(value,), daemon=True).start()
            return jsonify({"response": value})

    # Kein bekannter Befehl → Satz selbst generieren
    generated_sentence = generate_sentence_from_wordlist(user_input=user_input)
    threading.Thread(target=speak_with_robot_voice, args=(generated_sentence,), daemon=True).start()
    return jsonify({"response": generated_sentence})

if __name__ == '__main__':
    print("Starte Server auf Port 7567...")
    app.run(host='0.0.0.0', port=7567)
