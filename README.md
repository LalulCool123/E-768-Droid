# Projekt E-768 – Autonomer Droide mit eigener KI & Verhaltenslogik

> Experimentelles KI‑Projekt: Ein virtueller Droide mit eigener Entscheidungs‑, Lern‑ und Verhaltenslogik.

---

## 🧾 Überblick

Projekt **E-768** ist ein Simulations‑/Entwicklungsprojekt für einen **autonomen Droiden**, der:

- eine **eigene KI‑Komponente** für Wahrnehmung und Entscheidung nutzt,
- eine modulare **Verhaltenslogik** (State Machines / Behavior Trees / GOAP o. Ä.) besitzt,
- auf **Ereignisse und Umgebung** reagiert (Sensorik‑Simulation),
- sein Verhalten **schrittweise optimieren oder erlernen** kann.

Ziel ist es, eine flexible Architektur zu schaffen, in der man:
- neue **Sensoren**, **Aktionen** und **Verhaltensmuster** schnell ergänzen kann,
- verschiedene **KI‑Strategien** (Regelbasis, RL, Planner, LLM‑Backend, …) ausprobieren kann.

---

## 🏗 Projektstruktur


```text
E-768-Droid/
├── E-Sieben_de_raspberry-pi_v3_0_0/
│   └── E-7_Befehle/
├── Sounds/
├── __pycache__/
├── model/
│   └── vosk-model-small-de-0.15/
├── rhino/
│   └── binding/
│       └── python/
├── whisper-venv/
│
├── AAA_E-7_Micro.html
├── Befehle.txt
├── Birthday.mp3
├── LICENSE
├── README.md
├── Roboter_Tonsprache_Tabelle.pdf
├── Servotest.py
├── grok_image_1773002297769.jpg
├── kippschutz.py
├── lauf.py
├── robot_sprache.py
├── run.mp3
├── sats.txt
├── scan.mp3
├── server2.py
├── ultraschall_messung.py
└── woerter.txt

