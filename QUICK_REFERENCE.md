# E-768 Droid – Quick Reference Guide

## 📋 PROJECT AT A GLANCE

**What**: Voice-controlled AI robot for Raspberry Pi  
**Language**: German (Deutsch)  
**Core Tech**: Vosk (offline speech recognition) + Servo control + Tone-based robot language  
**Status**: Experimental/Educational

---

## 🎯 KEY COMPONENTS

```
USER → Web UI (HTML) → Flask Server → Voice Synthesis → Robot Hardware
                ↓                          ↓              ↓
           REST API                Command Parser    Sensors/Servos
```

| Component | File | Role |
|-----------|------|------|
| **Web Server** | `server2.py` | Flask API + command dispatch + audio synthesis |
| **Movement** | `robot_movement.py` | Servo control + idle animations |
| **Robot Speech** | `robot_sprache.py` | Phonetic tone-based language |
| **Walking** | `lauf.py` | Gait animation |
| **Distance Sensor** | `ultraschall_messung.py` | HC-SR04 obstacle detection |
| **Balance** | `kippschutz.py` | MPU6050 tilt protection |
| **Testing** | `Servotest.py` | Servo calibration |

---

## 🚀 QUICK START

```bash
cd E-768-Droid
source venv/bin/activate  # or whisper-venv/bin/activate
python3 server2.py        # Starts Flask on port 7567
```

Open browser → `http://localhost:7567`

---

## 💬 HOW VOICE WORKS

```
Microphone → Vosk (speech recognition) → Text
           ↓
        Befehl.txt (command lookup)
        {keyword: action}
           ↓
        Match found? → Execute action (Python script / MP3 / TTS)
        No match? → Generate random sentence from woerter.txt
           ↓
        Text-to-Speech (pico2wave) → Sound effects (sox) → Speaker
```

**Example**: User says "Hallo"
- ✅ Matched in `Befehle.txt` → plays "Hallo, ich bin E-7 6 8"
- ❌ Not matched → generates "Ich mache gerade [random_noun]"

---

## 🔧 HARDWARE PINOUT

```
Raspberry Pi GPIO
├── I2C Bus (GPIO 2/3)
│   ├── PCA9685 (0x40) → 5 Servos
│   │   ├── Ch0: Head horizontal (look left/right)
│   │   ├── Ch1: Head vertical (look up/down)
│   │   ├── Ch2: Left leg (walking)
│   │   ├── Ch3: Right leg (walking)
│   │   └── Ch4: Body rotate (turning)
│   └── MPU6050 (0x68) → Tilt sensor
├── GPIO 27 → Ultrasound TRIG
└── GPIO 17 → Ultrasound ECHO
```

**Servo Range**: 1000-2000 µs (0°-180°)  
**Standard Position**: 1500 µs (90°)

---

## ⚡ PERFORMANCE ISSUES (CRITICAL)

| Issue | Bottleneck | Impact | Fix |
|-------|-----------|--------|-----|
| **TTS Latency** | pico2wave + sox (2-4s) | User gets slow response | Cache results, lighter effects |
| **Sensor Polling** | GPIO busy-wait loops | CPU 100%, blocks robot | Use edge detection (RPi.GPIO) |
| **I2C Contention** | Sequential servo + IMU reads | Servo jitter | Move I2C to separate thread |
| **Audio Queue** | Single pygame mixer | Only one sound at a time | Multi-channel playback |
| **Unbounded Memory** | woerter.txt grows forever | Eventually → OOM | Set max 5000 words |

---

## 📂 COMMAND SYNTAX

### Movement Commands (hardcoded in server2.py)
```
"lauf", "laufen", "go", "los" → robot_state = "walking"
"halt", "stop", "stopp" → robot_state = "stopped"
"idle", "ruh", "pause" → robot_state = "idle"
"dreh", "drehen" → robot_state = "turning"
```

### Befehle.txt Format (keyword:action)
```
hallo:hallo ich bin e-7 6 8         (speak text)
systemcheck:Servotest.py            (execute script, read output)
geburtstag:Birthday.mp3             (play MP3 file)
scan:ultraschall_messung.py         (run sensor, speak result)
```

### Tone Language (robot_sprache.py)
```
Text "ABC" → Sound sequence:
A=HKHK → play HK.wav, HK.wav
B=HKHL → play HK.wav, HL.wav
C=HKTK → play HK.wav, TK.wav
```

---

## 📊 DATA FILES

| File | Purpose | Max Size | Notes |
|------|---------|----------|-------|
| `Befehle.txt` | Command → Action map | Small | Edit manually |
| `woerter.txt` | Vocabulary list | ⚠️ Unbounded | Grows with every command |
| `sats.txt` | Sentence templates | (empty) | For future expansion |

---

## 🔌 API ENDPOINTS

### POST /command
```json
{
  "intent": "lauf"
}

Response:
{
  "response": "Ich laufe jetzt los!",
  "robot_state": "walking"
}
```

