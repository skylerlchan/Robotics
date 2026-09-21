"""Magnet-locked fingertip pad: pull-out test. Reduced-order MuJoCo model, scripted, no learning.

  python magpad.py                          headless suite -> out/magpad.json (about 2 min on 10 cores)
  mjpython magpad.py live mr ball 5 position    watch one trial: pad type, object, pinch force in newtons, force|position grip
  pads: rigid rubber mr_off mr vacuum       objects: plate rod_axial rod_cross ball egg ribbed

What is modelled
  Two opposing fingers pinch a part with a fixed force. Each fingertip pad is a 6 x 10 array of pins on 4 mm pitch, each
  pin a column of pad material that slides in and out by +-2.5 mm (5 mm pad).
  - A fluid bag keeps its volume: the pins of one pad are tied so that pushing some in pushes the others out. That is what
    makes a bag wrap around a part.
  - LOCK freezes every pin where it is. A locked pin is stiff until the force on it passes its yield force, then it creeps
    (elastic-perfectly-plastic). Yield force = C_IND * tau_y * pin area. tau_y per pin comes from magpad_field.py.
  - The whole pad can also shear as a layer along the pull direction. Locked, it yields at tau_weak_layer * pad area; after
    3 mm of travel the membrane goes taut and carries the load.
  Test: hold the part still, close with the pinch force, lock, let go of the part, pull it along the pad with a force that
  ramps at 4 N/s. F_firm = pull force when the part has moved 1 mm. F_out = pull force when it has moved 8 mm (capped at 100 N).
  Two kinds of gripper: grip="force" keeps pushing with the pinch force and can be wedged open (air, or current control).
  grip="position" closes with the pinch force, then freezes the finger where it is, up to a 40 N stall (a geared servo).
  The thresholds were fixed for grip="force". The position case was added after seeing that run, so it is reported apart.

What is NOT modelled: the membrane between pins, iron settling, wear, steel parts being attracted, heat, the time the magnet
takes to switch. C_IND (how much harder a confined yield-stress layer is to indent than to shear) is the biggest unknown:
1.73 is a free-standing column, 5.14 a fully confined punch; 3 is used, and the sweep shows both ends.
"""
import os, sys, json, time, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import magpad_field as F

PITCH, NY, NZ, R_TIP, STROKE, SHEAR_TRAVEL = 0.004, 6, 10, 0.0023, 0.0025, 0.003
DT, MU = 0.0002, 0.8
KP_PIN, KV_PIN, KP_SHEAR, KV_SHEAR = 9600.0, 7.0, 2.0e5, 180.0   # locked stiffness: ~3 MPa layer modulus over one pin / over the pad
K_MEMBRANE, K_RUBBER = 15.0, 960.0                                 # N/m per pin: bag membrane; 5 mm of 0.3 MPa silicone
C_IND, TAU_VACUUM = 3.0, 45e3                                      # VERSABALL reports 35-48 kPa pinching pressure
RATE, F_MAX, T_LOCK, T_PULL = 4.0, 100.0, 2.5, 3.0
KP_FINGER, F_STALL = 5.0e4, 40.0                                  # position-held finger: servo + linkage stiffness, and the most it can push
A_PIN, A_PAD = PITCH**2, NY*NZ*PITCH**2
MAGNET = "single 4 mm + plate"

PADS = ["rigid", "rubber", "mr_off", "mr", "vacuum"]
OBJECTS = {   # geoms, half-thickness along the pinch axis. Pinch is along x, pull is along -z.
    "plate":     ('<geom type="box" size="0.003 0.025 0.04"/>', 0.003),
    "rod_axial": ('<geom type="cylinder" size="0.008 0.04"/>', 0.008),
    "rod_cross": ('<geom type="cylinder" size="0.008 0.03" euler="90 0 0"/>', 0.008),
    "ball":      ('<geom type="sphere" size="0.014"/>', 0.014),
    "egg":       ('<geom type="ellipsoid" size="0.015 0.015 0.021"/>', 0.015),
    "ribbed":    ('<geom type="box" size="0.005 0.02 0.03"/>' + "".join(f'<geom type="capsule" size="0.002" fromto="{sx*0.005} -0.02 {z} {sx*0.005} 0.02 {z}"/>' for sx in (-1, 1) for z in (-0.012, 0.0, 0.012)), 0.007),
}
SHAPED, CONTROLS = ["rod_cross", "ball", "egg", "ribbed"], ["plate", "rod_axial"]
PINCHES = [2.0, 5.0, 15.0]

