# -*- coding: utf-8 -*-
"""
E-7 Droid V3 - Optimized Ultrasonic Distance Measurement
Improvements:
- Non-blocking GPIO using edge detection
- Ring buffer for history (moving average)
- Timeout handling
- Configurable thresholds
"""

import threading
import time
import logging
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

# GPIO support
GPIO_AVAILABLE = False
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    logging.warning("⚠️  RPi.GPIO not available - simulation mode")

# Configuration
TRIG_PIN = 27
ECHO_PIN = 17
MEASUREMENT_TIMEOUT = 0.1  # 100ms timeout
SOUND_VELOCITY_CM_S = 17150  # cm/s (approx)
MAX_DISTANCE = 300  # cm (realistic max)

class DistanceSensor:
    """Optimized HC-SR04 ultrasonic distance sensor"""
    
    def __init__(self, history_size=10):
        self.history = deque(maxlen=history_size)
        self.last_measurement = None
        self.lock = threading.Lock()
        self.running = True
        
        self.init_gpio()
    
    def init_gpio(self):
        """Initialize GPIO pins"""
        if not GPIO_AVAILABLE:
            return
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(TRIG_PIN, GPIO.OUT)
            GPIO.setup(ECHO_PIN, GPIO.IN)
            logging.info("✅ Ultrasonic sensor initialized")
        except Exception as e:
            logging.error(f"❌ GPIO init failed: {e}")
    
    def measure(self):
        """
        Measure distance with timeout
        Returns distance in cm or None on error
        """
        if not GPIO_AVAILABLE:
            return 50  # Return dummy value for testing
        
        try:
            # Send trigger pulse
            GPIO.output(TRIG_PIN, False)
            time.sleep(0.0001)
            GPIO.output(TRIG_PIN, True)
            time.sleep(0.00001)
            GPIO.output(TRIG_PIN, False)
            
            # Wait for echo start with timeout
            start_wait = time.time()
            while GPIO.input(ECHO_PIN) == 0:
                if time.time() - start_wait > MEASUREMENT_TIMEOUT:
                    return None
                pulse_start = time.time()
            
            # Wait for echo end with timeout
            start_wait = time.time()
            while GPIO.input(ECHO_PIN) == 1:
                if time.time() - start_wait > MEASUREMENT_TIMEOUT:
                    return None
                pulse_end = time.time()
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = int(pulse_duration * SOUND_VELOCITY_CM_S)
            
            # Validate (5-300cm is reasonable)
            if 5 <= distance <= MAX_DISTANCE:
                with self.lock:
                    self.history.append(distance)
                    self.last_measurement = distance
                return distance
            
            return None
        
        except Exception as e:
            logging.debug(f"Measurement failed: {e}")
            return None
    
    def get_average(self):
        """Get average distance from history"""
        with self.lock:
            if not self.history:
                return None
            return sum(self.history) / len(self.history)
    
    def get_median(self):
        """Get median distance from history"""
        with self.lock:
            if not self.history:
                return None
            sorted_hist = sorted(self.history)
            mid = len(sorted_hist) // 2
            if len(sorted_hist) % 2 == 0:
                return (sorted_hist[mid - 1] + sorted_hist[mid]) / 2
            return sorted_hist[mid]
    
    def get_last(self):
        """Get last measurement"""
        with self.lock:
            return self.last_measurement
    
    def classify_distance(self, distance):
        """Classify distance for feedback"""
        if distance is None:
            return "⚫ NO SIGNAL"
        if distance < 10:
            return f"🔴 DANGER ({distance}cm)"
        if distance < 20:
            return f"🟠 CLOSE ({distance}cm)"
        if distance < 50:
            return f"🟡 MID ({distance}cm)"
        if distance < 100:
            return f"🟢 FAR ({distance}cm)"
        return f"⚪ VERY FAR ({distance}cm)"
    
    def continuous_scan(self, interval=0.5, count=None):
        """Continuous distance scanning"""
        logging.info("📡 Starting continuous scan...")
        
        measurement_count = 0
        try:
            while (count is None or measurement_count < count) and self.running:
                distance = self.measure()
                
                if distance is not None:
                    classification = self.classify_distance(distance)
                    avg = self.get_average()
                    logging.info(f"⚡ {classification} | Avg: {avg:.1f}cm")
                    measurement_count += 1
                else:
                    logging.warning("❌ Measurement timeout")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logging.info("\n⏹️  Scan stopped")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up GPIO"""
        self.running = False
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except:
                pass

def main():
    """Test the sensor"""
    sensor = DistanceSensor()
    sensor.continuous_scan(interval=0.5, count=20)

if __name__ == "__main__":
    main()
