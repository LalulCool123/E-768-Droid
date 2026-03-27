# E-768 Droid – Complete Project Architecture Analysis

**Project**: Voice-Controlled AI Robot for Raspberry Pi  
**Language**: German (Deutsch)  
**Date**: March 27, 2026  
**Status**: Active Development/Experimental

---

## 1. PROJECT OVERVIEW

E-768 Droid is an experimental voice-controlled robotics project for Raspberry Pi that combines:
- **Offline speech recognition** (Vosk, optional Rhino/Whisper)
- **Custom robot language** with audio feedback (MP3 sounds + tone-based communication)
- **Active sensor systems** (ultrasound distance measurement, tilt protection)
- **Motor control** (servo-based movement)
- **Autonomous behavior logic** with expandable command structure

**Key Characteristics**:
- Completely **offline-capable** (critical for Raspberry Pi with limited bandwidth)
- Deutsche Spracherkennung (German speech recognition)
- Modular architecture with separate concerns for sensors, movement, speech, and server logic
- Experimental/educational focus – designed for learning and extension

---

## 2. PROJECT STRUCTURE

```
E-768-Droid/
├── Core Python Modules
│   ├── server2.py                      ⭐ MAIN SERVER ENTRY POINT (Flask-based)
│   ├── robot_sprache.py                🎤 Robot Language Module (tone-based communication)
│   ├── robot_movement.py               🤖 Movement Control (servo + state management)
│   ├── lauf.py                         🚶 Walking/Gait Animation Logic
│   ├── Servotest.py                    🔧 Servo Testing & Calibration
│   ├── ultraschall_messung.py          📏 Ultrasound Distance Measurement (HC-SR04)
│   ├── kippschutz.py                   ⚖️  Tilt Protection (MPU6050 IMU)
│
├── Offline Speech Model
│   └── model/
│       └── vosk-model-small-de-0.15/   📦 German Vosk Speech Recognition Model
│
├── Optional Components
│   ├── rhino/binding/python/           🎙️  Rhino hotword detection bindings (optional)
│   └── whisper-venv/                   🗣️  Virtual env for OpenAI Whisper (optional)
│
├── Data & Configuration Files
│   ├── Befehle.txt                     📋 Command-to-Action Mapping (verb:action pairs)
│   ├── woerter.txt                     📚 Vocabulary List (for sentence generation)
│   ├── sats.txt                        📝 (Empty) Sentences/Phrases File
│
├── Audio Resources
│   ├── Sounds/
│   │   ├── HK.wav, HL.wav, TK.wav      🔊 Robot tone sounds (Phonemes)
│   │   ├── BX.wav, WX.wav
│   │   └── (7 base sound files for tone-based language)
│   ├── run.mp3                         🎵 Party/Music Mode Sound
│   ├── scan.mp3                        🔍 Scan Mode Sound
│   └── Birthday.mp3                    🎂 Birthday Mode Sound
│
├── Web UI
│   └── AAA_E-7_Micro.html              🌐 Web Control Interface
│
├── Documentation
│   ├── README.md                       📖 Project Documentation
│   ├── Roboter_Tonsprache_Tabelle.pdf  📊 Robot Language Phoneme Mapping
│   ├── grok_image_1773002297769.jpg    📸 Hardware Reference Image
│   └── LICENSE
│
└── Supporting Folders
    ├── E-Sieben_de_raspberry-pi_v3_0_0/ (Legacy version reference)
    ├── __pycache__/                     (Python cache)
    └── .git/                            (Version control)
```

---

## 3. MAIN COMPONENTS & ARCHITECTURE

### 3.1 COMMUNICATION LAYERS

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│ • Web UI: AAA_E-7_Micro.html (HTML + JavaScript + CSS)          │
│ • REST API Interface (Flask)                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                     APPLICATION LAYER (server2.py)              │
├─────────────────────────────────────────────────────────────────┤
│ • Flask Web Server (Port 7567)                                  │
│ • Command Parser & Intent Matching                              │
│ • Speech Generation & Audio Output Threading                    │
│ • Robot Movement Process Management                             │
│ • Dynamic Vocabulary Learning (woerter.txt)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌─────────────────┬┴────────────┬────────────────┐
        │                 │             │                │
