#!/usr/bin/env python
"""Where the robot stands against the bar: 100 clean runs in a row.

    python report.py                 # all runs
    python report.py --label act-v1  # just one policy

A run is clean when every object ended up home and nobody touched anything.
The streak is the number that matters: it resets to zero on any failure, which is
exactly how a product behaves.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import defaultdict

HERE = pathlib.Path(__file__).parent
BAR = 100


def load(path, label=None):
    if not path.exists():
        raise SystemExit("no runs yet — record one with: python score.py run --label teleop")
    runs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    return [r for r in runs if not label or r.get("label") == label]


def block(runs, title):
    n = len(runs)
    clean = sum(r["clean"] for r in runs)
    inter = sum(r["interventions"] for r in runs)
    placed = sum(r["after"]["home"] for r in runs)
    total = sum(r["after"]["objects"] for r in runs) or 1
    dur = [r["duration_s"] for r in runs if r.get("duration_s")]
    streak = best = 0
    for r in runs:
        streak = streak + 1 if r["clean"] else 0
        best = max(best, streak)
    print(f"\n{title}")
    print(f"  runs                {n}")
    print(f"  clean runs          {clean}/{n} ({clean/n*100:.0f}%)" if n else "  clean runs          0")
    print(f"  objects put away    {placed}/{total} ({placed/total*100:.0f}%)")
    print(f"  interventions       {inter} total, {inter/n:.2f} per run" if n else "")
    if dur:
        print(f"  time per run        {sum(dur)/len(dur):.0f}s median-ish (min {min(dur):.0f}, max {max(dur):.0f})")
    print(f"  clean streak now    {streak}")
    print(f"  best streak         {best}")
    bar_len = 28
    filled = min(bar_len, int(streak / BAR * bar_len))
    print(f"  toward the bar      [{'#' * filled}{'.' * (bar_len - filled)}] {streak}/{BAR}")
    if streak >= BAR:
        print("  -> it works. Ship it and pick the next job.")
    elif n >= 10 and clean / n < 0.3:
        print("  -> under 30% clean after 10 runs. Change the job or the setup, not the model.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=str(HERE / "runs.jsonl"))
    ap.add_argument("--label", default=None)
    ap.add_argument("--by-label", action="store_true", help="one block per label")
    args = ap.parse_args()
    runs = load(pathlib.Path(args.log), args.label)
    if not runs:
        raise SystemExit("no runs match that label")
    if args.by_label:
        groups = defaultdict(list)
        for r in runs:
            groups[r.get("label") or "(no label)"].append(r)
        for label, rs in groups.items():
            block(rs, label)
    else:
        block(runs, args.label or "all runs")
    last = runs[-1]
    print(f"\n  last run            {last['ts']} · {last.get('label') or '(no label)'} · "
          f"{'clean' if last['clean'] else 'not clean'}")


if __name__ == "__main__":
    main()
