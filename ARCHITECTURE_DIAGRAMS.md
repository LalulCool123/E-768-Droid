# E-768 Droid – Architecture Diagrams & Data Flow

## 1. SYSTEM ARCHITECTURE (High-Level)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐  │
│  │   Web UI Browser         │    │   Voice Input (Microphone)   │  │
│  │ (HTML/JavaScript/CSS)    │    │   or                         │  │
│  │ - Status display         │    │   Text Input (Keywords)      │  │
│  │ - Command buttons        │    │                              │  │
│  │ - Response text          │    │   [Triggers] → POST /command │  │
│  └────────────┬─────────────┘    └──────────────┬───────────────┘  │
│               │                                  │                  │
│               └──────────────────┬───────────────┘                  │
│                                  │                                  │
└──────────────────────────────────┼──────────────────────────────────┘
                    ▼ (REST API)
┌─────────────────────────────────────────────────────────────────────┐
│               APPLICATION/SERVER LAYER (server2.py)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Flask Web Server (Port 7567)                              │    │
│  │ ─────────────────────────────────────────────────────────  │    │
│  │ • Route: POST /command                                    │    │
│  │ • Route: GET /status                                      │    │
│  │ • Route: GET /static (HTML assets)                        │    │
│  └───────────┬──────────────────────────────────────────────┘    │
│              │ (parse intent/command)                             │
│              ▼                                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Command Parser & Dispatcher                               │    │
│  │ ─────────────────────────────────────────────────────────  │    │
│  │                                                            │    │
│  │  1. Try hardcoded movement command (lauf, halt, idle)    │    │
│  │                                    ↓                       │    │
│  │  2. Try Befehle.txt lookup (keyword match)               │    │
│  │                                    ↓                       │    │
│  │  3. Fallback: generate_sentence_from_wordlist()          │    │
│  │                                                            │    │
│  └────────────┬──────────────────────────────────────────────┘    │
│               │ (text output from matched action)                 │
│               ▼                                                    │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐   │
│  │ Audio Synthesis Engine   │  │ Robot Movement Manager       │   │
│  │ ────────────────────────  │  │ ──────────────────────────  │   │
│  │                          │  │                             │   │
│  │ Text → pico2wave         │  │ • Start/Stop subprocess     │   │
│  │      ↓ WAV (raw)         │  │ • Track PID                 │   │
│  │ WAV → sox (effects)      │  │ • Update robot_state        │   │
│  │      ↓ WAV (processed)   │  │ • Monitor for completion    │   │
│  │ WAV → pygame.mixer       │  │                             │   │
│  │      ↓ Speaker output    │  └────────► robot_movement.py │   │
│  │                          │             (background proc)  │   │
│  └──────────────────────────┘  └──────────────────────────────┘   │
│                                                                    │
│  Threading                                                         │
│  ├─ Main: Flask HTTP requests                                     │
│  ├─ Audio: pico2wave (TTS generation)                             │
│  ├─ Audio: sox (effect processing)                                │
│  ├─ Audio: pygame playback (blocking wait on music.get_busy())    │
│  └─ File I/O: woerter.txt append, Befehle.txt read              │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
          │                              │
          │ (spawns subprocess)          │ (via threading)
          │                              │
