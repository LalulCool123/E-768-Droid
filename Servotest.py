# -*- coding: utf-8 -*-
import smbus
import time

# I2C-Adresse des PCA9685
PCA9685_ADDR = 0x40
bus = smbus.SMBus(1)

def init_pca9685():
    bus.write_byte_data(PCA9685_ADDR, 0x00, 0x00)  # Wake up (MODE1 register)
    set_pwm_freq(50)  # 50 Hz für Servos

def set_pwm_freq(freq_hz):
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
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
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 50       # 50 Hz
    pulse_length //= 4096     # 12 bits of resolution
    pulse = int(pulse_us / pulse_length)
    on = 0
    off = pulse
    reg_base = 0x06 + 4 * channel
    bus.write_byte_data(PCA9685_ADDR, reg_base, on & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 1, on >> 8)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 2, off & 0xFF)
    bus.write_byte_data(PCA9685_ADDR, reg_base + 3, off >> 8)

def move_all_servos_together():
    print("Alle Servos auf 1000 us (Min-Position)")
    for ch in range(5):
        set_servo(ch, 1000)
    time.sleep(0.5)

    print("Alle Servos auf 2000 us (Max-Position)")
    for ch in range(5):
        set_servo(ch, 2000)
    time.sleep(0.5)

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
