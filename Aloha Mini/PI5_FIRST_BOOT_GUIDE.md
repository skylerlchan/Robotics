> **SUPERSEDED (2026-09-11):** commands, paths, env name and the Pi 5 assumption in this file are out of date. Use [PI4_FULL_TELEOP_GUIDE.md](PI4_FULL_TELEOP_GUIDE.md).

# Raspberry Pi 5 First Boot Setup Guide
**Date:** April 4, 2026

Complete walkthrough for setting up your AlohaMini Raspberry Pi 5 from scratch.

---

## What You Need

Hardware:
- [ ] Raspberry Pi 5
- [ ] MicroSD card (32GB+ recommended)
- [ ] MicroSD card reader (for your PC)
- [ ] 12V battery with buck converter
- [ ] (Optional) 7-inch HDMI display + HDMI cable
- [ ] (Optional) USB keyboard + mouse (for first setup)

Information:
- [ ] Your WiFi network name (SSID)
- [ ] Your WiFi password

---

## Step 1: Download Raspberry Pi Imager (On Your PC)

1. **Open your web browser** and go to:
   ```
   https://www.raspberrypi.com/software/
   ```

2. **Download Raspberry Pi Imager** for macOS (you're on Mac based on your system)

3. **Install the application**:
   - Open the downloaded `.dmg` file
   - Drag "Raspberry Pi Imager" to Applications folder
   - Open from Applications

---

## Step 2: Flash the MicroSD Card

### 2a. Insert MicroSD Card
- Insert your microSD card into your Mac's card reader
- Wait for it to appear (you might see it on desktop)

### 2b. Open Raspberry Pi Imager
- Launch "Raspberry Pi Imager" from Applications

### 2c. Choose Operating System
1. Click **"CHOOSE DEVICE"**
   - Select: **Raspberry Pi 5**

2. Click **"CHOOSE OS"**
   - Select: **Raspberry Pi OS (64-bit)**
   - (The first option with "Recommended" label)
   - This includes the desktop environment

3. Click **"CHOOSE STORAGE"**
   - Select your microSD card
   - ⚠️ **WARNING**: All data on this card will be erased!

### 2d. Configure Advanced Settings (IMPORTANT!)

1. Click the **gear icon ⚙️** (or press `Cmd+Shift+X`)

2. **OS Customization Settings** window opens:

   **General Tab:**
   - ✅ **Set hostname:** `alohamini` (or whatever you prefer)
   - ✅ **Set username and password:**
     - Username: `pi` (or your choice)
     - Password: `[choose a secure password]`
     - Write these down! You'll need them.

   **Services Tab:**
   - ✅ **Enable SSH**
     - Select: "Use password authentication"

   **Options Tab:**
   - ✅ **Configure wireless LAN**
     - SSID: `[your WiFi network name]`
     - Password: `[your WiFi password]`
     - Wireless LAN country: `US` (or your country)
   - ✅ **Set locale settings**
     - Timezone: `America/New_York` (or your timezone)
     - Keyboard layout: `us` (or your layout)

3. Click **"SAVE"**

### 2e. Write to MicroSD Card

1. Click **"WRITE"** (might be called "NEXT" then "YES")

2. **Confirm** - you'll get a warning that all data will be erased
   - Click "YES"

3. **Wait** (~5-10 minutes):
   - Progress bar shows writing
   - Then verifying
   - You'll see "Write Successful!" when done

4. **Eject the microSD card** safely from your Mac

---

## Step 3: Install MicroSD into Raspberry Pi 5

1. **Locate the microSD slot** on Pi5:
   - It's on the **underside** of the board
   - Small slot near one edge

2. **Insert the microSD card**:
   - Push it in gently until it clicks
   - Metal contacts face up (toward the board)
   - Card should be flush with the board

---

## Step 4: Connect Hardware (First Boot)

### 4a. Connect Display (Optional but Recommended for First Boot)

1. **Connect HDMI cable**:
   - From 7-inch display to Pi5 HDMI port
   - Pi5 has 2 HDMI ports - use either one (HDMI0 preferred)

2. **Power the display**:
   - Connect Type-C power cable to display

3. **Position display** on robot or table where you can see it

### 4b. Connect Peripherals (Optional)

- **USB keyboard** → any USB-A port on Pi5
- **USB mouse** → any USB-A port on Pi5
- (You can skip these if going headless, but helpful for troubleshooting)

### 4c. DO NOT Connect Servo Controllers Yet

- For first boot, keep it simple
- We'll connect the Waveshare controllers after OS is verified working

---

## Step 5: Power On!

1. **Double-check all connections**:
   - [ ] MicroSD card inserted
   - [ ] Display connected (HDMI + power)
   - [ ] Buck converter connected to 12V battery
   - [ ] Buck converter NOT yet connected to Pi5

2. **Power on the buck converter** (if it has a switch)

3. **Connect buck converter to Pi5 USB-C power port**

4. **Watch the Pi5**:
   - 🔴 Red LED should light up (power)
   - 🟢 Green LED should start flashing (activity)

5. **Watch the display**:
   - **First 5 seconds**: Raspberry Pi logo
   - **Next 30-60 seconds**: Boot messages scrolling
   - **After ~1-2 minutes**: Desktop appears!

---

## Step 6: Initial Desktop Setup

### If Desktop Loads Successfully:

You'll see the Raspberry Pi welcome wizard:

1. **Welcome Screen**
   - Click "Next"

2. **Country Settings**
   - Should already be set from imager
   - Click "Next"

3. **Create User** (might be skipped if you set it in imager)
   - Already configured
   - Click "Next"

4. **WiFi Network**
   - Should already be connected
   - Verify WiFi icon in top-right shows connected
   - Click "Next"

5. **Update Software**
   - Click "Next" to update
   - This might take 5-10 minutes
   - **Let it finish!**

6. **Setup Complete**
   - Click "Restart"

7. **Wait for reboot** (~30 seconds)

---

## Step 7: Verify Network Connection

After reboot, open Terminal (click terminal icon in top toolbar):

```bash
# Check if WiFi is connected
hostname -I
```

**Expected output:** Something like `192.168.1.123` (your Pi5's IP address)

**Write this IP address down!** You'll need it to SSH from your PC.

```bash
# Test internet connection
ping -c 3 google.com
```

**Expected output:** 3 packets sent and received

If both work: ✅ **Network is configured correctly!**

---

## Step 8: SSH from Your PC (Test Remote Access)

On your **Mac** (not the Pi5), open Terminal and try:

```bash
ssh pi@alohamini.local
```

Or using the IP address:

```bash
ssh pi@192.168.1.XXX
```
(Replace XXX with the actual IP from Step 7)

**First connection prompt:**
```
The authenticity of host 'alohamini.local' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
Type: `yes` and press Enter

**Password prompt:**
Enter the password you set in the Raspberry Pi Imager

**If successful:** You'll see:
```
pi@alohamini:~ $
```

✅ **You're now connected to your Pi5 remotely!**

Type `exit` to disconnect for now.

---

## Step 9: Connect Robot Hardware

Now that the Pi5 is working, let's connect the robot:

### 9a. Power Off Pi5
```bash
sudo shutdown now
```
Wait 30 seconds, then disconnect power.

### 9b. Connect Servo Controllers

1. **Left arm Waveshare controller** → Pi5 USB-C cable
2. **Right arm Waveshare controller** → Pi5 USB-C cable

### 9c. Connect Cameras

1. **Left arm camera** → Pi5 USB-A port
2. **Right arm camera** → Pi5 USB-A port
3. **Top camera** → Pi5 USB-A port
4. **Front camera** → Pi5 USB-A port
5. **Back camera** → Pi5 USB-A port

### 9d. Power On Again

- Reconnect power
- Wait for boot (~1 minute)

---

## Step 10: Verify Hardware Detection

SSH back into the Pi5:

```bash
ssh pi@alohamini.local
```

Check servo controllers:
```bash
ls /dev/ttyACM*
```

**Expected output:**
```
/dev/ttyACM0  /dev/ttyACM1
```

Check cameras:
```bash
ls /dev/video*
```

**Expected output:**
```
/dev/video0  /dev/video2  /dev/video4  /dev/video6  /dev/video8
```
(Numbers might vary, but should see 5 cameras)

---

## Step 11: Install Robot Software

Now we're ready to install the AlohaMini control software!

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install git (if not already)
sudo apt install git -y

# Clone the lerobot_alohamini repository
cd ~
git clone https://github.com/liyiteng/lerobot_alohamini.git
cd lerobot_alohamini

# Follow the installation instructions in that repository's README
# (This will include installing Python dependencies, configuring ports, etc.)
```

---

## Troubleshooting

### Problem: Display shows nothing
- **Check:** HDMI cable firmly connected
- **Check:** Display powered on
- **Check:** Try the other HDMI port on Pi5

### Problem: No WiFi connection
- **Check:** WiFi credentials were correct in imager
- **Try:** Manually configure WiFi:
  - Click WiFi icon in top-right
  - Select your network
  - Enter password

### Problem: Can't SSH
- **Check:** Pi5 and PC on same WiFi network
- **Try:** Use IP address instead of hostname
- **Try:** `ping alohamini.local` to verify Pi5 is reachable

### Problem: No servo controllers detected
- **Check:** USB-C cables are data cables (not power-only)
- **Check:** Waveshare controllers are powered (via servo bus)
- **Try:** Unplug/replug USB-C cables

### Problem: Cameras not detected
- **Check:** All cameras plugged into USB ports
- **Check:** Cameras powered (USB provides power)
- **Try:** Different USB ports

---

## What's Next?

✅ **You've completed the Pi5 setup!**

Next steps:
1. Follow the `lerobot_alohamini` repository installation guide
2. Configure port mappings for your specific setup
3. Test teleoperation
4. Start collecting data!

Refer back to the main [SETUP_GUIDE.md](SETUP_GUIDE.md) for the overall architecture and next steps.

---

## Quick Reference

**Pi5 Credentials:**
- Hostname: `alohamini` (or what you chose)
- Username: `pi` (or what you chose)
- Password: [what you set]
- IP Address: [write it here after Step 7]

**Useful Commands:**
```bash
# Shutdown Pi5
sudo shutdown now

# Reboot Pi5
sudo reboot

# Check WiFi status
hostname -I

# SSH from your PC
ssh pi@alohamini.local
```
