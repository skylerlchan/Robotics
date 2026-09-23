"""The UNIVERSAL gripper form: one bag pressed down onto an object, jammed, then lifted. Vacuum vs magnet.

  python magball.py                       headless suite -> out/magball.json (about 2 min on 10 cores)
  mjpython magball.py live magnet_top sphere45 30    watch one: bag type, object, press force in newtons
  bags: soft vacuum magnet_top magnet_shell     objects: sphere30 sphere45 sphere63 cube40 disc bolt

Why this is a different test from magpad.py
  A fingertip pad resists a SIDEWAYS pull; interlock comes from the part's own dents. A universal bag resists a
  pull straight DOWN, and the only thing stopping that is a skirt of jammed material that got below the object's
  widest point. So the bag must flow down around the object, not just dent.

What is modelled
  A 90 mm bag (Empire Robotics' small VERSABALL head) as 61 columns on a 9 mm hex grid, each with TWO degrees of
  freedom: it slides down (forming the skirt) and it splays outward (letting the object escape). Both freeze on lock.
  Resting shape is a dome, so the rim columns must travel to wrap anything.
  - Volume conservation ties the down-slides: pushing the middle in pushes the rim down. That is what makes a skirt.
  - Lock freezes both axes at their current place, each with its own yield force = tau_y x column area.
  - VACUUM also SHRINKS the bag on lock (the membrane is pulled in by ~1 atm), which pinches the object. Empire
    measured 35-48 kPa of pinching pressure. A magnet has no equivalent: it freezes the shape but never squeezes.
  - VACUUM on a smooth sealed face also gets real suction. Included for the disc only, at 20 kPa over the sealed area.
  Test: press down at the given force, lock, then pull the object straight down with a force ramping at 4 N/s.
  F_out = pull force when the object has dropped 8 mm, capped at 100 N.

tau_y for the magnet cases comes from magpad_field.py's field model at each column's actual depth below the magnet.
  magnet_top   = one 40 x 40 x 20 mm N42 block above a 90 mm bag. The naive "put a magnet on a jamming gripper" design.
  magnet_shell = the fix: a shallow 20 mm bag with the magnet right behind it, so the field reaches the contact face.

NOT modelled: the membrane between columns, air flow, iron settling, wear, steel objects being attracted, the time
either lock takes. Columns cannot shear sideways locally, which flatters both bags.
"""
import os, sys, json, time, math, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import magpad_field as F

PITCH, R_BAG, R_TIP = 0.009, 0.045, 0.0052
DT, MU = 0.0002, 0.8
KP_Z, KV_Z, KP_R, KV_R = 7000.0, 6.0, 5000.0, 5.0      # frozen-column stiffness, down axis and splay axis
K_MEMB_Z, K_MEMB_R = 12.0, 40.0                         # membrane: weak along the column, and a steady inward pull so the
                                                        # skirt hugs whatever it drapes over. That hug is what a real bag does.
RATE, F_MAX, T_LOCK, T_PULL = 4.0, 100.0, 2.5, 3.0
TAU_VACUUM, SHRINK_VAC, SUCTION_PA = 45e3, 0.0035, 20e3
A_COL = PITCH**2
RHO_MAG = 7500.0
PRESSES = [10.0, 30.0, 60.0]                            # Empire needed 22-66 N of push on this head size

def hexgrid():
    pts = [(0.0, 0.0)]
    for ring in range(1, 5):
        n = 6*ring
        for k in range(n):
            a = 2*math.pi*k/n
            x, y = ring*PITCH*math.cos(a), ring*PITCH*math.sin(a)
            if math.hypot(x, y) <= R_BAG - 0.004: pts.append((x, y))
    return pts
COLS = hexgrid()
def rest_z(x, y):                                       # domed underside, deepest in the middle
    s = math.hypot(x, y)/R_BAG; return -0.045*math.sqrt(max(0.0, 1 - s*s))

