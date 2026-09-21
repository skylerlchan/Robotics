"""Field and iron-fluid strength inside a thin fingertip pad. Reduced-order, no FEM.

  python magpad_field.py            prints the magnet-layout table and writes out/magpad_field.json

Frame: x across the pad (25 mm), y along it (40 mm), z out of the finger toward the part. Fluid fills 0 < z < T_PAD.
Magnets sit behind a thin wall, top face at z = -WALL, inside a 20 x 30 mm footprint.

1. Air field: uniformly magnetised blocks, magnetic-charge model (each pole face is a sheet of point charges).
   A steel backing plate is a mirror: image charges of opposite sign. The plate is treated as infinite, which flatters it a little.
2. Field inside the fluid: the pad is a thin permeable slab, so H_in,i = H_air,i / (1 + N_i (mu_r - 1)), with demagnetising
   factors N_i of a slab this shape, solved together with the fluid's own B-H curve. Field ALONG the pad gets in almost
   unreduced; field THROUGH the pad is cut several-fold. That is why the layouts differ so much.
3. Fluid law: Carlson's empirical fits for iron-in-oil MR fluids (LORD), "MR fluids and devices in the real world":
   tau_y = C * 271700 * phi^1.5239 * tanh(6.33e-6 H)  [Pa, H in A/m],  B = 1.91 phi^1.133 (1 - exp(-10.97 mu0 H)) + mu0 H.
"""
import json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MU0 = 4e-7*np.pi
PAD_X, PAD_Y, T_PAD, WALL = 0.025, 0.040, 0.005, 0.0008
MAG_X, MAG_Y = 0.020, 0.030
PHI, C_OIL = 0.32, 0.95                  # iron volume fraction (LORD MRF-132DG class); silicone-oil carrier
BR = 1.32                                # N42 remanence, tesla
RHO_MAG, RHO_STEEL, RHO_IRON, RHO_OIL = 7500.0, 7850.0, 7860.0, 970.0
PLATE_T = 0.001

def bh(H): return 1.91*PHI**1.133*(1 - np.exp(-10.97*MU0*H)) + MU0*H
def tau_y(H): return C_OIL*271700*PHI**1.5239*np.tanh(6.33e-6*H)

def demag(a, b, c):
    """Demagnetising factors of an a x b x c slab (c thin), oblate-spheroid estimate, in-plane share split by length."""
    m = np.sqrt(a*b)/c; s = np.sqrt(m*m - 1)
    nz = m*m/(m*m - 1)*(1 - np.arcsin(s/m)/s); rest = 1 - nz
    return np.array([rest*b/(a + b), rest*a/(a + b), nz])
N_DEMAG = demag(PAD_X, PAD_Y, T_PAD)

def block(center, size, mdir, h=0.00025):
    """Point charges for one block magnetised along +-axis `mdir` = (axis, sign). Returns (positions, charges in A*m)."""
    ax, sign = mdir; center = np.asarray(center, float); size = np.asarray(size, float)
    u, v = [i for i in range(3) if i != ax]; M = BR/MU0
    nu, nv = max(2, int(round(size[u]/h))), max(2, int(round(size[v]/h)))
    A, B = np.meshgrid((np.arange(nu) + .5)/nu*size[u] - size[u]/2, (np.arange(nv) + .5)/nv*size[v] - size[v]/2, indexing="ij")
    pts, qs = [], []
    for face in (+1, -1):
        p = np.zeros(A.shape + (3,)); p[..., u] = A; p[..., v] = B; p[..., ax] = face*size[ax]/2
        pts.append((p + center).reshape(-1, 3)); qs.append(np.full(nu*nv, face*sign*M*(size[u]/nu)*(size[v]/nv)))
    return np.vstack(pts), np.concatenate(qs)

def layout(kind, L=0.004, n=5, plate=True, sense=+1):
    """Charges for a named layout. single: one block magnetised through the pad. stripes: n strips along y, alternating
    up/down. halbach: n strips whose magnetisation rotates a quarter turn each step (field thrown to one side)."""
    zc = -WALL - L/2; P, Q = [], []
    if kind == "single":
        p, q = block((0, 0, zc), (MAG_X, MAG_Y, L), (2, +1)); P.append(p); Q.append(q)
    else:
        w = MAG_Y/n
        seq = [(2, +1), (1, +sense), (2, -1), (1, -sense)] if kind == "halbach" else [(2, +1), (2, -1)]
        for i in range(n):
            p, q = block((0, -MAG_Y/2 + (i + .5)*w, zc), (MAG_X, w, L), seq[i % len(seq)]); P.append(p); Q.append(q)
    P, Q = np.vstack(P), np.concatenate(Q)
    if plate:
        zp = -WALL - L; Pi = P.copy(); Pi[:, 2] = 2*zp - Pi[:, 2]; P, Q = np.vstack([P, Pi]), np.concatenate([Q, -Q])
    mass = MAG_X*MAG_Y*L*RHO_MAG + (MAG_X*MAG_Y*PLATE_T*RHO_STEEL if plate else 0)
    return P, Q, mass

