#!/bin/bash

# Simple arm identification script
# Tests each USB port and asks user which arm moved

PYTHON=$HOME/miniforge3/envs/lerobot_alohamini/bin/python3

PORTS=(
  "/dev/cu.usbmodem5AE60529891"
  "/dev/cu.usbmodem5AE60551511"
  "/dev/cu.usbmodem5AE60554691"
  "/dev/cu.usbmodem5AE60833451"
)

echo "============================================"
echo "AlohaMini Arm Identifier"
echo "============================================"
echo ""
echo "All 4 arms detected:"
for i in "${!PORTS[@]}"; do
  echo "  Port $i: ${PORTS[$i]}"
done
echo ""
echo "============================================"
echo "INSTRUCTIONS:"
echo "1. Make sure all 4 arms are powered"
echo "2. Watch which arm becomes stiffer when tested"
echo "3. Record which arm corresponds to each port"
echo "============================================"
echo ""

declare -A ARM_MAP

for i in "${!PORTS[@]}"; do
  PORT="${PORTS[$i]}"
  echo ""
  echo "=========================================="
  echo "Testing Port $i: $PORT"
  echo "=========================================="

  read -p "Press Enter to test this port..."

  # Test the port by trying to connect
  $PYTHON -c "
import serial
import time
try:
    ser = serial.Serial('$PORT', baudrate=1000000, timeout=1)
    print('✅ Connected to $PORT')
    print('⚡ One arm should now be stiffer or twitch')
    time.sleep(2)
    ser.close()
    print('Connection closed')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>&1

  echo ""
  echo "Which arm moved/got stiffer?"
  echo "  1 = Leader Left"
  echo "  2 = Leader Right"
  echo "  3 = Follower Left"
  echo "  4 = Follower Right"
  echo "  0 = No arm / Not sure"

  read -p "Enter number (0-4): " choice

  case $choice in
    1) ARM_MAP[$i]="Leader Left" ;;
    2) ARM_MAP[$i]="Leader Right" ;;
    3) ARM_MAP[$i]="Follower Left" ;;
    4) ARM_MAP[$i]="Follower Right" ;;
    *) ARM_MAP[$i]="Unknown" ;;
  esac

  echo "✅ Recorded: Port $i = ${ARM_MAP[$i]}"
done

echo ""
echo "=========================================="
echo "ARM IDENTIFICATION COMPLETE!"
echo "=========================================="
echo ""

LEADER_LEFT=""
LEADER_RIGHT=""
FOLLOWER_LEFT=""
FOLLOWER_RIGHT=""

for i in "${!ARM_MAP[@]}"; do
  echo "Port $i (${PORTS[$i]})"
  echo "  → ${ARM_MAP[$i]}"
  echo ""

  case "${ARM_MAP[$i]}" in
    "Leader Left") LEADER_LEFT="${PORTS[$i]}" ;;
    "Leader Right") LEADER_RIGHT="${PORTS[$i]}" ;;
    "Follower Left") FOLLOWER_LEFT="${PORTS[$i]}" ;;
    "Follower Right") FOLLOWER_RIGHT="${PORTS[$i]}" ;;
  esac
done

echo "=========================================="
echo "CONFIGURATION CODE:"
echo "=========================================="
echo ""
echo "Copy these into your config files:"
echo ""
echo "--- For examples/alohamini/teleoperate_bi.py ---"
if [ -n "$LEADER_LEFT" ] && [ -n "$LEADER_RIGHT" ]; then
  echo "LEADER_PORT_LEFT = \"$LEADER_LEFT\""
  echo "LEADER_PORT_RIGHT = \"$LEADER_RIGHT\""
else
  echo "⚠️  Leader ports not fully identified!"
fi

echo ""
echo "--- For lerobot/robots/alohamini/config_lekiwi.py ---"
if [ -n "$FOLLOWER_LEFT" ] && [ -n "$FOLLOWER_RIGHT" ]; then
  echo "FOLLOWER_PORT_LEFT = \"$FOLLOWER_LEFT\""
  echo "FOLLOWER_PORT_RIGHT = \"$FOLLOWER_RIGHT\""
else
  echo "⚠️  Follower ports not fully identified!"
fi

echo ""
echo "=========================================="
