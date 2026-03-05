import time
import os
import pygame

# Initialisiere Pygame Mixer nur einmal
pygame.mixer.init()

# Roboter-Tonsprache Zuordnung
robot_sounds = {
    "A": "HKHK",
    "B": "HKHL",
    "C": "HKTK",
    "D": "HKTL",
    "E": "HKBK",
    "F": "HLHK",
    "G": "HLHL",
    "H": "HLTK",
    "I": "HLTL",
    "J": "HLBK",
    "K": "TKHK",
    "L": "TKHL",
    "M": "TKTK",
    "N": "TKTL",
    "O": "TKBK",
    "P": "TLHK",
    "Q": "TLHL",
    "R": "TLTK",
    "S": "TLTL",
    "T": "TLBK",
    "U": "BXHK",
    "V": "BXHL",
    "W": "BXTK",
    "X": "BXTL",
    "Y": "BXBX",
    "Z": "BXWX",
    "0": "WXHK",
    "1": "WXHL",
    "2": "WXTK",
    "3": "WXTL",
    "4": "WXBX",
    "5": "HKWX",
    "6": "TKWX",
    "7": "BXWX",
    "8": "WXWX",
    "9": "WXBK"
}

def play_sound(sound_code):
    base_path = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(base_path, "Sounds", f"{sound_code}.wav")
    
    if os.path.exists(sound_path):
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
            while pygame.mixer.get_busy():
                time.sleep(0.1)
        except pygame.error as e:
            print(f"Fehler beim Abspielen von {sound_code}: {e}")
    else:
        print(f"⚠️ Sounddatei nicht gefunden: {sound_path}")

def speak_robot(text):
    text = text.upper()
    for char in text:
        if char == " ":
            time.sleep(1.2)  # Lange Pause für Leerzeichen
            continue
        if char in robot_sounds:
            sound_sequence = robot_sounds[char]
            for i in range(0, len(sound_sequence), 2):
                part = sound_sequence[i:i+2]
                play_sound(part)
            time.sleep(0.3)  # Kurze Pause nach jedem Buchstaben
        else:
            print(f"'{char}' nicht in der Tonsprache definiert.")

if __name__ == "__main__":
    user_input = input("Gib einen Text ein: ")
    speak_robot(user_input)