┌───────▼──────┐ ┌────────▼──────┐ ┌──▼──────────┐ ┌───▼──────────┐
│  Movement    │ │   Speech      │ │   Sensors   │ │  Audio I/O   │
│   Engine     │ │   Engine      │ │             │ │              │
│              │ │               │ │             │ │              │
│ • robot_     │ │ • robot_      │ │ • ultra-    │ │ • pico2wave  │
│   movement   │ │   sprache.py  │ │   schall    │ │   (TTS)      │
│   .py        │ │   (Tone-Lang) │ │ • kippschutz│ │ • pygame     │
│ • lauf.py    │ │               │ │             │ │ • sox        │
│ • Servo-     │ │ • Tone Mapping│ │ • MPU6050   │ │ • mp3 playback
│   control    │ │   (HK/HL/TK/  │ │ • Distance  │ │              │
│              │ │    BX/WX)     │ │   Detection │ │ • Text-to-   │
└──────────────┘ └───────────────┘ └─────────────┘ │   Speech     │
                                                     └──────────────┘
             ↓                      ↓                    ↓
    ┌─────────────────────────────────────────────────────────┐
    │         HARDWARE ABSTRACTION LAYER                      │
    ├─────────────────────────────────────────────────────────┤
    │ • I2C Bus (SMBus) – PCA9685, MPU6050                    │
    │ • GPIO – Ultrasound (TRIG, ECHO pins)                  │
    │ • PWM Control – Servo pulse width modulation            │
    │ • Audio Devices – Microphone, Speaker/Jack             │
    └─────────────────────────────────────────────────────────┘
             ↓
    ┌─────────────────────────────────────────────────────────┐
    │              RASPBERRY PI HARDWARE                      │
    ├─────────────────────────────────────────────────────────┤
    │ • GPIO Pins (Servo, Ultrasound, IMU)                   │
    │ • I2C Interface (PCA9685, MPU6050, Audio DAC)           │
    │ • Audio Input/Output Jacks                              │
    │ • USB Ports (Microphone/Audio devices)                 │
    └─────────────────────────────────────────────────────────┘
             ↓
    ┌─────────────────────────────────────────────────────────┐
    │            ROBOT HARDWARE PERIPHERALS                   │
    ├─────────────────────────────────────────────────────────┤
    │ • Servo Motors (5 channels via PCA9685)                 │
    │   - Head horizontal (channel 0, left/right look)        │
    │   - Head vertical (channel 1, up/down look)             │
    │   - Left leg (channel 2, walking)                       │
    │   - Right leg (channel 3, walking)                      │
    │   - Body rotation (channel 4, turning)                  │
    │ • HC-SR04 Ultrasound Sensor (distance detection)        │
    │ • MPU6050 6-axis IMU (tilt/balance detection)           │
    │ • Microphone (USB or I2S)                              │
    │ • Speaker/Audio Output                                 │
    └─────────────────────────────────────────────────────────┘