### GET /status
```json
{
  "robot_state": "idle",
  "movement_running": true,
  "status": "Online ✅"
}
```

---

## 🎛️ WEB UI CONTROLS

(From `AAA_E-7_Micro.html`)

- **Status Bar** → Robot state indicator
- **Voice Input** → Voice recognition via browser microphone
- **Text Input** → Manual command entry
- **Command Buttons** → Preset actions (Walk, Stop, Scan, etc.)
- **Output Display** → Shows robot response

---

## 🐛 DEBUGGING TIPS

```bash
# Test speech synthesis
pico2wave -l=de-DE -w=test.wav "Hallo"
sox test.wav output.wav pitch +100 echo 0.8 0.7 100 0.3 reverb

# Test audio playback
paplay run.mp3  # or 'aplay'

# Test microphone
arecord -d 3 test.wav

# Test GPIO/I2C
i2cdetect -y 1          # List I2C devices (should see 40 = PCA9685, 68 = MPU6050)
gpio readall            # Show GPIO state

# Test servos interactively
python3 Servotest.py

# Monitor Flask server
python3 server2.py --debug  # (if debug mode supported)
```

---

## 📈 SCALING IMPROVEMENTS

### Immediate (< 1 hour)
- ✅ Cache TTS results (text hash → WAV file)
- ✅ Deduplicate woerter.txt during write, not read
- ✅ Use lighter sox effects (skip reverb)

### Short-term (half day)
- ✅ Move I2C to background thread
- ✅ Implement audio request queue
- ✅ Replace GPIO polling with edge detection

### Long-term (days)
- ✅ Add real NLP (spaCy, Rasa intent classification)
- ✅ Implement PID servo control
- ✅ Add comprehensive logging + monitoring
- ✅ Unit + integration tests

---

## 🔗 KEY DEPENDENCIES

```
Required:
- Python 3.7+
- vosk (speech recognition)
- flask (web server)
- pygame (audio playback)
- RPi.GPIO (GPIO control)
- smbus (I2C control)

Optional:
- whisper (alternative speech synthesis)
- rhino (hotword detection)
- gpiozero (higher-level GPIO)
- rasa (intent classification)
- spacy-de (NLP for German)
```

Install all:
```bash
pip install vosk flask flask-cors pygame RPi.GPIO smbus-cffi sounddevice
```

---

## 📍 FILE LOCATIONS (Relative to project root)

```
/Befehle.txt                    ← Command configuration
/woerter.txt                    ← Vocabulary (grows)
/sats.txt                       ← Sentences (empty)
/model/vosk-model-small-de-0.15/   ← Speech model (~50MB)
/Sounds/                        ← Robot tone files (HK.wav, etc.)
/*.mp3                          ← Sound effects (run.mp3, scan.mp3, Birthday.mp3)
```

---

## 🎓 SUGGESTED LEARNING PATHS

1. **New to Robotics?**
   - Start with `Servotest.py` → understand servo control
   - Then `lauf.py` → learn gait animation
   - Then `robot_movement.py` → see it all together

2. **New to Speech?**
   - Play with `robot_sprache.py` → tone language
   - Edit `Befehle.txt` → add custom commands
   - Use `server2.py` web UI → test responses

3. **New to Sensors?**
   - Run `ultraschall_messung.py` → distance reading
   - Run `kippschutz.py` → balance monitoring
   - Understand MPU6050/HC-SR04 wiring

4. **Building from Scratch?**
   - Fork the repo
   - Modify `Befehle.txt` with YOUR commands
   - Add custom Python scripts for new behaviors
   - Wire YOUR hardware (might differ from E-7 reference)

---

## ⚠️ COMMON ISSUES & FIXES

| Problem | Cause | Solution |
|---------|-------|----------|
| "Cannot find vosk model" | Path not set correctly | Ensure model/ folder exists in project root |
| Servo doesn't move | I2C not enabled | `sudo raspi-config` → I2C → Enable |
| No sound output | Audio device not configured | `alist` or check `/etc/asound.conf` |
| "GPIO in use" | Different script already using pins | Kill other Python processes first |
| Server won't start | Port 7567 in use | `sudo lsof -i :7567` or use different port |
| Robot "freezes" | TTS pipeline blocking | Response is normal, takes 2-4s |
| Out of memory | woerter.txt too large | Manually delete old entries or set max size |

---

## 📞 SUPPORT RESOURCES

- **Official Repo**: https://github.com/LalulCool123/E-768-Droid
- **Vosk Docs**: https://alphacephei.com/vosk/
- **Raspberry Pi GPIO**: https://www.raspberrypi.org/documentation/usage/gpio/
- **PCA9685 Datasheet**: https://www.nxp.com/docs/en/application-note/AN10974.pdf
- **MPU6050 Datasheet**: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf

---

*Quick Reference v1.0 – March 27, 2026*