# Pass thresholds, fixed before the first pull-out run. "light pinch" = 5 N, about what a hobby-servo gripper holds all day.
THRESHOLDS = {
    "T1 fluid strength":  "pad-mean yield stress >= 10 kPa from a magnet of <= 30 g that fits behind a 25 x 40 mm pad",
    "T2 worth it":        "at 5 N pinch, locked mr pad holds >= 2x the firm-hold force of a plain rubber pad on >= 3 of 4 shaped parts",
    "T3 honest controls": "on the flat plate and the axial rod (nothing to lock onto), mr pull-out is within 25% of rubber",
    "T4 payload":         "at 5 N pinch, mr pull-out >= 9.8 N (0.5 kg with 2x margin) on >= 3 of 4 shaped parts",
    "T5 versus vacuum":   "at 5 N pinch, mr pull-out >= 50% of the vacuum-jammed pad on >= 3 of 4 shaped parts",
    "T6 weight":          "fluid + magnet <= 40 g per finger",
}

def build(obj):
    geoms, hx = OBJECTS[obj]; x0 = hx + F.T_PAD + STROKE + 0.004
    def finger(side, sx):
        pins = "".join(f'<body name="{side}{i}_{j}" pos="{sx*(F.T_PAD - R_TIP):.5f} {(i - (NY - 1)/2)*PITCH:.5f} {(j - (NZ - 1)/2)*PITCH:.5f}">'
                       f'<joint name="{side}{i}_{j}" class="pin" axis="{sx} 0 0"/><geom class="pin"/></body>' for i in range(NY) for j in range(NZ))
        return (f'<body name="finger{side}" pos="{-sx*x0:.5f} 0 0"><joint name="f{side}" type="slide" axis="{sx} 0 0" damping="200"/>'
                f'<geom type="box" size="0.004 0.016 0.026" pos="{-sx*0.004} 0 0" mass="0.1" contype="0" conaffinity="0" rgba=".55 .6 .66 1"/>'
                f'<body name="pad{side}"><joint name="shear{side}" type="slide" axis="0 0 1" range="{-SHEAR_TRAVEL} {SHEAR_TRAVEL}" stiffness="300" damping="5" armature="0.02" solreflimit="0.002 1"/>'
                f'<geom type="box" size="0.0006 0.013 0.021" mass="0.02" contype="0" conaffinity="0" rgba=".2 .5 .38 1"/>{pins}</body></body>')
    act = "".join(f'<motor name="f{s}" joint="f{s}"/>' for s in "LR")
    act += "".join(f'<general name="a{s}{i}_{j}" joint="{s}{i}_{j}" gainprm="0" biastype="affine" biasprm="0 0 0"/>' for s in "LR" for i in range(NY) for j in range(NZ))
    act += "".join(f'<general name="ashear{s}" joint="shear{s}" gainprm="0" biastype="affine" biasprm="0 0 0"/>' for s in "LR")
    ten = "".join(f'<fixed name="vol{s}">' + "".join(f'<joint joint="{s}{i}_{j}" coef="1"/>' for i in range(NY) for j in range(NZ)) + "</fixed>" for s in "LR")
    return f"""<mujoco model="magpad"><option timestep="{DT}" gravity="0 0 0" cone="elliptic" impratio="10" integrator="implicitfast"/>
    <visual><global offwidth="1280" offheight="960"/><quality shadowsize="2048"/></visual>
    <default><geom condim="3" friction="{MU} 0.005 0.0001" solref="0.002 1" solimp="0.95 0.99 0.0005"/>
      <default class="pin"><joint type="slide" range="{-STROKE} {STROKE}" stiffness="{K_MEMBRANE}" damping="0.5" armature="0.001" solreflimit="0.002 1"/>
        <geom type="sphere" size="{R_TIP}" mass="0.00026" contype="1" conaffinity="2" rgba=".92 .72 .3 1"/></default></default>
    <worldbody><light pos="0.1 -0.3 0.4" dir="-0.2 0.6 -0.8"/><light pos="-0.2 -0.2 0.3" dir="0.4 0.4 -0.8" diffuse=".4 .4 .4"/>
      <body name="obj"><joint name="obj_z" type="slide" axis="0 0 1" damping="1"/>{geoms.replace("<geom ", '<geom contype="2" conaffinity="1" rgba=".55 .62 .7 1" mass="0.02" ')}</body>
      {finger("L", 1)}{finger("R", -1)}</worldbody>
    <tendon>{ten}</tendon>
    <equality><joint name="hold" joint1="obj_z" polycoef="0 0 0 0 0"/><tendon name="eqL" tendon1="volL" solref="0.004 1"/><tendon name="eqR" tendon1="volR" solref="0.004 1"/></equality>
    <actuator>{act}</actuator></mujoco>"""