┌─────────▼──────────────────┐  ┌────────▼──────────────────────────┐
│  ROBOT MOVEMENT PROCESS    │  │  AUDIO I/O SUBSYSTEM              │
│  (robot_movement.py)       │  │                                   │
├────────────────────────────┤  └────────────────────────────────────┘
│ - State machine (IDLE/     │
│   WALKING/TURNING)         │
│ - Servo control (servos    │
│   0-4 on PCA9685)          │
│ - Distance sensing         │
│   (ultrasound)             │
│ - Balance monitoring       │
│   (tilt sensor)            │
└────────┬───────────────────┘
         │ (via I2C bus, GPIO)
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 HARDWARE (Raspberry Pi GPIO/I2C)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  I2C Bus (GPIO 2/3)          GPIO (Direct)                         │
│  ├─ 0x40: PCA9685            ├─ GPIO 27: Ultrasound TRIG          │
│  │   └─ 5 servo PWM channels │ └─ GPIO 17: Ultrasound ECHO        │
│  │       (0=head_x, 1=head_y,│                                    │
│  │        2=left_leg,         │ Audio Devices                      │
│  │        3=right_leg,        │ ├─ Microphone (USB/I2S)           │
│  │        4=body_rotate)      │ └─ Speaker (3.5mm/HDMI/USB)       │
│  │                            │                                    │
│  └─ 0x68: MPU6050            │ EEPROM (Optional)                  │
│     └─ 6-axis IMU            │ └─ Calibration data, configs       │
│        (accel + gyro)        │                                    │
│                              │                                    │
└──────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ROBOT HARDWARE PERIPHERALS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  • 5x SG90 Servo Motors      • HC-SR04 Ultrasound Sensor           │
│    - Head horizontal (pan)   • MPU6050 IMU (6-axis)                │
│    - Head vertical (tilt)    • Power distribution                  │
│    - Left leg                • External motor drivers              │
│    - Right leg               • Battery/Power supply                │
│    - Body rotation                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. VOICE COMMAND FLOW (Detailed)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INPUT                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Option A: Voice                 Option B: Text                    │
│  ┌────────────────────┐          ┌─────────────────────┐           │
│  │ Microphone Audio   │          │ Type in Web UI      │           │
│  │ ↓                  │          │ ↓                   │           │
│  │ Vosk Recognition   │          │ Parse text directly │           │
│  │ ↓                  │          └──────────┬──────────┘           │
│  │ Text (German)      │                     │                      │
│  └────────────┬───────┘                     │                      │
│               └─────────────────┬───────────┘                      │
│                                 │                                   │
│                                 ▼                                   │
│                    ┌──────────────────────┐                         │
│                    │ POST /command        │                         │
│                    │ {"intent": "TEXT"}   │                         │
│                    └──────────┬───────────┘                         │
│                               │                                     │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│            COMMAND PROCESSING (server2.py, handle_command)          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Stage 1: Clean Input                                              │
│  ┌─────────────────────────────────────────┐                       │
│  │ user_input = "lauf"                     │                       │
│  │ user_input.lower().replace("e7", "")    │                       │
│  └──────────────────┬──────────────────────┘                       │
│                     │                                               │
│  Stage 2: Learning  ▼                                              │
│  ┌─────────────────────────────────────────┐                       │
│  │ Extract words: ["lauf"]                 │                       │
│  │ Append to woerter.txt                   │                       │
│  └──────────────────┬──────────────────────┘                       │
│                     │                                               │
│  Stage 3: Match Intent                     ▼                       │
│  ╔═════════════════════════════════════════════════════════════╗   │
│  ║ Try Match (Priority):                                       ║   │
│  ║ ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡   ║   │
│  ║                                                             ║   │
│  ║ [1] HARDCODED MOVEMENT                                      ║   │
│  ║     if "lauf" in ["lauf","laufen","go","los",...]:         ║   │
│  ║         robot_state = "walking"  ✓ MATCH!                 ║   │
│  ║         return {"response": "Ich laufe jetzt los!"}        ║   │
│  ║                                                             ║   │
│  ╚═════════════════════════════════════════════════════════════╝   │
│                                                                     │
│  [If no match, try next:]                                          │
│                                 ▼                                   │
│  ╔═════════════════════════════════════════════════════════════╗   │
│  ║ [2] BEFEHLE.TXT LOOKUP                                      ║   │
│  ║     Load Befehle.txt:                                       ║   │
│  ║     ─────────────────                                       ║   │
│  ║     hallo:hallo ich bin e-7 6 8                           ║   │
│  ║     scan:ultraschall_messung.py                          ║   │
│  ║     witz:warum legen hüner eier?...                      ║   │
│  ║                                                             ║   │
│  ║     Search: is "lauf" or any word in line a key?           ║   │
│  ║     → NO MATCH                                              ║   │
│  ║                                                             ║   │
│  ╚═════════════════════════════════════════════════════════════╝   │
│                                                                     │
│  [If still no match, fallback:]                                    │
│                                 ▼                                   │
│  ╔═════════════════════════════════════════════════════════════╗   │
│  ║ [3] GENERATE RESPONSE FROM WORDLIST                         ║   │
│  ║     generate_sentence_from_wordlist(user_input="lauf")      ║   │
│  ║                                                              ║   │
│  ║     Check if question: starts with wer/was/wie/warum?       ║   │
│  ║     → NO (not a question)                                    ║   │
│  ║                                                              ║   │
│  ║     Load woerter.txt → extract subjects, verbs, objects      ║   │
│  ║     Pick random sentence structure:                          ║   │
│  ║       - Short:   "Ich mache ein_beliebiges_objekt."         ║   │
│  ║       - Normal:  "Ich mache gerade ein_beliebiges_objekt."  ║   │
│  ║       - Long:    "Ich mache ... weil ich es wichtig finde." ║   │
│  ║                                                              ║   │
│  ║     Return: {"response": "generated sentence"}              ║   │
│  ║                                                              ║   │
│  ╚═════════════════════════════════════════════════════════════╝   │
│                                                                     │
│  Stage 4: Action Execution (after matching)                        │
│  ┌──────────────────────────────────────────┐                      │
│  │ if matched_value.endswith(".py"):        │                      │
│  │   → execute Python script, read stdout   │                      │
│  │                                          │                      │
│  │ if matched_value.endswith(".mp3"):       │                      │
│  │   → thread: play_mp3(file_path)          │                      │
│  │                                          │                      │
│  │ else:                                    │                      │
│  │   → thread: speak_with_robot_voice(text) │                      │
│  └──────────────────┬───────────────────────┘                      │
│                     │                                               │
│  Stage 5: Response  ▼                                              │
│  ┌──────────────────────────────────────────┐                      │
│  │ return jsonify({"response": text})       │                      │
│  └──────────────────────────────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
           │                                          │
           │ (spawns robot_movement in bg)           │ (threading.Thread)
           │                                          │
           ▼                                          ▼
