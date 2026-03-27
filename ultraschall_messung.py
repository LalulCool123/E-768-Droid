# -*- coding: utf-8 -*-
"""
Ultraschall-Entfernungsmessung
Misst Abstände mit HC-SR04 Sensor
"""

import RPi.GPIO as GPIO
import time
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# GPIO-Pins
TRIG_PIN = 27  # Trigger
ECHO_PIN = 17  # Echo

def setup_gpio():
    """Initialisiere GPIO-Pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    logging.info("✅ GPIO initialisiert")

def measure_distance():
    """
    Messe Entfernung mit Ultraschall-Sensor.
    Gibt die Entfernung in cm zurück oder None bei Fehler.
    """
    try:
        # Trigger-Pin niedrig setzen
        GPIO.output(TRIG_PIN, False)
        time.sleep(0.5)
        
        # 10µs Trigger-Impuls
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)
        
        # Auf Echo warten (Low→High)
        timeout = time.time() + 1  # 1 Sekunde Timeout
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                logging.warning("⚠️ Echo-Start Timeout")
                return None
        
        # Auf Echo-Ende warten (High→Low)
        timeout = time.time() + 1
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                logging.warning("⚠️ Echo-Ende Timeout")
                return None
        
        # Berechne Entfernung
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Schallgeschwindigkeit: 343 m/s
        
        return int(distance)
    
    except Exception as e:
        logging.error(f"❌ Fehler bei Messung: {e}")
        return None

def continuous_scan(interval=1.0, count=None):
    """
    Kontinuierliche Abstandsmessung
    
    Args:
        interval: Messintervall in Sekunden (default: 1.0)
        count: Anzahl der Messungen (None = unbegrenzt)
    """
    logging.info("📡 Starte kontinuierliche Abstandsmessung...")
    
    measurement_count = 0
    try:
        while count is None or measurement_count < count:
            distance = measure_distance()
            
            if distance is not None:
                status = ""
                if distance < 10:
                    status = "🔴 SEHR NAH!"
                elif distance < 20:
                    status = "🟠 NAH"
                elif distance < 50:
                    status = "🟡 MITTEL"
                elif distance < 100:
                    status = "🟢 WEIT"
                else:
                    status = "⚫ SEHR WEIT"
                
                logging.info(f"📏 Abstand: {distance:3d} cm {status}")
                measurement_count += 1
            else:
                logging.warning("❌ Messung fehlgeschlagen")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logging.info("⏹️  Messung unterbrochen")
    
    finally:
        GPIO.cleanup()
        logging.info(f"✅ {measurement_count} Messungen durchgeführt")

def main():
    """Haupt-Funktion"""
    print("=" * 50)
    print("🤖 E-7-Droid Ultraschall-Sensor Test V2")
    print("=" * 50)
    
    try:
        setup_gpio()
        
        # Single Measurement
        logging.info("📡 Mache Einzelmessung...")
        distance = measure_distance()
        
        if distance is not None:
            print(f"\n📊 Messergebnis:")
            print(f"   Abstand: {distance} cm")
            
            if distance < 20:
                print("   🔴 HINDERNIS ERKANNT!")
            else:
                print("   ✅ Frei")
        else:
            logging.error("Messung fehlgeschlagen")
        
        # Continuous Scan (10 Messungen)
        logging.info("\n📡 Starte kontinuierliche Abstandsmessung (10 Messungen)...")
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)
        continuous_scan(interval=0.5, count=10)
        
    except Exception as e:
        logging.error(f"Kritischer Fehler: {e}")
    
    finally:
        GPIO.cleanup()
        logging.info("GPIO bereinigt")

if __name__ == "__main__":
    main()