_field = {}
def field(name):
    if name not in _field: _field[name] = F.LAYOUTS[name]()
    return _field[name]

def trial(pad, obj, pinch, c_ind=C_IND, magnet=MAGNET, grip="force", viewer=None, model=None, data=None):
    m = model or mujoco.MjModel.from_xml_string(build(obj)); d = data or mujoco.MjData(m)
    nid = lambda t, n: mujoco.mj_name2id(m, t, n); J, A, E, B, G = (mujoco.mjtObj.mjOBJ_JOINT, mujoco.mjtObj.mjOBJ_ACTUATOR, mujoco.mjtObj.mjOBJ_EQUALITY, mujoco.mjtObj.mjOBJ_BODY, mujoco.mjtObj.mjOBJ_GEOM)
    names = [f"{s}{i}_{j}" for s in "LR" for i in range(NY) for j in range(NZ)]
    pj = np.array([nid(J, n) for n in names]); pq = m.jnt_qposadr[pj]; pa = np.array([nid(A, "a" + n) for n in names])
    pg = np.array([np.flatnonzero(m.geom_bodyid == nid(B, n))[0] for n in names])
    sq = np.array([m.jnt_qposadr[nid(J, "shear" + s)] for s in "LR"]); sa = np.array([nid(A, "ashear" + s) for s in "LR"])
    fa = [nid(A, "fL"), nid(A, "fR")]; fq = np.array([m.jnt_qposadr[nid(J, "f" + s)] for s in "LR"]); q_hold = None; hold = nid(E, "hold"); vols = [nid(E, "eqL"), nid(E, "eqR")]; ob = nid(B, "obj"); oz = m.jnt_qposadr[nid(J, "obj_z")]

    fluid = pad in ("mr_off", "mr", "vacuum")
    if pad == "rubber": m.jnt_stiffness[pj] = K_RUBBER
    if not fluid:
        for e in vols: d.eq_active[e] = 0
    if pad == "mr": s = field(magnet); tau_pin = np.tile(s["tau_col"].reshape(-1), 2); tau_shear = s["tau_weak_layer"]
    elif pad == "vacuum": tau_pin = np.full(len(pj), TAU_VACUUM); tau_shear = TAU_VACUUM
    fy_pin = np.full(len(pj), 1e9); fy_shear = 1e9; pin_locked = shear_locked = False

    def lock(pins, shear):
        nonlocal pin_locked, shear_locked
        if pins: m.actuator_gainprm[pa, 0] = KP_PIN; m.actuator_biasprm[pa, 1] = -KP_PIN; m.actuator_biasprm[pa, 2] = -KV_PIN; d.ctrl[pa] = d.qpos[pq]; pin_locked = True
        if shear: m.actuator_gainprm[sa, 0] = KP_SHEAR; m.actuator_biasprm[sa, 1] = -KP_SHEAR; m.actuator_biasprm[sa, 2] = -KV_SHEAR; d.ctrl[sa] = d.qpos[sq]; shear_locked = True
    if pad == "rigid": lock(True, True)
    if pad == "rubber": lock(False, True)       # solid rubber does not flow sideways

    d.ctrl[fa] = pinch; out = dict(pad=pad, obj=obj, pinch=pinch, c_ind=c_ind, grip=grip, magnet=magnet if pad == "mr" else None, f_firm=None, f_out=None, curve=[])
    last_sync = time.time(); next_sample = T_PULL; fpull = 0.0; yielding = np.zeros(len(pj), bool)
    while True:
        t = d.time
        if fluid and pad != "mr_off" and not pin_locked and t >= T_LOCK:
            fy_pin = c_ind*tau_pin*A_PIN; fy_shear = tau_shear*A_PAD; lock(True, True)
            out["pins_touching"] = int(len({c.geom1 for c in d.contact[:d.ncon]} | {c.geom2 for c in d.contact[:d.ncon]}) - 1)
            out["wrap_mm"] = float((d.qpos[pq].max() - d.qpos[pq].min())*1000)
        if grip == "position" and t >= T_LOCK:
            if q_hold is None: q_hold = d.qpos[fq].copy()
            d.ctrl[fa] = np.clip(pinch + KP_FINGER*(q_hold - d.qpos[fq]), 0, F_STALL)
        if t >= T_PULL:
            d.eq_active[hold] = 0; fpull = min(F_MAX, RATE*(t - T_PULL)); d.xfrc_applied[ob, 2] = -fpull
        if pin_locked:      # plastic creep: the set-point follows once the pin is loaded past its yield force
            q = d.qpos[pq]; err = d.ctrl[pa] - q; lim = fy_pin/KP_PIN; yielding = np.abs(err) > lim; d.ctrl[pa] = q + np.clip(err, -lim, lim)
        if shear_locked:
            q = d.qpos[sq]; lim = fy_shear/KP_SHEAR; d.ctrl[sa] = q + np.clip(d.ctrl[sa] - q, -lim, lim)
        mujoco.mj_step(m, d); z = -d.qpos[oz]
        if t >= next_sample: out["curve"].append((round(fpull, 2), round(z*1000, 3))); next_sample += 0.1
        if out["f_firm"] is None and z > 0.001: out["f_firm"] = fpull
        if z > 0.008: out["f_out"] = fpull; break
        if t > T_PULL + F_MAX/RATE + 0.3: break
        if viewer is not None and time.time() - last_sync > 1/60:
            m.geom_rgba[pg] = np.where(yielding[:, None], (.85, .25, .2, 1), (.2, .35, .85, 1) if pin_locked and pad != "rigid" else (.92, .72, .3, 1))
            viewer.sync(); last_sync = time.time()
            if not viewer.is_running(): break
    out["held_to_cap"] = out["f_out"] is None; out["f_out"] = F_MAX if out["f_out"] is None else out["f_out"]; out["f_firm"] = out["f_out"] if out["f_firm"] is None else out["f_firm"]
    return out