┌──────────────────────────┐              ┌──────────────────────────────┐
│ robot_movement.py        │              │ Audio Synthesis (Threaded)  │
│ ─────────────────        │              │ ────────────────────────────  │
│ Starts walking gait      │              │                             │
│ Updates servo positions  │              │ speak_with_robot_voice()    │
│ Monitors ultrasound      │              │ or play_mp3()               │
└──────────────────────────┘              └────────┬────────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────────────┐
                                          │ pico2wave -l=de-DE ...       │
                                          │ Generates German TTS         │
                                          └─────────┬────────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────────────┐
                                          │ sox effect processing        │
                                          │ pitch +100                   │
                                          │ tempo 0.9                    │
                                          │ echo reverb                  │
                                          └─────────┬────────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────────────┐
                                          │ pygame.mixer.music.play()    │
                                          │ Blocking: wait for completion│
                                          └─────────┬────────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────────────────┐
                                          │ Speaker Output               │
                                          │ (audio jack, HDMI, USB)      │
                                          └──────────────────────────────┘
```

---

## 3. MOVEMENT & SENSOR LOOP (robot_movement.py)

```
┌─────────────────────────────────────────────────────────────────┐
│                  ROBOT MOVEMENT PROCESS (Continuous Loop)       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Initialize                                               │   │
│  │ ─────────────                                            │   │
│  │ PCA9685 @ 50 Hz PWM                                      │   │
│  │ Load servo position cache                                │   │
│  │ State = IDLE                                             │   │
│  └───────────────────┬────────────────────────────────────┘   │
│                      │                                        │
│                      ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │              MAIN STATE MACHINE                          │   │
│  │              ─────────────────────                       │   │
│  │                                                          │   │
│  │              ┌────────────────────┐                      │   │
│  │              │   Check State      │                      │   │
│  │              │                    │                      │   │
│  │              │ from server2.py    │                      │   │
│  │              └─┬────────┬────────┬┘                      │   │
│  │                │        │        │                      │   │
│  │         IDLE   │ WALKING│TURNING │ STOPPED              │   │
│  │         ▼      ▼        ▼        ▼                       │   │
│  │                                                          │   │
│  │  ╔════════════════════════════════════════════╗          │   │
│  │  ║ IDLE STATE: Ambient Animation            ║          │   │
│  │  ║ ──────────────────────────────────────── ║          │   │
│  │  ║ Random head movements every 2-3s:        ║          │   │
│  │  ║  • Look left (head_x = 1300)             ║          │   │
│  │  ║  • Look right (head_x = 1700)            ║          │   │
│  │  ║  • Look down (head_y = 1400)             ║          │   │
│  │  ║  • Look up (head_y = 1600)               ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ Smooth interpolation: 10 steps × 50ms    ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ No distance check (not moving forward)   ║          │   │
│  │  ╚────────────────────────────────────────═╝          │   │
│  │                      ▼                                 │   │
│  │  ╔════════════════════════════════════════════╗          │   │
│  │  ║ WALKING STATE: Gait Cycle + Obstacle Sense║          │   │
│  │  ║ ──────────────────────────────────────── ║          │   │
│  │  ║ Loop:                                     ║          │   │
│  │  ║  1. Raise left leg (left_leg = 1700)    ║          │   │
│  │  ║  2. Measure distance (ultrasound)        ║          │   │
│  │  ║     IF distance < 20cm → STOP, log warn ║          │   │
│  │  ║  3. Lower left leg, raise right (rotate) ║          │   │
│  │  ║  4. Measure distance again               ║          │   │
│  │  ║     IF distance < 20cm → STOP, log warn ║          │   │
│  │  ║  5. Continue until robot_state changes  ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ Timing: ~0.3s per half-step              ║          │   │
│  │  ╚════════════════════════════════════════╝          │   │
│  │                      ▼                                 │   │
│  │  ╔════════════════════════════════════════════╗          │   │
│  │  ║ TURNING STATE: Body Rotation              ║          │   │
│  │  ║ ──────────────────────────────────────── ║          │   │
│  │  ║ Rotate body_rotate servo (channel 4):     ║          │   │
│  │  ║  • 1300 µs: Turn left                     ║          │   │
│  │  ║  • 1500 µs: Face forward                  ║          │   │
│  │  ║  • 1700 µs: Turn right                    ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ Smooth motion: 10-step interpolation      ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ (Status: legs stay in place)             ║          │   │
│  │  ╚════════════════════════════════════════╝          │   │
│  │                      ▼                                 │   │
│  │  ╔════════════════════════════════════════════╗          │   │
│  │  ║ STOPPED STATE: Hold Position              ║          │   │
│  │  ║ ──────────────────────────────────────── ║          │   │
│  │  ║ Maintain all servo positions at current  ║          │   │
│  │  ║ No movement, no animation                ║          │   │
│  │  ║                                          ║          │   │
│  │  ║ (Robot frozen in place)                  ║          │   │
│  │  ╚════════════════════════════════════════╝          │   │
│  │                      │                                 │   │
│  │                      └──────────────┬──────────────┘   │   │
│  │                                     │                 │   │
│  │                                  sleep(0.1)           │   │
│  │                                     │                 │   │
│  │                                     ▼                 │   │
│  │                        [Loop back to Check State]     │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Sensors Active (in all states):                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Ultrasound Distance Check (if WALKING):                 │ │
│  │   GPIO 27 (TRIG) → pulse for 10µs                        │ │
│  │   GPIO 17 (ECHO) → measure high time                     │ │
│  │   distance = pulse_time × 17150 (cm)                    │ │
│  │   If < 20cm → log obstacle warning, consider stopping    │ │
│  │                                                           │ │
│  │ • Tilt Check (if needed):                                │ │
│  │   Read MPU6050 @ 0x68 over I2C                          │ │
│  │   Compute angle from acceleration                        │ │
│  │   If > 45° → warning, if > 60° → emergency stop         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
            │                              │
            │ (I2C writes every step)      │ (GPIO polling for distance)
            │                              │
            ▼                              ▼
     ┌─────────────────┐         ┌──────────────────┐
     │ PCA9685         │         │ HC-SR04 Sensor   │
     │ (5 servos)      │         │ (distance)       │
     └─────────────────┘         └──────────────────┘
