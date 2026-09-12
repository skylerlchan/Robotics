> **SUPERSEDED (2026-09-11):** commands, paths, env name and the Pi 5 assumption in this file are out of date. Use [PI4_FULL_TELEOP_GUIDE.md](PI4_FULL_TELEOP_GUIDE.md).

# AlohaMini Teleoperation Setup for macOS
**Date:** April 4, 2026

Guide for setting up and testing your AlohaMini arms on your Mac before the Pi5 is ready.

---

## What You Can Test Now (Without Pi5)

✅ **Leader Arms** - Connect to your Mac, test position reading
✅ **Follower Arms** - Connect to your Mac temporarily, test movement
✅ **Software Environment** - Install all dependencies on your Mac

⏳ **Full Teleoperation** - Requires Pi5 setup (leader arms on Mac → follower arms on Pi5)

---

## Hardware Setup

### What You Have:
- Mac computer
- 2 Leader arms (with Waveshare controllers)
- 2 Follower arms (with Waveshare controllers)
- Batteries to power the arms

### Connections for Testing:

**Leader Arms:**
```
Left Leader Arm:
  Waveshare Controller → USB-C cable → Mac

Right Leader Arm:
  Waveshare Controller → USB-C cable → Mac

Power:
  5V battery → 1-to-2 splitter → both leader arms
```

**Follower Arms** (for testing only):
```
Left Follower Arm:
  Waveshare Controller → USB-C cable → Mac

Right Follower Arm:
  Waveshare Controller → USB-C cable → Mac

Power:
  12V battery → 1-to-2 splitter → both follower arms
```

---

## Step 1: Install Software on Your Mac

### 1a. Install Homebrew (if not already installed)

Open Terminal and run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 1b. Install Conda (Miniforge for M1/M2/M3 Macs)

```bash
# Download Miniforge for macOS ARM (M1/M2/M3)
cd ~/Downloads
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh

# Install
bash Miniforge3-MacOSX-arm64.sh -b -p $HOME/miniforge3

# Initialize
$HOME/miniforge3/bin/conda init zsh
source ~/.zshrc
```

If you have an **Intel Mac** instead, use:
```bash
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
bash Miniforge3-MacOSX-x86_64.sh -b -p $HOME/miniforge3
$HOME/miniforge3/bin/conda init zsh
source ~/.zshrc
```

### 1c. Create Python Environment

```bash
# Create conda environment
conda create -y -n lerobot_alohamini python=3.10

# Activate environment
conda activate lerobot_alohamini
```

### 1d. Install LeRobot AlohaMini Dependencies

```bash
# Navigate to the lerobot_alohamini directory
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"

# Install using macOS requirements
pip install -e .[all]
pip install pyzmq
pip install feetech-servo-sdk

# Install ffmpeg
conda install ffmpeg=7.1.1 -c conda-forge
```

**This will take 5-10 minutes to install all dependencies.**

---

## Step 2: Connect Leader Arms to Mac

### 2a. Physical Connection

1. **Power the leader arms**:
   - Connect 5V battery to 1-to-2 DC splitter
   - Connect both leader arm power cables

2. **Connect to Mac**:
   - Left leader arm Waveshare → USB-C cable → Mac
   - Right leader arm Waveshare → USB-C cable → Mac

3. **Verify servos have power**:
   - Servos should be "springy" (some resistance when you move them)
   - If limp/loose, check power connections

### 2b. Find Port Numbers

In Terminal:
```bash
ls /dev/cu.usbmodem*
```

**Expected output:**
```
/dev/cu.usbmodem1101
/dev/cu.usbmodem1201
```
(Numbers may vary)

**Write down these port numbers!** You'll need them in the next step.

You can also use the built-in finder:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot_alohamini
lerobot-find-port
```

---

## Step 3: Configure Port Numbers

### 3a. Edit Leader Arm Configuration

Open the teleoperation script:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
code examples/alohamini/teleoperate_bi.py
```
(Or use any text editor: `nano`, `vim`, or TextEdit)

**Find the section with port configuration** (around line 30-50):

Look for something like:
```python
LEADER_PORT_LEFT = "/dev/ttyACM0"
LEADER_PORT_RIGHT = "/dev/ttyACM1"
```

**Change to your Mac ports:**
```python
LEADER_PORT_LEFT = "/dev/cu.usbmodem1101"   # Your left leader port
LEADER_PORT_RIGHT = "/dev/cu.usbmodem1201"  # Your right leader port
```

Save the file.

---

## Step 4: Calibrate Leader Arms

### 4a. Position Arms in "Middle Position"

Position both leader arms like this:
![Calibration Position](lerobot_alohamini/examples/alohamini/media/mid_position_so100.png)

