#!/usr/bin/env python
"""Score a put-away run: how many objects ended up where they live.

The robot is only "working" when this script says so, run after run, with nobody
touching anything. Markers make the scoring exact, so the instrument is never the
thing that failed.

    python score.py selftest                 # no camera needed, checks the install
    python score.py state                    # one frame: where is everything now
    python score.py watch                    # live window with the overlay
    python score.py run --label "act-v1"     # score one job, append to runs.jsonl

Run it with the lerobot env python:
    /Users/skyler/miniforge3/envs/lerobot_alohamini/bin/python score.py state
Keep it in its own process: OpenCV and PyAV ship duplicate libav on macOS.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import time
import tomllib

import cv2
import numpy as np

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
LOG = HERE / "runs.jsonl"


# ---------------------------------------------------------------- job spec
class Job:
    def __init__(self, data: dict):
        self.name = data.get("name", "put-away")
        self.camera = int(data.get("camera", 0))
        self.dict_name = data.get("dict", "DICT_4X4_50")
        self.bins = {int(k): v for k, v in data.get("bins", {}).items()}
        self.objects = {int(k): v for k, v in data.get("objects", {}).items()}
        for oid, o in self.objects.items():
            if int(o["home"]) not in self.bins:
                raise SystemExit(f"object {oid} ({o['name']}) has home {o['home']}, which is not a bin")

    @classmethod
    def load(cls, path: pathlib.Path):
        with open(path, "rb") as f:
            return cls(tomllib.load(f))


def detector(dict_name: str):
    d = getattr(cv2.aruco, dict_name, None)
    if d is None:
        raise SystemExit(f"unknown marker dictionary {dict_name}")
    return cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(d), cv2.aruco.DetectorParameters())


def detect(frame, det) -> dict[int, dict]:
    """Marker id -> {center (x, y), side (px)}."""
    corners, ids, _ = det.detectMarkers(frame)
    out = {}
    if ids is None:
        return out
    for c, i in zip(corners, ids.flatten()):
        pts = c.reshape(4, 2)
        sides = [float(np.linalg.norm(pts[k] - pts[(k + 1) % 4])) for k in range(4)]
        out[int(i)] = {"center": pts.mean(axis=0), "side": float(np.mean(sides)), "corners": pts}
    return out


def evaluate(marks: dict[int, dict], job: Job) -> list[dict]:
    """One row per object: seen, which bin it sits in, whether that is home."""
    rows = []
    for oid, o in sorted(job.objects.items()):
        row = {"id": oid, "name": o["name"], "home": int(o["home"]), "seen": oid in marks, "in_bin": None}
        if row["seen"]:
            oc = marks[oid]["center"]
            best, best_d = None, None
            for bid, b in job.bins.items():
                if bid not in marks:
                    continue
                bc, side = marks[bid]["center"], marks[bid]["side"]
                d = float(np.linalg.norm(oc - bc))
                if d <= float(b.get("radius", 3.0)) * side and (best_d is None or d < best_d):
                    best, best_d = bid, d
            row["in_bin"] = best
        row["home_ok"] = row["seen"] and row["in_bin"] == row["home"]
        rows.append(row)
    return rows


def summarise(rows: list[dict]) -> dict:
    return {
        "objects": len(rows),
        "home": sum(r["home_ok"] for r in rows),
        "out_of_place": sum(not r["home_ok"] and r["seen"] for r in rows),
        "missing": sum(not r["seen"] for r in rows),
    }


def draw(frame, marks, job: Job, rows):
    out = frame.copy()
    for bid, b in job.bins.items():
        if bid not in marks:
            continue
        c, side = marks[bid]["center"], marks[bid]["side"]
        r = int(float(b.get("radius", 3.0)) * side)
        cv2.circle(out, tuple(c.astype(int)), r, (90, 90, 90), 2)
        lx = int(min(max(c[0] - r, 8), out.shape[1] - 160))
        ly = int(min(max(c[1] - r - 10, 22), out.shape[0] - 8))
        cv2.putText(out, b.get("name", f"bin {bid}"), (lx, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 2)
    for row in rows:
        if not row["seen"]:
            continue
        c = marks[row["id"]]["center"].astype(int)
        ok = row["home_ok"]
        colour = (60, 160, 60) if ok else (40, 40, 200)
        cv2.drawMarker(out, tuple(c), colour, cv2.MARKER_CROSS, 18, 2)
        cv2.putText(out, row["name"], tuple(c + [10, -8]), cv2.FONT_HERSHEY_SIMPLEX, 0.55, colour, 2)
    s = summarise(rows)
    cv2.putText(out, f"home {s['home']}/{s['objects']}  out {s['out_of_place']}  missing {s['missing']}",
                (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)
    return out


# ---------------------------------------------------------------- camera
def open_camera(index: int):
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY)
    if not cap.isOpened():
        raise SystemExit(f"camera {index} would not open. On macOS, grant your terminal Camera access in "
                         "System Settings > Privacy & Security > Camera, then try again.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap


def grab(cap, warmup: int = 8):
    frame = None
    for _ in range(warmup):
        ok, f = cap.read()
        if ok:
            frame = f
        time.sleep(0.03)
    if frame is None:
        raise SystemExit("no frame from the camera")
    return frame


def read_state(job: Job, cap=None):
    own = cap is None
    cap = cap or open_camera(job.camera)
    try:
        frame = grab(cap)
    finally:
        if own:
            cap.release()
    det = detector(job.dict_name)
    marks = detect(frame, det)
    rows = evaluate(marks, job)
    return frame, marks, rows


def print_rows(rows):
    for r in rows:
        where = "missing" if not r["seen"] else ("home" if r["home_ok"] else
                                                 (f"bin {r['in_bin']}" if r["in_bin"] is not None else "loose"))
        print(f"  {r['name']:<22s} {where}")
    s = summarise(rows)
    print(f"  -> {s['home']}/{s['objects']} home, {s['out_of_place']} out of place, {s['missing']} missing")


# ---------------------------------------------------------------- commands
def cmd_state(job, args):
    _, _, rows = read_state(job)
    print(f"{job.name}:")
    print_rows(rows)


def cmd_watch(job, args):
    cap = open_camera(job.camera)
    det = detector(job.dict_name)
    print("q or esc to quit")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue
            marks = detect(frame, det)
            rows = evaluate(marks, job)
            cv2.imshow("put-away", draw(frame, marks, job, rows))
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def cmd_run(job, args):
    RUNS.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    cap = open_camera(job.camera)
    try:
        frame, marks, before = read_state(job, cap)
        cv2.imwrite(str(RUNS / f"{stamp}-before.jpg"), draw(frame, marks, job, before))
        print(f"{job.name} — before:")
        print_rows(before)
        t0 = time.time()
        input("\nstart the run. press Enter when the robot is finished (or it gave up)... ")
        frame, marks, after = read_state(job, cap)
        cv2.imwrite(str(RUNS / f"{stamp}-after.jpg"), draw(frame, marks, job, after))
    finally:
        cap.release()
    dur = time.time() - t0
    sa, sb = summarise(after), summarise(before)
    entry = {
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "job": job.name,
        "label": args.label,
        "duration_s": round(dur, 1),
        "interventions": args.interventions,
        "before": sb,
        "after": sa,
        "clean": sa["out_of_place"] == 0 and sa["missing"] == 0 and args.interventions == 0,
        "notes": args.notes,
        "frames": [f"runs/{stamp}-before.jpg", f"runs/{stamp}-after.jpg"],
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print("\nafter:")
    print_rows(after)
    print(f"\n{'CLEAN RUN' if entry['clean'] else 'not clean'} · {dur:.0f}s · "
          f"{args.interventions} intervention(s) · logged to runs.jsonl")


def cmd_selftest(job, args):
    """Draw a fake scene, score it, and check the answer. No camera, no robot."""
    d = getattr(cv2.aruco, job.dict_name)
    dic = cv2.aruco.getPredefinedDictionary(d)
    canvas = np.full((900, 1400, 3), 245, np.uint8)

    def paste(mid, cx, cy, px):
        img = cv2.aruco.generateImageMarker(dic, mid, px)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        x, y = int(cx - px / 2), int(cy - px / 2)
        canvas[y:y + px, x:x + px] = img

    bins = sorted(job.bins)
    objs = sorted(job.objects)
    if len(bins) < 1 or len(objs) < 2:
        raise SystemExit("selftest needs at least 1 bin and 2 objects in the job file")
    spots = {}
    for i, bid in enumerate(bins):
        x = 260 + i * 520
        paste(bid, x, 360, 120)
        spots[bid] = (x, 360)
    # every other object goes home; the rest are left loose in the open
    expect_home, per_bin, loose = 0, {}, 0
    for i, oid in enumerate(objs):
        if i % 2 == 0:
            home = int(job.objects[oid]["home"])
            bx, by = spots[home]
            k = per_bin.get(home, 0); per_bin[home] = k + 1
            paste(oid, bx - 45 + k * 90, by + 140, 64)
            expect_home += 1
        else:
            paste(oid, 180 + loose * 130, 780, 64)
            loose += 1

    marks = detect(canvas, detector(job.dict_name))
    rows = evaluate(marks, job)
    print("synthetic scene:")
    print_rows(rows)
    s = summarise(rows)
    ok = (s["home"] == expect_home and s["missing"] == 0
          and s["out_of_place"] == len(job.objects) - expect_home)
    out = HERE / "selftest.jpg"
    cv2.imwrite(str(out), draw(canvas, marks, job, rows))
    print(f"wrote {out.name}")
    print("PASS — detection and scoring work" if ok else "FAIL — check the job file and the marker ids")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["state", "watch", "run", "selftest"])
    p.add_argument("--job", default=str(HERE / "job.toml"))
    p.add_argument("--label", default="", help="what you are testing, e.g. act-v1 or teleop")
    p.add_argument("--interventions", type=int, default=0, help="times a human had to touch it")
    p.add_argument("--notes", default="")
    args = p.parse_args()
    job = Job.load(pathlib.Path(args.job))
    return {"state": cmd_state, "watch": cmd_watch, "run": cmd_run, "selftest": cmd_selftest}[args.command](job, args)


if __name__ == "__main__":
    sys.exit(main() or 0)
