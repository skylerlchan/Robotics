#!/usr/bin/env python3
"""Quick test to see which arm responds to which port"""

import sys
import time

try:
    from feetech_servo_sdk import SyncReadWrite
except ImportError:
    print("ERROR: feetech-servo-sdk not installed!")
    sys.exit(1)

# Your detected ports
PORTS = [
    "/dev/cu.usbmodem5AE60529891",
    "/dev/cu.usbmodem5AE60551511",
    "/dev/cu.usbmodem5AE60554691",
    "/dev/cu.usbmodem5AE60833451",
]

if len(sys.argv) < 2:
    print("Usage: python3 test_port.py <port_number>")
    print(f"\nAvailable ports:")
    for i, port in enumerate(PORTS):
        print(f"  {i}: {port}")
    print("\nExample: python3 test_port.py 0")
    sys.exit(1)

port_index = int(sys.argv[1])
if port_index < 0 or port_index >= len(PORTS):
    print(f"ERROR: Port index must be between 0 and {len(PORTS)-1}")
    sys.exit(1)

port = PORTS[port_index]

print(f"Testing port {port_index}: {port}")
print("👀 WATCH YOUR ARMS - one should become stiffer or twitch slightly...")

try:
    bus = SyncReadWrite(port, baudrate=1000000)
    print("✅ Connected!")
    print("⚡ The arm on this port should now feel different (stiffer)")
    time.sleep(3)
    bus.close()
    print("✅ Test complete - connection closed")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
