# kippschutz.py
import smbus
import time
import math
import os

# MPU6050 Adresse und Register
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# I2C starten
bus = smbus.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

# Hilfsfunktion zum Auslesen
def read_raw(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    value = (high << 8) + low
    if value > 32767:
        value -= 65536
    return value

# Servos auf 0° setzen (hier Beispiel mit pigpio, kannst du anpassen)
def reset_servos():
    try:
        import pigpio
        pi = pigpio.pi()
        if not pi.connected:
            print("Fehler: pigpio nicht verbunden.")
            return
        for pin in [17, 18, 27]:  # Passe diese Pins an
            pi.set_servo_pulsewidth(pin, 1500)  # 1500 µs = 0° Mitte
        time.sleep(1)
        pi.stop()
    except Exception as e:
        print(f"Fehler beim Zurücksetzen der Servos: {e}")

# Sprache ausgeben
def say_warning():
    os.system('pico2wave -l=de-DE -w=/tmp/warn.wav "Neigungswinkel zu weit überschritten." && aplay /tmp/warn.wav')

# Hauptlogik
def check_tilt():
    while True:
        acc_x = read_raw(ACCEL_XOUT_H) / 16384.0
        acc_y = read_raw(ACCEL_XOUT_H + 2) / 16384.0
        acc_z = read_raw(ACCEL_XOUT_H + 4) / 16384.0

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