```

### 3.2 MAIN ENTRY POINT: `server2.py`

**Purpose**: Central Flask-based server that coordinates all robot functions

**Key Functions**:
- **Web Server**: Runs Flask on port 7567, provides REST API endpoints
- **Speech Synthesis**: Uses `pico2wave` for text-to-speech (German) + `sox` for robot effects
- **Audio Playback**: Plays pre-recorded MP3 sounds and generated speech via pygame mixer
- **Command Processing**: 
  - Maps user speech input to actions from `Befehle.txt`
  - Falls back to dynamic sentence generation from `woerter.txt`
- **Robot Movement Management**: Spawns `robot_movement.py` as background subprocess
- **Dynamic Learning**: Adds unrecognized words to vocabulary file for future learning

**Key Routes**:
```python
POST /command          # Main voice command endpoint
GET /status            # Query robot state
```

**Internal Threading**:
- Multiple pygame mixer locks for thread-safe audio playback
- Threading for speech synthesis (doesn't block other operations)
- Background process for robot movement

**Potential Bottlenecks**:
1. **pico2wave + sox pipeline**: Runs sequentially (generate WAV → apply effects → play). With effects like pitch/tempo/reverb, this can take 2-4 seconds per sentence.
2. **Pygame mixer blocking**: Audio playback is blocking. Multiple concurrent audio requests will queue.
3. **No request concurrency limit**: Could lead to audio queue overflow with many simultaneous commands.

---

### 3.3 CONVERSATIONAL AI: How It Currently Works

The project uses a **rule-based, learning-enabled** approach:

#### **Phase 1: Speech Recognition**
- Input: Audio from microphone
- Tool: **Vosk** (offline German model: `vosk-model-small-de-0.15`)
- Output: Text string in German
- **Note**: Not explicitly shown in `server2.py` – assumes either:
  - Vosk runs separately and sends text via API
  - or command comes from the web UI (JavaScript)

#### **Phase 2: Intent Matching**
The `handle_command()` function tries these in order:

1. **Hardcoded Movement Commands**:
   ```python
   if user_input in ["lauf", "laufen", "go", "los", "gehen", ...]:
       robot_state = "walking"  # Set internal state
   ```
   Keywords like "lauf" (run), "halt" (stop), "dreh" (turn), "idle" (standby)

2. **Command File Lookup** (`Befehle.txt`):
   ```
   hallo:hallo ich bin e-7 6 8
   systemcheck:Servotest.py
   geburtstag:Birthday.mp3
   scan:ultraschall_messung.py
   witz:warum legen hüner eier?...
   partymodus:run.mp3
   ```
   If a key from this file is found in the user input:
   - If value ends with `.py`: Execute script, read output, speak it
   - If value ends with `.mp3`: Play the sound file
   - Otherwise: Speak the text directly

3. **Fallback: Dynamic Sentence Generation** (`generate_sentence_from_wordlist()`)
   - Reads vocabulary from `woerter.txt`
   - Groups words into: subjects, verbs, objects
   - Generates grammatically simple sentences:
     - Short: "Ich mache Daten."
     - Normal: "Ich mache gerade Daten."
     - Long: "Ich mache Daten, weil ich es wichtig finde."
   - For questions (starting with "wer", "was", "wie", etc.), returns canned responses:
     - "Das ist eine gute Frage, die ich noch nicht beantworten kann."

#### **Phase 3: Speech Output**
Three channels:
1. **Robot Voice** (TTS via pico2wave + sox effects):
   ```bash
   pico2wave -l=de-DE -w=/tmp/robot_raw.wav "TEXT"
   sox /tmp/robot_raw.wav /tmp/robot_voice.wav \
       pitch +100 tempo 0.9 echo 0.8 0.7 100 0.3 reverb
   ```
   Effects: Pitch up (+100 cents), slow tempo (0.9x), echo, reverb → robotic sound

2. **MP3 Playback** (pre-recorded sounds):
   - Category-based: birthday, party, scanning, running

3. **Robot Tone Language** (via `robot_sprache.py`):
   - Converts text to phonetic tone sequences
   - Each letter/digit maps to a 2-character tone code (HK, HL, TK, BX, WX, etc.)
   - Plays corresponding WAV files from `Sounds/`
   - Example: A = "HKHK" → plays HK.wav, then HK.wav

#### **Architectural Weakness - No Real Learning**:
- The system learns **vocabulary** (adds words to `woerter.txt`)
- But does **NOT learn patterns** from user interactions
- It only learns **surface words**, not semantic relationships or new command patterns
- Suggestions for improvement:
  - Add intent clustering based on word similarity
  - Implement simple NLP (spaCy for German)
  - Create a simple knowledge graph of command → action
  - Log successful matches and use them to improve rankings

---

### 3.4 ROBOT MOVEMENT: `robot_movement.py`

**Purpose**: Independent process that handles servo control and idle animations

**States**:
```python
IDLE      # Perform random head movements (looking around)
WALKING   # leg-based forward movement
TURNING   # body rotation
STOPPED   # hold position
```

**Hardware Interface**:
- **I2C Bus (SMBus)**: Controls PCA9685 PWM servo controller at address 0x40
- **5 Servo Channels**:
  ```python
  head_x (channel 0)      # Horizontal head movement (1300-1700 µs)
  head_y (channel 1)      # Vertical head movement
  left_leg (channel 2)    # Left leg servo
  right_leg (channel 3)   # Right leg servo
  body_rotate (channel 4) # Body rotation
  ```
- **Ultrasound Integration**: Reads HC-SR04 to detect obstacles
- **IMU Integration**: Reads MPU6050 to monitor balance

**Key Methods**:
- `init_servos()`: Initializes PCA9685 at 50 Hz PWM
- `set_servo(channel, pulse_us)`: Sets servo position via I2C register writes
- `move_servo_smooth()`: Animates servo movement over N steps
- `measure_distance()`: Reads ultrasound sensor
- `idle_movement_loop()`: Randomly moves head while waiting for commands
- `walk_cycle()`: Alternates leg positions for walking gait

**Animation Logic**:
- **Idle mode**: Randomly picks from predefined head positions every 2-3 seconds
- **Walking mode**: Leg movements with distance sensing for obstacle avoidance
- **Smooth transitions**: All servo movements interpolated over 10 steps with 50ms delays

**Potential Bottlenecks**:
1. **Synchronous I2C**: All servo commands block until I2C write completes
2. **GPIO polling for ultrasound**: Busy-wait loops during distance measurement
3. **No motion planning**: Movements are simple sequences, no inverse kinematics
4. **Blocking sleep() calls**: 50-200ms delays between servo steps could add up

---

### 3.5 SENSORY SYSTEMS

#### **3.5.1 Ultrasound Distance Measurement** (`ultraschall_messung.py`)

**Sensor**: HC-SR04 ultrasonic sensor
```
Pins:
  TRIG (GPIO 27) → Trigger pulse output
  ECHO (GPIO 17) → Time-of-flight measurement