OBJECTS = {   # geoms, half-height (the object is held with its top at z = 0)
    "sphere30": ('<geom type="sphere" size="0.015"/>', 0.015),
    "sphere45": ('<geom type="sphere" size="0.0225"/>', 0.0225),
    "sphere63": ('<geom type="sphere" size="0.0315"/>', 0.0315),
    "cube40":   ('<geom type="box" size="0.02 0.02 0.02"/>', 0.02),
    "disc":     ('<geom type="cylinder" size="0.035 0.004"/>', 0.004),
    "bolt":     ('<geom type="cylinder" size="0.005 0.025"/>', 0.025),
}
WRAPPABLE, FLAT = ["sphere30", "sphere45", "sphere63", "cube40", "bolt"], ["disc"]
BAGS = ["soft", "vacuum", "magnet_top", "magnet_shell"]

# Pass thresholds, fixed before the first run.
THRESHOLDS = {
 "U1 magnet reaches the face": "at the contact face the fluid yields at >= 10 kPa, a quarter of vacuum's 45 kPa",
 "U2 it grips at all":         "at 30 N press, magnet_top lifts >= 9.8 N (0.5 kg with 2x margin) on >= 2 of 3 spheres",
 "U3 versus vacuum":           "at 30 N press, magnet_top >= 50% of the vacuum bag on >= 2 of 3 spheres",
 "U4 the shallow fix works":   "magnet_shell beats magnet_top on >= 3 of 5 wrappable objects",
 "U5 weight":                  "bag fill + magnet <= 400 g, against 81 g of coffee grounds plus an off-board pump",
}

def build(obj):
    geoms, hh = OBJECTS[obj]
    cols = ""
    for i, (x, y) in enumerate(COLS):
        r = math.hypot(x, y); ux, uy = (x/r, y/r) if r > 1e-9 else (1.0, 0.0)
        cols += (f'<body name="c{i}" pos="{x:.5f} {y:.5f} {rest_z(x, y):.5f}">'
                 f'<joint name="z{i}" class="down"/><joint name="r{i}" class="splay" axis="{ux:.4f} {uy:.4f} 0"/>'
                 f'<geom class="col"/></body>')
    act  = '<motor name="press" joint="bagz"/>'
    act += "".join(f'<general name="az{i}" joint="z{i}" gainprm="0" biastype="affine" biasprm="0 0 0"/>'
                   f'<general name="ar{i}" joint="r{i}" gainprm="0" biastype="affine" biasprm="0 0 0"/>' for i in range(len(COLS)))
    vol  = '<fixed name="vol">' + "".join(f'<joint joint="z{i}" coef="1"/>' for i in range(len(COLS))) + "</fixed>"
    return f"""<mujoco model="magball"><option timestep="{DT}" gravity="0 0 0" cone="elliptic" impratio="10" integrator="implicitfast"/>
 <visual><global offwidth="1280" offheight="960"/><quality shadowsize="2048"/></visual>
 <default><geom condim="3" friction="{MU} 0.005 0.0001" solref="0.002 1" solimp="0.95 0.99 0.0005"/>
  <default class="down"><joint type="slide" axis="0 0 -1" range="-0.030 0.030" stiffness="{K_MEMB_Z}" damping="0.6" armature="0.001" solreflimit="0.002 1"/></default>
  <default class="splay"><joint type="slide" range="-0.014 0.014" stiffness="{K_MEMB_R}" springref="-0.014" damping="0.6" armature="0.001" solreflimit="0.002 1"/></default>
  <default class="col"><geom type="sphere" size="{R_TIP}" mass="0.0012" contype="1" conaffinity="2" rgba=".92 .72 .3 1"/></default></default>
 <worldbody><light pos="0.12 -0.3 0.4" dir="-0.25 0.6 -0.8"/><light pos="-0.2 -0.2 0.35" dir="0.4 0.4 -0.8" diffuse=".4 .4 .4"/>
  <body name="obj" pos="0 0 {-0.045 - hh - 0.004:.5f}"><joint name="obj_z" type="slide" axis="0 0 1" damping="1"/>
   {geoms.replace('<geom ', '<geom contype="2" conaffinity="1" rgba=".55 .62 .7 1" mass="0.05" ')}</body>
  <body name="bag" pos="0 0 0"><joint name="bagz" type="slide" axis="0 0 -1" damping="150"/>
   <geom type="cylinder" size="{R_BAG} 0.004" pos="0 0 0.006" mass="0.2" contype="0" conaffinity="0" rgba=".55 .6 .66 1"/>{cols}</body></worldbody>
 <tendon>{vol}</tendon>
 <equality><joint name="hold" joint1="obj_z" polycoef="0 0 0 0 0"/><tendon name="eqv" tendon1="vol" solref="0.004 1"/></equality>
 <actuator>{act}</actuator></mujoco>"""

