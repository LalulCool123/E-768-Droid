# E-7 Droid V3 - Deployment & Installation Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Raspberry Pi 3/4+ with Python 3.7+
- E-7 Droid V2 hardware (servos, sensors, I2C)
- Git installed (`sudo apt-get install git`)
- Internet connection (for initial setup)

### Step 1: Clone V3 Branch
```bash
cd /workspaces/E-768-Droid
git pull origin
git checkout V3-improved-ai-performance
```

### Step 2: Install Dependencies (if not present)
```bash
# Python packages
pip install flask flask-cors pygame

# System packages (optional - for optimization)
sudo apt-get install python3-smbus python3-rpi.gpio
```

### Step 3: Update Configuration
```bash
# Edit IP address in HTML (if needed)
sed -i 's/192.168.3.227/<YOUR_PI_IP>/g' AAA_E-7_Micro_V3.html
```

### Step 4: Start the Server
```bash
# Option A: Use V3 improved server (RECOMMENDED)
python3 server3_improved.py &

# Option B: Keep using V2 server (for backward compatibility)
python3 server2.py &

# Option C: Hybrid (V3 movement + V2 server)
# - Start server2.py
# - Replace robot_movement.py symlink to robot_movement_v3.py
```

### Step 5: Access Web UI
```
Browser: http://<YOUR_PI_IP>:7567/AAA_E-7_Micro_V3.html
```

---

## 📋 Full Installation Options

### Option A: Full V3 Deployment (Recommended for New Setups)

**Best for**: New installations, development, full optimization

```bash
# 1. Backup V2 (optional)
mkdir backup_v2
cp server2.py robot_movement.py AAA_E-7_Micro.html backup_v2/

# 2. Setup V3
ln -sf server3_improved.py server2.py          # Symlink for compatibility
ln -sf robot_movement_v3.py robot_movement.py
ln -sf AAA_E-7_Micro_V3.html AAA_E-7_Micro.html

# 3. Create TTS cache directory
mkdir -p /tmp/e7_tts_cache
chmod 777 /tmp/e7_tts_cache

# 4. Start server
systemctl start e7-robot  # if systemd service configured
# OR
python3 server3_improved.py &
```

### Option B: Gradual Migration (Recommended for Existing Setups)

**Best for**: Existing installations, testing, safe rollout

```bash
# 1. Keep V2 as primary
python3 server2.py &

# 2. Update UI to V3 only
cp AAA_E-7_Micro_V3.html AAA_E-7_Micro.html  # Switch UI only

# 3. Test V3 movement in background
python3 robot_movement_v3.py &  # Parallel test

# 4. After testing, switch server
# pkill server2.py
# python3 server3_improved.py &
```

### Option C: Docker Deployment (Production)

**Best for**: Server deployment, cloud, isolation

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors pygame
EXPOSE 7567
CMD ["python3", "server3_improved.py"]
```

Build & Run:
```bash
docker build -t e7-droid:v3 .
docker run -p 7567:7567 --device /dev/i2c-1 e7-droid:v3
```

---

## ⚙️ Configuration Reference

### Environment Variables (Optional)

```bash
# TTS Cache settings
export TTS_CACHE_DIR="/tmp/e7_tts_cache"
export TTS_CACHE_MODE="enabled"

# Performance tuning
export MAX_VOCABULARY_SIZE="5000"
export SIMILARITY_THRESHOLD="0.6"
export AUDIO_EFFECTS="true"

# Server settings
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="7567"
export FLASK_DEBUG="false"

# Start server with env
export TTS_CACHE_MODE=enabled python3 server3_improved.py
```

### Config File (server3_improved.py)

```python
# Modify these lines in server3_improved.py

# Line 21-24: Cache & performance
TTS_CACHE_DIR = "/tmp/e7_tts_cache"
MAX_VOCABULARY_SIZE = 5000          # ← Adjust for memory
SIMILARITY_THRESHOLD = 0.6           # ← 0.5=fuzzy, 0.9=strict
AUDIO_EFFECTS_ENABLED = True         # ← False for speed