```

**Algorithm**:
1. Pulse TRIG pin low (500ms settle)
2. Send 10µs high pulse on TRIG
3. Measure ECHO pin high duration (time of flight)
4. Distance = pulse_duration × 17150 (cm)
5. Returns integer distance or None on timeout

**Performance Issues**:
- **Blocking GPIO polling**: `while GPIO.input(ECHO_PIN) == 0:` blocks CPU
- **1-second timeout per measurement**: Slow fallback behavior
- **No filtering/averaging**: Raw noisy measurements

**Improvement Ideas**:
- Use hardware PWM edge detection instead of polling
- Implement exponential moving average filter
- Parallel sensor reads with timeout handling

---

#### **3.5.2 Tilt/Balance Protection** (`kippschutz.py`)

**Sensor**: MPU6050 6-axis IMU (accelerometer + gyro)
```
I2C Address: 0x68
Registers: ACCEL_XOUT_H through ACCEL_ZOUT_L
```

**Algorithm**:
1. Read 3-axis acceleration (X, Y, Z)
2. Scale by 1/16384 for gravitational units
3. Calculate tilt angle: `atan2(acc_x, acc_z)`
4. Compare against thresholds:
   - TILT_THRESHOLD: 45° (warning)
   - CRITICAL_THRESHOLD: 60° (emergency stop)

**Current Implementation**:
- Continuous monitoring loop
- Outputs warnings to console
- (Action on tilt not shown – likely integrated into movement logic)

**Limitations**:
- Only uses accelerometer (not gyro)
- No sensor fusion (complementary filter)
- Assumes static or slowly-moving robot

---

### 3.6 HARDWARE CONTROL: Servo Testing & Walking (`Servotest.py`, `lauf.py`)

#### **Servotest.py (Calibration & Testing)**

Tests all 5 servo channels:
- Ranges from 1000µs to 2000µs (0° to 180° for standard servos)
- Interactive test: user selects channel, position value
- PWM calculation for PCA9685:
  ```
  pulse_length = 1000000 / (50 Hz × 4096 channels) = 4.88 µs per unit
  pulse_value = pulse_width_microseconds / 4.88
  ```

#### **lauf.py (Walking Gait)**

Simple walking animation:
```python
def walk_animation(steps=5, step_height=200, delay=0.3):
    for each step:
        left_leg.up(step_height)        # Raise left leg
        right_leg.down()                 # Lower right leg
        sleep(delay)
        left_leg.down()                  # Lower left leg
        right_leg.up(step_height)        # Raise right leg
        sleep(delay)
```

**Limitations**:
- No inverse kinematics (assumes 2-servo legs)
- Fixed step pattern (not adaptive to terrain)
- No feedback from actual servo position

---

### 3.7 ROBOT TONE LANGUAGE: `robot_sprache.py`

**Concept**: Custom phonetic communication system where text is converted to tone sequences

**Phoneme Mapping** (from `Roboter_Tonsprache_Tabelle.pdf`):
```
Letters (A-Z):
A=HKHK, B=HKHL, C=HKTK, ..., Z=BXWX

Digits (0-9):
0=WXHK, 1=WXHL, 2=WXTK, ..., 9=WXBK

Sound Files in Sounds/:
HK.wav, HL.wav, TK.wav, TL.wav, BX.wav, WX.wav (6 base phonemes)
```

**Speech Algorithm**:
```python
for each character in text.upper():
    if char == space:
        sleep(1.2 seconds)  # Long pause
    else:
        tone_code = robot_sounds[char]  # e.g., "HKHK"
        for pair in tone_code (every 2 chars):
            play_sound(pair)  # play HK.wav, then HK.wav
            sleep(0.3 seconds)
