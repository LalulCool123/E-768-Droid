# -*- coding: utf-8 -*-
"""
Robot Movement Control Script
Handles Idle und Walk States mit Servo-Steuerung
"""

import time
import threading
import os
import sys
from enum import Enum

# Servo-Steuerung (SMBus für I2C PCA9685)
try:
    import smbus
    bus = smbus.SMBus(1)
    SERVO_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Servo-Hardware nicht verfügbar: {e}")
    SERVO_AVAILABLE = False

# PCA9685 Konfiguration
PCA9685_ADDR = 0x40
TRIG_PIN = 27  # Ultraschall
ECHO_PIN = 17  # Ultraschall

# Servo-Kanäle (GPIO)
SERVO_CHANNELS = {
    "head_x": 0,      # Kopf Horizontal (Links/Rechts)
    "head_y": 1,      # Kopf Vertikal (Oben/Unten)
    "left_leg": 2,    # Linkes Bein
    "right_leg": 3,   # Rechtes Bein
    "body_rotate": 4  # Körper Rotation
}

class RobotState(Enum):
    IDLE = 1
    WALKING = 2
    TURNING = 3
    STOPPED = 4

class RobotMovement:
    def __init__(self):
        self.state = RobotState.IDLE
        self.running = True
        self.is_moving = False
        self.last_distance = None
        self.lock = threading.Lock()
        
        # Idle-Verhalten: zufällige Kopfbewegungen
        self.idle_movements = [
            {"head_x": 1300},  # Links gucken
            {"head_x": 1700},  # Rechts gucken
            {"head_y": 1400},  # Etwas runter gucken
            {"head_y": 1600},  # Etwas hoch gucken
        ]
        self.idle_index = 0
        
        # Servo-Standard-Positionen
        self.servo_positions = {
            "head_x": 1500,      # Mitte
            "head_y": 1500,      # Mitte
            "left_leg": 1500,    # Neutral
            "right_leg": 1500,   # Neutral
            "body_rotate": 1500  # Neutral
        }
        
        if SERVO_AVAILABLE:
            self.init_servos()
    
    def init_servos(self):
        """Initialisiere PCA9685 Servo-Controller"""
        try:
            bus.write_byte_data(PCA9685_ADDR, 0x00, 0x00)  # Wake up
            self.set_pwm_freq(50)  # 50 Hz für Servos
            print("✅ Servos initialisiert")
        except Exception as e:
            print(f"❌ Fehler beim Initialisieren der Servos: {e}")
    
    def set_pwm_freq(self, freq_hz):
        """Setze PWM Frequenz"""
        try:
            prescaleval = 25000000.0 / 4096.0 / float(freq_hz) - 1.0
            prescale = int(prescaleval + 0.5)
            
            oldmode = bus.read_byte_data(PCA9685_ADDR, 0x00)
            newmode = (oldmode & 0x7F) | 0x10
            bus.write_byte_data(PCA9685_ADDR, 0x00, newmode)
            bus.write_byte_data(PCA9685_ADDR, 0xFE, prescale)
            bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode)
            time.sleep(0.005)
            bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode | 0xA1)
        except Exception as e:
            print(f"❌ Fehler bei PWM-Frequenz: {e}")
    
    def set_servo(self, channel, pulse_us):
        """Setze Servo auf bestimmte Position (Pulsweite in µs)"""
        if not SERVO_AVAILABLE:
            return
        
        try:
            pulse_length = 1000000 // 50 // 4096
            pulse = int(pulse_us / pulse_length)
            on = 0
            off = pulse
            reg_base = 0x06 + 4 * channel
            
            bus.write_byte_data(PCA9685_ADDR, reg_base, on & 0xFF)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 1, on >> 8)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 2, off & 0xFF)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 3, off >> 8)
        except Exception as e:
            print(f"❌ Servo-Fehler: {e}")
    
    def move_servo_smooth(self, channel, target_us, steps=10, delay=0.05):
        """Bewege Servo sanft zur Zielposition"""
        if not SERVO_AVAILABLE:
            return
        
        current = self.servo_positions.get(list(SERVO_CHANNELS.keys())[channel], 1500)
        step_size = (target_us - current) / steps
        
        for i in range(steps):
            new_pos = int(current + step_size * (i + 1))
            self.set_servo(channel, new_pos)
            time.sleep(delay)
        
        self.servo_positions[list(SERVO_CHANNELS.keys())[channel]] = target_us
    
    def measure_distance(self):
        """Messe Entfernung mit Ultraschall-Sensor"""
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.5)
            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)
            GPIO.output(TRIG_PIN, False)
            
            while GPIO.input(ECHO_PIN) == 0:
                pulse_start = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            distance = int(pulse_duration * 17150)  # cm
            
            GPIO.cleanup()
            return distance
        except Exception as e:
            print(f"⚠️ Abstandsmessung fehlgeschlagen: {e}")
            return None
    
    def idle_state(self):
        """IDLE State - Roboter umschaut sich um"""
        print("🤖 [IDLE] Umschauen...")
        
        while self.state == RobotState.IDLE and self.running:
            try:
                # Sanfte Kopfbewegungen
                movement = self.idle_movements[self.idle_index % len(self.idle_movements)]
                
                for servo_name, position in movement.items():
                    if servo_name in SERVO_CHANNELS:
                        channel = SERVO_CHANNELS[servo_name]
                        self.move_servo_smooth(channel, position, steps=5, delay=0.08)
                
                self.idle_index += 1
                time.sleep(2)  # Kurz halten, dann nächste Position
                
            except Exception as e:
                print(f"❌ Fehler im IDLE-State: {e}")
                time.sleep(1)
    
    def walking_state(self):
        """WALKING State - Roboter läuft und umgeht Hindernisse"""
        print("🚶 [WALKING] Läuft los...")
        
        while self.state == RobotState.WALKING and self.running:
            try:
                # Ultraschall-Messung: Hindernisse erkennen
                distance = self.measure_distance()
                
                if distance is not None:
                    self.last_distance = distance
                    print(f"📏 Abstand: {distance} cm", end=" ... ")
                    
                    if distance < 20:  # Hindernis erkannt
                        print("🔴 HINDERNIS! Drehe um...")
                        self.turn_state()
                    else:
                        print("✅ Frei! Weiterlaufen...")
                        # Geh-Animation: Beine abwechselnd bewegen
                        self.walk_animation()
                else:
                    self.walk_animation()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Fehler im WALKING-State: {e}")
                time.sleep(1)
    
    def walk_animation(self):
        """Animiere Geh-Bewegung"""
        if not SERVO_AVAILABLE:
            return
        
        # Linkes Bein vorwärts
        self.move_servo_smooth(SERVO_CHANNELS["left_leg"], 1700, steps=3, delay=0.05)
        time.sleep(0.3)
        
        # Rechtes Bein vorwärts
        self.move_servo_smooth(SERVO_CHANNELS["right_leg"], 1700, steps=3, delay=0.05)
        time.sleep(0.3)
        
        # Zurück zur Neutral-Position
        self.move_servo_smooth(SERVO_CHANNELS["left_leg"], 1500, steps=3, delay=0.05)
        self.move_servo_smooth(SERVO_CHANNELS["right_leg"], 1500, steps=3, delay=0.05)
    
    def turn_state(self):
        """TURNING State - Roboter dreht sich um"""
        print("🔄 [TURNING] Drehe mich um...")
        
        with self.lock:
            old_state = self.state
            self.state = RobotState.TURNING
        
        try:
            # Körper-Rotation durchführen
            for rotation in [1300, 1400, 1600, 1700, 1500]:
                if self.state != RobotState.TURNING:
                    break
                self.move_servo_smooth(SERVO_CHANNELS["body_rotate"], rotation, steps=2, delay=0.1)
                time.sleep(0.2)
            
            time.sleep(1)
        except Exception as e:
            print(f"❌ Fehler beim Drehen: {e}")
        finally:
            with self.lock:
                self.state = old_state
    
    def stop(self):
        """Stoppe den Roboter - alle Servos neutral"""
        print("⏹️  [STOPPED] Roboter steht still.")
        
        with self.lock:
            self.state = RobotState.STOPPED
            self.is_moving = False
        
        try:
            # Alle Servos zur Neutral-Position
            if SERVO_AVAILABLE:
                for servo_name, channel in SERVO_CHANNELS.items():
                    self.move_servo_smooth(channel, 1500, steps=5, delay=0.05)
        except Exception as e:
            print(f"❌ Fehler beim Stoppen: {e}")
    
    def start_walking(self):
        """Starte Walk-Modus"""
        print("🚀 Starte Lauf-Modus...")
        
        with self.lock:
            old_state = self.state
            self.state = RobotState.WALKING
            self.is_moving = True
        
        try:
            self.walking_state()
        except Exception as e:
            print(f"❌ Fehler beim Gehen: {e}")
        finally:
            with self.lock:
                self.state = old_state
    
    def start_idle(self):
        """Starte Idle-Modus"""
        print("💤 Wechsle zu Idle-Modus...")
        
        with self.lock:
            self.state = RobotState.IDLE
            self.is_moving = False
        
        try:
            self.idle_state()
        except Exception as e:
            print(f"❌ Fehler im Idle: {e}")
    
    def run(self):
        """Hauptloop - Starte im Idle-Modus"""
        print("🤖 E-7-Droid Bewegungssteuerung startet...")
        
        try:
            self.start_idle()
        except KeyboardInterrupt:
            print("\n⏹️  Beende Roboter...")
            self.running = False
            self.stop()
        except Exception as e:
            print(f"❌ Kritischer Fehler: {e}")
        finally:
            print("🛑 Roboter beendet.")

if __name__ == "__main__":
    robot = RobotMovement()
    robot.run()
