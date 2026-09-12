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
    ap.add_argument("--fast", action="store_true",
                    help="low-latency profile: 100 Hz loop, servo speed cap 3000 ticks/s, accel 60, max-step 80")
    args = ap.parse_args()
    if args.fast:
        args.hz, args.speed, args.accel, args.max_step = 100.0, 3000, 60, 80

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

    # tighten software limits with the follower's own calibrated servo limits
    for j in JOINTS:
        try:
            mn = follower.read("Min_Position_Limit", j, normalize=False)
            mx = follower.read("Max_Position_Limit", j, normalize=False)
            if 0 < mn < mx < 4096:
                lo, hi = LIMITS[j]
                LIMITS[j] = (max(lo, mn), min(hi, mx))
        except Exception as e:
            print(f"[limits] could not read servo limits for {j}: {e}")
    print("[limits] follower clamp (ticks): " + " ".join(f"{j[:5]}=[{LIMITS[j][0]},{LIMITS[j][1]}]" for j in JOINTS))

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

    def arm_follower(bus: FeetechMotorsBus, hold: dict[str, int]) -> None:
        """Set gentle limits, then enable torque one joint at a time (staggers the 12 V inrush)."""
        for j in JOINTS:
            bus.write("Acceleration", j, args.accel)
            bus.write("Goal_Velocity", j, args.speed)
            bus.write("Goal_Position", j, hold[j], normalize=False)   # hold where it is
            bus.enable_torque(j)
            time.sleep(0.15)
        # verify the bus survived torque-on
        for attempt in range(5):
            try:
                pres = bus.sync_read("Present_Position", normalize=False)
                te = [bus.read("Torque_Enable", j, normalize=False) for j in JOINTS]
                print(f"[teleop] torque-on verified: enable={te}  volts={volts(bus):.1f}", flush=True)
                return
            except Exception as e:
                print(f"[teleop] post-torque check failed ({attempt+1}/5): {e}", flush=True)
                time.sleep(0.5)
        raise ConnectionError("follower bus not answering after torque-on")

    arm_follower(follower, goal)
    print(f"\n[teleop] torque ON (follower IDs 1-6). soft start {args.ramp:.0f}s, then live at {args.hz:.0f} Hz. Ctrl-C to stop.\n")

    period = 1.0 / args.hz
    t_start = time.time()
    last_log = 0.0
    fails = 0
    MAX_FAILS = 10
    stats = {k: [] for k in ("rd_lead", "rd_fol", "wr", "period", "lag", "vel")}
    prev_raw, prev_t, last_cycle = None, 0.0, None          # consecutive bad cycles before we drop the ports and reconnect

    def reconnect():
        nonlocal leader, follower, goal, start_pose, t_start, fails, prev_raw, last_cycle
        print("\n[teleop] bus dropout — closing ports, waiting for the boards to come back ...", flush=True)
        for b in (leader, follower):
            try: b.port_handler.closePort()
            except Exception: pass
        while True:
            time.sleep(2.0)
            try:
                leader = make_bus(args.leader)
                follower = make_bus(args.follower)
                vf = volts(follower)
                if vf < 9.0:
                    print(f"[teleop] follower back but only {vf:.1f} V — waiting for 12 V", flush=True)
                    leader.port_handler.closePort(); follower.port_handler.closePort()
                    continue
                leader.disable_torque()
                goal = follower.sync_read("Present_Position", normalize=False)
                start_pose = dict(goal)
                arm_follower(follower, goal)
                t_start = time.time()      # soft-start again from wherever the follower is now
                fails = 0
                prev_raw, last_cycle = None, None
                print(f"[teleop] reconnected ({vf:.1f} V); soft start {args.ramp:.0f}s", flush=True)
                return
            except Exception as e:
                print(f"[teleop] reconnect attempt failed: {e}", flush=True)
                for b in (leader, follower):
                    try: b.port_handler.closePort()
                    except Exception: pass

    try:
        while True:
            t0 = time.time()
            try:
                t_r0 = time.perf_counter()
                raw = leader.sync_read("Present_Position", normalize=False)
                t_r1 = time.perf_counter()
                pres = follower.sync_read("Present_Position", normalize=False)
                t_r2 = time.perf_counter()
                stats["rd_lead"].append((t_r1 - t_r0) * 1e3)
                stats["rd_fol"].append((t_r2 - t_r1) * 1e3)
                # motion-lag estimate: how far the follower trails the leader, in time, on the fastest joint
                if prev_raw is not None:
                    dt_l = t0 - prev_t
                    vel = {j: (raw[j] - prev_raw[j]) / dt_l for j in JOINTS}
                    jf = max(JOINTS, key=lambda j: abs(vel[j]))
                    if abs(vel[jf]) > 150:  # ticks/s (~13°/s) — only when the leader is really moving
                        tgt_now = target_from_leader(raw)[jf]
                        lag_s = (tgt_now - pres[jf]) / (sign[jf] * vel[jf])
                        stats["lag"].append(max(0.0, min(lag_s, 2.0)) * 1e3)
                        stats["vel"].append(abs(vel[jf]) / DEG)
                prev_raw, prev_t = raw, t0
                tgt = target_from_leader(raw)
                alpha = min(1.0, (t0 - t_start) / args.ramp)
                new_goal = {}
                for j in JOINTS:
                    blended = start_pose[j] + alpha * (tgt[j] - start_pose[j])  # soft start
                    step = clamp(blended - goal[j], -args.max_step, args.max_step)
                    new_goal[j] = int(goal[j] + step)
                t_w0 = time.perf_counter()
                follower.sync_write("Goal_Position", new_goal, normalize=False)
                stats["wr"].append((time.perf_counter() - t_w0) * 1e3)
                goal = new_goal
                fails = 0
                if last_cycle is not None:
                    stats["period"].append((t0 - last_cycle) * 1e3)
                last_cycle = t0

                if t0 - last_log >= 1.0:
                    jw = max(JOINTS, key=lambda j: abs(pres[j] - goal[j]))
                    err = abs(pres[jw] - goal[jw])
                    vf = volts(follower)
                    med = lambda k: (sorted(stats[k])[len(stats[k]) // 2] if stats[k] else float("nan"))
                    mx = lambda k: (max(stats[k]) if stats[k] else float("nan"))
                    lag_txt = (f"lag~{med('lag'):4.0f}ms (max {mx('lag'):4.0f}) @{med('vel'):3.0f}°/s"
                               if stats["lag"] else "lag: leader idle")
                    print(f"[{t0 - t_start:6.1f}s] ramp {alpha*100:3.0f}%  {vf:.1f}V  err {err:3d}t ({err/DEG:4.1f}° {jw[:6]})  "
                          f"loop {med('period'):5.1f}ms (max {mx('period'):5.1f})  rdL {med('rd_lead'):4.1f}ms  rdF {med('rd_fol'):4.1f}ms  "
                          f"wr {med('wr'):4.1f}ms  {lag_txt}  | "
                          + " ".join(f"{j[:5]}={goal[j]}" for j in JOINTS), flush=True)
                    for k in stats: stats[k].clear()
                    last_log = t0
            except ConnectionError as e:
                fails += 1
                if fails == 1 or fails % 5 == 0:
                    print(f"[teleop] comm error ({fails}/{MAX_FAILS}): {e}", flush=True)
                if fails >= MAX_FAILS:
                    reconnect()
                    continue

            deadline = t0 + period
            slack = deadline - time.time() - 0.006   # macOS coalesces background timers: sleep overshoots ~4 ms, so spin the tail
            if slack > 0:
                time.sleep(slack)
            while time.time() < deadline:
                pass
    except KeyboardInterrupt:
        print("\n[teleop] stopping")
    finally:
        for attempt in range(3):
            try:
                follower.disable_torque()
                break
            except Exception as e:
                print(f"[teleop] torque-off retry {attempt+1}/3: {e}", flush=True)
                time.sleep(0.3)
        for b, dis in ((follower, True), (leader, False)):
            try: b.disconnect(disable_torque=dis)
            except Exception:
                try: b.port_handler.closePort()
                except Exception: pass
        print("[teleop] follower torque OFF (best effort), ports closed", flush=True)


if __name__ == "__main__":
    main()