```

**Use Cases**:
- **"Binär"** command: Trigger robot tone speech of input text
- **Command codes**: e.g., "101", "107", "7567" (protocol transmissions in robot language)

**Performance**:
- Simple/fast (just file lookups and playback)
- Minimal CPU overhead

**Limitation**: Only supports A-Z and 0-9, not punctuation or special characters

---

## 4. DATA FLOW EXAMPLES

### Example 1: User Says "Hallo"

```
Microphone audio
    ↓
Vosk speech recognition (offline)
    ↓
Text: "hallo"
    ↓
server2.py /command endpoint (POST)
    ↓
handler matches "hallo" in Befehle.txt
    ↓
Value: "hallo ich bin e-7 6 8"
    ↓
pico2wave generates German speech WAV
    ↓
sox applies robotic effects (pitch, echo, reverb)
    ↓
pygame mixer plays result
    ↓
Speaker output: distorted robot voice saying greeting
    ↓
woerter.txt updated with: "hallo"
```

### Example 2: User Says "Lauf"

```
Text: "lauf"
    ↓
server2.py matches movement command
    ↓
robot_state = "walking"
    ↓
robot_movement.py process reads state change
    ↓
Servos execute walk_cycle():
    - left_leg up, right_leg down (0.3s)
    - left_leg down, right_leg up (0.3s)
    - repeat with distance check via ultrasound
    ↓
If obstacle detected (< 20cm):
    - Stop legs
    - Output warning
    ↓
User can interrupt with "halt"
```

### Example 3: User Says Unknown Word "Xyz"

```
Text: "xyz" (not in Befehle.txt)
    ↓
No hardcoded command match
    ↓
generate_sentence_from_wordlist():
    - Extract nouns from woerter.txt
    - Pick random subject, verb, object
    - Generate: "Das System macht xyz momentan."
    ↓
Speak via pico2wave + sox
    ↓
Add "xyz" to woerter.txt for next time
```

---

## 5. PERFORMANCE BOTTLENECKS & ANALYSIS

### 5.1 **CRITICAL BOTTLENECK: Speech Synthesis Pipeline**

**Issue**: Sequential pipeline causes 2-4 second latency per response

**Components**:
1. `pico2wave`: TTS generation (0.5-1s)
2. `sox`: Audio effects processing (1-2s for reverb/echo)
3. `pygame mixer.play()`: Playback (blocking, duration = audio length)

**Problem**: User experience lag between command and audio feedback

**Impact**: 
- User gives command at T=0
- Audio starts at T=2-3 seconds
- Feels unresponsive

**Current Mitigations**:
- Threading (`daemon=True`) – doesn't block next command
- Temporary file cleanup after playback

**Recommended Fixes**:
- Cache generated speech (hash voice + text → cached wav)
- Pre-compute common responses
- Use lighter effects (skip reverb, use simpler pitch shift)
- Consider espeak-ng (faster than pico2wave) for backup
- Add incremental playback (start speaking before effects complete)

---

### 5.2 **Sensor I/O Bottleneck: GPIO Polling**

**Issue**: Busy-wait loops block CPU during sensing

**Code Pattern** (in `ultraschall_messung.py`):
```python
while GPIO.input(ECHO_PIN) == 0:
    pulse_start = time.time()  # BUSY WAIT – ties up one CPU core
while GPIO.input(ECHO_PIN) == 1:
    pulse_end = time.time()    # BUSY WAIT
```

**Problem**: 
- 100% CPU usage during measurement (even if 10µs pulse)
- Blocks other robot operations if called frequently
- 1-second timeout prevents graceful degradation

**Impact**:
- Obstacle avoidance during walking can stall the whole system
- Multiple sensor reads can compound the issue

**Recommended Fixes**:
- Use `RPi.GPIO` edge detection callbacks (interrupt-driven, not polling)
- Implement `gpiozero` library (higher-level, non-blocking)
- Pre-compute distance cache (measure every 100ms, reuse value)
- Run sensor reading in separate thread

---

### 5.3 **I2C Bus Contention**

**Components Sharing I2C**:
- PCA9685 (servos) at 0x40
- MPU6050 (IMU) at 0x68
- Potentially: Audio DAC, RTC, other I2C devices

**Issue**: Sequential I2C transactions block until complete

**Example**:
```python
# servo.set_servo(channel, pulse)
bus.write_byte_data(0x40, reg_base, on & 0xFF)       # ~100µs
bus.write_byte_data(0x40, reg_base + 1, on >> 8)     # ~100µs
# ... more writes