def _run(a): return trial(*a[0], **a[1])

def evaluate(R, grip="force"):
    g = lambda pad, obj, pinch=5.0, c=C_IND, mag=MAGNET: next(r for r in R if r["grip"] == grip and r["pad"] == pad and r["obj"] == obj and r["pinch"] == pinch and r["c_ind"] == c and (r["magnet"] in (None, mag)))
    s = field(MAGNET); grams = F.fluid_mass_g() + s["magnet_g"]; V = {}
    V["T1 fluid strength"] = (s["tau_mean"] >= 10e3 and s["magnet_g"] <= 30, f"{s['tau_mean']/1000:.1f} kPa mean from a {s['magnet_g']:.0f} g magnet ({MAGNET})")
    k = [g("mr", o)["f_firm"]/max(g("rubber", o)["f_firm"], 1e-6) for o in SHAPED]; V["T2 worth it"] = (sum(x >= 2 for x in k) >= 3, "firm-hold gain over rubber: " + ", ".join(f"{o} {x:.2f}x" for o, x in zip(SHAPED, k)))
    k = [g("mr", o)["f_out"]/g("rubber", o)["f_out"] for o in CONTROLS]; V["T3 honest controls"] = (all(abs(x - 1) <= 0.25 for x in k), "mr / rubber pull-out: " + ", ".join(f"{o} {x:.2f}" for o, x in zip(CONTROLS, k)))
    k = [g("mr", o)["f_out"] for o in SHAPED]; V["T4 payload"] = (sum(x >= 9.8 for x in k) >= 3, "mr pull-out: " + ", ".join(f"{o} {x:.1f} N" for o, x in zip(SHAPED, k)))
    k = [g("mr", o)["f_out"]/g("vacuum", o)["f_out"] for o in SHAPED]; V["T5 versus vacuum"] = (sum(x >= 0.5 for x in k) >= 3, "mr / vacuum pull-out: " + ", ".join(f"{o} {x:.2f}" for o, x in zip(SHAPED, k)))
    V["T6 weight"] = (grams <= 40, f"{F.fluid_mass_g():.1f} g fluid + {s['magnet_g']:.1f} g magnet and plate = {grams:.1f} g, before membrane and housing")
    return {k: dict(passed=bool(p), detail=t, rule=THRESHOLDS[k]) for k, (p, t) in V.items()}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        import mujoco.viewer
        pad, obj, pinch, grip = (sys.argv[2:] + ["mr", "ball", "5", "position"][len(sys.argv) - 2:])[:4]
        print(__doc__.split("What is modelled")[0]); print("amber = soft, blue = locked, red = a pin creeping past its yield force")
        m0 = mujoco.MjModel.from_xml_string(build(obj)); d0 = mujoco.MjData(m0)
        with mujoco.viewer.launch_passive(m0, d0) as v:
            v.cam.lookat[:] = (0, 0, 0); v.cam.distance = 0.16; v.cam.azimuth = 70; v.cam.elevation = -12
            r = trial(pad, obj, float(pinch), grip=grip, viewer=v, model=m0, data=d0)
            print(f"{pad} on {obj} at {pinch} N pinch: firm hold {r['f_firm']:.1f} N, pull-out {r['f_out']:.1f} N" + (" (never pulled out, capped)" if r["held_to_cap"] else ""))
            while v.is_running(): time.sleep(0.05)
        sys.exit()

    from multiprocessing import Pool
    GRIPS = ["force", "position"]
    jobs = [((p, o, f), dict(grip=g)) for g in GRIPS for p in PADS for o in OBJECTS for f in PINCHES]
    jobs += [(("mr", o, 5.0), dict(c_ind=c, grip=g)) for g in GRIPS for o in SHAPED for c in (1.73, 5.14)]                  # how much the biggest unknown matters
    jobs += [(("mr", o, 5.0), dict(magnet=mg, grip=g)) for g in GRIPS for o in SHAPED for mg in ("halbach x5, 4 mm", "stripes x5, 4 mm + plate")]   # weaker, better-contained magnets
    t0 = time.time()
    with Pool(min(10, os.cpu_count() or 4)) as pool: R = pool.map(_run, jobs, chunksize=1)
    verdict = evaluate(R, "force"); posthoc = evaluate(R, "position"); os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    fs = {k: {kk: (vv.tolist() if hasattr(vv, "tolist") else vv) for kk, vv in field(k).items()} for k in (MAGNET, "halbach x5, 4 mm", "stripes x5, 4 mm + plate")}
    json.dump(dict(params=dict(pitch=PITCH, pins=[NY, NZ], stroke=STROKE, mu=MU, c_ind=C_IND, tau_vacuum=TAU_VACUUM, magnet=MAGNET, rate=RATE, f_max=F_MAX, f_stall=F_STALL, kp_finger=KP_FINGER),
                   field=fs, thresholds=verdict, posthoc_position=posthoc, trials=R), open(os.path.join(HERE, "out", "magpad.json"), "w"), indent=1)
    print(f"{len(R)} trials in {time.time() - t0:.0f} s\n")
    base = lambda r: r["c_ind"] == C_IND and r["magnet"] in (None, MAGNET)
    for g in GRIPS:
        for f in PINCHES:
            print(f"grip={g}  pinch {f:g} N   firm-hold / pull-out, newtons ('+' = never pulled out)"); print(f"{'':10s}" + "".join(f"{p:>16s}" for p in PADS))
            for o in OBJECTS:
                row = [next(r for r in R if base(r) and r["grip"] == g and r["pad"] == p and r["obj"] == o and r["pinch"] == f) for p in PADS]
                print(f"{o:10s}" + "".join(f"{r['f_firm']:8.1f}/{r['f_out']:5.1f}{'+' if r['held_to_cap'] else ' '} " for r in row))
            print()
    print("sensitivity, mr pad at 5 N pinch, pull-out N:   c_ind 1.73 / 3 / 5.14   |   magnet: single+plate / halbach x5 / stripes x5")
    for g in GRIPS:
        for o in SHAPED:
            pick = lambda **k: next(r for r in R if r["grip"] == g and r["pad"] == "mr" and r["obj"] == o and r["pinch"] == 5.0 and all(r[a] == b for a, b in k.items()))
            cs = [pick(c_ind=c, magnet=MAGNET)["f_out"] for c in (1.73, C_IND, 5.14)]; ms = [pick(c_ind=C_IND, magnet=mg)["f_out"] for mg in (MAGNET, "halbach x5, 4 mm", "stripes x5, 4 mm + plate")]
            print(f"  {g:9s}{o:10s}  " + " / ".join(f"{x:5.1f}" for x in cs) + "   |   " + " / ".join(f"{x:5.1f}" for x in ms))
    print("\nverdict, grip=force (thresholds fixed before the run)")
    for k, v in verdict.items(): print(f"  {'PASS' if v['passed'] else 'FAIL'}  {k}: {v['detail']}")
    print("same checks, grip=position (added after the first run, so not a pre-registered verdict)")
    for k, v in posthoc.items(): print(f"  {'pass' if v['passed'] else 'fail'}  {k}: {v['detail']}")
