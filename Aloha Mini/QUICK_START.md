> **SUPERSEDED (2026-09-11):** commands, paths, env name and the Pi 5 assumption in this file are out of date. Use [PI4_FULL_TELEOP_GUIDE.md](PI4_FULL_TELEOP_GUIDE.md).

# AlohaMini Quick Start - Teleoperation NOW
**Date:** April 4, 2026

All 4 arms detected! Let's get them moving.

## Detected USB Ports:
```
Port 1: /dev/cu.usbmodem5AE60529891
Port 2: /dev/cu.usbmodem5AE60551511
Port 3: /dev/cu.usbmodem5AE60554691
Port 4: /dev/cu.usbmodem5AE60833451
```

---

## Step 1: Install Software (15 minutes)

### 1a. Install Miniforge (Conda)

Open Terminal and run these commands ONE AT A TIME:

```bash
# Download Miniforge
cd ~/Downloads
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh

# Install (press Enter when prompted, type 'yes' to accept license)
bash Miniforge3-MacOSX-arm64.sh

# When asked "Do you wish to update your shell profile to automatically initialize conda?"
# Type: yes

# Close and reopen Terminal, or run:
source ~/.zshrc
```

### 1b. Create Environment

```bash
# Create Python environment
conda create -y -n lerobot python=3.10

# Activate it
conda activate lerobot
```

### 1c. Install Dependencies

```bash
# Navigate to lerobot_alohamini
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"

# Install everything
pip install -e .[all]
pip install pyzmq
pip install feetech-servo-sdk
conda install -y ffmpeg=7.1.1 -c conda-forge
```

**This takes ~10-15 minutes. Let it run!**

---

## Step 2: Identify Which Arm is Which

Now we need to figure out which USB port connects to which arm.

### 2a. Physical Labeling

Grab 4 pieces of tape/paper and **physically label your arms**:
- "Leader Left"
- "Leader Right"
- "Follower Left"
- "Follower Right"

Stick labels on each arm so you can identify them visually.

### 2b. Test Each Port

We'll test each USB port one at a time to see which arm moves.

**Prepare:**
- Make sure ALL arms are powered (batteries connected)
- Keep all 4 USB cables plugged in

**Test Port 1:**
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot

# Test first port
python -c "
from feetech_servo_sdk import SyncReadWrite
port = '/dev/cu.usbmodem5AE60529891'
bus = SyncReadWrite(port, baudrate=1000000)
print(f'Testing {port}...')
print('If an arm twitches or gets stiffer, that is the arm on this port!')
bus.close()
"
```

**Watch all 4 arms** - which one reacted? Write it down:
```
Port 1 (/dev/cu.usbmodem5AE60529891) = [which arm?]
```

**Repeat for other ports:**

Port 2:
```bash
python -c "
from feetech_servo_sdk import SyncReadWrite
port = '/dev/cu.usbmodem5AE60551511'
bus = SyncReadWrite(port, baudrate=1000000)
print(f'Testing {port}...')
bus.close()
"
```

Port 3:
```bash
python -c "
from feetech_servo_sdk import SyncReadWrite
port = '/dev/cu.usbmodem5AE60554691'
bus = SyncReadWrite(port, baudrate=1000000)
print(f'Testing {port}...')
bus.close()
"
```

Port 4:
```bash
python -c "
from feetech_servo_sdk import SyncReadWrite
port = '/dev/cu.usbmodem5AE60833451'
bus = SyncReadWrite(port, baudrate=1000000)
print(f'Testing {port}...')
bus.close()
"
```

**Write down your mapping:**
```
Port: /dev/cu.usbmodem5AE60529891 = ___________
Port: /dev/cu.usbmodem5AE60551511 = ___________
Port: /dev/cu.usbmodem5AE60554691 = ___________
Port: /dev/cu.usbmodem5AE60833451 = ___________
```

---

## Step 3: Configure Ports

Once you know which port is which arm, we'll edit the config files.

### 3a. Edit Follower Arm Config

```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
code lerobot/robots/alohamini/config_lekiwi.py
```

Find lines with:
```python
FOLLOWER_PORT_LEFT = ...
FOLLOWER_PORT_RIGHT = ...
```

Change to YOUR follower ports:
```python
FOLLOWER_PORT_LEFT = "/dev/cu.usbmodem5AE60XXXXXX"   # Your left follower port
FOLLOWER_PORT_RIGHT = "/dev/cu.usbmodem5AE60YYYYYY"  # Your right follower port
```

Save the file.

### 3b. Edit Leader Arm Config

```bash
code examples/alohamini/teleoperate_bi.py
```

Find lines with (around line 30-80):
```python
LEADER_PORT_LEFT = ...
LEADER_PORT_RIGHT = ...
```

Change to YOUR leader ports:
```python
LEADER_PORT_LEFT = "/dev/cu.usbmodem5AE60ZZZZZZ"   # Your left leader port
LEADER_PORT_RIGHT = "/dev/cu.usbmodem5AE60WWWWWW"  # Your right leader port
```

Save the file.

---

## Step 4: Start Teleoperation!

### 4a. Start Host (Follower Arm Controller)

Open Terminal 1:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot

python -m lerobot.robots.alohamini.lekiwi_host \
  --arm_profile so-arm-5dof
```

**First time:** It will ask you to calibrate. Position follower arms in middle position, press Enter, rotate joints, press Enter again.

**After calibration:** It will say "Waiting for commands..." - this is good! Leave this terminal running.

### 4b. Start Teleoperation (Leader Arm Reader)

Open Terminal 2:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot

python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof
```

**First time:** It will ask you to calibrate leader arms. Same process - middle position, rotate, done.

### 4c. Teleoperate!

✨ **Move your leader arms - follower arms should copy the movement!** ✨

---

## Troubleshooting

### "Module not found" errors
**Solution:** Make sure conda environment is activated:
```bash
conda activate lerobot
```

### Port permission errors
**Solution:** Try with sudo (not ideal but works for testing):
```bash
sudo python -m lerobot.robots.alohamini.lekiwi_host --arm_profile so-arm-5dof
```

### Servos don't move
**Check:**
- [ ] All batteries connected and charged?
- [ ] All USB cables plugged in?
- [ ] Servos feel "springy" (powered) not limp?

### Wrong arm moves
**Solution:** Swap the port assignments in the config files and try again.

---

## Quick Reference

**Your detected ports:**
```
/dev/cu.usbmodem5AE60529891
/dev/cu.usbmodem5AE60551511
/dev/cu.usbmodem5AE60554691
/dev/cu.usbmodem5AE60833451
```

**Activate environment:**
```bash
conda activate lerobot
```

**Start host (Terminal 1):**
```bash
python -m lerobot.robots.alohamini.lekiwi_host --arm_profile so-arm-5dof
```

**Start teleoperation (Terminal 2):**
```bash
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof
```
