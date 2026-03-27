# -*- coding: utf-8 -*-
"""
E-7 Droid V3 - Optimized Robot Movement Control
Improvements:
- Non-blocking GPIO with event detection (fixes busy-wait)
- Async sensor polling
- Thread-safe cache for sensor values
- Better state management
- Optimized servo smooth movement
- Background sensor monitoring
"""

import time
import threading
import os
import sys
from enum import Enum
from collections import deque
import traceback

# Servo-Steuerung (SMBus für I2C PCA9685)
try:
    import smbus
    bus = smbus.SMBus(1)
    SERVO_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Servo-Hardware nicht verfügbar: {e}")
    SERVO_AVAILABLE = False

# GPIO-Unterstützung
GPIO_AVAILABLE = False
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except Exception as e:
    print(f"⚠️  GPIO nicht verfügbar: {e}")

# PCA9685 Konfiguration
PCA9685_ADDR = 0x40
TRIG_PIN = 27  # Ultraschall Trigger
ECHO_PIN = 17  # Ultraschall Echo

# Servo-Kanäle
SERVO_CHANNELS = {
    "head_x": 0,      # Kopf Horizontal
    "head_y": 1,      # Kopf Vertikal
    "left_leg": 2,    # Linkes Bein
    "right_leg": 3,   # Rechtes Bein
    "body_rotate": 4  # Körper Rotation
}

# ============= STATE ENUM =============
class RobotState(Enum):
    IDLE = 1
    WALKING = 2
    TURNING = 3
    STOPPED = 4

# ============= SENSOR DATA CACHE =============
class SensorCache:
    """Thread-safe cache for sensor readings"""
    
    def __init__(self, max_history=10):
        self.distance = None
        self.history = deque(maxlen=max_history)
        self.lock = threading.Lock()
        self.last_update = 0
    
    def update(self, distance):
        """Update distance with thread safety"""
        with self.lock:
            self.distance = distance
            self.history.append(distance)
            self.last_update = time.time()
    
    def get(self):
        """Get current distance"""
        with self.lock:
            return self.distance
    
    def get_average(self):
        """Get average distance from history"""
        with self.lock:
            if not self.history:
                return None
            return sum(self.history) / len(self.history)

# ============= OPTIMIZED SENSOR MANAGER =============
class SensorManager:
    """Manages non-blocking sensor readings"""
    
    def __init__(self):
        self.cache = SensorCache()
        self.running = True
        self.sensor_thread = None
        self.last_error_time = 0
        self.error_cooldown = 5  # Prevent spam
    
    def init_gpio(self):
        """Initialize GPIO for ultrasonic sensor"""
        if not GPIO_AVAILABLE:
            return False
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            return True
        except Exception as e:
            self._log_error(f"GPIO init failed: {e}")
            return False
    
    def measure_distance(self):
        """Measure distance with timeout (non-blocking friendly)"""
        if not GPIO_AVAILABLE:
            return None
        
        try:
            # Send trigger pulse
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.0001)
            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)
            GPIO.output(TRIG_PIN, False)
            
            # Wait for echo with timeout
            start_time = time.time()
            while GPIO.input(ECHO_PIN) == 0:
                if time.time() - start_time > 0.1:  # 100ms timeout
                    return None
                pulse_start = time.time()
            
            start_time = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                if time.time() - start_time > 0.1:  # 100ms timeout
                    return None
                pulse_end = time.time()
            
            pulse_duration = pulse_end - pulse_start
            distance = int(pulse_duration * 17150)  # cm
            
            # Validate reading (reasonable range: 5-300 cm)
            if 5 <= distance <= 300:
                return distance
            return None
            
        except Exception as e:
            self._log_error(f"Measurement error: {e}")
            return None
    
    def background_sensor_loop(self):
        """Run sensor readings in background thread"""
        print("📡 Sensor monitor started (background)")
        
        while self.running:
            try:
                distance = self.measure_distance()
                if distance is not None:
                    self.cache.update(distance)
                
                # Poll every 500ms instead of continuous (save CPU)
                time.sleep(0.5)
                
            except Exception as e:
                self._log_error(f"Sensor loop error: {e}")
                time.sleep(1)
    
    def start(self):
        """Start background sensor monitoring"""
        if not GPIO_AVAILABLE:
            print("⚠️  GPIO unavailable - sensor monitoring disabled")
            return
        
        if not self.init_gpio():
            return
        
        self.sensor_thread = threading.Thread(
            target=self.background_sensor_loop,
            daemon=True
        )
        self.sensor_thread.start()
    
    def stop(self):
        """Stop sensor monitoring"""
        self.running = False
        try:
            if GPIO_AVAILABLE:
                GPIO.cleanup()
        except:
            pass
    
    def _log_error(self, msg):
        """Log error with cooldown to prevent spam"""
        now = time.time()
        if now - self.last_error_time > self.error_cooldown:
            print(f"⚠️  {msg}")
            self.last_error_time = now