_TAU = {}
def tau_profile(kind):
    """Yield stress at each column tip, and the magnet's mass in grams.

    magnet_top:   one 40 x 40 x 20 mm N42 block sitting on top of the bag. Every column tip is 4 to 49 mm below it,
                  and the deepest point of the dome -- the part that touches the object first -- is the furthest away.
    magnet_shell: the only way to get field to the face of a bag this big: small magnets bedded into the skin itself,
                  following the dome 15 mm behind the contact face. Priced as 8 mm magnets over half the dome area.
    """
    if kind in _TAU: return _TAU[kind]
    old = (F.MAG_X, F.MAG_Y, F.PHI, F.N_DEMAG)
    F.PHI = 0.32; F.N_DEMAG = np.array([1/3, 1/3, 1/3])        # a roundish blob of fluid, not a thin slab
    if kind == "magnet_top":
        F.MAG_X = F.MAG_Y = 0.040
        P, Q, mass = F.layout("single", L=0.020, plate=False)
        pts = np.array([[x, y, 0.004 - rest_z(x, y)] for x, y in COLS])
        tau = F.tau_y(np.linalg.norm(F.h_inside(F.h_air(P, Q, pts)), axis=1))
    else:
        F.MAG_X = F.MAG_Y = 0.020
        P, Q, _ = F.layout("single", L=0.008, plate=False)
        pts = np.array([[0.0, 0.0, 0.015]])
        tau = np.full(len(COLS), F.tau_y(np.linalg.norm(F.h_inside(F.h_air(P, Q, pts)), axis=1))[0])
        mass = 2*math.pi*R_BAG**2 * 0.008 * 0.5 * RHO_MAG      # 8 mm magnets over half the dome
    F.MAG_X, F.MAG_Y, F.PHI, F.N_DEMAG = old
    _TAU[kind] = (tau, mass*1000); return _TAU[kind]

def fill_grams(kind):
    depth = 0.045 if kind != "magnet_shell" else 0.020
    vol = (2/3*math.pi*R_BAG**3) if kind != "magnet_shell" else (math.pi*R_BAG**2*depth)
    rho = F.PHI*F.RHO_IRON + (1 - F.PHI)*F.RHO_OIL if kind.startswith("magnet") else 450.0   # coffee grounds
    return vol*rho*1000

