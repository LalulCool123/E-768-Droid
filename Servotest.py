# -*- coding: utf-8 -*-
"""
Servo Test und Kalibrierungs-Script
Testet alle 5 Servo-Kanäle des PCA9685
"""

import smbus
import time
import sys

# I2C-Adresse des PCA9685
PCA9685_ADDR = 0x40
bus = smbus.SMBus(1)

# Servo-Kanäle
SERVO_CHANNELS = {
    "head_x": 0,
    "head_y": 1,
    "left_leg": 2,
    "right_leg": 3,
    "body_rotate": 4
}

def init_pca9685():
    """Initialisiere PCA9685 Servo-Controller"""
    try:
        bus.write_byte_data(PCA9685_ADDR, 0x00, 0x00)  # Wake up (MODE1 register)
        set_pwm_freq(50)  # 50 Hz für Servos
        print("✅ PCA9685 initialisiert")
    except Exception as e:
        print(f"❌ Fehler bei Initialisierung: {e}")
        sys.exit(1)

def set_pwm_freq(freq_hz):
    """Setze PWM Frequenz"""
    prescaleval = 25000000.0
    prescaleval /= 4096.0
    prescaleval /= float(freq_hz)
    prescaleval -= 1.0
    prescale = int(prescaleval + 0.5)

    oldmode = bus.read_byte_data(PCA9685_ADDR, 0x00)
    newmode = (oldmode & 0x7F) | 0x10  # Sleep
    bus.write_byte_data(PCA9685_ADDR, 0x00, newmode)
    bus.write_byte_data(PCA9685_ADDR, 0xFE, prescale)
    bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode)
    time.sleep(0.005)
    bus.write_byte_data(PCA9685_ADDR, 0x00, oldmode | 0xA1)  # Auto-increment

def set_servo(channel, pulse_us):
    """Setze Servo auf bestimmte Position (Pulsweite in µs)"""
    pulse_length = 1000000
    pulse_length //= 50
    pulse_length //= 4096
    pulse = int(pulse_us / pulse_length)
    on = 0
    off = pulse
    reg_base = 0x06 + 4 * channel
    
    bus.write_byte_data(PCA9685_ADDR, reg_base, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 1, on >> 8)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 2, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 3, off >> 8)

def test_servo(channel_name, channel_num):
    """Teste einen Servo durch die gesamte Bewegungsrange"""
    print(f"\n🔧 Teste {channel_name} (Kanal {channel_num})...")
    
    positions = [1000, 1250, 1500, 1750, 2000]
    
    for pos in positions:
        print(f"  → {pos} µs", end="")
        set_servo(channel_num, pos)
        time.sleep(0.5)
        print(" ✓")
    
    # Zurück zur Mittelposition
    set_servo(channel_num, 1500)
    time.sleep(0.3)
    print(f"  ✅ {channel_name} zurück zur Mittelposition (1500 µs)")

def test_all_together():
    """Teste alle Servos gleichzeitig"""
    print("\n🔄 Teste ALLE Servos zusammen...")
    
    print("  → Min-Position (1000 µs)")
    for channel in range(5):
        set_servo(channel, 1000)
    time.sleep(0.8)
    
    print("  → Max-Position (2000 µs)")
    for channel in range(5):
        set_servo(channel, 2000)
    time.sleep(0.8)
    
    print("  → Mittelposition (1500 µs)")
    for channel in range(5):
        set_servo(channel, 1500)
    time.sleep(0.5)
    
    print("  ✅ Alle Servos zurück zur Mittelposition")

def main():
    """Haupt-Testprogramm"""
    print("=" * 50)
    print("🤖 E-7-Droid Servo Test V2")
    print("=" * 50)
    
    try:
        init_pca9685()
        
        # Teste jeden Servo einzeln
        for servo_name, channel_num in SERVO_CHANNELS.items():
            test_servo(servo_name, channel_num)
            time.sleep(1)
        
        # Teste alle zusammen
        test_all_together()
        
        print("\n✅ Alle Tests abgeschlossen!")
        print("ℹ️  Alle Servos sind nun in ihrer Mittelposition (1500 µs)")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test unterbrochen.")
        # Alle Servos neutral
        for channel in range(5):
            set_servo(channel, 1500)
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main()


    print("Alle Servos auf 1500 us (Mittelstellung)")
    for ch in range(5):
        set_servo(ch, 1500)
    time.sleep(0.5)

def wave_motion():
    print("Wellenbewegung")
    for ch in range(5):
        set_servo(ch, 1000)
        time.sleep(0.2)
        set_servo(ch, 2000)
        time.sleep(0.2)
    for ch in range(5):
        set_servo(ch, 1500)
    time.sleep(0.5)

def fast_zickzack():
    print("Schnelles Zickzack")
    for _ in range(5):
        for ch in range(5):
            set_servo(ch, 1000)
        time.sleep(0.1)
        for ch in range(5):
            set_servo(ch, 2000)
        time.sleep(0.1)
    for ch in range(5):
        set_servo(ch, 1500)
    time.sleep(0.5)

if __name__ == "__main__":
    init_pca9685()
    print("Starte Servobewegungen...")

    while True:
        move_all_servos_together()
        wave_motion()
        fast_zickzack()
