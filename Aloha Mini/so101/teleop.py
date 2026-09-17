#!/usr/bin/env python
"""Raw-tick leader -> follower teleop for the SO-101 pair. The fast path: no
calibration files, no ZMQ, no Pi — Present_Position ticks are mapped straight
across (both arms use the SO-101 convention "2048 = middle of range").

    python teleop.py                 # ports and tuning come from arms.toml
    python teleop.py --fast          # 100 Hz, higher servo speed/accel caps
    python teleop.py --dry-run       # show the mapping, never enable torque

Supersedes ../teleop_direct.py (kept frozen as the known-good fallback). What is
new here: ports resolve themselves from arms.toml, and each joint can use a
range->range map instead of a plain tick copy — needed when the two arms were
calibrated to different servo limits, as this pair's grippers were.

Safety (unchanged from the proven script):
  * torque is enabled ONLY on follower IDs 1-6, one joint at a time with 150 ms
    gaps — a simultaneous torque-on browned out the 12 V supply on 2026-09-12
  * follower Acceleration + Goal_Velocity are capped before torque comes on
  * soft start: ramps from wherever the follower is to the leader pose over --ramp
  * per-cycle step clamp and per-joint position limits, intersected with each
    follower servo's own Min/Max_Position_Limit
  * refuses to run on an under-volted follower bus unless --allow-low-voltage
  * Ctrl-C or any error disables follower torque before exiting
  * auto-reconnect if the boards re-enumerate mid-session
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

from ports import DEG, JOINTS, MID, load_config, resolve


@dataclass
class JointMap:
    """leader tick -> follower tick for one joint, plus its safety clamp."""
    name: str
    sign: int = 1
    scale: float = 1.0
    offset: int = 0
    lo: int = 0
    hi: int = 4095
    # only used by mode="limits"
    src: tuple[int, int] | None = None
    dst: tuple[int, int] | None = None

    def target(self, raw: int) -> int:
        if self.src and self.dst:
            lmin, lmax = self.src
            fmin, fmax = self.dst
            frac = (raw - lmin) / (lmax - lmin)
            frac = 0.0 if frac < 0.0 else 1.0 if frac > 1.0 else frac
            if self.sign < 0:
                frac = 1.0 - frac
            v = fmin + frac * (fmax - fmin) + self.offset
        else:
            v = MID + self.sign * (raw - MID) * self.scale + self.offset
        return int(clamp(round(v), self.lo, self.hi))

    def describe(self) -> str:
        how = (f"limits {self.src[0]}-{self.src[1]} -> {self.dst[0]}-{self.dst[1]}"
               if self.src else f"direct sign{self.sign:+d} scale{self.scale:.2f} offset{self.offset:+d}")
        return f"{self.name:>14}  {how:<38} clamp [{self.lo},{self.hi}]"


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def make_bus(port: str) -> FeetechMotorsBus:
    motors = {j: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, j in enumerate(JOINTS)}
    bus = FeetechMotorsBus(port=port, motors=motors)
    bus.connect(handshake=True)
    return bus


def volts(bus: FeetechMotorsBus) -> float:
    return bus.read("Present_Voltage", JOINTS[0], normalize=False) / 10.0


def servo_limits(bus: FeetechMotorsBus, joint: str) -> tuple[int, int] | None:
    try:
        mn = bus.read("Min_Position_Limit", joint, normalize=False)
        mx = bus.read("Max_Position_Limit", joint, normalize=False)
        return (mn, mx) if 0 <= mn < mx <= 4095 else None
    except Exception as e:
        print(f"[limits] could not read servo limits for {joint}: {e}")
        return None


def build_maps(cfg: dict, leader: FeetechMotorsBus, follower: FeetechMotorsBus,
               flips: list[str], offsets: dict[str, int]) -> dict[str, JointMap]:
    joints_cfg = cfg["raw"].get("joints", {})
    clamp_deg = cfg["raw"]["clamp_deg"]
    maps: dict[str, JointMap] = {}
    for j in JOINTS:
        jc = joints_cfg.get(j, {})
        lo_deg, hi_deg = clamp_deg[j]
        lo, hi = MID + int(lo_deg * DEG), MID + int(hi_deg * DEG)
        fl = servo_limits(follower, j)
        if fl:                                   # the servo's own calibrated range always wins
            lo, hi = max(lo, fl[0]), min(hi, fl[1])
        m = JointMap(
            name=j,
            sign=-1 if (j in flips or jc.get("flip")) else 1,
            scale=float(jc.get("scale", 1.0)),
            offset=int(offsets.get(j, jc.get("offset", 0))),
            lo=lo, hi=hi,
        )
        if jc.get("mode") == "limits":
            ll = servo_limits(leader, j)
            if ll and fl:
                m.src, m.dst = ll, fl
            else:
                print(f"[limits] {j}: mode='limits' needs both arms' servo limits — falling back to direct")
        maps[j] = m
    return maps


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leader", help="override the leader device path")
    ap.add_argument("--follower", help="override the follower device path")
    ap.add_argument("--hz", type=float)
    ap.add_argument("--ramp", type=float, help="seconds for the soft start")
    ap.add_argument("--max-step", type=int, help="max follower move per cycle, ticks")
    ap.add_argument("--accel", type=int, help="servo Acceleration register (0-254, lower = gentler)")
    ap.add_argument("--speed", type=int, help="servo Goal_Velocity cap, ticks/s")
    ap.add_argument("--flip", action="append", default=[], choices=JOINTS)
    ap.add_argument("--offset", action="append", default=[], metavar="JOINT=TICKS")
    ap.add_argument("--allow-low-voltage", action="store_true")
    ap.add_argument("--wait-for-power", action="store_true",
                    help="if the follower bus is under 9 V, poll until the 12 V supply appears, then start")
    ap.add_argument("--dry-run", action="store_true", help="never enable torque; only print what would be sent")
    ap.add_argument("--fast", action="store_true", help="use the [raw.fast] profile from arms.toml")
    args = ap.parse_args()

    cfg = load_config()
    tune = dict(cfg["raw"])
    if args.fast:
        tune.update(cfg["raw"]["fast"])
    for key in ("hz", "ramp", "max_step", "accel", "speed"):
        if getattr(args, key) is not None:
            tune[key] = getattr(args, key)

    offsets = {}
    for spec in args.offset:
        j, n = spec.split("=")
        offsets[j] = int(n)

    lead_port, fol_port = resolve(cfg, args.leader, args.follower)
    leader = make_bus(lead_port)
    follower = make_bus(fol_port)
    vl, vf = volts(leader), volts(follower)
    print(f"[leader]   {lead_port}  bus {vl:.1f} V")
    print(f"[follower] {fol_port}  bus {vf:.1f} V")
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
              f"!! Turn on the robot's 12 V supply, or re-run with --allow-low-voltage to try anyway.")
        leader.disconnect(disable_torque=False); follower.disconnect(disable_torque=False)
        sys.exit(2)

    maps = build_maps(cfg, leader, follower, args.flip, offsets)
    print("\n[map] leader tick -> follower tick")
    for j in JOINTS:
        print("  " + maps[j].describe())

    def target_from_leader(raw: dict[str, int]) -> dict[str, int]:
        return {j: maps[j].target(raw[j]) for j in JOINTS}

    leader.disable_torque()  # the leader must stay free to move by hand
    goal = follower.sync_read("Present_Position", normalize=False)
    start_pose = dict(goal)
    first_target = target_from_leader(leader.sync_read("Present_Position", normalize=False))
    print("\ninitial follower -> leader deltas:")
    for j in JOINTS:
        d = first_target[j] - start_pose[j]
        print(f"  {j:>14}: follower {start_pose[j]:>5} -> target {first_target[j]:>5}   ({d:+5d} ticks, {d / DEG:+6.1f}°)")
    big = max(JOINTS, key=lambda j: abs(first_target[j] - start_pose[j]))
    if abs(first_target[big] - start_pose[big]) > 40 * DEG:
        print(f"\n!! {big} has to travel {abs(first_target[big] - start_pose[big]) / DEG:.0f}° on the soft start — "
              f"check nothing is in the way (an unpowered follower slumps to its hard stop).")

    if args.dry_run:
        print("\n[dry-run] torque NOT enabled; exiting.")
        leader.disconnect(disable_torque=False); follower.disconnect(disable_torque=False)
        return

    def arm_follower(bus: FeetechMotorsBus, hold: dict[str, int]) -> None:
        """Set gentle limits, then enable torque one joint at a time (staggers the 12 V inrush)."""
        for j in JOINTS:
            bus.write("Acceleration", j, tune["accel"])
            bus.write("Goal_Velocity", j, tune["speed"])
            bus.write("Goal_Position", j, hold[j], normalize=False)   # hold where it is
            bus.enable_torque(j)
            time.sleep(0.15)
        for attempt in range(5):
            try:
                bus.sync_read("Present_Position", normalize=False)
                te = [bus.read("Torque_Enable", j, normalize=False) for j in JOINTS]
                print(f"[teleop] torque-on verified: enable={te}  volts={volts(bus):.1f}", flush=True)
                return
            except Exception as e:
                print(f"[teleop] post-torque check failed ({attempt + 1}/5): {e}", flush=True)
                time.sleep(0.5)
        raise ConnectionError("follower bus not answering after torque-on")

    arm_follower(follower, goal)
    print(f"\n[teleop] torque ON (follower IDs 1-6). soft start {tune['ramp']:.0f}s, then live at "
          f"{tune['hz']:.0f} Hz. Ctrl-C to stop.\n")

    period = 1.0 / tune["hz"]
    t_start = time.time()
    last_log = 0.0
    fails = 0
    MAX_FAILS = 10          # consecutive bad cycles before we drop the ports and reconnect
    stats = {k: [] for k in ("rd_lead", "rd_fol", "wr", "period", "lag", "vel")}
    prev_raw, prev_t, last_cycle = None, 0.0, None

    def reconnect():
        nonlocal leader, follower, goal, start_pose, t_start, fails, prev_raw, last_cycle
        print("\n[teleop] bus dropout — closing ports, waiting for the boards to come back ...", flush=True)
        for b in (leader, follower):
            try: b.port_handler.closePort()
            except Exception: pass
        while True:
            time.sleep(2.0)
            try:
                leader = make_bus(lead_port)
                follower = make_bus(fol_port)
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
                print(f"[teleop] reconnected ({vf:.1f} V); soft start {tune['ramp']:.0f}s", flush=True)
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
                        tgt_now = maps[jf].target(raw[jf])
                        lag_s = (tgt_now - pres[jf]) / (maps[jf].sign * vel[jf])
                        stats["lag"].append(max(0.0, min(lag_s, 2.0)) * 1e3)
                        stats["vel"].append(abs(vel[jf]) / DEG)
                prev_raw, prev_t = raw, t0
                tgt = target_from_leader(raw)
                alpha = min(1.0, (t0 - t_start) / tune["ramp"])
                new_goal = {}
                for j in JOINTS:
                    blended = start_pose[j] + alpha * (tgt[j] - start_pose[j])  # soft start
                    step = clamp(blended - goal[j], -tune["max_step"], tune["max_step"])
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
                    print(f"[{t0 - t_start:6.1f}s] ramp {alpha * 100:3.0f}%  {vf:.1f}V  err {err:3d}t ({err / DEG:4.1f}° {jw[:6]})  "
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
                print(f"[teleop] torque-off retry {attempt + 1}/3: {e}", flush=True)
                time.sleep(0.3)
        for b, dis in ((follower, True), (leader, False)):
            try: b.disconnect(disable_torque=dis)
            except Exception:
                try: b.port_handler.closePort()
                except Exception: pass
        print("[teleop] follower torque OFF (best effort), ports closed", flush=True)


if __name__ == "__main__":
    main()
