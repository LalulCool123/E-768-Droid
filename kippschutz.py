# -*- coding: utf-8 -*-
"""
Kippschutz / Gleichgewichtschutz
Überwacht die Neigung des Roboters mit MPU6050
"""

import smbus
import time
import math
import os
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# MPU6050 Addressen und Register
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Grenzwerte für Neigung (in Grad)
TILT_THRESHOLD = 45  # Warnung bei 45°
CRITICAL_THRESHOLD = 60  # Alarm bei 60°

# I2C Bus
try:
    bus = smbus.SMBus(1)
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)
    logging.info("✅ MPU6050 initialisiert")
except Exception as e:
    logging.error(f"❌ MPU6050 Fehler: {e}")
    bus = None

def read_raw(addr):
    """Lese zwei zusammenhängende Register (High und Low Byte)"""
    if not bus:
        return 0
    
    try:
        high = bus.read_byte_data(MPU_ADDR, addr)
        low = bus.read_byte_data(MPU_ADDR, addr + 1)
        value = (high << 8) + low
        if value > 32767:
            value -= 65536
        return value
    except Exception as e:
        logging.warning(f"⚠️ Fehler beim Lesen: {e}")
        return 0

def get_acceleration():
    """Lese X, Y, Z Beschleunigungswerte"""
    acc_x = read_raw(ACCEL_XOUT_H) / 16384.0
    acc_y = read_raw(ACCEL_XOUT_H + 2) / 16384.0
    acc_z = read_raw(ACCEL_XOUT_H + 4) / 16384.0
    return acc_x, acc_y, acc_z

def calculate_tilt_angle():
    """Berechne Neigungswinkel aus Beschleunigung"""
    acc_x, acc_y, acc_z = get_acceleration()
    
    # Berechne Neigung in X-Richtung (Roll)
    tilt_x = math.degrees(math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2)))
    
    # Berechne Neigung in Y-Richtung (Pitch)
    tilt_y = math.degrees(math.atan2(acc_x, math.sqrt(acc_y**2 + acc_z**2)))
    
    # Gesamt-Neigung (Magnitude)
    total_tilt = math.sqrt(tilt_x**2 + tilt_y**2)
    
    return tilt_x, tilt_y, total_tilt, (acc_x, acc_y, acc_z)

def reset_servos():
    """Setze alle Servos auf neutrale Position (Gleichgewicht halten)"""
    try:
        import smbus as smbus_servo
        pca_bus = smbus_servo.SMBus(1)
        PCA9685_ADDR = 0x40
        
        logging.warning("🔧 Versuche Servos zu zentrieren...")
        
        for ch in range(5):
            # Alle Servos auf Mittelposition 1500 µs
            pulse = 97  # Ungefähr 1500 µs
            reg_base = 0x06 + 4 * ch
            pca_bus.write_byte_data(PCA9685_ADDR, reg_base + 2, pulse & 0xFF)
            pca_bus.write_byte_data(PCA9685_ADDR, reg_base + 3, pulse >> 8)
        
        logging.info("✅ Servos zentriert")
    except Exception as e:
        logging.warning(f"⚠️ Konnteervos nicht zentrieren: {e}")

def speak_warning(message):
    """Sprachmitteilung bei Gleichgewichtsproblem"""
    try:
        os.system(f'pico2wave -l=de-DE -w=/tmp/warn.wav "{message}" 2>/dev/null && aplay /tmp/warn.wav 2>/dev/null')
    except Exception as e:
        logging.warning(f"⚠️ Sprachausgabe fehlgeschlagen: {e}")

def monitor_tilt(interval=0.5, duration=None):
    """
    Überwache die Neigung des Roboters kontinuierlich
    
    Args:
        interval: Messintervall in Sekunden
        duration: Maximale Dauer in Sekunden (None = unbegrenzt)
    """
    logging.info("👁️  Starte Neigungsüberwachung...")
    
    start_time = time.time()
    measurement_count = 0
    
    try:
        while True:
            tilt_x, tilt_y, total_tilt, (acc_x, acc_y, acc_z) = calculate_tilt_angle()
            
            # Formatierte Ausgabe
            status = ""
            if total_tilt > CRITICAL_THRESHOLD:
                status = "🔴 CRITICAL!"
                logging.critical(f"⚠️  KRITISCHE NEIGUNG: {total_tilt:.1f}°")
                speak_warning("Gleichgewicht verloren!")
                reset_servos()
            elif total_tilt > TILT_THRESHOLD:
                status = "🟠 WARNING"
                logging.warning(f"⚠️  Neigung zu hoch: {total_tilt:.1f}°")
                speak_warning("Achtung, neige mich.")
            else:
                status = "✅ OK"
            
            logging.info(f"📐 Neigung: X={tilt_x:6.1f}° Y={tilt_y:6.1f}° Total={total_tilt:6.1f}° {status}")
            measurement_count += 1
            
            # Check Dauer
            if duration and (time.time() - start_time) > duration:
                break
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logging.info("⏹️  Überwachung unterbrochen")
    
    finally:
        logging.info(f"✅ {measurement_count} Messungen durchgeführt")

def main():
    """Haupt-Funktion"""
    print("=" * 50)
    print("🤖 E-7-Droid Kippschutz / Gleichgewicht")
    print("=" * 50)
    
    if not bus:
        logging.error("❌ MPU6050 nicht verfügbar!")
        return
    
    try:
        # Single Test
        logging.info("📡 Mache Einzelmessung...")
        tilt_x, tilt_y, total_tilt, accel = calculate_tilt_angle()
        
        print(f"\n📊 Messergebnis:")
        print(f"   X-Neigung: {tilt_x:6.1f}°")
        print(f"   Y-Neigung: {tilt_y:6.1f}°")
        print(f"   Gesamt:    {total_tilt:6.1f}°")
        print(f"   Beschleunigung: X={accel[0]:6.3f}g Y={accel[1]:6.3f}g Z={accel[2]:6.3f}g")
        
        # Kontinuierliche Überwachung (30 Sekunden)
        logging.info("\n👁️  Starte kontinuierliche Überwachung (30 Sekunden)...")
        monitor_tilt(interval=0.5, duration=30)
        
    except Exception as e:
        logging.error(f"❌ Kritischer Fehler: {e}")

if __name__ == "__main__":
    main()


        winkel_x = math.degrees(math.atan2(acc_y, acc_z))
        winkel_y = math.degrees(math.atan2(acc_x, acc_z))

        print(f"Neigung X: {winkel_x:.1f}°, Y: {winkel_y:.1f}°")

        if abs(winkel_x) > 45 or abs(winkel_y) > 45:
            print("WARNUNG: Kippwinkel überschritten!")
            reset_servos()
            say_warning()
            break

        time.sleep(0.5)

if __name__ == "__main__":
    check_tilt()
