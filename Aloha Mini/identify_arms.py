#!/usr/bin/env python3
"""
Helper script to identify which USB port connects to which arm.
Run this to test each port and figure out your arm mapping.
"""

import time
import sys

# Check if feetech-servo-sdk is installed
try:
    from feetech_servo_sdk import SyncReadWrite
except ImportError:
    print("ERROR: feetech-servo-sdk not installed!")
    print("Please run: pip install feetech-servo-sdk")
    sys.exit(1)

# Detected ports
PORTS = [
    "/dev/cu.usbmodem5AE60529891",
    "/dev/cu.usbmodem5AE60551511",
    "/dev/cu.usbmodem5AE60554691",
    "/dev/cu.usbmodem5AE60833451",
]

print("=" * 60)
print("AlohaMini Arm Identifier")
print("=" * 60)
print("\nDetected 4 USB ports:")
for i, port in enumerate(PORTS, 1):
    print(f"  Port {i}: {port}")

print("\n" + "=" * 60)
print("INSTRUCTIONS:")
print("=" * 60)
print("1. Make sure ALL 4 arms are powered (batteries connected)")
print("2. Keep ALL 4 USB cables plugged into your Mac")
print("3. Watch all arms closely")
print("4. When you press Enter, one arm will become stiffer/twitch")
print("5. Note which arm reacted")
print("=" * 60)

results = {}

for i, port in enumerate(PORTS, 1):
    print(f"\n\n{'='*60}")
    print(f"Testing Port {i}: {port}")
    print('='*60)

    input(f"\n👀 Press Enter to test Port {i}...")

    try:
        print(f"Opening connection to {port}...")
        bus = SyncReadWrite(port, baudrate=1000000)
        print("✅ Connection established!")
        print("⚡ Arm should now be stiffer or twitched slightly")
        time.sleep(2)
        bus.close()
        print("Connection closed.")

        print(f"\n📝 Which arm reacted?")
        print("   1 = Leader Left")
        print("   2 = Leader Right")
        print("   3 = Follower Left")
        print("   4 = Follower Right")
        print("   0 = No arm reacted / Not sure")

        while True:
            choice = input("\nEnter number (0-4): ").strip()
            if choice in ['0', '1', '2', '3', '4']:
                break
            print("Invalid input! Please enter 0, 1, 2, 3, or 4")

        arm_names = {
            '0': 'Unknown/No reaction',
            '1': 'Leader Left',
            '2': 'Leader Right',
            '3': 'Follower Left',
            '4': 'Follower Right'
        }

        results[port] = arm_names[choice]
        print(f"✅ Recorded: {port} = {arm_names[choice]}")

    except Exception as e:
        print(f"❌ Error connecting to {port}: {e}")
        results[port] = "ERROR - Could not connect"

# Print summary
print("\n\n" + "=" * 60)
print("IDENTIFICATION COMPLETE!")
print("=" * 60)
print("\nYour arm mapping:")
for port, arm in results.items():
    print(f"  {port}")
    print(f"    → {arm}")
    print()

# Generate config snippets
print("\n" + "=" * 60)
print("CONFIGURATION SNIPPETS")
print("=" * 60)

leader_left = None
leader_right = None
follower_left = None
follower_right = None

for port, arm in results.items():
    if arm == "Leader Left":
        leader_left = port
    elif arm == "Leader Right":
        leader_right = port
    elif arm == "Follower Left":
        follower_left = port
    elif arm == "Follower Right":
        follower_right = port

print("\n📝 Copy these lines into your config files:")
print("\n--- For examples/alohamini/teleoperate_bi.py ---")
if leader_left and leader_right:
    print(f'LEADER_PORT_LEFT = "{leader_left}"')
    print(f'LEADER_PORT_RIGHT = "{leader_right}"')
else:
    print("⚠️  Leader arm ports not fully identified!")
    print(f'LEADER_PORT_LEFT = "{leader_left or "UNKNOWN"}"')
    print(f'LEADER_PORT_RIGHT = "{leader_right or "UNKNOWN"}"')

print("\n--- For lerobot/robots/alohamini/config_lekiwi.py ---")
if follower_left and follower_right:
    print(f'FOLLOWER_PORT_LEFT = "{follower_left}"')
    print(f'FOLLOWER_PORT_RIGHT = "{follower_right}"')
else:
    print("⚠️  Follower arm ports not fully identified!")
    print(f'FOLLOWER_PORT_LEFT = "{follower_left or "UNKNOWN"}"')
    print(f'FOLLOWER_PORT_RIGHT = "{follower_right or "UNKNOWN"}"')

print("\n" + "=" * 60)
print("Next steps:")
print("1. Copy the config snippets above")
print("2. Edit the config files with the correct ports")
print("3. Run the teleoperation scripts!")
print("=" * 60)