def trial(bag, obj, press, viewer=None, model=None, data=None):
    m = model or mujoco.MjModel.from_xml_string(build(obj)); d = data or mujoco.MjData(m)
    nid = lambda t, n: mujoco.mj_name2id(m, t, n); J, A, E, B = (mujoco.mjtObj.mjOBJ_JOINT, mujoco.mjtObj.mjOBJ_ACTUATOR, mujoco.mjtObj.mjOBJ_EQUALITY, mujoco.mjtObj.mjOBJ_BODY)
    N = len(COLS)
    zq = np.array([m.jnt_qposadr[nid(J, f"z{i}")] for i in range(N)]); za = np.array([nid(A, f"az{i}") for i in range(N)])
    rq = np.array([m.jnt_qposadr[nid(J, f"r{i}")] for i in range(N)]); ra = np.array([nid(A, f"ar{i}") for i in range(N)])
    cg = np.array([np.flatnonzero(m.geom_bodyid == nid(B, f"c{i}"))[0] for i in range(N)])
    pa = nid(A, "press"); bq = m.jnt_qposadr[nid(J, "bagz")]; hold = nid(E, "hold"); vol = nid(E, "eqv")
    ob = nid(B, "obj"); oz = m.jnt_qposadr[nid(J, "obj_z")]

    if bag == "vacuum":         tau = np.full(N, TAU_VACUUM); grams = fill_grams(bag)
    elif bag.startswith("magnet"): tau, mg = tau_profile(bag); grams = fill_grams(bag) + mg
    else:                       tau = np.zeros(N); grams = fill_grams("soft")
    locked = False; q_bag = None; fy_z = fy_r = np.full(N, 1e9)
    out = dict(bag=bag, obj=obj, press=press, grams=round(grams, 1), f_out=None, skirt_mm=None, curve=[])
    fpull = 0.0; nxt = T_PULL; yielding = np.zeros(N, bool); last = time.time(); z0 = None

    while True:
        t = d.time
        if not locked and t >= T_LOCK:
            if bag != "soft":
                fy_z = tau*A_COL*3.0; fy_r = tau*A_COL*3.0                       # same confinement factor as magpad
                m.actuator_gainprm[za, 0] = KP_Z; m.actuator_biasprm[za, 1] = -KP_Z; m.actuator_biasprm[za, 2] = -KV_Z
                m.actuator_gainprm[ra, 0] = KP_R; m.actuator_biasprm[ra, 1] = -KP_R; m.actuator_biasprm[ra, 2] = -KV_R
                d.ctrl[za] = d.qpos[zq] + (SHRINK_VAC if bag == "vacuum" else 0.0)   # vacuum pulls the membrane in: a real squeeze
                d.ctrl[ra] = d.qpos[rq] - (SHRINK_VAC if bag == "vacuum" else 0.0)
                locked = True
            q_bag = d.qpos[bq]
            below = d.qpos[zq] + np.array([-rest_z(x, y) for x, y in COLS])
            out["skirt_mm"] = float(np.percentile(below, 90)*1000)
            out["cols_touching"] = int(len({c.geom1 for c in d.contact[:d.ncon]} | {c.geom2 for c in d.contact[:d.ncon]}) - 1)
        if q_bag is not None: d.ctrl[pa] = float(np.clip(press + 4.0e4*(q_bag - d.qpos[bq]), 0, 120))
        else:                 d.ctrl[pa] = press
        if t >= T_PULL:
            if z0 is None: z0 = d.qpos[oz]                      # the press itself pushes the object down; measure the drop from here
            d.eq_active[hold] = 0; fpull = min(F_MAX, RATE*(t - T_PULL))
            suck = SUCTION_PA*math.pi*0.035**2 if (bag == "vacuum" and obj == "disc") else 0.0
            d.xfrc_applied[ob, 2] = -fpull + suck
        if locked:
            for q, a, fy, kp in ((zq, za, fy_z, KP_Z), (rq, ra, fy_r, KP_R)):
                cur = d.qpos[q]; err = d.ctrl[a] - cur; lim = fy/kp
                if q is zq: yielding = np.abs(err) > lim
                d.ctrl[a] = cur + np.clip(err, -lim, lim)
        mujoco.mj_step(m, d); drop = (z0 - d.qpos[oz]) if z0 is not None else 0.0
        if t >= nxt: out["curve"].append((round(fpull, 2), round(drop*1000, 3))); nxt += 0.1
        if z0 is not None and drop > 0.008: out["f_out"] = fpull; break
        if t > T_PULL + F_MAX/RATE + 0.3: break
        if viewer is not None and time.time() - last > 1/60:
            m.geom_rgba[cg] = np.where(yielding[:, None], (.85, .25, .2, 1), (.2, .35, .85, 1) if locked else (.92, .72, .3, 1))
            viewer.sync(); last = time.time()
            if not viewer.is_running(): break
    out["held_to_cap"] = out["f_out"] is None; out["f_out"] = F_MAX if out["f_out"] is None else out["f_out"]
    return out

def _run(a): return trial(*a)

