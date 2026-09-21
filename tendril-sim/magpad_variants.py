"""Lighter pads: how much holding force is lost when the magnet-locked pad gets thinner or the iron is diluted.

  python magpad_variants.py        -> out/magpad_variants.json (about 1 min)

Same model as magpad.py, position-held gripper, 5 N pinch, the four shaped parts. The fluid law is still Carlson's
iron-in-oil fit. Dry iron grains are reported to jam stiffer than oil-based fluid, so for a dry fill these are low estimates.
"""
import os, json, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = {   # pad thickness m, magnet thickness m, iron volume fraction
    "5 mm pad, 4 mm magnet (baseline)": (0.005, 0.004, 0.32),
    "3 mm pad, 3 mm magnet":            (0.003, 0.003, 0.32),
    "3 mm pad, 2 mm magnet":            (0.003, 0.002, 0.32),
    "5 mm pad, iron diluted to 20%":    (0.005, 0.004, 0.20),
}
PARTS = ["rod_cross", "ball", "egg", "ribbed"]

def run(job):
    name, pad, part = job; t, L, phi = VARIANTS[name]
    import magpad_field as F, magpad as M
    F.T_PAD, F.PHI = t, phi; F.N_DEMAG = F.demag(F.PAD_X, F.PAD_Y, t)
    F.LAYOUTS["variant"] = lambda: F.strength("single", L=L, plate=True); M._field.clear()
    M.STROKE = t/2; M.KP_PIN = 9600.0*0.005/t; M.K_RUBBER = 960.0*0.005/t
    r = M.trial(pad, part, 5.0, magnet="variant", grip="position"); s = M.field("variant")
    return dict(variant=name, pad=pad, part=part, f_firm=r["f_firm"], f_out=r["f_out"], tau_mean_kpa=s["tau_mean"]/1000, tau_part_side_kpa=s["tau_weak_layer"]/1000,
                fluid_g=F.fluid_mass_g(), magnet_g=s["magnet_g"], dry_iron_g=F.PAD_X*F.PAD_Y*t*0.58*F.RHO_IRON*1000)

if __name__ == "__main__":
    jobs = [(v, p, o) for v in VARIANTS for p in ("rubber", "mr") for o in PARTS]
    with Pool(min(10, os.cpu_count() or 4)) as pool: R = pool.map(run, jobs, chunksize=1)
    json.dump(R, open(os.path.join(HERE, "out", "magpad_variants.json"), "w"), indent=1)
    print(f"{'variant':36s} {'fill g':>7s} {'magnet g':>8s} {'total g':>8s} {'kPa mean':>9s} {'kPa part side':>13s}   pull-out N, magnet pad (rubber): " + "  ".join(PARTS))
    for v in VARIANTS:
        a = [r for r in R if r["variant"] == v]; m = a[0]
        cell = lambda o: f"{next(r for r in a if r['pad'] == 'mr' and r['part'] == o)['f_out']:5.1f} ({next(r for r in a if r['pad'] == 'rubber' and r['part'] == o)['f_out']:4.1f})"
        print(f"{v:36s} {m['fluid_g']:7.1f} {m['magnet_g']:8.1f} {m['fluid_g'] + m['magnet_g']:8.1f} {m['tau_mean_kpa']:9.1f} {m['tau_part_side_kpa']:13.1f}   " + "  ".join(cell(o) for o in PARTS))
    print("dry packed iron (58% by volume) instead of fluid would weigh: " + ", ".join(f"{t*1000:.0f} mm pad {0.025*0.040*t*0.58*7860*1000:.1f} g" for t in (0.003, 0.005)))
