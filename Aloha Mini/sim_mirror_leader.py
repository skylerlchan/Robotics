#!/usr/bin/env python
"""
Mirror a real SO-101 arm (AlohaMini leader or follower) into a MuJoCo simulation,
or run the simulation alone with no hardware.

Live mirror (macOS needs mjpython for the interactive viewer):
    mjpython sim_mirror_leader.py --port /dev/cu.usbmodem5AE60833451

Sim only, no robot plugged in (gentle sinusoid demo, drag joints with ctrl+right-drag):
    mjpython sim_mirror_leader.py --no-robot

Headless check: render the arm's current real pose to a PNG:
    python sim_mirror_leader.py --port /dev/cu.usbmodem5AE60833451 --snapshot pose.png

Conventions
-----------
* Servo raw ticks 0..4095 cover one full turn; 2048 is the "middle" both for a freshly
  assembled SO-101 and after lerobot calibration (lerobot writes Homing_Offset into the
  servo, so Present_Position already reads 2048 at the calibrated middle).
  => joint_rad = (raw - 2048) * 2*pi / 4096
* The MJCF is the menagerie "robotstudio_so101" model, which was derived from
  so101_new_calib.xml, i.e. it uses that same lerobot middle-pose zero.
* If a joint visibly moves the wrong way, pass --flip <joint_name> (repeatable).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np

import mujoco

JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
DEFAULT_MJCF = os.environ.get(
    "SO101_MJCF",
    "/Users/skyler/Projects/personal/exahuman/public/mujoco_menagerie/robotstudio_so101/scene.xml",
)
TICKS_PER_TURN = 4096
MID_TICK = 2048


def raw_to_rad(raw: int, sign: float = 1.0) -> float:
    return sign * (raw - MID_TICK) * (2.0 * math.pi / TICKS_PER_TURN)


class RealArm:
    """Thin wrapper over lerobot's FeetechMotorsBus. Read-only: never enables torque."""

    def __init__(self, port: str, baudrate: int = 1_000_000):
        from lerobot.motors import Motor, MotorNormMode
        from lerobot.motors.feetech import FeetechMotorsBus

        motors = {name: Motor(i + 1, "sts3215", MotorNormMode.RANGE_M100_100) for i, name in enumerate(JOINTS)}
        self.bus = FeetechMotorsBus(port=port, motors=motors)
        self.bus.connect(handshake=True)
        volts = self.bus.read("Present_Voltage", JOINTS[0], normalize=False) / 10.0
        print(f"[arm] connected on {port}: ids 1-6 answered, bus {volts:.1f} V "
              f"({'leader-style 5V supply' if volts < 9 else 'follower-style 12V supply'})")

    def read_raw(self) -> dict[str, int]:
        return self.bus.sync_read("Present_Position", normalize=False)

    def close(self):
        try:
            self.bus.disconnect(disable_torque=False)
        except Exception:
            pass


def load_model(path: str):
    model = mujoco.MjModel.from_xml_path(path)
    data = mujoco.MjData(model)
    qadr = {}
    for j in JOINTS:
        jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, j)
        if jid < 0:
            sys.exit(f"joint '{j}' not found in {path}")
        qadr[j] = model.jnt_qposadr[jid]
    return model, data, qadr


def apply_pose(model, data, qadr, q: dict[str, float]):
    for j, val in q.items():
        lo, hi = model.jnt_range[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, j)]
        data.qpos[qadr[j]] = float(np.clip(val, lo, hi))
    mujoco.mj_forward(model, data)


def fmt(q: dict[str, float]) -> str:
    return "  ".join(f"{j}={math.degrees(v):6.1f}°" for j, v in q.items())


def snapshot(model, data, out_path: str, w: int = 960, h: int = 720):
    from PIL import Image

    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = [0.0, 0.0, 0.16]
    cam.distance = 1.0
    cam.azimuth = 150
    cam.elevation = -15
    model.vis.global_.offwidth = max(model.vis.global_.offwidth, w)
    model.vis.global_.offheight = max(model.vis.global_.offheight, h)
    with mujoco.Renderer(model, height=h, width=w) as r:
        r.update_scene(data, camera=cam)
        Image.fromarray(r.render()).save(out_path)
    print(f"[sim] wrote {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", help="serial port of the arm's bus board (e.g. /dev/cu.usbmodem5AE60833451)")
    ap.add_argument("--no-robot", action="store_true", help="run the sim with no hardware (sinusoid demo)")
    ap.add_argument("--mjcf", default=DEFAULT_MJCF, help="path to so101 scene.xml")
    ap.add_argument("--flip", action="append", default=[], choices=JOINTS, help="invert this joint's direction")
    ap.add_argument("--hz", type=float, default=50.0, help="mirror update rate")
    ap.add_argument("--snapshot", metavar="PNG", help="render one frame of the current pose and exit (headless)")
    args = ap.parse_args()

    if not args.no_robot and not args.port:
        ap.error("give --port <serial device> or --no-robot")

    sign = {j: (-1.0 if j in args.flip else 1.0) for j in JOINTS}
    model, data, qadr = load_model(args.mjcf)
    arm = None if args.no_robot else RealArm(args.port)

    def current_q() -> dict[str, float]:
        if arm is None:
            t = time.time()
            return {j: 0.35 * math.sin(0.6 * t + k) for k, j in enumerate(JOINTS)}
        raw = arm.read_raw()
        return {j: raw_to_rad(raw[j], sign[j]) for j in JOINTS}

    try:
        if args.snapshot:
            q = current_q()
            apply_pose(model, data, qadr, q)
            print("[pose] " + fmt(q))
            snapshot(model, data, args.snapshot)
            return

        import mujoco.viewer  # needs mjpython on macOS

        period = 1.0 / args.hz
        last_print = 0.0
        with mujoco.viewer.launch_passive(model, data) as viewer:
            viewer.cam.lookat[:] = [0.0, 0.0, 0.16]
            viewer.cam.distance = 1.0
            viewer.cam.azimuth = 150
            viewer.cam.elevation = -15
            print("[sim] viewer open — close the window or ctrl-c to stop")
            while viewer.is_running():
                t0 = time.time()
                q = current_q()
                apply_pose(model, data, qadr, q)
                viewer.sync()
                if t0 - last_print > 1.0:
                    print("\r[pose] " + fmt(q), end="", flush=True)
                    last_print = t0
                dt = period - (time.time() - t0)
                if dt > 0:
                    time.sleep(dt)
        print()
    except KeyboardInterrupt:
        print()
    finally:
        if arm is not None:
            arm.close()


if __name__ == "__main__":
    main()