```

---

## 4. AUDIO SYNTHESIS PIPELINE

```
Input Text: "Hallo, ich bin E-7 6 8"
│
▼
┌──────────────────────────────────────────────────┐
│       Threaded: speak_with_robot_voice()        │
│                                                  │
│  1. Generate thread-safe temp filenames         │
│     /tmp/robot_raw_{thread_id}.wav              │
│     /tmp/robot_voice_{thread_id}.wav            │
│                                                  │
│  2. Call pico2wave (German text-to-speech)      │
│     $ pico2wave -l=de-DE \                      │
│              -w=/tmp/robot_raw_123.wav \       │
│              "Hallo, ich bin E-7 6 8"          │
│     ↓ Output: Raw PCM 48kHz mono WAV          │
│                                                  │
│  3. Apply effects with sox                      │
│     $ sox /tmp/robot_raw.wav /tmp/robot_voice/ │
│              pitch +100   [pitch shift up]     │
│              tempo 0.9    [slow by 10%]        │
│              echo 0.8 0.7 100 0.3  [echo]      │
│              reverb       [reverb effect]       │
│     ↓ Output: Processed WAV with effects       │
│                                                  │
│  4. Load into pygame mixer (thread-safe lock)   │
│     with mixer_lock:                             │
│         pygame.mixer.music.load()               │
│         pygame.mixer.music.play()               │
│         while mixer.get_busy():  [BLOCKING]     │
│             sleep(0.1)                         │
│     ↓ Blocks until audio finishes playing      │
│                                                  │
│  5. Clean up temp files                        │
│     os.remove(raw_file)                         │
│     os.remove(effects_file)                     │
│                                                  │
└──────────────────────────────────────────────────┘
│
▼
Speaker Output
(3.5mm jack / HDMI / USB audio device)

