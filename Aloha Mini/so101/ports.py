#!/usr/bin/env python
"""Board discovery for the SO-101 pair — shared by the raw path and the lerobot path.

    python ports.py                # table of every connected board
    python ports.py --leader       # just the leader device path
    python ports.py --export       # LEADER_PORT=... / FOLLOWER_PORT=... for eval in shell

Resolution order for each role: an explicit device path, then the serial in
arms.toml, then a probe of the bus (leader ≈ 5 V USB-powered, follower ≈ 12 V).
The serial path never opens a port, so it stays fast and cannot disturb a bus.
"""
from __future__ import annotations

import argparse
import glob
import shlex
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "arms.toml"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MID = 2048
DEG = 4096 / 360.0
FOLLOWER_MIN_VOLTS = 9.0   # a 12 V follower bus reads ≥ 9 V; a USB-only leader reads ~5 V


def load_config(path: Path | None = None) -> dict:
    with open(path or CONFIG, "rb") as f:
        return tomllib.load(f)


def env_python(cfg: dict) -> Path:
    return Path(cfg["env"]["prefix"]).expanduser() / "bin" / "python"


def devices() -> list[str]:
    """Every CH343 serial board currently enumerated, sorted by device path."""
    return sorted(glob.glob("/dev/cu.usbmodem*"))


def serial_of(device: str) -> str:
    """/dev/cu.usbmodem5AA90243401 -> 5AA90243401 (board serial + interface digit)."""
    return Path(device).name.removeprefix("cu.usbmodem")


def device_for_serial(serial: str) -> str | None:
    for dev in devices():
        if serial_of(dev).startswith(serial):
            return dev
    return None


def probe(device: str) -> dict | None:
    """Ping the bus and read its voltage. Never enables torque. None if nothing answers."""
    from lerobot.motors import Motor, MotorNormMode
    from lerobot.motors.feetech import FeetechMotorsBus

    motors = {f"id{i}": Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i in range(1, 12)}
    bus = FeetechMotorsBus(port=device, motors=motors)
    try:
        bus.connect(handshake=False)
    except Exception:
        return None
    try:
        ids = sorted((bus.broadcast_ping(num_retry=2) or {}))
        if not ids:
            return None
        volts = bus.read("Present_Voltage", f"id{ids[0]}", normalize=False) / 10.0
        role = "follower" if volts >= FOLLOWER_MIN_VOLTS else "leader"
        return {"device": device, "serial": serial_of(device), "ids": ids, "volts": volts, "role": role}
    finally:
        try:
            bus.disconnect(disable_torque=False)
        except Exception:
            pass


def survey() -> list[dict]:
    """Probe every connected board. Slow (~1 s each) — only used as a fallback."""
    return [r for r in (probe(d) for d in devices()) if r]


def resolve(cfg: dict, leader: str | None = None, follower: str | None = None) -> tuple[str, str]:
    """Return (leader_device, follower_device), or exit with a useful message."""
    found = {"leader": leader, "follower": follower}
    for role in ("leader", "follower"):
        if found[role]:
            continue
        serial = cfg.get(role, {}).get("serial")
        if serial:
            found[role] = device_for_serial(serial)

    missing = [r for r in ("leader", "follower") if not found[r]]
    if missing:
        by_role: dict[str, list[dict]] = {}
        for r in survey():
            by_role.setdefault(r["role"], []).append(r)
        for role in missing:
            hits = by_role.get(role, [])
            if len(hits) == 1:
                found[role] = hits[0]["device"]
                print(f"[ports] {role} auto-detected: {hits[0]['device']} "
                      f"({hits[0]['volts']:.1f} V, IDs {hits[0]['ids']})", file=sys.stderr)
            elif len(hits) > 1:
                sys.exit(f"[ports] {len(hits)} boards look like a {role}: "
                         f"{[h['device'] for h in hits]}. Pass --{role} explicitly.")

    still = [r for r in ("leader", "follower") if not found[r]]
    if still:
        hint = ("the follower's 12 V supply is off, so both buses read ~5 V and look alike"
                if "follower" in still else "the board may be unplugged")
        sys.exit(f"[ports] could not find the {', '.join(still)} board — {hint}.\n"
                 f"        connected: {devices() or 'none'}\n"
                 f"        fix: power the follower, update the serial in arms.toml, "
                 f"or pass --leader/--follower.")
    return found["leader"], found["follower"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--leader", action="store_true", help="print the leader device path only")
    ap.add_argument("--follower", action="store_true", help="print the follower device path only")
    ap.add_argument("--export", action="store_true", help="print shell assignments for eval")
    args = ap.parse_args()
    cfg = load_config()

    if args.leader or args.follower or args.export:
        lead, fol = resolve(cfg)
        if args.export:
            lr, rec = cfg["lerobot"], cfg["lerobot"]["record"]
            for key, value in (
                ("LEADER_PORT", lead), ("FOLLOWER_PORT", fol),
                ("LEADER_ID", cfg["leader"]["lerobot_id"]), ("FOLLOWER_ID", cfg["follower"]["lerobot_id"]),
                ("ROBOT_TYPE", lr["robot_type"]), ("TELEOP_TYPE", lr["teleop_type"]),
                ("ARM_PROFILE", lr["arm_profile"]), ("FPS", lr["fps"]),
                ("REPO_ID", rec["repo_id"]), ("SINGLE_TASK", rec["single_task"]),
                ("EPISODE_TIME_S", rec["episode_time_s"]), ("RESET_TIME_S", rec["reset_time_s"]),
                ("NUM_EPISODES", rec["num_episodes"]), ("CAMERAS", rec["cameras"]),
            ):
                print(f"{key}={shlex.quote(str(value))}")
        elif args.leader:
            print(lead)
        else:
            print(fol)
        return

    devs = devices()
    if not devs:
        sys.exit("[ports] no /dev/cu.usbmodem* boards connected")
    want = {cfg[r]["serial"]: r for r in ("leader", "follower") if cfg.get(r, {}).get("serial")}
    print(f"{'device':>30} {'serial':>12} {'volts':>6} {'role':>9}  {'arms.toml':>10}  servos")
    for dev in devs:
        r = probe(dev)
        serial = serial_of(dev)
        known = next((role for s, role in want.items() if serial.startswith(s)), "-")
        if r:
            print(f"{dev:>30} {serial:>12} {r['volts']:>5.1f}V {r['role']:>9}  {known:>10}  {r['ids']}")
        else:
            print(f"{dev:>30} {serial:>12} {'-':>6} {'silent':>9}  {known:>10}  (no reply)")


if __name__ == "__main__":
    main()