# Meanwhile, tilt detection reads MPU6050:
bus.read_byte_data(0x68, ACCEL_XOUT_H)               # ~100µs
```

**Problem**: No priority or interleaving – all reads/writes serialize

**Impact**:
- Servo updates become choppy under concurrent sensor reads
- Walking gait timing degrades with simultaneous tilt checks
- No real-time guarantees

**Recommended Fixes**:
- Move I2C operations to dedicated thread with queue
- Batch multiple register writes (block I2C transfers)
- Use DMA or interrupt-driven reading for sensors
- Separate servo updates from sensor reads (e.g. 50Hz vs 10Hz)

---

### 5.4 **Audio Mixer Contention**

**Issue**: Single pygame mixer, multiple potential audio sources

**Code**:
```python
mixer_lock = threading.Lock()

def speak_with_robot_voice(text):
    with mixer_lock:
        pygame.mixer.music.load(tmp_fx)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # BLOCKING WAIT
            time.sleep(0.1)
```

**Problem**:
- Lock prevents concurrent audio (sensible)
- But blocking `.get_busy()` loop ties up thread
- Multiple speech threads pile up behind lock

**Example Scenario**:
- User: "Scan" (1.5s audio)
- Before it finishes, server processes "What?" (1.2s audio)
- Second call blocks waiting for lock + first audio completes
- Second audio starts ~2.7s after second command

**Recommended Fixes**:
- Queue audio requests (priority queue: urgent > normal > background)
- Use pygame mixer channels (simultaneous playback on different channels)
- Implement sound level ducking (lower background during speech)
- Add option for non-blocking audio with callbacks

---

### 5.5 **Memory & CPU on Raspberry Pi**

**Current Usage** (estimated):
- Vosk model in RAM: ~50-100 MB
- Python interpreter: ~30 MB
- flask + pygame: ~50 MB
- **Total baseline**: ~150 MB

**Problematic Patterns**:
```python
# Accumulates word list in memory
with open("woerter.txt", "a", encoding="utf-8") as f:
    for word in words:
        f.write(word + "\n")  # No deduplication

# Loads entire word file every time
with open("woerter.txt", "r", encoding="utf-8") as f:
    words = list(set(word.strip().lower() for word in f if word.strip()))
```

**Problems**:
- `woerter.txt` grows unbounded (can reach MB)
- `generate_sentence_from_wordlist()` re-reads and deduplicates every time (O(n))
- No limit on command history or state storage

**Recommended Fixes**:
- Set word list max size (e.g., keep last 5000 unique words)
- Cache deduplicated word list in memory
- Implement simple LRU cache for sentence generation

---

### 5.6 **Servo Motion Jerky/Imprecise**

**Issue**: Simple step-based servo control lacks precision

**Code** (from `robot_movement.py`):
```python
def move_servo_smooth(self, channel, target_us, steps=10, delay=0.05):
    current = self.servo_positions.get(..., 1500)
    step_size = (target_us - current) / steps
    for i in range(steps):
        new_pos = int(current + step_size * (i + 1))
        self.set_servo(channel, new_pos)
        time.sleep(delay)  # 0.05s × 10 = 0.5s total movement
