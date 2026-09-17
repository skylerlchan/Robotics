#!/usr/bin/env python
"""Non-destructive register dump of every connected bus board. Never enables torque.

    python probe.py                      # every /dev/cu.usbmodem* board
    python probe.py /dev/cu.usbmodemXXX  # just this one

Use it to tell a leader from a follower (bus voltage), to confirm both arms are
calibrated in-servo (non-zero Homing_Offset, custom Min/Max), and to see where
the arms are sitting before enabling torque.
"""
from __future__ import annotations

import sys

from ports import DEG, MID, devices, serial_of

JOINT_NAMES = {1: "shoulder_pan", 2: "shoulder_lift", 3: "elbow_flex", 4: "wrist_flex",
               5: "wrist_roll", 6: "gripper", 8: "base_left", 9: "base_back",
               10: "base_right", 11: "lift"}


def dump(device: str) -> None:
    from lerobot.motors import Motor, MotorNormMode
    from lerobot.motors.feetech import FeetechMotorsBus

    print(f"\n=== {device}  (serial {serial_of(device)}) ===", flush=True)
    motors = {f"id{i}": Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i in range(1, 12)}
    bus = FeetechMotorsBus(port=device, motors=motors)
    try:
        bus.connect(handshake=False)
    except Exception as e:
        print(f"  !! could not open port: {e}")
        return
    try:
        ids = sorted((bus.broadcast_ping(num_retry=2) or {}))
        if not ids:
            print("  no servos answered (board enumerated but bus silent — arm unpowered?)")
            return
        volts = bus.read("Present_Voltage", f"id{ids[0]}", normalize=False) / 10.0
        role = "FOLLOWER (12 V supply on)" if volts >= 9.0 else "LEADER (USB-powered)"
        if any(i >= 8 for i in ids):
            role += " + base/lift IDs present"
        print(f"  servos {ids}   bus {volts:.1f} V  ->  {role}")
        print(f"  {'id':>3} {'joint':>14} {'pos':>6} {'deg':>7} {'homing':>7} {'min':>5} {'max':>5} {'torque':>6}")
        for i in ids:
            name = f"id{i}"
            try:
                pos = bus.read("Present_Position", name, normalize=False)
                print(f"  {i:>3} {JOINT_NAMES.get(i, '?'):>14} {pos:>6} {(pos - MID) / DEG:>+7.1f} "
                      f"{bus.read('Homing_Offset', name, normalize=False):>7} "
                      f"{bus.read('Min_Position_Limit', name, normalize=False):>5} "
                      f"{bus.read('Max_Position_Limit', name, normalize=False):>5} "
                      f"{bus.read('Torque_Enable', name, normalize=False):>6}")
            except Exception as e:
                print(f"  {i:>3} read failed: {e}")
    finally:
        try:
            bus.disconnect(disable_torque=False)
        except Exception:
            pass


if __name__ == "__main__":
    targets = sys.argv[1:] or devices()
    if not targets:
        sys.exit("no /dev/cu.usbmodem* boards connected")
    for dev in targets:
        dump(dev)
