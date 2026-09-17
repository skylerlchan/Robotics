#!/usr/bin/env python
"""Bridge between the two teleop layers: the arms' in-servo calibration <-> lerobot JSON.

Both of these arms are already calibrated *in the servos* (non-zero Homing_Offset,
custom Min/Max_Position_Limit), which is what lets the raw-tick path mirror ticks
1:1 with no files. The stock lerobot path wants the same numbers in a JSON file —
and `lerobot-calibrate` would get there by running `set_half_turn_homings()`, which
OVERWRITES those in-servo offsets and breaks the raw path.

So don't run it. Read the servos instead:

    python snapshot.py             # show what each arm has stored
    python snapshot.py --backup    # save both arms to so101/calibration/backup/
    python snapshot.py --install   # backup, then write lerobot's calibration JSONs
    python snapshot.py --restore calibration/backup/leader-<stamp>.json --role leader

--install writes exactly what `read_calibration()` reports, so lerobot's
`_is_calibrated()` check passes on connect and nothing is written to the servos.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import draccus
from lerobot.motors import Motor, MotorCalibration, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.utils.constants import HF_LEROBOT_CALIBRATION, ROBOTS, TELEOPERATORS

from ports import HERE, load_config, resolve

# the so-arm-5dof profile: IDs 1-6, gripper normalised 0-100
PROFILE = [("shoulder_pan", 1), ("shoulder_lift", 2), ("elbow_flex", 3),
           ("wrist_flex", 4), ("wrist_roll", 5), ("gripper", 6)]
BACKUP_DIR = HERE / "calibration" / "backup"


def open_bus(device: str) -> FeetechMotorsBus:
    motors = {
        name: Motor(i, "sts3215",
                    MotorNormMode.RANGE_0_100 if name == "gripper" else MotorNormMode.RANGE_M100_100)
        for name, i in PROFILE
    }
    bus = FeetechMotorsBus(port=device, motors=motors)
    bus.connect(handshake=True)
    return bus


def read(device: str) -> dict[str, MotorCalibration]:
    bus = open_bus(device)
    try:
        return bus.read_calibration()
    finally:
        bus.disconnect(disable_torque=False)


def dump_json(cal: dict[str, MotorCalibration], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f, draccus.config_type("json"):
        draccus.dump(cal, f, indent=4)


def lerobot_path(cfg: dict, role: str) -> Path:
    if role == "leader":
        return HF_LEROBOT_CALIBRATION / TELEOPERATORS / cfg["lerobot"]["teleop_type"] / f"{cfg['leader']['lerobot_id']}.json"
    return HF_LEROBOT_CALIBRATION / ROBOTS / cfg["lerobot"]["robot_type"] / f"{cfg['follower']['lerobot_id']}.json"


def show(role: str, cal: dict[str, MotorCalibration]) -> None:
    print(f"\n[{role}]")
    print(f"  {'joint':>14} {'id':>3} {'homing':>7} {'min':>5} {'max':>5} {'span':>5}")
    for name, c in cal.items():
        print(f"  {name:>14} {c.id:>3} {c.homing_offset:>7} {c.range_min:>5} "
              f"{c.range_max:>5} {c.range_max - c.range_min:>5}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backup", action="store_true", help="save both arms' in-servo calibration to so101/calibration/backup/")
    ap.add_argument("--install", action="store_true", help="backup, then write lerobot's calibration JSONs from the servos")
    ap.add_argument("--restore", metavar="FILE", help="write a saved calibration back into an arm's servos")
    ap.add_argument("--role", choices=["leader", "follower"], help="which arm --restore targets")
    ap.add_argument("--leader", help="override the leader device path")
    ap.add_argument("--follower", help="override the follower device path")
    ap.add_argument("--print-paths", action="store_true",
                    help="print where lerobot expects the calibration JSONs (for the shell wrappers)")
    args = ap.parse_args()

    cfg = load_config()
    if args.print_paths:                       # no arm needed, so resolve nothing
        print(f"CAL_LEADER={lerobot_path(cfg, 'leader')}")
        print(f"CAL_FOLLOWER={lerobot_path(cfg, 'follower')}")
        return

    lead, fol = resolve(cfg, args.leader, args.follower)
    ports = {"leader": lead, "follower": fol}

    if args.restore:
        if not args.role:
            sys.exit("--restore needs --role leader|follower")
        with open(args.restore) as f, draccus.config_type("json"):
            cal = draccus.load(dict[str, MotorCalibration], f)
        show(f"restore -> {args.role}", cal)
        if input(f"\nwrite these to {ports[args.role]} ({args.role})? [y/N] ").strip().lower() != "y":
            sys.exit("aborted")
        bus = open_bus(ports[args.role])
        try:
            bus.disable_torque()          # EPROM writes need torque off and Lock cleared
            bus.write_calibration(cal)
            print(f"[snapshot] restored {args.restore} -> {args.role}")
        finally:
            bus.disconnect(disable_torque=False)
        return

    cals = {role: read(dev) for role, dev in ports.items()}
    for role, cal in cals.items():
        show(f"{role} {ports[role]}", cal)

    if args.backup or args.install:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        for role, cal in cals.items():
            path = BACKUP_DIR / f"{role}-{stamp}.json"
            dump_json(cal, path)
            print(f"[snapshot] backed up {role} -> {path}")

    if args.install:
        for role, cal in cals.items():
            path = lerobot_path(cfg, role)
            if path.exists():
                old = json.loads(path.read_text())
                if old != json.loads(json.dumps({k: vars(v) for k, v in cal.items()})):
                    print(f"[snapshot] {path} exists and differs — overwriting (a backup is in {BACKUP_DIR})")
            dump_json(cal, path)
            print(f"[snapshot] installed {role} -> {path}")
        print("\n[snapshot] the stock lerobot path is ready; nothing was written to the servos.")
        print("[snapshot] run ./teleop_lerobot.sh — do NOT run lerobot-calibrate (see calibrate.sh).")


if __name__ == "__main__":
    main()
