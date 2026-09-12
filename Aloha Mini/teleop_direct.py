#!/usr/bin/env python
"""
Direct leader -> follower teleop for one SO-101 arm pair, both plugged into this Mac.
No Pi, no ZMQ, no calibration files: raw servo ticks are mirrored 1:1
(both arms use the SO-101 convention "2048 = middle of range").

    python teleop_direct.py --leader /dev/cu.usbmodem5AE60833451 --follower /dev/cu.usbmodem5AE60551511

Safety built in:
  * torque is enabled ONLY on follower arm IDs 1-6 (base wheels 8-10 are never touched)
  * follower servo Acceleration + Goal_Velocity are capped (slow, smooth moves)
  * soft start: the follower ramps from where it is to the leader pose over --ramp seconds
  * per-cycle step clamp (--max-step ticks) and per-joint position limits
  * Ctrl-C (or any error) disables follower torque before exiting
  * refuses to run if the follower bus is under-volted unless --allow-low-voltage

Options:
  --flip JOINT        invert this joint (leader tick delta is mirrored around 2048)
  --offset JOINT=N    add N ticks to this follower joint
  --hz 50             loop rate
"""
from __future__ import annotations

import argparse
import math
import sys
import time

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MID = 2048
DEG = 4096 / 360.0
# conservative software limits (ticks), derived from the SO-101 MJCF joint ranges around 2048
LIMITS = {
    "shoulder_pan":  (MID - int(110 * DEG), MID + int(110 * DEG)),
    "shoulder_lift": (MID - int(100 * DEG), MID + int(100 * DEG)),
    "elbow_flex":    (MID - int(97 * DEG),  MID + int(97 * DEG)),
    "wrist_flex":    (MID - int(95 * DEG),  MID + int(95 * DEG)),
    "wrist_roll":    (MID - int(157 * DEG), MID + int(157 * DEG)),
    "gripper":       (MID - int(10 * DEG),  MID + int(100 * DEG)),
}


def make_bus(port: str) -> FeetechMotorsBus:
    motors = {j: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, j in enumerate(JOINTS)}
    bus = FeetechMotorsBus(port=port, motors=motors)
    bus.connect(handshake=True)
    return bus