def evaluate(R):
    g = lambda b, o, p=30.0: next(r for r in R if r["bag"] == b and r["obj"] == o and r["press"] == p)
    sph = ["sphere30", "sphere45", "sphere63"]; V = {}
    tau_t, mg_t = tau_profile("magnet_top"); tau_s, mg_s = tau_profile("magnet_shell")
    face_t, face_s = tau_t.min()/1000, tau_s.min()/1000
    V["U1 magnet reaches the face"] = (face_t >= 10, f"magnet_top {face_t:.1f} kPa at the face ({tau_t.mean()/1000:.1f} mean); magnet_shell {face_s:.1f} kPa; vacuum 45.0")
    k = [g("magnet_top", o)["f_out"] for o in sph]
    V["U2 it grips at all"] = (sum(x >= 9.8 for x in k) >= 2, "magnet_top lift: " + ", ".join(f"{o} {x:.1f} N" for o, x in zip(sph, k)))
    k = [g("magnet_top", o)["f_out"]/max(g("vacuum", o)["f_out"], 1e-6) for o in sph]
    V["U3 versus vacuum"] = (sum(x >= 0.5 for x in k) >= 2, "magnet_top / vacuum: " + ", ".join(f"{o} {x:.2f}" for o, x in zip(sph, k)))
    k = [(o, g("magnet_shell", o)["f_out"], g("magnet_top", o)["f_out"]) for o in WRAPPABLE]
    V["U4 the shallow fix works"] = (sum(a > b for _, a, b in k) >= 3, "shell vs top: " + ", ".join(f"{o} {a:.0f}/{b:.0f} N" for o, a, b in k))
    tot = fill_grams("magnet_top") + mg_t
    V["U5 weight"] = (tot <= 400, f"magnet_top {fill_grams('magnet_top'):.0f} g fill + {mg_t:.0f} g magnet = {tot:.0f} g; vacuum bag {fill_grams('vacuum'):.0f} g of grounds")
    return {k: dict(passed=bool(p), detail=t, rule=THRESHOLDS[k]) for k, (p, t) in V.items()}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        import mujoco.viewer
        bag, obj, press = (sys.argv[2:] + ["magnet_top", "sphere45", "30"][len(sys.argv) - 2:])[:3]
        print("amber = soft, blue = jammed, red = a column creeping past its yield force")
        m0 = mujoco.MjModel.from_xml_string(build(obj)); d0 = mujoco.MjData(m0)
        with mujoco.viewer.launch_passive(m0, d0) as v:
            v.cam.lookat[:] = (0, 0, -0.05); v.cam.distance = 0.30; v.cam.azimuth = 90; v.cam.elevation = -10
            r = trial(bag, obj, float(press), viewer=v, model=m0, data=d0)
            print(f"{bag} on {obj} at {press} N press: lifts {r['f_out']:.1f} N" + (" (capped)" if r["held_to_cap"] else "") + f", skirt {r['skirt_mm']:.1f} mm")
            while v.is_running(): time.sleep(0.05)
        sys.exit()

    from multiprocessing import Pool
    jobs = [(b, o, p) for b in BAGS for o in OBJECTS for p in PRESSES]
    t0 = time.time()
    with Pool(min(10, os.cpu_count() or 4)) as pool: R = pool.map(_run, jobs, chunksize=1)
    verdict = evaluate(R); os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    json.dump(dict(params=dict(r_bag=R_BAG, cols=len(COLS), pitch=PITCH, tau_vacuum=TAU_VACUUM, shrink=SHRINK_VAC, suction=SUCTION_PA),
                   tau={k: dict(per_col=tau_profile(k)[0].tolist(), magnet_g=tau_profile(k)[1]) for k in ("magnet_top", "magnet_shell")},
                   thresholds=verdict, trials=R), open(os.path.join(HERE, "out", "magball.json"), "w"), indent=1)
    print(f"{len(R)} trials in {time.time() - t0:.0f} s, {len(COLS)} columns per bag\n")
    for p in PRESSES:
        print(f"press {p:g} N   lift force before the object drops 8 mm, newtons ('+' = never came off)")
        print(f"{'':10s}" + "".join(f"{b:>15s}" for b in BAGS))
        for o in OBJECTS:
            row = [next(r for r in R if r["bag"] == b and r["obj"] == o and r["press"] == p) for b in BAGS]
            print(f"{o:10s}" + "".join(f"{r['f_out']:12.1f}{'+' if r['held_to_cap'] else ' '}  " for r in row))
        print()
    print("skirt depth at lock (how far the bag got below its own resting dome), mm:")
    for b in BAGS:
        print(f"  {b:13s}" + "  ".join(f"{o} {next(r for r in R if r['bag']==b and r['obj']==o and r['press']==30.0)['skirt_mm']:5.1f}" for o in ("sphere45", "cube40", "disc")))
    print()
    for k, v in verdict.items(): print(f"{'PASS' if v['passed'] else 'FAIL'}  {k}: {v['detail']}")
