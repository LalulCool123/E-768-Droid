import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as quelle:
    print("Sag etwas...")
    audio = r.listen(quelle)

print("Audio aufgenommen. Versuche zu erkennen...")

try:
    text = r.recognize_google(audio, language="de-DE")
    print("Erkannt:", text)
except sr.UnknownValueError:
    print("NICHTS verstanden.")
except sr.RequestError as e:
    print("API-Fehler:", e)