```

**Problems**:
- Servo position cache (`servo_positions`) may become out-of-sync with actual hardware
- No feedback from servo potentiometer → open-loop control
- Fixed timing (50ms) doesn't account for load
- Integer arithmetic can miss target position

**Recommended Fixes**:
- Add servo feedback (read analog pot, compare to target)
- Implement PID controller for smooth reaching
- Add load detection (current monitoring)
- Use velocity profiling (accelerate/decelerate smoothly)

---

## 6. KEY FILES & PURPOSES SUMMARY

| **File** | **Module** | **Purpose** | **Dependencies** | **Performance Impact** |
|----------|-----------|-----------|-----------------|----------------------|
| `server2.py` | Flask Server | Central command dispatcher, audio synthesis, web API | flask, flask_cors, pygame, subprocess | ⚠️ **HIGH** – TTS + sox bottleneck |
| `robot_sprache.py` | Tone Language | Convert text to phonetic tone sequences, playback | pygame, logging | ✅ Low |
| `robot_movement.py` | Movement Control | Servo control, idle animations, state management | smbus, time, threading, enum | ⚠️ **HIGH** – I2C + GPIO polling |
| `lauf.py` | Walking Gait | Walking animation sequences, leg coordination | smbus | ⚠️ **HIGH** – blocking I2C writes |
| `Servotest.py` | Calibration | Interactive servo testing, range discovery | smbus | ✅ Low (manual testing only) |
| `ultraschall_messung.py` | Distance Sensor | HC-SR04 distance measurement, obstacle detection | RPi.GPIO | ⚠️ **CRITICAL** – busy-wait polling |
| `kippschutz.py` | Tilt Protection | MPU6050 balance monitoring, angle calculation | smbus, math | ✅ Low – infrequent reads |
| `Befehle.txt` | Config | Command → Action mapping (text file) | — | ✅ None (read at startup) |
| `woerter.txt` | Config | Growing vocabulary list | — | ⚠️ **MEDIUM** – re-read every inference |
| `AAA_E-7_Micro.html` | Web UI | Rich interface for remote control, voice input | (none, client-side HTML/JS) | ✅ None |
| `model/vosk-model-small-de-0.15/` | Model | German speech recognition model (offline) | vosk library | ⚠️ **HIGH** – depends on vosk recognition speed |

---

## 7. MAIN ARCHITECTURAL STRENGTHS

1. ✅ **Modular Design**: Clear separation of concerns (sensors, movement, speech, server)
2. ✅ **Offline Capability**: No internet required (critical for robotics)
3. ✅ **Learning-Enabled**: Dynamic vocabulary accumulation
4. ✅ **Educational Focus**: Code is readable and well-commented
5. ✅ **Extensible**: Easy to add new commands or sensors
6. ✅ **Multi-Channel Audio**: Supports MP3, TTS, tone-based speech, pre-recorded sounds
7. ✅ **Web-Based UI**: Remote access via browser, RESTful API

---

## 8. MAIN ARCHITECTURAL WEAKNESSES & RISKS

1. ❌ **No True AI/NLP**: Rule-based system, not machine learning
2. ❌ **Synchronous Bottlenecks**: pico2wave, sox, I2C all block
3. ❌ **No Error Recovery**: Timeouts lead to hangs, not graceful degradation
4. ❌ **Memory Unbounded**: `woerter.txt` grows without limit
5. ❌ **Sensor Reliability**: GPIO busy-wait, no edge detection
6. ❌ **Poor Concurrency**: Mutex locks on shared resources, no queuing
7. ❌ **Open-Loop Control**: Servos have no feedback
8. ❌ **Scalability**: Hard to add more servos, sensors without redesign
9. ❌ **Documentation Gap**: Web UI JavaScript not shown (API/format unclear)
10. ❌ **Testing**: No unit tests, integration tests, or CI/CD

---

## 9. RECOMMENDED OPTIMIZATIONS (Priority Order)

### **PHASE 1: Quick Wins (1-2 hours)**
1. **Reduce TTS Latency**:
   - Cache pico2wave output + sox effects by text hash
   - Use simpler sox effects (skip reverb if time is critical)
   - Pre-generate responses for common commands

2. **Fix Sensor Polling**:
   - Replace `while GPIO.input()` loops with `RPi.GPIO.wait_for_edge()`
   - Add distance reading cache (measure every 100ms in thread)

3. **Bound Memory**:
   - Limit `woerter.txt` to 5000 lines, rotate oldest words out
   - Deduplicate entries during append, not read

### **PHASE 2: Medium Effort (half day)**
1. **Move I2C to Separate Thread**:
   - Singleton I2C controller with request queue
   - Prevents servo + sensor contention

2. **Async Audio Queue**:
   - Replace `mixer_lock` + blocking with priority queue
   - Speaker thread pulls from queue independently

3. **PID Servo Control**:
   - Add simple proportional control to servo positioning
   - Better smooth movement, faster settling

4. **Add Logging & Metrics**:
   - Track TTS latency, sensor read times
   - Identify runtime bottlenecks

### **PHASE 3: Long-Term (days)**
1. **Implement NLP Layer**:
   - Use spaCy + German models for entity extraction
   - Build intent classifier (decision tree or simple NN)

2. **Real-Time Scheduler**:
   - Prioritize movement over speech, speech over UI updates
   - Use multiprocessing instead of threading for servo control

3. **Hardware Upgrades**:
   - Add analog/PWM feedback on servos
   - Consider faster I2C clock (400kHz → 1MHz)

4. **Testing Infrastructure**:
   - Unit tests for speech generation, command parsing
   - Integration tests for servo sequences
   - Continuous integration on each commit

---

## 10. TECHNOLOGY STACK SUMMARY

| **Component** | **Technology** | **Version/Model** | **Notes** |
|---------------|----------------|------------------|----------|
| **Speech Recognition** | Vosk | vosk-model-small-de-0.15 | Offline, German, ~50MB model |
| **Speech Synthesis** | pico2wave + sox | system package | German TTS, effects pipeline |
| **Audio Playback** | pygame mixer | pygame stable | Thread-safe music playback |
| **Web Framework** | Flask | >1.0 | Lightweight WSGI server |
| **GPIO Control** | RPi.GPIO (legacy) | 0.7.0+ | Or gpiozero for higher-level |
| **I2C Control** | smbus (py-smbus) | 1.1 | Direct register access |
| **Servo Hardware** | PCA9685 | 16-channel PWM | $3-5 breakout board |
| **IMU Sensor** | MPU6050 | 6-axis accelerometer | $2-3 sensor module |
| **Distance Sensor** | HC-SR04 | Ultrasonic | $1-2 sensor module |
| **Motor Control** | Standard servos | SG90 or equivalent | 5V PWM servos |
| **Microprocessor** | Raspberry Pi | 3B/3B+/4B | Dual/quad-core ARM |
| **OS** | Raspberry Pi OS | 32-bit or 64-bit | Debian-based |

---

## 11. ENTRY POINTS & HOW TO RUN

### **Starting the Robot**

```bash
# On Raspberry Pi
cd E-768-Droid
source venv/bin/activate  # or whisper-venv/bin/activate