# Line 272: Server binding
app.run(host='0.0.0.0', port=7567, debug=False, threaded=True)
```

---

## 🧪 Testing & Validation

### 1. Health Check
```bash
# Check if server is running
curl -s http://localhost:7567/status | python3 -m json.tool

# Expected output:
# {
#   "robot_state": "idle",
#   "movement_running": true,
#   "status": "Online ✅",
#   "vocabulary_size": 245,
#   "cache_size": 12
# }
```

### 2. Test Voice Command
```bash
# Send test command
curl -X POST http://localhost:7567/command \
  -H "Content-Type: application/json" \
  -d '{"intent": "e7 hallo"}'

# Expected response:
# {
#   "response": "Hallo! Ich bin E-7 6 8, dein Roboter-Assistent."
# }
```

### 3. Cache Performance Test
```bash
# Time first response (TTS generation)
time curl -X POST http://localhost:7567/command \
  -H "Content-Type: application/json" \
  -d '{"intent": "e7 test eins zwei drei"}'
# Expected: ~3-4 seconds

# Time second identical response (cache hit)
time curl -X POST http://localhost:7567/command \
  -H "Content-Type: application/json" \
  -d '{"intent": "e7 test eins zwei drei"}'
# Expected: ~0.2 seconds (20x faster!)
```

### 4. Memory Usage Test
```bash
# Monitor vocabulary growth
watch -n 2 'echo "Vocab lines: $(wc -l < woerter.txt)"'

# Should stabilize at ~5000 lines (V3 management)
# V2 would grow unbounded
```

### 5. GPIO Performance Test
```bash
# Monitor CPU usage (robot movement)
# Terminal 1:
python3 robot_movement_v3.py

# Terminal 2:
watch -n 0.5 'top -p $(pidof python3) -b -n 1'

# Should show <5% CPU for V3
# vs 100% for V2 (busy-wait)
```

---

## 🛠️ Troubleshooting

### Issue: TTS Cache Not Working
**Symptoms**: All responses are slow (3.8s even for repeated phrases)

**Solution**:
```bash
# Check cache directory exists
ls -la /tmp/e7_tts_cache/

# Ensure writable
sudo chmod 777 /tmp/e7_tts_cache/

# Verify server is using cache
grep "Cache hit" /tmp/robot*.log

# Restart server
pkill -f server3_improved
python3 server3_improved.py
```

### Issue: Servo Not Moving
**Symptoms**: Robot doesn't respond to movement commands

**Solution**:
```bash
# Check I2C connection
i2cdetect -y 1

# Should show "40" (PCA9685)
# If not found:
# 1. Check wiring
# 2. Try V2 movement: python3 robot_movement.py
# 3. Set SERVO_AVAILABLE = False for simulation
```

### Issue: GPIO Not Available
**Symptoms**: "GPIO not available" error

**Solution**:
```bash
# Install GPIO library
sudo apt-get install python3-rpi.gpio

# Run with root/sudo
sudo python3 robot_movement_v3.py

# OR for development on non-RPi:
# Edit ultraschall_messung_v3.py line 42
# GPIO_AVAILABLE = True  ← Force False for simulation mode
```

### Issue: Server Won't Start
**Symptoms**: `Address already in use` error

**Solution**:
```bash
# Find what's using port 7567
sudo lsof -i :7567

# Kill old process
sudo kill -9 <PID>

# Or use different port
sed -i 's/port=7567/port=8888/g' server3_improved.py
```

### Issue: High Memory Usage
**Symptoms**: Robot runs slow, RAM nearly full

**Solution**:
```bash
# Check woerter.txt size
wc -l woerter.txt