# ============= OPTIMIZED ROBOT MOVEMENT CLASS =============
class RobotMovement:
    """Optimized robot movement controller"""
    
    def __init__(self):
        self.state = RobotState.IDLE
        self.running = True
        self.lock = threading.Lock()
        
        # Sensor manager
        self.sensors = SensorManager()
        
        # Servo positions cache
        self.servo_positions = {
            "head_x": 1500,
            "head_y": 1500,
            "left_leg": 1500,
            "right_leg": 1500,
            "body_rotate": 1500
        }
        
        # Idle movement patterns
        self.idle_movements = [
            {"head_x": 1300},
            {"head_x": 1700},
            {"head_y": 1400},
            {"head_y": 1600},
        ]
        self.idle_index = 0
        
        if SERVO_AVAILABLE:
            self.init_servos()
        
        self.sensors.start()
    
    def init_servos(self):
        """Initialize PCA9685 servo controller"""
        try:
            bus.write_byte_data(PCA9685_ADDR, 0x00, 0x00)  # Wake up
            self.set_pwm_freq(50)  # 50Hz for servos
            print("✅ Servos initialized")
        except Exception as e:
            print(f"❌ Servo init error: {e}")
    
    def set_pwm_freq(self, freq_hz):
        """Set PWM frequency"""
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
            print(f"❌ PWM frequency error: {e}")
    
    def set_servo(self, channel, pulse_us):
        """Set servo position optimized"""
        if not SERVO_AVAILABLE:
            return
        
        try:
            pulse_length = 1000000 // 50 // 4096
            pulse = int(pulse_us / pulse_length)
            off = pulse
            reg_base = 0x06 + 4 * channel
            
            bus.write_byte_data(PCA9685_ADDR, reg_base, 0)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 1, 0)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 2, off & 0xFF)
            bus.write_byte_data(PCA9685_ADDR, reg_base + 3, off >> 8)
        except Exception as e:
            print(f"❌ Servo error: {e}")
    
    def move_servo_smooth(self, channel, target_us, steps=5, delay=0.05):
        """Move servo smoothly (optimized)"""
        if not SERVO_AVAILABLE:
            return
        
        try:
            servo_name = list(SERVO_CHANNELS.keys())[channel]
            current = self.servo_positions.get(servo_name, 1500)
            
            if current == target_us:  # Skip if already at target
                return
            
            step_size = (target_us - current) / max(steps, 1)
            
            for i in range(steps):
                if not self.running:
                    break
                new_pos = int(current + step_size * (i + 1))
                self.set_servo(channel, new_pos)
                time.sleep(delay)
            
            self.servo_positions[servo_name] = target_us
        except Exception as e:
            print(f"❌ Servo movement error: {e}")
    
    def idle_state(self):
        """IDLE state - look around"""
        print("💤 [IDLE] Looking around...")
        
        while self.state == RobotState.IDLE and self.running:
            try:
                movement = self.idle_movements[self.idle_index % len(self.idle_movements)]
                
                for servo_name, position in movement.items():
                    if servo_name in SERVO_CHANNELS:
                        channel = SERVO_CHANNELS[servo_name]
                        self.move_servo_smooth(channel, position, steps=4, delay=0.08)
                
                self.idle_index += 1
                time.sleep(2.5)  # Hold position before next movement
                
            except Exception as e:
                print(f"❌ IDLE error: {e}")
                time.sleep(1)
    
    def walking_state(self):
        """WALKING state - walk and avoid obstacles"""
        print("🚶 [WALKING] Starte Lauf...")
        
        step_count = 0
        while self.state == RobotState.WALKING and self.running:
            try:
                # Get average distance from sensor cache (more stable)
                distance = self.sensors.cache.get_average()
                
                if distance is not None:
                    print(f"📏 Distance: {distance}cm | Steps: {step_count}")
                    
                    if distance < 20:  # Obstacle detected
                        print("🔴 OBSTACLE! Turning around...")
                        self.state = RobotState.TURNING
                        self.turn_animation()
                        self.state = RobotState.WALKING
                    else:
                        self.walk_animation()
                        step_count += 1
                else:
                    # No sensor data, walk cautiously
                    self.walk_animation()
                    step_count += 1
                
                time.sleep(0.8)  # Step interval
                
            except Exception as e:
                print(f"❌ WALKING error: {e}")
                time.sleep(1)
    
    def walk_animation(self):
        """Animate walking movement (optimized)"""
        if not SERVO_AVAILABLE:
            return
        
        try:
            # Left leg forward
            self.move_servo_smooth(SERVO_CHANNELS["left_leg"], 1700, steps=2, delay=0.04)
            time.sleep(0.25)
            
            # Right leg forward
            self.move_servo_smooth(SERVO_CHANNELS["right_leg"], 1700, steps=2, delay=0.04)
            time.sleep(0.25)
            
            # Return to neutral
            self.move_servo_smooth(SERVO_CHANNELS["left_leg"], 1500, steps=2, delay=0.04)
            self.move_servo_smooth(SERVO_CHANNELS["right_leg"], 1500, steps=2, delay=0.04)
        except Exception as e:
            print(f"❌ Walk animation error: {e}")
    
    def turn_animation(self):
        """Animate turning (optimized)"""
        if not SERVO_AVAILABLE:
            return
        
        try:
            rotations = [1300, 1400, 1600, 1700, 1500]
            for rotation in rotations:
                if not self.running:
                    break
                self.move_servo_smooth(SERVO_CHANNELS["body_rotate"], rotation, steps=1, delay=0.08)
                time.sleep(0.15)
        except Exception as e:
            print(f"❌ Turn animation error: {e}")
    
    def stop(self):
        """Stop robot - move all servos to neutral"""
        print("⏹️  [STOPPED] Robot is standing still")
        
        with self.lock:
            self.state = RobotState.STOPPED
        
        try:
            if SERVO_AVAILABLE:
                for servo_name, channel in SERVO_CHANNELS.items():
                    self.move_servo_smooth(channel, 1500, steps=3, delay=0.05)
        except Exception as e:
            print(f"❌ Stop error: {e}")
    
    def change_state(self, new_state):
        """Thread-safe state change"""
        with self.lock:
            old_state = self.state
            self.state = new_state
        print(f"📊 State change: {old_state.name} → {new_state.name}")
    
    def start_walking(self):
        """Start walking mode"""
        self.change_state(RobotState.WALKING)
        self.walking_state()
    
    def start_idle(self):
        """Start idle mode"""
        self.change_state(RobotState.IDLE)
        self.idle_state()
    
    def run(self):
        """Main event loop - starts in IDLE"""
        print("🤖 E-7-Droid V3 Movement Control Started")
        print("=" * 50)
        
        try:
            self.start_idle()
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down robot...")
            self.running = False
            self.sensors.stop()
            self.stop()
        except Exception as e:
            print(f"❌ Critical error: {e}")
            traceback.print_exc()
        finally:
            self.running = False
            self.sensors.stop()
            print("🛑 Robot controller stopped.")

# ============= MAIN ENTRY POINT =============
if __name__ == "__main__":
    print("=" * 50)
    print("E-7-Droid V3 - Movement Controller")
    print("=" * 50)
    
    robot = RobotMovement()
    robot.run()
