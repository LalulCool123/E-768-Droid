# -*- coding: utf-8 -*-
"""
Robot Tonsprache Module
Konvertiert Buchstaben und Zahlen in Roboter-Tonsprache
"""

import time
import os
import pygame
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Initialisiere Pygame Mixer nur einmal
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except Exception as e:
    logging.warning(f"⚠️ Audio nicht verfügbar: {e}")
    AUDIO_AVAILABLE = False

# Roboter-Tonsprache Zuordnung (Buchstaben und Zahlen)
robot_sounds = {
    "A": "HKHK", "B": "HKHL", "C": "HKTK", "D": "HKTL", "E": "HKBK",
    "F": "HLHK", "G": "HLHL", "H": "HLTK", "I": "HLTL", "J": "HLBK",
    "K": "TKHK", "L": "TKHL", "M": "TKTK", "N": "TKTL", "O": "TKBK",
    "P": "TLHK", "Q": "TLHL", "R": "TLTK", "S": "TLTL", "T": "TLBK",
    "U": "BXHK", "V": "BXHL", "W": "BXTK", "X": "BXTL", "Y": "BXBX",
    "Z": "BXWX",
    "0": "WXHK", "1": "WXHL", "2": "WXTK", "3": "WXTL", "4": "WXBX",
    "5": "HKWX", "6": "TKWX", "7": "BXWX", "8": "WXWX", "9": "WXBK"
}

def play_sound(sound_code):
    """Spiele einen Roboter-Ton ab"""
    if not AUDIO_AVAILABLE:
        return
    
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(base_path, "Sounds", f"{sound_code}.wav")
        
        if os.path.exists(sound_path):
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.05)
        else:
            logging.warning(f"⚠️ Sounddatei nicht gefunden: {sound_path}")
    except Exception as e:
        logging.error(f"❌ Fehler beim Abspielen von {sound_code}: {e}")

def speak_robot(text):
    """
    Wandelt Text in Roboter-Tonsprache um und spielt ihn ab.
    Unterstützt Großbuchstaben und Zahlen.
    """
    text = text.upper()
    logging.info(f"🤖 Spreche: {text}")
    
    for char in text:
        if char == " ":
            logging.info("   [Pause]")
            time.sleep(1.2)  # Lange Pause für Leerzeichen
            continue
        
        if char in robot_sounds:
            sound_sequence = robot_sounds[char]
            logging.info(f"   {char}: {sound_sequence}")
            
            for i in range(0, len(sound_sequence), 2):
                part = sound_sequence[i:i+2]
                play_sound(part)
            time.sleep(0.3)  # Kurze Pause nach jedem Buchstaben
        else:
            logging.warning(f"   '{char}' nicht in Tonsprache definiert.")

def main():
    """Hauptfunktion für direkte Verwendung"""
    try:
        user_input = input("🎤 Gib einen Text ein: ")
        if user_input.strip():
            speak_robot(user_input)
        else:
            logging.warning("Keine Eingabe!")
    except KeyboardInterrupt:
        print("\n⏹️  Abgebrochen.")
    except Exception as e:
        logging.error(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main()

