# -*- coding: utf-8 -*-
"""
Lauf-Script - Bewegungs-Test
Testet die Geh-Bewegungen des Roboters
"""

import smbus
import time
import sys
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# I2C-Adresse des PCA9685
PCA9685_ADDR = 0x40

try:
    bus = smbus.SMBus(1)
    bus.write_byte_data(PCA9685_ADDR, 0x00, 0x00)
    logging.info("✅ PCA9685 initialisiert")
except Exception as e:
    logging.error(f"❌ Fehler: {e}")
    bus = None

# Servo-Kanäle
SERVO_CHANNELS = {
    "left_leg": 2,
    "right_leg": 3
}

def set_pwm_freq(freq_hz):
    """Setze PWM Frequenz auf 50 Hz für Servos"""
    if not bus:
        return
    
    prescaleval = 25000000.0 / 4096.0 / float(freq_hz) - 1.0
    prescale = int(prescaleval + 0.5)
    
    oldmode = bus.read_byte_data(PCA9685_ADDR, 0x00)
    newmode = (oldmode & 0x7F) | 0x10
    bus.write_byte_data(PCA9685_ADDR, 0x00, newmode)
    bus.write_byte_data(PCA9685_ADDR, 0xFE, prescale)
    bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode)
    time.sleep(0.005)
    bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode | 0xA1)

def set_servo(channel, pulse_us):
    """Setze Servo auf bestimmte Position"""
    if not bus:
        return
    
    pulse_length = 1000000 // 50 // 4096
    pulse = int(pulse_us / pulse_length)
    on = 0
    off = pulse
    reg_base = 0x06 + 4 * channel
    
    bus.write_byte_data(PCA9685_ADDR, reg_base, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 1, on >> 8)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 2, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 3, off >> 8)

def walk_animation(steps=5, step_height=200, delay=0.3):
    """
    Führe Geh-Animation durch
    
    Args:
        steps: Anzahl der Schritte
        step_height: Wie hoch die Beine bewegt werden (µs)
        delay: Verzögerung zwischen Schritten (Sekunden)
    """
    logging.info(f"🚶 Starte {steps}-Schritt Geh-Animation...")
    
    neutral_pos = 1500
    
    for step_num in range(steps):
        logging.info(f"   Schritt {step_num + 1}/{steps}")
        
        # Linkes Bein heben
        set_servo(SERVO_CHANNELS["left_leg"], neutral_pos + step_height)
        time.sleep(delay / 2)
        
        # Rechtes Bein senken
        set_servo(SERVO_CHANNELS["right_leg"], neutral_pos - (step_height // 2))
        time.sleep(delay / 2)
        
        # Linkes Bein senken
        set_servo(SERVO_CHANNELS["left_leg"], neutral_pos - (step_height // 2))
        time.sleep(delay / 2)
        
        # Rechtes Bein heben
        set_servo(SERVO_CHANNELS["right_leg"], neutral_pos + step_height)
        time.sleep(delay / 2)
    
    # Zurück zur Neutralposition
    logging.info("   → Zurück zu Neutralposition")
    set_servo(SERVO_CHANNELS["left_leg"], neutral_pos)
    set_servo(SERVO_CHANNELS["right_leg"], neutral_pos)
    time.sleep(0.2)
    
    logging.info("✅ Geh-Animation abgeschlossen")

def quick_walk():
    """Schneller Lauf"""
    logging.info("🏃 Schneller Lauf...")
    walk_animation(steps=10, step_height=250, delay=0.15)

def slow_walk():
    """Langsamer Lauf"""
    logging.info("🚶 Langsamer Lauf...")
    walk_animation(steps=5, step_height=150, delay=0.5)

def test_servo_range():
    """Teste die volle Bewegungsrange der Beine"""
    logging.info("🔧 Teste Servo-Range...")
    
    neutral = 1500
    positions = [1000, 1200, 1350, 1500, 1650, 1800, 2000]
    
    for pos in positions:
        logging.info(f"   → Linkes Bein: {pos} µs")
        set_servo(SERVO_CHANNELS["left_leg"], pos)
        time.sleep(0.3)
    
    # Neutral
    set_servo(SERVO_CHANNELS["left_leg"], neutral)
    set_servo(SERVO_CHANNELS["right_leg"], neutral)
    logging.info("✅ Servo-Range Test abgeschlossen")

def main():
    """Haupt-Funktion"""
    print("=" * 50)
    print("🤖 E-7-Droid Lauf-Test V2")
    print("=" * 50)
    
    if not bus:
        logging.error("❌ PCA9685 nicht verfügbar!")
        return
    
    try:
        set_pwm_freq(50)
        
        # Test Servo-Range
        test_servo_range()
        time.sleep(1)
        
        # Langsamer Lauf
        slow_walk()
        time.sleep(1)
        
        # Schneller Lauf
        quick_walk()
        time.sleep(1)
        
        # Finale Neutral-Position
        logging.info("🛑 Setze beide Beine auf Neutralposition")
        set_servo(SERVO_CHANNELS["left_leg"], 1500)
        set_servo(SERVO_CHANNELS["right_leg"], 1500)
        
        logging.info("\n✅ Alle Lauf-Tests abgeschlossen!")
        
    except KeyboardInterrupt:
        logging.info("⏹️  Test unterbrochen")
        # Neutral
        set_servo(SERVO_CHANNELS["left_leg"], 1500)
        set_servo(SERVO_CHANNELS["right_leg"], 1500)
    except Exception as e:
        logging.error(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main()