# If > 5000 lines, V3 management isn't working
# Manually prune (keeps 5000 most frequent)
python3 << 'EOF'
from collections import Counter
lines = open('woerter.txt').read().split('\n')
freq = Counter(lines)
top_5000 = [w for w,_ in freq.most_common(5000)]
open('woerter.txt','w').write('\n'.join(top_5000))
print(f"Pruned to {len(top_5000)} words")
EOF
```

---

## 📊 Performance Monitoring

### Setup Monitoring Dashboard
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "=== E-7 Droid V3 Monitor ==="
  echo "Time: $(date)"
  echo ""
  echo "CPU Usage:"
  top -p $(pgrep -f server3) -b -n 1 | tail -1
  echo ""
  echo "Memory:"
  free -h | grep Mem
  echo ""
  echo "Vocabulary Size:"
  wc -l woerter.txt
  echo ""
  echo "TTS Cache Size:"
  du -sh /tmp/e7_tts_cache/
  echo ""
  echo "Network:"
  curl -s http://localhost:7567/status | python3 -m json.tool
  sleep 5
done
EOF

chmod +x monitor.sh
./monitor.sh
```

### Setup Systemd Service (Optional)
```bash
# Create service file
sudo tee /etc/systemd/system/e7-droid.service << EOF
[Unit]
Description=E-7 Droid V3 Robot Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/E-768-Droid
ExecStart=/usr/bin/python3 /home/pi/E-768-Droid/server3_improved.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable e7-droid
sudo systemctl start e7-droid
sudo systemctl status e7-droid
```

---

## 🔄 Rollback Procedure

### If V3 has Issues
```bash
# Option 1: Quick fallback to V2
git checkout main
# Restart server
pkill -f "server3_improved\|server2"
python3 server2.py &

# Option 2: Keep V3 code, revert HTML only
git checkout main -- AAA_E-7_Micro.html
# Still using server3_improved.py with V2 UI

# Option 3: Use backup if available
rm server2.py robot_movement.py AAA_E-7_Micro.html
cp backup_v2/* .
# Restart
```

---

## 📈 Upgrade Path

```
V2 (Original)
    ↓
V3 (Current) ← You are here
    ↓
V4 (Planned)
  - ML-based NLP (Hugging Face)
  - Multi-language support
  - Web command editor
  - Custom voice synthesis
```

---

## 📞 Support Resources

### Log Files
```bash
# Server logs (if redirected)
tail -f /tmp/e7-robot.log

# System logs
journalctl -u e7-droid -f

# Debug verbose
python3 server3_improved.py 2>&1 | tee debug.log
```

### Common Commands
```bash
# List all processes
pgrep -af "e7\|robot\|server"

# Kill all robot processes safely
pkill -f "server2\|server3\|robot_movement"

# Check which version is running
strings /proc/$(pgrep -f server)/cmdline

# Monitor real-time
python3 -c "
import requests, json, time
while True:
    r = requests.get('http://localhost:7567/status')
    print(json.dumps(r.json(), indent=2))
    time.sleep(2)
"
```

---

## ✅ Deployment Checklist

- [ ] V3 branch cloned
- [ ] Dependencies installed
- [ ] IP address configured
- [ ] TTS cache directory created (`/tmp/e7_tts_cache`)
- [ ] Server starts without errors
- [ ] Health check passes (`/status` endpoint)
- [ ] Voice command works
- [ ] Web UI loads correctly
- [ ] Movement responds to commands
- [ ] Sensors reading values
- [ ] Performance acceptable (CPU <20%, latency <4s)
- [ ] Old V2 backed up (optional)

---

## 📝 Version Info

```
E-7 Droid V3
├─ server3_improved.py: 550 lines
├─ robot_movement_v3.py: 380 lines
├─ ultraschall_messung_v3.py: 180 lines
├─ AAA_E-7_Micro_V3.html: 580 lines
└─ Total: 1,690 lines of V3 improvements
```

**Released**: March 2026
**Python**: 3.7+
**Compatibility**: All E-7 Droid hardware (Pi 3+)
**Status**: ✅ Production Ready

---

*For updates and support, check the V3 branch*
