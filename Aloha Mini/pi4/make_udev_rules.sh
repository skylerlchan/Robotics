#!/usr/bin/env bash
# Interactive udev rule generator for the AlohaMini host (Raspberry Pi).
# Produces /etc/udev/rules.d/90-alohamini.rules so the code's fixed names exist:
#   /dev/am_arm_follower_left   /dev/am_arm_follower_right
#   /dev/am_camera_forward  /dev/am_camera_backward  /dev/am_camera_chest
#   /dev/am_camera_wrist_left  /dev/am_camera_wrist_right
#
# Arms   are keyed by the Waveshare board's USB serial number  (stable no matter which port).
# Cameras are keyed by the USB port path they are plugged into (identical cameras have no unique serial),
#         so ALWAYS plug each camera back into the same physical port / hub socket.
#
# Usage: start with everything UNPLUGGED, run:  bash make_udev_rules.sh
#        then plug devices in one at a time when prompted.
set -euo pipefail

RULES=/etc/udev/rules.d/90-alohamini.rules
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

list_tty()   { ls /dev/ttyACM* 2>/dev/null | sort || true; }
list_video() {
  # only capture nodes (index 0); metadata nodes have index 1
  local v idx
  for v in /dev/video*; do
    if [ -e "$v" ]; then
      idx=$(cat "/sys/class/video4linux/$(basename "$v")/index" 2>/dev/null || echo 9)
      if [ "$idx" = "0" ]; then echo "$v"; fi
    fi
  done | sort
  return 0
}
serial_of() { udevadm info --attribute-walk --name="$1" | awk -F'"' '/ATTRS\{serial\}/{print $2; exit}'; }
usbport_of() {
  # e.g. .../usb1/1-1/1-1.3/1-1.3:1.0/video4linux/video0  ->  1-1.3
  udevadm info -q path -n "$1" | sed -E 's#.*/([0-9]+-[0-9.]+):[0-9.]+/.*#\1#'
}
wait_new() { # $1 = list function; prints the newly appeared device
  local before after new
  before=$($1)
  read -r -p "   >>> plug it in now, wait 3 s, then press Enter " _
  sleep 1
  after=$($1)
  new=$(comm -13 <(echo "$before") <(echo "$after") | head -n1)
  echo "$new"
}

echo "# AlohaMini fixed device names — generated $(date -Is) by make_udev_rules.sh" > "$TMP"
echo "# Reload with: sudo udevadm control --reload-rules && sudo udevadm trigger" >> "$TMP"
echo >> "$TMP"

echo "=============================================================="
echo " ARMS (Waveshare Bus Servo Adapter boards)  — keyed by serial"
echo "=============================================================="
for side in left right; do
  echo
  echo "== FOLLOWER $side arm board (the one whose servo chain is the $side arm; the LEFT one also carries wheels 8/9/10 + lift 11)"
  dev=$(wait_new list_tty)
  if [ -z "$dev" ]; then echo "   !! no new /dev/ttyACM* appeared — skipping $side"; continue; fi
  ser=$(serial_of "$dev")
  echo "   found $dev  serial=$ser"
  if [ -z "$ser" ]; then echo "   !! no serial attribute — cannot key this board by serial"; continue; fi
  echo "SUBSYSTEM==\"tty\", ATTRS{serial}==\"$ser\", SYMLINK+=\"am_arm_follower_$side\", MODE=\"0666\", ENV{ID_MM_DEVICE_IGNORE}=\"1\"" >> "$TMP"
done

echo
echo "=============================================================="
echo " CAMERAS — keyed by USB port path (plug each into its permanent port)"
echo "=============================================================="
for cam in forward backward chest wrist_left wrist_right; do
  echo
  read -r -p "== camera '$cam': add it? [Y/n] " yn
  case "${yn:-Y}" in [nN]*) continue;; esac
  dev=$(wait_new list_video)
  if [ -z "$dev" ]; then echo "   !! no new /dev/video* capture node appeared — skipping $cam"; continue; fi
  port=$(usbport_of "$dev")
  name=$(cat "/sys/class/video4linux/$(basename "$dev")/name" 2>/dev/null || echo "?")
  echo "   found $dev  usb-port=$port  ($name)"
  echo "SUBSYSTEM==\"video4linux\", KERNELS==\"$port\", ATTR{index}==\"0\", SYMLINK+=\"am_camera_$cam\"" >> "$TMP"
done

echo
echo "------------------ generated rules ------------------"
cat "$TMP"
echo "-----------------------------------------------------"
read -r -p "Write to $RULES and reload udev? [Y/n] " yn
case "${yn:-Y}" in [nN]*) echo "not written (copy from above if you want)"; exit 0;; esac
sudo cp "$TMP" "$RULES"
sudo udevadm control --reload-rules
sudo udevadm trigger
sleep 1
echo
echo "Stable names now present:"
ls -l /dev/am_* 2>/dev/null || echo "(none yet — unplug/replug the devices once, or reboot)"
