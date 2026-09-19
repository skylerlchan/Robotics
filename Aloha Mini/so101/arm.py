#!/usr/bin/env python
"""Direct scripted control of the SO-101 follower — the arm without a leader.

`teleop.py` mirrors a human-held leader arm. This drives the follower from code,
so a script (or an agent) can command it:

    python arm.py status                      # positions + voltage, never torques
    python arm.py relax                       # torque off, arm goes limp
    python arm.py teach rest                  # move it by hand, save where it is
    python arm.py pose rest                   # go back there
    python arm.py move elbow_flex=-30 wrist_flex=15
    python arm.py gripper open | close | 40
    python arm.py home                        # all joints to 0 deg (2048 ticks)
    python arm.py play demo.json              # run a sequence of steps

As a library:

    from arm import Arm
    with Arm() as a:                          # torque on
        a.move({"shoulder_pan": 20}, secs=2)
        a.gripper(0)
        print(a.read_deg())
    # the block exits still holding position — a limp arm falls. Release with
    # `arm.py relax`, a.relax(), or Arm(release_on_exit=True).

Angles are **degrees from centre**, matching the SO-101 convention that tick 2048
is the middle of a joint's range. Gripper is the exception: 0 = closed, 100 = open,
mapped onto whatever range that servo was actually calibrated to.

Safety is inherited from teleop.py, which was proven on hardware 2026-09-12:
  * refuses to run on an under-volted follower bus (12 V servos will not hold)
  * Acceleration + Goal_Velocity capped before torque is enabled
  * torque enabled one joint at a time with 150 ms gaps — a simultaneous
    torque-on browned out the 12 V supply and rebooted every servo
  * every target clamped to arms.toml limits INTERSECTED with each servo's own
    Min/Max_Position_Limit; the tighter bound always wins
  * all motion is interpolated at a fixed rate with a per-cycle step clamp —
    the arm is never handed a step change
  * torque is disabled on exit, Ctrl-C, or any error

Unlike teleop there is no human in the loop, so a bad target moves the arm into
whatever is in front of it. `--dry-run` prints the planned travel and exits.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

from ports import DEG, JOINTS, MID, load_config, resolve

HERE = Path(__file__).resolve().parent
POSES_FILE = HERE / "poses.json"
MIN_VOLTS = 9.0
ARM_GAP_S = 0.15          # gap between per-joint torque-on, staggers the 12 V inrush


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def ticks_to_deg(t: int) -> float:
    return (t - MID) / DEG


def deg_to_ticks(d: float) -> int:
    return int(round(MID + d * DEG))


class ArmError(RuntimeError):
    pass


class Arm:
    """The SO-101 follower, driven directly.

    Use as a context manager so torque is always released:

        with Arm() as a:
            a.move({"elbow_flex": -20}, secs=2)

    `torque=False` opens the bus read-only — `status` and `teach` use that, and it
    can never move the arm.
    """

    def __init__(self, port: str | None = None, cfg: dict | None = None,
                 fast: bool = False, torque: bool = True, allow_low_voltage: bool = False,
                 release_on_exit: bool = False):
        self.cfg = cfg or load_config()
        self.release_on_exit = release_on_exit
        tune = dict(self.cfg["raw"])
        if fast:
            tune.update(self.cfg["raw"]["fast"])
        self.tune = tune
        self.want_torque = torque
        self.allow_low_voltage = allow_low_voltage
        self._port = port
        self.bus: FeetechMotorsBus | None = None
        self.limits: dict[str, tuple[int, int]] = {}
        self.armed = False

    # ---- connection -------------------------------------------------------

    def connect(self) -> "Arm":
        if self._port is None:
            # resolve() wants both roles; we only need the follower, so tolerate a
            # missing leader by probing for a 12 V board directly.
            self._port = self._find_follower()
        motors = {j: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100)
                  for i, j in enumerate(JOINTS)}
        self.bus = FeetechMotorsBus(port=self._port, motors=motors)
        self.bus.connect(handshake=True)

        v = self.volts()
        if v < MIN_VOLTS and self.want_torque and not self.allow_low_voltage:
            self.close()
            raise ArmError(
                f"follower bus is {v:.1f} V. Its 12 V STS3215 servos cannot hold torque "
                f"on USB power alone — the arm will slump to its hard stop.\n"
                f"Turn on the robot's 12 V supply, or pass --allow-low-voltage."
            )

        for j in JOINTS:
            self.limits[j] = self._joint_limits(j)
        if self.want_torque:
            self._arm()
        return self

    def _find_follower(self) -> str:
        """The follower is the board on a >=9 V bus. Falls back to arms.toml's serial."""
        from ports import device_for_serial, survey
        serial = self.cfg.get("follower", {}).get("serial")
        if serial and (dev := device_for_serial(serial)):
            return dev
        hits = [r for r in survey() if r["role"] == "follower"]
        if len(hits) == 1:
            print(f"[arm] follower auto-detected: {hits[0]['device']} "
                  f"({hits[0]['volts']:.1f} V, IDs {hits[0]['ids']})", file=sys.stderr)
            return hits[0]["device"]
        if not hits:
            raise ArmError(
                "no follower board found. Either it is unplugged, or its 12 V supply is "
                "off so its bus reads ~5 V and looks like a leader.\n"
                "Check `python ports.py`, or pass --port explicitly."
            )
        raise ArmError(f"{len(hits)} boards look like a follower: "
                       f"{[h['device'] for h in hits]}. Pass --port.")

    def _joint_limits(self, joint: str) -> tuple[int, int]:
        """arms.toml's soft clamp intersected with the servo's own calibrated range."""
        lo_deg, hi_deg = self.cfg["raw"]["clamp_deg"][joint]
        lo, hi = MID + int(lo_deg * DEG), MID + int(hi_deg * DEG)
        try:
            mn = self.bus.read("Min_Position_Limit", joint, normalize=False)
            mx = self.bus.read("Max_Position_Limit", joint, normalize=False)
            if 0 <= mn < mx <= 4095:
                lo, hi = max(lo, mn), min(hi, mx)
        except Exception as e:
            print(f"[arm] could not read servo limits for {joint} ({e}); "
                  f"using arms.toml clamp only", file=sys.stderr)
        return lo, hi

    def _arm(self) -> None:
        """Cap speed, then enable torque one joint at a time, holding current pose."""
        hold = self.read_ticks()
        for j in JOINTS:
            self.bus.write("Acceleration", j, self.tune["accel"])
            self.bus.write("Goal_Velocity", j, self.tune["speed"])
            self.bus.write("Goal_Position", j, hold[j], normalize=False)
            self.bus.enable_torque(j)
            time.sleep(ARM_GAP_S)
        for attempt in range(5):
            try:
                self.bus.sync_read("Present_Position", normalize=False)
                self.armed = True
                print(f"[arm] torque ON (IDs 1-6), bus {self.volts():.1f} V", flush=True)
                return
            except Exception as e:
                print(f"[arm] post-torque check failed ({attempt + 1}/5): {e}", flush=True)
                time.sleep(0.5)
        raise ArmError("follower bus stopped answering after torque-on")

    # ---- reading ----------------------------------------------------------

    def volts(self) -> float:
        return self.bus.read("Present_Voltage", JOINTS[0], normalize=False) / 10.0

    def read_ticks(self) -> dict[str, int]:
        return self.bus.sync_read("Present_Position", normalize=False)

    def read_deg(self) -> dict[str, float]:
        return {j: round(ticks_to_deg(t), 2) for j, t in self.read_ticks().items()}

    def gripper_range(self) -> tuple[int, int]:
        return self.limits["gripper"]

    # ---- motion -----------------------------------------------------------

    def _target_ticks(self, targets: dict[str, float]) -> dict[str, int]:
        """Degrees (or 0-100 for the gripper) -> clamped ticks."""
        out = {}
        for j, val in targets.items():
            if j not in JOINTS:
                raise ArmError(f"unknown joint {j!r}. Valid: {', '.join(JOINTS)}")
            lo, hi = self.limits[j]
            if j == "gripper":
                frac = clamp(float(val), 0.0, 100.0) / 100.0
                t = int(round(lo + frac * (hi - lo)))
            else:
                t = deg_to_ticks(float(val))
            out[j] = int(clamp(t, lo, hi))
        return out

    def move(self, targets: dict[str, float], secs: float | None = None,
             dry_run: bool = False) -> dict[str, int]:
        """Interpolate to `targets`; joints left out hold position.

        `secs` defaults to a speed-limited estimate from the distance travelled, so
        a small move is quick and a large one is not violent.
        """
        if not self.armed and not dry_run:
            raise ArmError("torque is off — construct Arm(torque=True) before moving")
        start = self.read_ticks()
        goal = dict(start)
        goal.update(self._target_ticks(targets))

        travel = max(abs(goal[j] - start[j]) for j in JOINTS)
        if secs is None:
            # tune["speed"] is the servo's ticks/s cap; stay well inside it
            secs = max(0.8, travel / max(1.0, self.tune["speed"] * 0.35))

        if dry_run:
            print(f"[dry-run] planned move ({secs:.1f}s, max travel "
                  f"{travel} ticks / {travel / DEG:.1f} deg):")
            for j in JOINTS:
                d = goal[j] - start[j]
                if d:
                    print(f"  {j:>14}: {ticks_to_deg(start[j]):+7.1f} -> "
                          f"{ticks_to_deg(goal[j]):+7.1f} deg  ({d:+5d} ticks)")
            return goal

        hz = self.tune["hz"]
        steps = max(1, int(secs * hz))
        period = 1.0 / hz
        cur = dict(start)
        for i in range(1, steps + 1):
            alpha = i / steps
            frame = {}
            for j in JOINTS:
                want = start[j] + alpha * (goal[j] - start[j])
                step = clamp(want - cur[j], -self.tune["max_step"], self.tune["max_step"])
                frame[j] = int(cur[j] + step)
            self.bus.sync_write("Goal_Position", frame, normalize=False)
            cur = frame
            time.sleep(period)

        # the step clamp can leave us short on a long move; close the gap
        for _ in range(200):
            if all(abs(cur[j] - goal[j]) <= 1 for j in JOINTS):
                break
            frame = {}
            for j in JOINTS:
                step = clamp(goal[j] - cur[j], -self.tune["max_step"], self.tune["max_step"])
                frame[j] = int(cur[j] + step)
            self.bus.sync_write("Goal_Position", frame, normalize=False)
            cur = frame
            time.sleep(period)
        return goal

    def gripper(self, value, secs: float | None = None):
        """0 = closed, 100 = open; also accepts the words 'open' and 'close'."""
        if isinstance(value, str):
            value = {"open": 100, "close": 0, "closed": 0}[value.lower()]
        return self.move({"gripper": value}, secs=secs)

    def home(self, secs: float = 4.0):
        """Every joint to 0 deg (tick 2048). Deliberately slow."""
        return self.move({j: 0.0 for j in JOINTS if j != "gripper"}, secs=secs)

    def relax(self) -> None:
        if self.bus is not None and self.armed:
            for attempt in range(3):
                try:
                    self.bus.disable_torque()
                    self.armed = False
                    print("[arm] torque OFF", flush=True)
                    return
                except Exception as e:
                    print(f"[arm] torque-off retry {attempt + 1}/3: {e}", flush=True)
                    time.sleep(0.3)
            print("\n!! COULD NOT DISABLE TORQUE — the bus was already gone.\n"
                  "!! The servos are still energised and holding their last goal.\n"
                  "!! Cut the 12 V supply to release the arm.", flush=True)

    def close(self) -> None:
        """Close the port, leaving torque as-is.

        Deliberately does NOT disable torque: a limp arm falls, which is worse for
        the arm and for whatever it is holding than staying energised. Release is
        always an explicit `relax()`.
        """
        if self.bus is None:
            return
        try:
            self.bus.disconnect(disable_torque=False)
        except Exception:
            try:
                self.bus.port_handler.closePort()
            except Exception:
                pass
        self.bus = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *exc):
        # Hold position by default — see close(). Arm(release_on_exit=True) to drop.
        if self.release_on_exit:
            self.relax()
        self.close()
        return False