Timeline Example:
T=0.0s: POST /command received
T=0.1s: pico2wave started
T=0.8s: pico2wave finished (~0.7s)
T=0.9s: sox processing started
T=2.1s: sox finished (~1.2s)
T=2.2s: pygame.mixer.play() started
T=3.8s: Audio finished playing (~1.6s duration)
────────────────────────────────────────────
Total latency: 3.8 seconds! ⚠️

BOTTLENECK: Sequential pipeline blocks until complete
```

---

## 5. CONFIGURATION & LEARNING FLOW

```
┌───────────────────────────────────────┐
│     User Speaks: "hallo wie geht's"   │
└─────────────────┬─────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  server2.py        │
         │  Word Extraction   │
         └─────────┬──────────┘
                   │
        words = ["hallo", "wie", "geht's"]
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Append to woerter.txt            │
    │ ──────────────────────────────── │
    │                                  │
    │ with open("woerter.txt", "a"):   │
    │   for word in words:             │
    │     f.write(word + "\n")         │
    │                                  │
    │ Before: 25 lines                 │
    │ After:  28 lines                 │
    │         + 3 new words            │
    └──────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ woerter.txt Content              │
    │ ──────────────────────────────── │
    │                                  │
    │ hallo                            │ ← new
    │ wie                              │ ← new
    │ geht's                           │ ← new
    │ geburtstag                       │
    │ datenbank                        │
    │ ... [accumulated over time]      │
    │                                  │
    │ Problem: Unbounded growth!       │
    │ woerter.txt can become MB         │
    │ No deduplication during write     │
    │ (dedup only on read)             │
    └──────────────────────────────────┘

Next sentence generation uses accumulated vocabulary:

┌──────────────────────────────────────────┐
│  generate_sentence_from_wordlist()       │
├──────────────────────────────────────────┤
│                                          │
│ 1. Load & deduplicate woerter.txt       │
│    words = list(set(...))  O(n) cost    │
│                                          │
│ 2. Filter by word type:                 │
│    subjects = [...] (hardcoded)         │
│    verbs = [w for w in words           │
│            if w in verb_list]           │
│    objects = [w for w ... len > 2]      │
│                                          │
│ 3. Handle questions:                    │
│    if tokens[0] in question_words:      │
│      return canned response             │
│                                          │
│ 4. Pick sentence template:              │
│    "Kurz":   "{subj} {verb} {obj}."    │
│    "Normal": "{subj} {verb} gerade.."  │
│    "Lang":   "Manchmal {verb} ich.."   │
│                                          │
│ 5. Generate & return sentence          │
│                                          │
└──────────────────────────────────────────┘