def volts(bus: FeetechMotorsBus) -> float:
    return bus.read("Present_Voltage", JOINTS[0], normalize=False) / 10.0


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leader", required=True)
    ap.add_argument("--follower", required=True)
    ap.add_argument("--hz", type=float, default=50.0)
    ap.add_argument("--ramp", type=float, default=6.0, help="seconds for the soft start")
    ap.add_argument("--max-step", type=int, default=40, help="max follower move per cycle, ticks (40 ≈ 3.5°)")
    ap.add_argument("--accel", type=int, default=20, help="servo Acceleration register (0-254, lower = gentler)")
    ap.add_argument("--speed", type=int, default=800, help="servo Goal_Velocity cap, ticks/s (800 ≈ 70°/s)")
    ap.add_argument("--flip", action="append", default=[], choices=JOINTS)
    ap.add_argument("--offset", action="append", default=[], metavar="JOINT=TICKS")
    ap.add_argument("--allow-low-voltage", action="store_true")
    ap.add_argument("--wait-for-power", action="store_true",
                    help="if the follower bus is under 9 V, poll until the 12 V supply appears, then start")
    ap.add_argument("--dry-run", action="store_true", help="never enable torque; only print what would be sent")
    args = ap.parse_args()

    offsets = {j: 0 for j in JOINTS}
    for spec in args.offset:
        j, n = spec.split("=")
        offsets[j] = int(n)
    sign = {j: (-1 if j in args.flip else 1) for j in JOINTS}

    leader = make_bus(args.leader)
    follower = make_bus(args.follower)
    vl, vf = volts(leader), volts(follower)
    print(f"[leader]   {args.leader}  bus {vl:.1f} V")
    print(f"[follower] {args.follower}  bus {vf:.1f} V")
    if vf < 9.0 and args.wait_for_power and not args.dry_run:
        print(f"[wait] follower bus is {vf:.1f} V — waiting for the robot's 12 V supply to be switched on ...", flush=True)
        while vf < 9.0:
            time.sleep(2.0)
            try:
                vf = volts(follower)
            except Exception as e:
                print(f"[wait] read failed ({e}); retrying", flush=True)
        print(f"[wait] follower bus now {vf:.1f} V — starting in 3 s", flush=True)
        time.sleep(3.0)
    if vf < 9.0 and not args.allow_low_voltage and not args.dry_run:
        print(f"!! follower bus is {vf:.1f} V. Its 12 V STS3215 servos will not hold torque on USB power.\n"
              f"!! Turn on the robot's battery / 12 V supply, or re-run with --allow-low-voltage to try anyway.")
        leader.disconnect(disable_torque=False); follower.disconnect(disable_torque=False)
        sys.exit(2)

    def target_from_leader(raw: dict[str, int]) -> dict[str, int]:
        t = {}
        for j in JOINTS:
            v = MID + sign[j] * (raw[j] - MID) + offsets[j]
            lo, hi = LIMITS[j]
            t[j] = int(clamp(v, lo, hi))
        return t

    leader.disable_torque()  # leader must stay free to move by hand
    goal = follower.sync_read("Present_Position", normalize=False)
    start_pose = dict(goal)
    first_target = target_from_leader(leader.sync_read("Present_Position", normalize=False))
    print("\ninitial follower -> leader deltas:")
    for j in JOINTS:
        d = first_target[j] - start_pose[j]
        print(f"  {j:>14}: follower {start_pose[j]:>5} -> target {first_target[j]:>5}   ({d:+5d} ticks, {d/DEG:+6.1f}°)")

    if args.dry_run:
        print("\n[dry-run] torque NOT enabled; exiting.")
        leader.disconnect(disable_torque=False); follower.disconnect(disable_torque=False)
        return

    # gentle servo-side limits, then torque on (arm joints only)
    for j in JOINTS:
        follower.write("Acceleration", j, args.accel)
        follower.write("Goal_Velocity", j, args.speed)
    follower.enable_torque()
    print(f"\n[teleop] torque ON (follower IDs 1-6). soft start {args.ramp:.0f}s, then live at {args.hz:.0f} Hz. Ctrl-C to stop.\n")

    period = 1.0 / args.hz
    t_start = time.time()
    last_log = 0.0
    try:
        while True:
            t0 = time.time()
            raw = leader.sync_read("Present_Position", normalize=False)
            tgt = target_from_leader(raw)
            alpha = min(1.0, (t0 - t_start) / args.ramp)
            new_goal = {}
            for j in JOINTS:
                blended = start_pose[j] + alpha * (tgt[j] - start_pose[j])  # soft start
                step = clamp(blended - goal[j], -args.max_step, args.max_step)
                new_goal[j] = int(goal[j] + step)
            goal = new_goal
            follower.sync_write("Goal_Position", goal, normalize=False)

            if t0 - last_log >= 1.0:
                pres = follower.sync_read("Present_Position", normalize=False)
                err = max(abs(pres[j] - goal[j]) for j in JOINTS)
                vf = volts(follower)
                print(f"\r[{t0 - t_start:6.1f}s] ramp {alpha*100:3.0f}%  follower {vf:.1f}V  max track err {err:4d} ticks ({err/DEG:4.1f}°)  "
                      + " ".join(f"{j[:5]}={goal[j]}" for j in JOINTS), end="", flush=True)
                last_log = t0

            dt = period - (time.time() - t0)
            if dt > 0:
                time.sleep(dt)
    except KeyboardInterrupt:
        print("\n[teleop] stopping")
    finally:
        try:
            follower.disable_torque()
        finally:
            follower.disconnect(disable_torque=True)
            leader.disconnect(disable_torque=False)
        print("[teleop] follower torque OFF, ports closed")


if __name__ == "__main__":
    main()