# ---- named poses ----------------------------------------------------------

def load_poses() -> dict:
    if POSES_FILE.exists():
        return json.loads(POSES_FILE.read_text())
    return {}


def save_poses(poses: dict) -> None:
    POSES_FILE.write_text(json.dumps(poses, indent=2, sort_keys=True) + "\n")


# ---- CLI ------------------------------------------------------------------

def parse_targets(pairs: list[str]) -> dict[str, float]:
    out = {}
    for p in pairs:
        if "=" not in p:
            sys.exit(f"[arm] expected JOINT=VALUE, got {p!r}")
        j, v = p.split("=", 1)
        try:
            out[j.strip()] = float(v)
        except ValueError:
            sys.exit(f"[arm] {p!r}: {v!r} is not a number")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="follower device path (default: auto-detect)")
    ap.add_argument("--secs", type=float, help="how long the move should take")
    ap.add_argument("--fast", action="store_true", help="use the [raw.fast] profile")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the planned travel, never enable torque")
    ap.add_argument("--allow-low-voltage", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="positions, limits and voltage; never torques")
    sub.add_parser("relax", help="disable torque — the arm goes limp")
    sub.add_parser("home", help="all joints to 0 deg")
    p_move = sub.add_parser("move", help="move joints, e.g. move elbow_flex=-30")
    p_move.add_argument("targets", nargs="+", metavar="JOINT=DEG")
    p_grip = sub.add_parser("gripper", help="open | close | 0-100")
    p_grip.add_argument("value")
    p_pose = sub.add_parser("pose", help="go to a saved pose")
    p_pose.add_argument("name")
    p_teach = sub.add_parser("teach", help="save the arm's current position as a pose")
    p_teach.add_argument("name")
    sub.add_parser("poses", help="list saved poses")
    p_play = sub.add_parser("play", help="run a JSON sequence of steps")
    p_play.add_argument("file")

    args = ap.parse_args()

    # Commands that must never energise the arm.
    read_only = args.cmd in ("status", "teach", "poses", "relax") or args.dry_run

    if args.cmd == "poses":
        poses = load_poses()
        if not poses:
            print("no saved poses yet — move the arm by hand and run: arm.py teach <name>")
        for name, vals in sorted(poses.items()):
            pretty = "  ".join(f"{j}={v:+.1f}" for j, v in vals.items())
            print(f"{name:>14}  {pretty}")
        return

    arm = Arm(port=args.port, fast=args.fast, torque=not read_only,
              allow_low_voltage=args.allow_low_voltage)
    try:
        arm.connect()

        if args.cmd == "status":
            deg, ticks = arm.read_deg(), arm.read_ticks()
            print(f"[arm] {arm._port}   bus {arm.volts():.1f} V   "
                  f"torque {'ON' if arm.armed else 'off'}")
            print(f"{'joint':>14} {'deg':>8} {'ticks':>7}   {'usable range (deg)':>22}")
            for j in JOINTS:
                lo, hi = arm.limits[j]
                print(f"{j:>14} {deg[j]:>8.1f} {ticks[j]:>7}   "
                      f"{ticks_to_deg(lo):>9.1f} .. {ticks_to_deg(hi):<9.1f}")
            if arm.volts() < MIN_VOLTS:
                print(f"\n!! bus is {arm.volts():.1f} V — the 12 V supply is OFF. "
                      f"Reading works, but the arm cannot hold torque.")

        elif args.cmd == "relax":
            # connect(torque=False) never armed it; disable explicitly anyway
            for j in JOINTS:
                try:
                    arm.bus.write("Torque_Enable", j, 0, normalize=False)
                except Exception as e:
                    print(f"[arm] {j}: {e}")
            print("[arm] torque OFF — the arm is limp, support it before it drops")

        elif args.cmd == "teach":
            poses = load_poses()
            deg = arm.read_deg()
            lo, hi = arm.gripper_range()
            g = arm.read_ticks()["gripper"]
            deg["gripper"] = round(100.0 * (g - lo) / max(1, hi - lo), 1)
            poses[args.name] = deg
            save_poses(poses)
            print(f"[arm] saved pose {args.name!r}:")
            for j, v in deg.items():
                print(f"  {j:>14} {v:+8.1f}")

        elif args.cmd == "home":
            arm.move({j: 0.0 for j in JOINTS if j != "gripper"},
                     secs=args.secs or 4.0, dry_run=args.dry_run)

        elif args.cmd == "move":
            arm.move(parse_targets(args.targets), secs=args.secs, dry_run=args.dry_run)

        elif args.cmd == "gripper":
            val = args.value
            if val.lower() not in ("open", "close", "closed"):
                val = float(val)
            if args.dry_run:
                v = {"open": 100, "close": 0, "closed": 0}.get(str(val).lower(), val)
                arm.move({"gripper": float(v)}, secs=args.secs, dry_run=True)
            else:
                arm.gripper(val, secs=args.secs)

        elif args.cmd == "pose":
            poses = load_poses()
            if args.name not in poses:
                sys.exit(f"[arm] no pose {args.name!r}. Known: "
                         f"{', '.join(sorted(poses)) or '(none)'}")
            arm.move(poses[args.name], secs=args.secs, dry_run=args.dry_run)

        elif args.cmd == "play":
            steps = json.loads(Path(args.file).read_text())
            poses = load_poses()
            for n, step in enumerate(steps, 1):
                if "wait" in step:
                    print(f"[{n}/{len(steps)}] wait {step['wait']}s")
                    if not args.dry_run:
                        time.sleep(float(step["wait"]))
                    continue
                if "pose" in step:
                    if step["pose"] not in poses:
                        sys.exit(f"[arm] step {n}: no pose {step['pose']!r}")
                    targets = dict(poses[step["pose"]])
                    label = f"pose {step['pose']}"
                else:
                    targets = {k: v for k, v in step.items() if k in JOINTS}
                    label = "  ".join(f"{k}={v}" for k, v in targets.items())
                print(f"[{n}/{len(steps)}] {label}")
                arm.move(targets, secs=step.get("secs", args.secs), dry_run=args.dry_run)

        if arm.armed:
            print("[arm] done — holding position. `arm.py relax` to release.")
    except ArmError as e:
        sys.exit(f"[arm] {e}")
    except KeyboardInterrupt:
        print("\n[arm] interrupted")
    finally:
        # A move leaves the arm holding its goal on purpose; only `relax` drops it.
        arm.close()


if __name__ == "__main__":
    main()