Example Generation Chain:
subjects = ["Ich", "Das System", "Wir"]
verbs = ["mache", "starte", "spiele"]
objects = ["geburtstag", "datenbank"]

Random Pick:
subject = "Das System" (randchoice)
verb = "starte"
obj = "datenbank"
template = "lang"

Generated: "Das System starte datenbank,
            weil ich es wichtig finde."
```

---

## 6. BEFEHLE.TXT COMMAND RESOLUTION

```
Befehle.txt Content Example:
─────────────────────────────
hallo:hallo ich bin e-7 6 8
systemcheck:Servotest.py
geburtstag:Birthday.mp3
scan:ultraschall_messung.py
witz:warum legen hüner eier?...
musik:run.mp3

User Input: "Hallo, wie geht's?"
             ↓ (lowercase)
        "hallo wie geht's"

Lookup Logic:
┌─────────────────────────────────┐
│ for key in commands.keys():      │
│   if key in user_input:          │
│     → matched!                   │
│     value = commands[key]        │
└─────────────────────────────────┘

Check: "hallo" in "hallo wie geht's" → YES ✓

Action Routing:
  if value.endswith(".py"):
    → Execute Python script
      output = subprocess.check_output(["python3", ...])
      speak_with_robot_voice(output)

  elif value.endswith(".mp3"):
    → Play audio file
      play_mp3(filepath)

  else:
    → Speak text directly
      speak_with_robot_voice(value)

Result: speak("hallo ich bin e-7 6 8")
```

---

## 7. DEVICE INTEGRATION MAP

```
┌────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 4B/3B+                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  GPIO Header (40 pins)                                         │
│  ├─ GPIO 2  ──────────┐                                        │
│  ├─ GPIO 3  ──────────┤──────► SDA (I2C)                       │
│  │                    │                                        │
│  ├─ GPIO 27 ─────────────────► HC-SR04 TRIG (Ultrasound)      │
│  ├─ GPIO 17 ─────────────────► HC-SR04 ECHO (Ultrasound)      │
│  │                                                            │
│  └─ GND ──────┐                                                │
│               │                                                │
│  CPU          │       I2C Bus @ 100-400 kHz                    │
│  Quad-core    │       ┌─────────────────────┐                  │
│  ARM          │       │ SDA (GPIO 2)        │                  │
│               │       │ SCL (GPIO 3)        │                  │
│  Audio        │       │ GND                 │                  │
│  Codec        │       └────┬────────┬───────┘                  │
│  (built-in)   │            │        │                          │
│               │            │        │                          │
└───────────────┼────────────┼────────┼──────────────────────────┘
                │            │        │
        ┌───────┴──────┐     │        │
        │              │     │        │
        ▼              ▼     ▼        ▼
    3.5mm         USB      0x40    0x68
    Jack          Ports    PCA9685  MPU6050
    │              │       PWM      6-axis
    │              │       Ctrl     IMU
    │              │       (5ch)
    │              │         │
    │    ┌─────────┘         │
    │    │                   │
    ▼    ▼                   ▼
  Speaker USB Mic     5x SG90 Servos
                     + Power Distribution
                           │
                     ┌──────┼──────┬──────┬──────┐
                     │      │      │      │      │
                     ▼      ▼      ▼      ▼      ▼
                    Head   Head  Left  Right  Body
                    Horiz  Vert  Leg   Leg    Rot

              HC-SR04 Sensor (2 wires)
                │
    ┌───────────┴───────────┐
    │                       │
 TRIG                     ECHO
 GPIO 27                GPIO 17
    │                       │
    └─►[Sensor]◄────────────┘
        (distance measurement)

MPU6050 (I2C Combo):
  SDA/SCL → I2C Bus
  (Measures acceleration X,Y,Z)
  (Computes tilt angle)
```

---

*Diagrams & flows v1.0 – March 2026*