- Shoulder perpendicular to base
- Elbow at ~90 degrees
- Wrist straight
- Gripper partially open

### 4b. Run Calibration

**Important:** This requires the Pi5 running the host script OR connecting follower arms to your Mac for testing.

**For now, let's test JUST reading leader arm positions:**

```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot_alohamini

# Test reading leader arms (this won't control anything, just reads positions)
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof \
  --calibrate_only
```

**Expected behavior:**
- Script prompts you to position arms in middle position
- Press Enter
- Rotate each joint 90° left, then 90° right
- Press Enter again
- Calibration data saved

---

## Step 5: Test Leader Arms (Reading Positions)

After calibration:

```bash
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof \
  --test_mode
```

**Expected behavior:**
- Terminal shows joint positions updating in real-time as you move the arms
- Numbers change when you move each joint
- This confirms leader arms are working!

---

## Step 6: Test Follower Arms (Optional - Temporary Setup)

If you want to test follower arms before Pi5 setup:

### 6a. Connect Follower Arms to Mac

**Temporarily connect follower arms to Mac** (instead of Pi5):
- Power: 12V battery → splitter → both follower arms
- Data: Follower arm Waveshare controllers → USB-C → Mac

### 6b. Find Follower Ports

```bash
ls /dev/cu.usbmodem*
```

You should now see **4 ports total** (2 leader + 2 follower).

### 6c. Configure Follower Ports

Edit the configuration file:
```bash
code lerobot/robots/alohamini/config_lekiwi.py
```

Find:
```python
FOLLOWER_PORT_LEFT = "/dev/ttyACM0"
FOLLOWER_PORT_RIGHT = "/dev/ttyACM1"
```

Change to:
```python
FOLLOWER_PORT_LEFT = "/dev/cu.usbmodem1301"   # Your left follower port
FOLLOWER_PORT_RIGHT = "/dev/cu.usbmodem1401"  # Your right follower port
```

### 6d. Start "Host" Script on Mac (Simulating Pi5)

In one Terminal window:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot_alohamini

python -m lerobot.robots.alohamini.lekiwi_host \
  --arm_profile so-arm-5dof
```

This starts a server that controls the follower arms.

### 6e. Start Teleoperation Script

In a **second Terminal window**:
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot_alohamini

python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof
```

**Expected behavior:**
✨ **Follower arms should mirror your leader arm movements!**

Move leader arms → follower arms copy the motion

---

## Troubleshooting

### Problem: "No module named 'lerobot'"
**Solution:** Make sure conda environment is activated:
```bash
conda activate lerobot_alohamini
```

### Problem: "Permission denied" on /dev/cu.usbmodem*
**Solution:** On Mac, you shouldn't need special permissions. Try unplugging and replugging USB cables.

### Problem: Can't find ports
**Solution:**
```bash
# List all USB devices
ls /dev/cu.*

# Should see cu.usbmodem* entries
```

### Problem: Servos don't move
**Check:**
- [ ] Battery connected and charged
- [ ] Power cables connected to servo bus
- [ ] Servos feel "springy" (powered) not limp

### Problem: Port numbers keep changing
**Solution:** This is normal on Mac. You'll need to:
1. Check ports each time: `ls /dev/cu.usbmodem*`
2. Update config files with new ports
3. (Advanced) Create udev rules to fix port names

---

## What's Next?

### Current Status:
✅ Software installed on Mac
✅ Leader arms connected and readable
✅ (Optional) Follower arms controllable from Mac

### After Pi5 Setup:
1. Install same software on Pi5
2. Connect follower arms to Pi5 (instead of Mac)
3. Connect cameras to Pi5
4. Run host script on Pi5
5. Run teleoperation script on Mac
6. **Full wireless teleoperation!**

---

## Architecture Summary

**Current Testing Setup:**
```
Mac (both leader & follower arms connected)
├── Leader arms → read positions
└── Follower arms → controlled by host script
```

**Final Production Setup:**
```
Mac (PC)                     Raspberry Pi 5 (Robot)
├── Leader arms              ├── Follower arms
└── Teleoperation script  ←WiFi→  Host script
                                 ├── Mobile base
                                 └── Cameras
```

---

## Quick Reference Commands

**Activate environment:**
```bash
conda activate lerobot_alohamini
```

**Find ports:**
```bash
ls /dev/cu.usbmodem*
```

**Test leader arms only:**
```bash
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof \
  --test_mode
```

**Full teleoperation (with Pi5 or Mac as host):**

Terminal 1 (Host side - will be Pi5 eventually):
```bash
python -m lerobot.robots.alohamini.lekiwi_host \
  --arm_profile so-arm-5dof
```

Terminal 2 (PC side):
```bash
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof
```

---

**Ready to start?** Let me know when you want to begin installing the software!
