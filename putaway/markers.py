#!/usr/bin/env python
"""Print the markers for a job: one per object, one per bin, labelled.

    python markers.py                # writes markers.png (A4, 40 mm markers)
    python markers.py --mm 60        # bigger markers, easier from far away

Print at 100% scale (no "fit to page"), cut out, tape the object markers on top of
each object and the bin markers on the front face of each bin. The camera has to
see every marker from its fixed spot, so test with `score.py watch` before you
start a run.
"""
from __future__ import annotations

import argparse
import pathlib
import tomllib

import cv2
import numpy as np

HERE = pathlib.Path(__file__).parent
DPI = 300
A4 = (int(8.27 * DPI), int(11.69 * DPI))  # width, height in px


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--job", default=str(HERE / "job.toml"))
    ap.add_argument("--mm", type=float, default=None, help="marker size in mm (default: job's marker_mm)")
    ap.add_argument("--out", default=str(HERE / "markers.png"))
    args = ap.parse_args()

    with open(args.job, "rb") as f:
        job = tomllib.load(f)
    mm = args.mm or float(job.get("marker_mm", 40))
    dic = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, job.get("dict", "DICT_4X4_50")))
    px = int(mm / 25.4 * DPI)

    items = [(int(k), v.get("name", f"bin {k}"), "bin") for k, v in job.get("bins", {}).items()]
    items += [(int(k), v.get("name", f"object {k}"), "object") for k, v in job.get("objects", {}).items()]
    items.sort(key=lambda t: (t[2] != "bin", t[0]))

    page = np.full((A4[1], A4[0], 3), 255, np.uint8)
    pad, label_h = int(0.28 * DPI), int(0.30 * DPI)
    cell_w, cell_h = px + pad, px + label_h + pad
    cols = max(1, (A4[0] - pad) // cell_w)
    for i, (mid, name, kind) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = pad + c * cell_w, pad + r * cell_h
        if y + cell_h > A4[1]:
            print(f"warning: {name} and later markers did not fit on one page")
            break
        img = cv2.cvtColor(cv2.aruco.generateImageMarker(dic, mid, px), cv2.COLOR_GRAY2BGR)
        page[y:y + px, x:x + px] = img
        cv2.rectangle(page, (x - 6, y - 6), (x + px + 6, y + px + 6), (200, 200, 200), 1)
        cv2.putText(page, f"{mid}  {name}", (x, y + px + int(0.19 * DPI)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 30, 30), 2)
        cv2.putText(page, kind, (x, y + px + int(0.30 * DPI) - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)
    cv2.putText(page, f"{job.get('name', 'put-away')} — print at 100%, markers are {mm:.0f} mm",
                (pad, int(0.22 * DPI)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (90, 90, 90), 2)
    cv2.imwrite(args.out, page)
    print(f"wrote {args.out} — {len(items)} markers at {mm:.0f} mm")


if __name__ == "__main__":
    main()
