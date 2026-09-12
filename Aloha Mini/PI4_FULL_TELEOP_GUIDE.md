# AlohaMini on a Raspberry Pi 4 — full teleoperation from this Mac

**Date:** 2026-09-11 · **Robot:** AlohaMini 1 (SO-101 5-DoF arms, STS3215 base + lift) · **Robot computer:** Raspberry Pi 4 · **Operator computer:** this Mac

This replaces the April guides in this folder (they assumed a Pi 5, an old repo layout and an old Python env).

---

## 0. The short answer

The way to do it is the stock LeRobot **host / client** split that AlohaMini ships with — the Pi 4 is the *host* bolted to the robot, your Mac is the *client*:

```
   THIS MAC (client)                     WiFi / Tailscale                RASPBERRY PI 4 on the robot (host)
   ─────────────────                    ──────────────────               ──────────────────────────────────
   2 leader arms  ──USB──▶ teleoperate_bi.py ──TCP 5555 (commands)──▶  alohamini_host.py ──USB──▶ LEFT Waveshare board
   keyboard (base/lift)      │                                              │                     │  arm servos 1-6
   Rerun viewer ◀────────────┘ ◀──TCP 5556 (state + JPEG frames)────────────┘                     │  wheels 8, 9, 10
                                                                            │                     └─ lift 11
                                                                            ├──USB──▶ RIGHT Waveshare board → arm servos 1-6
                                                                            └──USB hub──▶ cameras (forward, wrist_right, …)
```

Everything — both arms, the omni base, the lift, the cameras — goes through one process on the Pi (`alohamini_host`) and one process on the Mac (`teleoperate_bi.py`). Nothing else is needed. For "remote" beyond your own WiFi, put Tailscale on both machines and use the Pi's Tailscale IP (section 9).

**What I already did on the Mac today**