def h_air(P, Q, pts, chunk=40):
    out = np.zeros_like(pts)
    for i in range(0, len(pts), chunk):
        r = pts[i:i + chunk, None, :] - P[None, :, :]; d3 = (np.einsum("ijk,ijk->ij", r, r))**1.5
        out[i:i + chunk] = np.einsum("j,ijk->ik", Q, r/d3[..., None])/(4*np.pi)
    return out

def h_inside(Hair):
    Hin = Hair/(1 + N_DEMAG*4.0)
    for _ in range(80):
        Hm = np.linalg.norm(Hin, axis=1) + 1e-9; mur = bh(Hm)/(MU0*Hm)
        Hin = 0.5*Hin + 0.5*Hair/(1 + N_DEMAG*(mur[:, None] - 1))
    return Hin

def pad_grid(nx=6, ny=10, nz=5, pitch=0.004):
    xs = (np.arange(nx) - (nx - 1)/2)*pitch; ys = (np.arange(ny) - (ny - 1)/2)*pitch; zs = (np.arange(nz) + .5)/nz*T_PAD
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij"); return np.stack([X, Y, Z], -1)          # (nx, ny, nz, 3)

def strength(kind, **kw):
    """Yield-stress map for a layout: per pin column (depth mean), per depth layer, pad mean, magnet mass."""
    P, Q, mass = layout(kind, **kw); G = pad_grid(); Hair = h_air(P, Q, G.reshape(-1, 3)); Hin = h_inside(Hair)
    tau = tau_y(np.linalg.norm(Hin, axis=1)).reshape(G.shape[:3]); Bair = MU0*np.linalg.norm(Hair, axis=1).reshape(G.shape[:3])
    return dict(tau_col=tau.mean(axis=2), tau_layer=tau.mean(axis=(0, 1)), tau_mean=float(tau.mean()), tau_weak_layer=float(tau.mean(axis=(0, 1)).min()),
                b_air_mean=float(Bair.mean()), b_air_layer=Bair.mean(axis=(0, 1)), magnet_g=mass*1000)

def best_halbach(**kw):
    a, b = strength("halbach", sense=+1, **kw), strength("halbach", sense=-1, **kw); return a if a["tau_mean"] >= b["tau_mean"] else b

def fluid_mass_g(): return PAD_X*PAD_Y*T_PAD*(PHI*RHO_IRON + (1 - PHI)*RHO_OIL)*1000

LAYOUTS = {
    "single 4 mm, no plate":   lambda: strength("single", L=0.004, plate=False),
    "single 4 mm + plate":     lambda: strength("single", L=0.004, plate=True),
    "stripes x5, 4 mm + plate": lambda: strength("stripes", L=0.004, n=5, plate=True),
    "stripes x3, 4 mm + plate": lambda: strength("stripes", L=0.004, n=3, plate=True),
    "halbach x5, 4 mm":        lambda: best_halbach(L=0.004, n=5, plate=False),
    "halbach x9, 4 mm":        lambda: best_halbach(L=0.004, n=9, plate=False),
    "halbach x5, 6 mm":        lambda: best_halbach(L=0.006, n=5, plate=False),
}
DEFAULT = "halbach x5, 4 mm"

if __name__ == "__main__":
    print(f"demag factors (x, y, z) = {np.round(N_DEMAG, 3)}   fluid in pad = {fluid_mass_g():.1f} g   saturation yield = {tau_y(1e9)/1000:.1f} kPa")
    print(f"{'layout':28s} {'magnet g':>8s} {'B air mT':>9s} {'tau mean':>9s} {'weak layer':>10s}   tau by depth, kPa (magnet side -> part side)")
    res = {}
    for name, f in LAYOUTS.items():
        s = f(); res[name] = {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in s.items()}
        print(f"{name:28s} {s['magnet_g']:8.1f} {s['b_air_mean']*1000:9.0f} {s['tau_mean']/1000:8.1f}k {s['tau_weak_layer']/1000:9.1f}k   " + " ".join(f"{t/1000:5.1f}" for t in s["tau_layer"]))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    json.dump(dict(phi=PHI, pad_mm=[PAD_X*1e3, PAD_Y*1e3, T_PAD*1e3], demag=N_DEMAG.tolist(), fluid_g=fluid_mass_g(), layouts=res), open(os.path.join(HERE, "out", "magpad_field.json"), "w"), indent=1)
