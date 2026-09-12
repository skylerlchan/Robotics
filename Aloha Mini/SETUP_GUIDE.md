> **SUPERSEDED (2026-09-11):** commands, paths, env name and the Pi 5 assumption in this file are out of date. Use [PI4_FULL_TELEOP_GUIDE.md](PI4_FULL_TELEOP_GUIDE.md).

# AlohaMini Setup Guide with Raspberry Pi 5

## Overview

Your AlohaMini robot uses a **Raspberry Pi 5** as its main compute platform. The Pi 5 connects to:
- 2 Waveshare Bus Servo Controllers (for the follower arms)
- 5 USB cameras (3 on mobile base, 2 on arms)
- The mobile base servos (via the left arm controller)

## Hardware Connection Architecture

```
Raspberry Pi 5
├── USB-C #1 → Left Arm Waveshare Controller
│   └── Controls: Left follower arm servos (6 servos)
│   └── Also connects to: Mobile base lift servo #11 (via 90cm cable)
│
├── USB-C #2 → Right Arm Waveshare Controller
│   └── Controls: Right follower arm servos (6 servos)
│
├── USB #1 → Left Arm Camera
├── USB #2 → Right Arm Camera
├── USB #3 → Top Camera (mobile base)
├── USB #4 → Front Camera (mobile base)
├── USB #5 → Back Camera (mobile base)
│
└── Power: 12V→5V buck converter (from 12V battery)
```

## Physical Wiring Steps

Based on the assembly guide you've followed:

### 1. **Power Connection**
- Connect the 12V→5V buck converter to the Raspberry Pi 5's USB-C power port
- The buck converter draws from one of your 12V lithium batteries

### 2. **Servo Controllers (Waveshare Bus Servo Adapters)**
- Connect **left arm** Waveshare controller to Pi 5 via USB-C cable
- Connect **right arm** Waveshare controller to Pi 5 via USB-C cable
- Note: The mobile base servo #11 connects to the **left arm controller** via 90cm cable (this is already wired if you followed the assembly guide)

### 3. **Camera Connections**
- Connect all 5 USB cameras to the Raspberry Pi 5's USB-A ports
  - 2 arm cameras (32×32mm, 3.8mm focal length)
  - 3 base cameras (36×36mm, 2.4mm focal length)

## Software Setup

Now that hardware is wired, you need to install the control software on the Raspberry Pi 5:

### Step 1: Clone the LeRobot AlohaMini Repository

On your **Raspberry Pi 5**, clone the integrated software repository:

```bash
git clone https://github.com/liyiteng/lerobot_alohamini.git
cd lerobot_alohamini
```

### Step 2: Follow Installation Instructions

The `lerobot_alohamini` repository contains:
- Complete installation guide
- Port configuration for your servos
- Teleoperation scripts
- Data collection tools

**Next steps are in that repository's README** - it will guide you through:
1. Installing dependencies (Python, LeRobot, etc.)
2. Configuring USB ports (`/dev/ttyACM0`, `/dev/ttyACM1`, etc.)
3. Testing servo connections
4. Running teleoperation
5. Recording datasets

## Testing Your Setup

Once software is installed, you can test each subsystem:

### Test Mobile Base (wheels & lift)
```bash
# Test wheels (W/S/A/D for movement)
python examples/debug/wheels.py --port /dev/ttyACM0

# Test lift axis (U/J for up/down)
python examples/debug/axis.py --port /dev/ttyACM0
```

### Test Arms
Use the teleoperation scripts from `lerobot_alohamini` to verify both follower arms respond correctly.

## Key Reference Files

In the cloned `AlohaMini` directory, you have:
- [hardware_assembly.md](AlohaMini/docs/hardware_assembly.md) - Full assembly guide with images
- [BOM.md](AlohaMini/docs/BOM.md) - Complete parts list and architecture explanation
- [software_setup.md](AlohaMini/docs/software_setup.md) - Links to software repo

## Troubleshooting

### Can't find servo controllers?
```bash
ls /dev/ttyACM*
```
Should show `/dev/ttyACM0` and `/dev/ttyACM1` (or similar). If not:
- Check USB-C cables are data-capable (not power-only)
- Verify Waveshare controllers have power (from batteries via servo chains)

### Cameras not detected?
```bash
ls /dev/video*
```
Should show 5 video devices. If fewer appear:
- Try different USB ports
- Check camera power via USB
- Some cameras may need USB 2.0 vs 3.0 ports

## Next Steps

1. Set up Raspberry Pi 5 OS (if not already done)
2. Clone `lerobot_alohamini` on the Pi 5
3. Follow the software installation in that repository
4. Configure port mappings
5. Test teleoperation
6. Start collecting data!

## Architecture Notes

- **Client side (Host)**: Your Raspberry Pi 5 on the robot (follower arms + mobile base)
- **Host side (PC)**: Your PC workstation + leader arms for teleoperation
- Communication: Via WiFi (robot runs autonomously) or USB (tethered mode for initial testing)

---

**Official Repository**: https://github.com/liyiteng/AlohaMini
**Software Repository**: https://github.com/liyiteng/lerobot_alohamini
