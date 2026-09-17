"""What one overhead depth camera can and cannot tell you about a towel.

Two measurements, both on the same cell as laundry.py, both with the real MuJoCo cloth and the real rendered depth image.

  A  corner localisation: where are the towel's four corners?  Asked at three levels of mess.
  B  crease or free edge: after a towel has been folded in half, which of the two long edges is the open one?
     Getting this wrong makes the second fold undo the first, so it is not a detail.

  python perception.py 30
"""
import os, sys, math, json, time, numpy as np
import laundry as L

def corner_test(seeds, level):
    errs = []; t0 = time.time()
    for s in seeds:
        c = L.Cell(seed=s + 1000*L.LEVELS.index(level)); c.crumple(level)
        o = c.observe("depth")
        if o is None: errs.append(float("nan")); continue
        truth = c.verts()[c.corner_ids][:, :2]
        a = min(float(np.linalg.norm(np.roll(o["corners"], k, axis=0) - truth, axis=1).mean()) for k in range(4))
        b = min(float(np.linalg.norm(np.roll(o["corners"][::-1], k, axis=0) - truth, axis=1).mean()) for k in range(4))
        errs.append(min(a, b)*1000)
    e = np.array([x for x in errs if np.isfinite(x)])
    return dict(level=level, n=len(e), mean_mm=round(float(e.mean()), 1), median_mm=round(float(np.median(e)), 1),
                p90_mm=round(float(np.percentile(e, 90)), 1), max_mm=round(float(e.max()), 1),
                under_20mm=round(float((e < 20).mean()), 3), seconds=round(time.time()-t0, 1), errors=[round(x, 1) for x in errs])

def lay_folded(cell, ang, off, mess=0.0):
    """place the towel already folded in half: crease along one long edge, the two free edges along the other"""
    rest = cell.vp0[:, :2] - [L.CX, L.CY]
    loc = rest.copy(); top = loc[:, 1] > 1e-9
    loc[top, 1] = -loc[top, 1]                       # the +y half is folded over onto the -y half
    c, s = math.cos(ang), math.sin(ang)
    w = loc @ np.array([[c, -s], [s, c]]).T
    z = np.where(top, L.TABLE_Z + 0.016, L.TABLE_Z + 0.006)
    if mess:
        rng = np.random.default_rng(int(abs(ang)*1e6) % 99999)
        w = w + rng.normal(0, mess, w.shape); z = z + np.abs(rng.normal(0, mess*0.6, len(z)))
    for i in range(L.N*L.N): cell.set_vert(i, [w[i, 0] + L.CX + off[0], w[i, 1] + L.CY + off[1], z[i]])
    import mujoco; mujoco.mj_forward(cell.m, cell.d); cell.step(1.2)

def crease_test(seeds, mess=0.0):
    right = 0; rows = []; t0 = time.time()
    for s in seeds:
        c = L.Cell(seed=s); rng = np.random.default_rng(s)
        lay_folded(c, rng.uniform(-0.35, 0.35), rng.uniform(-0.03, 0.03, 2), mess=mess)
        o = c.observe("depth")
        if o is None: continue
        f, hf, _, _ = L.fold_axes(o)
        guess = c.free_side("depth", o["centre"], f, hf); truth = c.free_side("oracle", o["centre"], f, hf)
        ok = bool(guess == truth); right += ok
        cl = c.cloud; sgn = (cl[:, :2] - o["centre"]) @ f; band = 0.30*hf
        hi = cl[sgn > hf - band, 2]; lo = cl[sgn < -hf + band, 2]
        rows.append(dict(seed=s, ok=ok, step_mm=round(float(hi.mean()-lo.mean())*1000, 2) if len(hi) > 8 and len(lo) > 8 else None))
    return dict(mess_mm=round(mess*1000, 1), n=len(rows), correct=right, accuracy=round(right/max(len(rows), 1), 3), seconds=round(time.time()-t0, 1), rows=rows)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20; seeds = list(range(n))
    out = dict(corners=[], crease=None, towel_mm=round(L.SIDE*1000), camera=dict(height_mm=round((L.CAM_Z-L.TABLE_Z)*1000), pixels=L.CAM_PIX,
               mm_per_pixel=round((L.CAM_Z-L.TABLE_Z)*2*math.tan(math.radians(L.CAM_FOVY)/2)/L.CAM_PIX*1000, 2)))
    for lv in L.LEVELS:
        r = corner_test(seeds, lv); out["corners"].append(r)
        print(f"corners {lv:8s} n={r['n']:3d} mean {r['mean_mm']:6.1f} mm  median {r['median_mm']:6.1f}  p90 {r['p90_mm']:6.1f}  max {r['max_mm']:6.1f}  within 20 mm: {r['under_20mm']*100:.0f}%", flush=True)
        json.dump(out, open(os.path.join(L.OUT, "perception.json"), "w"), indent=1)
    out["crease"] = []
    for mess in (0.0, 0.008, 0.016):
        cr = crease_test(seeds, mess); out["crease"].append(cr)
        print(f"crease vs free edge, fold messiness {mess*1000:4.1f} mm: {cr['correct']}/{cr['n']} = {cr['accuracy']*100:3.0f}%  "
              f"(coin flip 50%)  height step {np.mean([r['step_mm'] for r in cr['rows'] if r['step_mm'] is not None]):+.2f} mm", flush=True)
        json.dump(out, open(os.path.join(L.OUT, "perception.json"), "w"), indent=1)
    json.dump(out, open(os.path.join(L.OUT, "perception.json"), "w"), indent=1)
