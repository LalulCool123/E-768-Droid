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

*(Beispiel – bitte an den tatsächlichen Code anpassen)*

```text
E-768/
├─ src/
│  ├─ core/              # Basis-Framework, Interfaces, Utils
│  ├─ ai/                # KI-Module (Agent, Planner, ggf. ML-Modelle)
│  ├─ behavior/          # Verhaltenslogik (FSM, Behavior Trees, …)
│  ├─ sensors/           # Sensor-Simulation (Umgebungsdaten, Events)
│  ├─ actuators/         # Aktionen des Droiden (Bewegen, Interagieren, …)
│  └─ simulation/        # Umgebung, Szenarien, Tests
├─ tests/                # Unit- & Integrationstests
├─ docs/                 # Zusätzliche Dokumentation, Diagramme
├─ .gitignore
├─ README.md
└─ LICENSE