- Fast-forwarded your `lerobot_alohamini` clone to upstream (357 commits). The host is now `alohamini_host` (was `lekiwi_host`), it needs Python ≥ 3.12, runs control at 50 Hz, and your robot is selected with `--robot_model alohamini1`.
- Created conda env **`lerobot_alohamini`** (Python 3.12, lerobot 0.6.1) and installed the client extras. The old `lerobot` env is dead — its editable install pointed at a OneDrive path that no longer exists.
- Patched `examples/alohamini/teleoperate_bi.py` and `calibrate_bi.py` to accept `--teleop.left_port` / `--teleop.right_port` (macOS has no udev, so the hardcoded `/dev/am_arm_leader_*` names can't exist here).
- Wrote the Pi-side helpers in `pi4/`: `install_pi4.sh`, `make_udev_rules.sh`, `alohamini-host.service`.

---

## 1. Wire the robot to the Pi 4

The Pi 4 differs from the Pi 5 in the BOM in ways that matter. Per the official Pi docs, all four ports hang off one VL805 controller and **every USB 2.0 device on a Pi 4 shares a single 480 Mbit/s USB 2.0 bus, whichever port or hub it is on**. The 720p cameras are USB 2.0 devices, so a hub adds ports and power but never bandwidth; MJPG (section 5) is what makes five cameras fit. The ports also supply about **1.2 A in total**. So: cameras on a **powered** hub, servo boards on the Pi's own ports.

| Connection | From | To | Notes |
|---|---|---|---|
| Pi power | 12 V battery #1 → 12 V→5 V/5 A buck converter | Pi 4 **USB-C power** port | Set the buck to 5.1 V measured at the Pi. Short, thick USB-C cable. The Pi 4 wants 5.1 V / 3 A and logs under-voltage below 4.63 V. If the red LED flickers, add a 1000–3300 µF capacitor across the buck output. Keep this battery separate from the servo battery (the reference design does). |
| Servo power | 12 V battery #2 → 1-to-2 DC splitter → two DC extension cables | Left arm chain and right arm chain | The base wheels (IDs 8/9/10) and lift (ID 11) are on the **left** arm's chain, so battery #2 powers arms + base + lift. |
| Left Waveshare board | USB-C **data** cable | Pi 4 **USB 2.0** port (black) | This board has two cables on it: the left arm chain and the 90 cm cable to base servo #11. |
| Right Waveshare board | USB-C **data** cable | Pi 4 **USB 2.0** port (black) | Arm only. |
| Waveshare jumper (both boards) | — | — | Jumper in the **USB (B)** position, not UART (A). The chip is a CH343 and appears as `/dev/ttyACM*` through the kernel's own cdc-acm driver; do **not** install WCH's vendor driver (it renames ports to `ttyCH343USB*`). |
| Cameras (up to 5) | USB | **Powered USB 3.0 hub** → Pi 4 **USB 3.0** port (blue) | Keep servo boards off the camera hub so servo latency isn't shared with video. |
| 7-inch display (optional) | HDMI + USB-C power | Pi 4 micro-HDMI 0 | Only for first boot / debugging. |

Sanity checks after wiring:

```bash
# on the Pi
ls /dev/ttyACM*              # expect 2 entries (the two Waveshare boards)
ls /dev/video*               # 2 entries per camera (capture + metadata)
vcgencmd get_throttled       # 0x0 = power is fine; 0x50005 = under-voltage, fix the buck/cable
dmesg | grep -i -E "voltage|usb" | tail   # under-voltage entries and USB enumeration
```

---

## 2. Flash and boot the Pi 4

1. On the Mac install **Raspberry Pi Imager** (raspberrypi.com/software).
2. Choose device **Raspberry Pi 4**, OS **Raspberry Pi OS (64-bit)**. Lite is enough for a headless robot; pick Desktop only if you'll use the 7-inch screen.
3. In the gear / "Edit settings" dialog: hostname `alohamini`, user `pi` + password, **enable SSH** (password auth), your WiFi SSID + password + country, timezone.
4. Write to a 32 GB+ microSD (A2-rated cards are noticeably faster), insert, power via the buck converter.
5. After ~1 min, from the Mac:

```bash
ssh pi@alohamini.local
hostname -I        # write down the LAN IP, e.g. 192.168.1.42
```

---

## 3. Install the software on the Pi

Copy the helper folder over and run the installer (it does apt packages, the `dialout` group, Miniforge for ARM64, a Python 3.12 env, the repo clone, and the `lekiwi,hardware` extras — torch is a core dependency so expect 15–30 min):

```bash
# on the Mac
scp -r "/Users/skyler/Projects/research/Robotics/Aloha Mini/pi4" pi@alohamini.local:~/pi4

# on the Pi
bash ~/pi4/install_pi4.sh
sudo reboot            # applies the dialout group
```

The installer finishes by importing torch. **On a Pi 4 this is the one step that can fail with `Illegal instruction`:** some PyTorch aarch64 wheels use LSE atomic instructions that the Pi 4's Cortex-A72 lacks. It bit torch 2.4.0 and 2.6.0 (pytorch issue 132032; lerobot issue 1738 was exactly this on a Pi 4). The repo pins torch 2.7–2.11 and nobody has confirmed those on a Pi 4. If it dies, pin a different CPU build and rerun the installer:

```bash
pip install --no-cache-dir --force-reinstall "torch==2.7.1" "torchvision==0.22.1"   # or try 2.8.x / 2.9.x
```

After reboot, every Pi command below assumes:

```bash
conda activate lerobot_alohamini
cd ~/lerobot_alohamini
```

---

## 4. Give the devices fixed names (udev)

The code opens `/dev/am_arm_follower_left`, `/dev/am_arm_follower_right` and `/dev/am_camera_<name>`. `ttyACM0/1` and `video0/2/4…` change between boots, so create udev aliases once. The generator keys **boards by USB serial number** (stable in any port) and **cameras by USB port path** (identical cameras have no serial — so always plug each camera back into the same hub socket).

```bash
# on the Pi — start with boards and cameras UNPLUGGED, plug each one in when asked
bash ~/pi4/make_udev_rules.sh
ls -l /dev/am_*
```

Which board is "left"? The one with **two** servo cables (arm chain + the 90 cm cable to the base). If you get it backwards the host will fail to find motors 8–11 on the right bus — just swap the two serials in `/etc/udev/rules.d/90-alohamini.rules` and run `sudo udevadm control --reload-rules && sudo udevadm trigger`.

Camera names used by the code → physical camera (my mapping; only consistency matters):

| udev / config name | AlohaMini camera |
|---|---|
| `forward` | top camera on the post (looks forward/down over the workspace) |
| `chest` | front camera lower on the post |
| `backward` | back camera |
| `wrist_left`, `wrist_right` | the two arm cameras |

---

## 5. Turn cameras on in the config (and use MJPG)

`src/lerobot/robots/alohamini/config_alohamini.py` on the Pi enables only `forward` and `wrist_right` by default. **Start with those two.** Uncomment more once the loop is stable. Add `fourcc="MJPG"` to each camera. Without it OpenCV negotiates uncompressed YUYV, which at 640×480×30 is about **147 Mbit/s per camera**: two cameras already exceed the Pi 4's single 480 Mbit/s USB 2.0 bus and the frame rate sags silently. MJPG is about **9 Mbit/s per camera**, so all five fit (~45 Mbit/s). Upstream LeRobot pinned MJPG for LeKiwi in July 2026 (issue 4082); the AlohaMini fork has not, so add it yourself.

```python
def alohamini_cameras_config() -> dict[str, CameraConfig]:
    return {
        "forward": OpenCVCameraConfig(
            index_or_path="/dev/am_camera_forward", fps=30, width=640, height=480,
            rotation=Cv2Rotation.NO_ROTATION, fourcc="MJPG",
        ),
        "wrist_right": OpenCVCameraConfig(
            index_or_path="/dev/am_camera_wrist_right", fps=30, width=640, height=480,
            rotation=Cv2Rotation.NO_ROTATION, fourcc="MJPG",
        ),
        # add "wrist_left", "chest", "backward" the same way when you want them
    }
```

Check a camera really offers MJPG 640×480 @ 30 before trusting it:

```bash
v4l2-ctl -d /dev/am_camera_forward --list-formats-ext | head -30
lerobot-find-cameras
```

---

## 6. Calibrate

**Follower arms + base + lift — on the Pi** (once; the host also prompts if the file is missing). Put each joint at its mid position (see `examples/alohamini/media/mid_position_so100.png`), Enter, then rotate each joint ~90° each way, Enter.

```bash
python -m lerobot.robots.alohamini.alohamini_calibrate --robot_model alohamini1
```

**Leader arms — on the Mac.** First find which `/dev/cu.usbmodem…` is which arm. The names contain each board's serial, so they are stable per board — do this once:

```bash
ls /dev/cu.usbmodem*          # unplug one leader, run again, the missing one is that arm
```

Then calibrate (same procedure, Pi does not need to be running):

```bash
conda activate lerobot_alohamini
cd "/Users/skyler/Projects/research/Robotics/Aloha Mini/lerobot_alohamini"
python examples/alohamini/calibrate_bi.py \
  --teleop.id so101_leader_bi \
  --teleop.arm_profile so-arm-5dof \
  --teleop.left_port  /dev/cu.usbmodemLEFTSERIAL \
  --teleop.right_port /dev/cu.usbmodemRIGHTSERIAL
```

Power-cycle both leader and follower arms after calibrating (upstream says the new values only take effect after that).

---

## 7. Teleoperate

**⚠ Lift homing:** every time the host connects it drives the lift **down to its hard stop** to zero itself. Keep hands and objects clear of the lift path before starting.

**Pi (host) — start this first:**

```bash
python -m lerobot.robots.alohamini.alohamini_host --robot_model alohamini1
# add --profile_timing to print per-second host/motor/camera/JPEG/network timings
```

**Mac (client):**

```bash
conda activate lerobot_alohamini
cd "/Users/skyler/Projects/research/Robotics/Aloha Mini/lerobot_alohamini"
python examples/alohamini/teleoperate_bi.py \
  --robot.remote_ip 192.168.1.42 \
  --robot.robot_model alohamini1 \
  --teleop.id so101_leader_bi \
  --teleop.arm_profile so-arm-5dof \
  --teleop.left_port  /dev/cu.usbmodemLEFTSERIAL \
  --teleop.right_port /dev/cu.usbmodemRIGHTSERIAL \
  --fps 50 --camera-fps 30
```

A **Rerun** viewer window opens on the Mac with the camera feeds and joint plots — that is your operator view. Arms follow the leaders; base and lift are keyboard:

| Key | Action | Key | Action |
|---|---|---|---|
| **W / S** | drive forward / back | **A / D** | rotate left / right |
| **Z / X** | strafe left / right | **T / G** | speed up / down (3 levels) |
| **U / J** | lift up / down (held) | **Q** | quit |

macOS gotcha: keyboard capture uses `pynput`, which needs **System Settings → Privacy & Security → Input Monitoring** enabled for your terminal app, or the base/lift keys do nothing.

Useful partial modes while bringing things up:

```bash
# base + lift only, no arms:   Pi: --no_follower      Mac: --no_leader
# leaders only, no robot:      Mac: --no_robot
```

---

## 8. Make the robot always-on (no SSH each time)

Run the host manually once so calibration is done, then install the service so the Pi starts the host at boot and restarts it if it exits (it exits by itself after `connection_time_s` = 6000 s):

```bash
# on the Pi
sudo cp ~/pi4/alohamini-host.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now alohamini-host
journalctl -u alohamini-host -f
```

Optional: in `config_alohamini.py` set `connection_time_s: int = 360000` so the host doesn't recycle (and re-home the lift) every 100 minutes.

---

## 9. Remote over the internet (Tailscale)

Same commands, different IP. Tailscale is already installed on this Mac (it was signed out — open Tailscale.app and sign in).

```bash
# on the Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up            # open the printed URL, sign in with the same account
tailscale ip -4              # e.g. 100.101.102.103

# on the Mac
tailscale status             # should list alohamini; the path should say "direct", not "relay"
```

Then `--robot.remote_ip 100.101.102.103` (or just `alohamini` with MagicDNS). SSH works the same way: `ssh pi@alohamini`.

Bandwidth: each camera is roughly 40 KB per JPEG at quality 70, so at 30 fps two cameras ≈ 20 Mbit/s **upload from the robot's WiFi**; five cameras ≈ 50 Mbit/s. Over the internet use `--camera-fps 10` (2 cams ≈ 7 Mbit/s). Control packets are tiny; latency is what you feel, and the base stops itself if no command arrives for 1 s (watchdog).

Nobody has published LeRobot ZMQ teleop over Tailscale, but the client only does a plain TCP connect to whatever IP you give it, so nothing else changes. Two timeouts bite on a slow path: the host halts motion after 1 s without a command, and the client's observation poll gives up after 200 ms. If you see stalls, confirm `tailscale status` shows a direct path and drop to `--fps 10 --camera-fps 10` while debugging.

---

## 10. What to expect from a Pi 4

- The 50 Hz control loop is bound by the servo bus (a handful of sync reads/writes over two 1 Mbaud links per cycle), not the CPU. A Pi 4 should hold it with two cameras; JPEG encoding runs in a thread pool.
- With all five cameras expect to lower `--camera-fps` to 15 and/or drop `max_loop_freq_hz` in `AlohaMiniHostConfig` from 50 to 30 if the arms jitter. Watch `top` and `--profile_timing`.
- Use 5 GHz WiFi on the Pi (`iw dev wlan0 link`), and `iperf3 -s` on the Pi / `iperf3 -c <pi>` on the Mac to check the link.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Timeout waiting for AlohaMini Host to connect expired` on the Mac | Host not running, wrong IP, or Mac and Pi not on the same network. `ping <pi_ip>`; check ports 5555/5556 aren't firewalled. |
| `/dev/am_arm_follower_left: No such file` | udev rule missing or board unplugged. `ls -l /dev/am_*`, rerun `make_udev_rules.sh`. |
| Permission denied on `/dev/ttyACM*` | Not in `dialout` yet — reboot after `install_pi4.sh`. |
| Host can't find motors 8–11 | Left/right boards swapped in the udev rules (left = the board with the base cable). |
| Camera opens but 5–10 fps, or "failed to set fourcc" | YUYV fallback / hub saturation. Confirm MJPG with `v4l2-ctl --list-formats-ext`; fewer cameras per hub; powered hub. |
| Lightning-bolt icon / `get_throttled` ≠ 0x0 | Under-voltage. Buck to 5.1 V, shorter/thicker cable, powered hub for cameras. |
| Base/lift keys ignored on the Mac | Grant Input Monitoring to the terminal app (pynput). |
| Arms twitch / jitter | Lower `--camera-fps`, then `max_loop_freq_hz`; check `--profile_timing`; check servo battery. |
| Lift slams on start | Expected homing move — clear the path. Set `connection_time_s` high so it doesn't repeat every 100 min. |
| Mac `import lerobot` fails | Wrong env: `conda activate lerobot_alohamini` (not `lerobot`). |
| `Illegal instruction` on the Pi for any lerobot command | torch wheel uses LSE atomics the Cortex-A72 lacks. `pip install --force-reinstall "torch==2.7.1" "torchvision==0.22.1"` (or another version) and retry. |
| Boards appear as `/dev/ttyCH343USB0`, not `ttyACM` | WCH vendor driver installed. Remove it; the kernel cdc-acm driver is the right one. |
| Board powered but no `/dev/ttyACM*` | Waveshare jumper in UART (A). Move it to USB (B). Also check the USB-C cable carries data. |
| Red power LED off or flickering | Under-voltage. Same fix as the lightning bolt. |

---

## 12. Files in this folder

| File | What |
|---|---|
| `pi4/install_pi4.sh` | One-shot Pi 4 installer (apt, dialout, Miniforge ARM64, py3.12 env, repo, extras). |
| `pi4/make_udev_rules.sh` | Interactive generator for `/etc/udev/rules.d/90-alohamini.rules` (boards by serial, cameras by port). |
| `pi4/alohamini-host.service` | systemd unit: host at boot, auto-restart. |
| `lerobot_alohamini/` | Your clone, now at upstream `main` + the two `--teleop.*_port` patches (uncommitted; `git diff` shows them). |
| `find_arms_simple.sh` | Old arm identifier, repointed at the new env (its port list is the April one — edit if boards changed). |

Upstream docs the above is built on: `lerobot_alohamini/docs/alohamini/{install,alohamini,commands,profiles}.md`.