# Method 1: Flask server (main UI + API)
python3 server2.py
# Listens on http://localhost:7567

# Method 2: Robot tone language demo
python3 robot_sprache.py
# Prompts for text, outputs tone sequences

# Method 3: Movement test
python3 lauf.py              # Walk animation
python3 Servotest.py         # Interactive servo calibration

# Method 4: Sensor testing
python3 ultraschall_messung.py     # Distance measurement
python3 kippschutz.py              # Tilt/balance check
```

### **Web UI Access**

Once `server2.py` is running:
1. Open browser → `http://raspberry-pi-ip:7567`
2. UI loads from `AAA_E-7_Micro.html`
3. Send voice/text commands via web interface
4. See real-time responses and status

### **Command Examples**

Via web UI or direct API:

```bash
# Movement commands
curl -X POST http://localhost:7567/command \
  -H "Content-Type: application/json" \
  -d '{"intent": "lauf"}'  # Walk forward

curl -X POST http://localhost:7567/command \
  -H "Content-Type: application/json" \
  -d '{"intent": "halt"}'  # Stop

# Query status
curl http://localhost:7567/status
```

---

## 12. DEPLOYMENT NOTES

### **Raspberry Pi Setup (First Time)**

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv alsa-utils sox

# 2. Install pico2wave, espeak
sudo apt install -y libpico-utils

# 3. Optional: Install GPIO library
pip install RPi.GPIO
# or newer:
pip install gpiozero

# 4. Clone project
git clone https://github.com/LalulCool123/E-768-Droid.git
cd E-768-Droid

# 5. Create venv & install Python packages
python3 -m venv venv
source venv/bin/activate
pip install vosk sounddevice flask flask-cors pygame smbus-cffi

# 6. Test audio
speaker-test -t sine -f 1000 -l 1  # Test speaker
arecord -d 3 test.wav               # Test microphone

# 7. Run server
python3 server2.py
```

### **Auto-Start on Boot** (optional)

Create `/etc/systemd/system/droid.service`:
```ini
[Unit]
Description=E-768 Droid Robot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/E-768-Droid
ExecStart=/home/pi/E-768-Droid/venv/bin/python3 server2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable droid.service
sudo systemctl start droid.service
```

---

## 13. CONCLUSION

**E-768 Droid** is a well-structured, education-focused robotics project that demonstrates:
- ✅ Offline speech recognition & synthesis
- ✅ Modular hardware control (servos, sensors)
- ✅ Web-based UI for remote interaction
- ✅ Learning-enabled dynamic vocabulary

**Current Limitations**:
- ❌ Rule-based, not ML-based conversational AI
- ❌ Synchronous bottlenecks in TTS + I2C
- ❌ Busy-wait polling for sensors
- ❌ No error recovery or graceful degradation

**Next Steps for Production-Grade System**:
1. Implement async/threaded I2C and GPIO
2. Add caching layer for TTS
3. Integrate real NLP (spaCy, Rasa)
4. Add comprehensive logging & monitoring
5. Write unit & integration tests
6. Implement priority-based task scheduling

The project is **ideal for learning** and **quick prototyping**, but would need significant refactoring for a robust, production robot system.

---

*Analysis Date: March 27, 2026*
*Project Repository: https://github.com/LalulCool123/E-768-Droid*
