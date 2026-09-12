> **SUPERSEDED (2026-09-11):** commands, paths, env name and the Pi 5 assumption in this file are out of date. Use [PI4_FULL_TELEOP_GUIDE.md](PI4_FULL_TELEOP_GUIDE.md).

# ✅ Setup Complete - Next Steps for Teleoperation

## What I've Done:

✅ **Installed Miniforge (Conda)** - Python environment manager
✅ **Created `lerobot` environment** - Python 3.10
✅ **Installed all dependencies** - LeRobot, PyZMQ, ffmpeg, etc.
✅ **Detected all 4 USB ports** - All arms are connected
✅ **Created identification script** - To map ports to arms

---

## What YOU Need to Do:

### Step 1: Identify Which Arm is Which (5 minutes)

**Run this command:**
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini"
./find_arms_simple.sh
```

**What will happen:**
1. Script tests each USB port one at a time
2. You press Enter to test a port
3. **One arm will become stiffer or twitch slightly**
4. You tell the script which arm moved (Leader Left/Right or Follower Left/Right)
5. Repeat for all 4 ports
6. Script generates the configuration code

**The script will output something like:**
```
LEADER_PORT_LEFT = "/dev/cu.usbmodem5AE60529891"
LEADER_PORT_RIGHT = "/dev/cu.usbmodem5AE60551511"
FOLLOWER_PORT_LEFT = "/dev/cu.usbmodem5AE60554691"
FOLLOWER_PORT_RIGHT = "/dev/cu.usbmodem5AE60833451"
```

**Copy these lines - you'll need them in Step 2!**

---

### Step 2: Configure the Ports

**Edit the follower arms config:**
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
open -e lerobot/robots/alohamini/config_lekiwi.py
```

Find the lines that say:
```python
FOLLOWER_PORT_LEFT = ...
FOLLOWER_PORT_RIGHT = ...
```

Replace with YOUR follower ports from Step 1.

**Edit the leader arms config:**
```bash
open -e examples/alohamini/teleoperate_bi.py
```

Find the lines that say:
```python
LEADER_PORT_LEFT = ...
LEADER_PORT_RIGHT = ...
```

Replace with YOUR leader ports from Step 1.

Save both files.

---

### Step 3: Start Teleoperation!

**Open 2 Terminal windows:**

**Terminal 1 (Host - controls follower arms):**
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot
python -m lerobot.robots.alohamini.lekiwi_host --arm_profile so-arm-5dof
```

**First time:** It will ask you to calibrate follower arms:
- Position arms in middle position (image will be shown)
- Press Enter
- Rotate each joint 90° left, then 90° right
- Press Enter
- Done!

**After calibration:** Terminal says "Waiting for commands..." - **leave this running!**

---

**Terminal 2 (Client - reads leader arms):**
```bash
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"
conda activate lerobot
python examples/alohamini/teleoperate_bi.py \
  --remote_ip 127.0.0.1 \
  --leader_id so101_leader_bi \
  --arm_profile so-arm-5dof
```

**First time:** It will ask you to calibrate leader arms (same process as follower arms).

**After calibration:**

🎉 **MOVE YOUR LEADER ARMS → FOLLOWER ARMS COPY THE MOVEMENT!** 🎉

---

## Your 4 Detected USB Ports:

```
/dev/cu.usbmodem5AE60529891
/dev/cu.usbmodem5AE60551511
/dev/cu.usbmodem5AE60554691
/dev/cu.usbmodem5AE60833451
```

You need to figure out which is which using the identification script!

---

## Summary:

1. ✅ **Software installed** (I did this)
2. ⏳ **Run `./find_arms_simple.sh`** (YOU do this - I can't see which arm moves)
3. ⏳ **Edit config files** with correct ports
4. ⏳ **Run Terminal 1** (host script)
5. ⏳ **Run Terminal 2** (teleoperation script)
6. ✨ **Teleoperate!**

---

## Need Help?

- See [QUICK_START.md](QUICK_START.md) for detailed instructions
- See [MAC_TELEOPERATION_SETUP.md](MAC_TELEOPERATION_SETUP.md) for Mac-specific setup
- See [PI5_FIRST_BOOT_GUIDE.md](PI5_FIRST_BOOT_GUIDE.md) for Pi5 setup (when you get microSD card)

---

**You're almost there! Just need to identify the arms and configure the ports!**
