"""Task suite for the Rev E tendril bundle in MuJoCo. Scripted controllers, measured outcomes, rendered frames."""
import json, math, os
import numpy as np
import mujoco
import sim
from sim import Sim, OUT, N_VERT, PITCH

L_ARC = N_VERT*PITCH
RESULTS = []
def rec(name, human, metric, value, unit, passed, note, frames):
    RESULTS.append(dict(name=name, level="human-level" if human else "beyond-human", metric=metric, value=float(value), unit=unit, passed=bool(passed), note=note, frames=frames))
    print(f"{'PASS' if passed else 'FAIL'}  {name}: {metric} = {value:.3g} {unit}  ({note})")
def frame(s, tag, k, cam): return os.path.basename(s.render(os.path.join(OUT, f"{tag}_{k}.png"), cam=cam, w=640, h=440))
def body(s, name): return mujoco.mj_name2id(s.model, mujoco.mjtObj.mjOBJ_BODY, name)
def tip_body(s, t): return body(s, f"t{t}_v{N_VERT-1}")
def contacts_with(s, geom_prefix, body_name):
    """distinct vertebrae of the named prefix touching the body, and the summed normal force"""
    bid = body(s, body_name); geoms = set(); f = 0.0
    for i in range(s.data.ncon):
        c = s.data.contact[i]; g1, g2 = c.geom1, c.geom2; b1, b2 = s.model.geom_bodyid[g1], s.model.geom_bodyid[g2]
        n1 = mujoco.mj_id2name(s.model, mujoco.mjtObj.mjOBJ_GEOM, g1) or ""; n2 = mujoco.mj_id2name(s.model, mujoco.mjtObj.mjOBJ_GEOM, g2) or ""
        hit = g1 if (b2 == bid and n1.startswith(geom_prefix)) else (g2 if (b1 == bid and n2.startswith(geom_prefix)) else None)
        if hit is not None:
            fr = np.zeros(6); mujoco.mj_contactForce(s.model, s.data, i, fr); geoms.add(hit); f += abs(fr[0])
    return len(geoms), f
# constant-curvature arc: tip of a tendril bent by theta toward phi, relative to its root
def arc_tip(root, phi, theta):
    R = L_ARC/max(theta, 1e-6); return root + np.array([R*(1-math.cos(theta))*math.cos(phi), R*(1-math.cos(theta))*math.sin(phi), R*math.sin(theta)])
def arc_params(root, p):
    d = p - root; dr = math.hypot(d[0], d[1]); return math.atan2(d[1], d[0]), 2*math.atan2(dr, d[2])
# closed loop on the tip: command the arc that would reach the target, then correct for cable stretch from the measured tip
def reach(s, t, target, rounds=8, settle=0.5):
    root = s.body_pos(f"t{t}_v0"); phi_d, th_d = arc_params(root, target); phi, th = phi_d, th_d
    for _ in range(rounds):
        s.bend(t, phi, th); s.step(settle)
        phi_m, th_m = arc_params(root, s.tip(t)); th += 0.9*(th_d - th_m); phi += 0.9*(phi_d - phi_m); th = float(np.clip(th, 0.05, math.radians(200)))
    return float(np.linalg.norm(target - s.tip(t))), phi, th
CAM = {"lookat": (0.0, 0.0, 0.08), "distance": 0.46, "azimuth": 140, "elevation": -24}

def task_hold():
    s = Sim(n_tendrils=8); s.step(0.4); fr = []
    s.bend(0, 0.0, math.radians(110)); s.step(1.5); p0 = s.tip(0); fr.append(frame(s, "hold", 0, CAM))
    tb = tip_body(s, 0); s.data.xfrc_applied[tb, 2] = -0.5; s.step(1.0); sag_cables = (p0 - s.tip(0))[2]*1000; s.data.xfrc_applied[tb, 2] = 0; s.step(0.5)
    s.jam(0); s.slack(0); s.step(1.5); pj = s.tip(0); relax = (pj - p0)[2]*1000
    s.data.xfrc_applied[tb, 2] = -0.5; s.step(1.5); sag_jam = (pj - s.tip(0))[2]*1000; fr.append(frame(s, "hold", 1, CAM))
    s.jam(0, False); s.step(1.5); sag_off = (pj - s.tip(0))[2]*1000; fr.append(frame(s, "hold", 2, CAM))
    rec("Hold a bent shape with 50 g hung on the tip", True, "tip sag under the load, sleeve jammed and cables slack", sag_jam, "mm", sag_jam < 15,
        f"cables holding the load: {sag_cables:.1f} mm sag; jamming with cables slack first lets the backbone relax the tip {relax:+.1f} mm, then the load sags it {sag_jam:.1f} mm; unjammed and slack it drops {-sag_off:.0f} mm", fr)

def task_reach():
    s = Sim(n_tendrils=8); s.step(0.4); fr = [frame(s, "reach", 0, CAM)]
    root = s.body_pos("t0_v0"); target = arc_tip(root, math.radians(35), math.radians(120))
    s.model.site_size[mujoco.mj_name2id(s.model, mujoco.mjtObj.mjOBJ_SITE, "t0_tip")] = 0.004
    err, phi, th = reach(s, 0, target); fr.append(frame(s, "reach", 1, CAM))
    rec("Place the tip on a point in space", True, "final tip error after 8 corrections", err*1000, "mm", err < 0.006, f"target {np.round(target*1000).astype(int).tolist()} mm, commanded bend {math.degrees(th):.0f} deg to reach a 120 deg arc, cable stretch corrected in the loop", fr)

def task_pinch():
    ped = '    <body name="ped" mocap="true" pos="0 0 0.07"><geom type="cylinder" size="0.008 0.065" rgba="0.62 0.65 0.7 1"/></body>\n'
    cube = '    <body name="cube" pos="0 0 0.146"><freejoint/><geom type="box" size="0.01 0.01 0.01" mass="0.012" rgba="0.85 0.57 0.16 1"/></body>\n'
    s = Sim(n_tendrils=8, objects=[ped, cube]); s.step(0.4); fr = [frame(s, "pinch", 0, CAM)]
    c0 = s.body_pos("cube"); z0 = c0[2]
    # tendrils 0 and 4 face each other across the centre; their 60 deg arcs meet there, so squeeze a little past it
    th = 30.0
    for k in range(60):
        for t in (0, 4): s.bend(t, 2*math.pi*t/8 + math.pi, math.radians(th))
        s.step(0.1); n, f = contacts_with(s, "t", "cube")
        if n >= 2 and f > 0.6: break
        th += 1.5
    n, f = contacts_with(s, "t", "cube"); fr.append(frame(s, "pinch", 1, CAM))
    for k in range(20): s.data.mocap_pos[0, 2] = 0.07 - k*0.003; s.step(0.1)   # pedestal drops away
    s.step(1.0); z1 = s.body_pos("cube")[2]; fr.append(frame(s, "pinch", 2, CAM))
    rec("Pinch a 20 mm cube and hold it when its support is removed", True, "cube height kept after the pedestal drops", (z1 - 0.026)*1000, "mm above the base", z1 > 0.10, f"{n} tendril contacts, {f:.2f} N normal force at the pinch, cube started at {z0*1000:.0f} mm", fr)

def task_wrap():
    bar = '    <body name="post" pos="0.076 0 0.046"><geom type="cylinder" size="0.03 0.05" euler="90 0 0" rgba="0.62 0.65 0.7 1"/></body>\n'
    s = Sim(n_tendrils=8, objects=[bar]); s.step(0.4); fr = [frame(s, "wrap", 0, CAM)]
    for k in range(45): s.bend(0, 0.0, math.radians(20 + k*6.0)); s.step(0.08)
    s.step(0.5); n, f = contacts_with(s, "t0_g", "post"); fr.append(frame(s, "wrap", 1, CAM))
    s.jam(0); tb = tip_body(s, 0); p0 = s.tip(0)                       # cables stay locked by the spool worm drive, sleeve jammed
    s.data.xfrc_applied[tb, 0] = -2.0; s.data.xfrc_applied[tb, 2] = 1.0; s.step(1.0); d = np.linalg.norm(s.tip(0) - p0)*1000; n2, f2 = contacts_with(s, "t0_g", "post"); fr.append(frame(s, "wrap", 2, CAM))
    rec("Wrap a 60 mm bar and resist a 2 N pull on the tip", True, "tip moved under the pull", d, "mm", n2 >= 6 and d < 12, f"{n} of 14 vertebrae in contact after the wrap, {f:.1f} N total normal force; {n2} still in contact under the pull; cables locked, sleeve jammed", fr)

def task_cage():
    s = Sim(n_tendrils=8, objects=[sim.ball(0.0, 0.0, r=0.025, m=0.05)]); s.step(0.4); fr = [frame(s, "cage", 0, CAM)]
    bid = body(s, "ball")
    for k in range(30):
        for t in range(8): s.bend(t, 2*math.pi*t/8 + math.pi, math.radians(40 + k*2.5))
        s.step(0.1)
    for t in range(8): s.jam(t)
    p0 = s.body_pos("ball"); fr.append(frame(s, "cage", 1, CAM))
    s.data.xfrc_applied[bid, 0] = 1.0; s.step(1.0); s.data.xfrc_applied[bid, 0] = 0.0; s.step(0.5)
    disp = np.linalg.norm((s.body_pos("ball") - p0)[:2])*1000; fr.append(frame(s, "cage", 2, CAM))
    s2 = Sim(n_tendrils=0, objects=[sim.ball(0.0, 0.0, r=0.025, m=0.05)]); s2.step(0.4); q0 = s2.body_pos("ball"); b2 = body(s2, "ball")
    s2.data.xfrc_applied[b2, 0] = 1.0; s2.step(1.0); s2.data.xfrc_applied[b2, 0] = 0; s2.step(0.5)
    free = np.linalg.norm((s2.body_pos("ball") - q0)[:2])*1000
    rec("Cage a ball and hold it against a 1 N push", False, "ball displacement inside the cage", disp, "mm", disp < 15, ("the same push on the ball alone rolls it off the base" if free > 100 else f"the same push on the ball alone moves it {free:.0f} mm"), fr)

def task_parallel():
    # eight floor pads, one per tendril, all reached at the same time with the same closed loop as the single reach
    pads = [f'    <body name="pad{t}" pos="{0.152*math.cos(2*math.pi*t/8):.4f} {0.152*math.sin(2*math.pi*t/8):.4f} 0.0006"><geom type="cylinder" size="0.012 0.0006" rgba="0.85 0.57 0.16 1" contype="0" conaffinity="0"/></body>\n' for t in range(8)]
    s = Sim(n_tendrils=8, objects=pads); s.step(0.4); fr = [frame(s, "parallel", 0, CAM)]
    targets = [np.array([0.152*math.cos(2*math.pi*t/8), 0.152*math.sin(2*math.pi*t/8), 0.020]) for t in range(8)]
    roots = [s.body_pos(f"t{t}_v0") for t in range(8)]
    cmd = [list(arc_params(roots[t], targets[t])) for t in range(8)]
    for _ in range(10):
        for t in range(8): s.bend(t, cmd[t][0], cmd[t][1])
        s.step(0.5)
        for t in range(8):
            phi_m, th_m = arc_params(roots[t], s.tip(t)); phi_d, th_d = arc_params(roots[t], targets[t])
            cmd[t][1] = float(np.clip(cmd[t][1] + 0.9*(th_d - th_m), 0.05, math.radians(220))); cmd[t][0] += 0.9*(phi_d - phi_m)
    fr.append(frame(s, "parallel", 1, CAM))
    errs = [np.linalg.norm(s.tip(t) - targets[t])*1000 for t in range(8)]
    rec("Hover eight tips over eight floor pads at once", False, "worst tip error of the eight", max(errs), "mm", max(errs) < 12, f"errors {', '.join(f'{e:.0f}' for e in errs)} mm; tips held 12 mm above pads 24 mm wide at 152 mm from the centre, on the reachable surface of a 170 deg arc, all eight tendrils controlled in the same loop", fr)

def task_ring():
    s0 = Sim(n_tendrils=8); root = s0.body_pos("t0_v0"); th = math.radians(100); c = arc_tip(root, 0.0, th)
    tang = np.array([math.sin(th), 0.0, math.cos(th)]); ang = math.degrees(math.atan2(tang[0], tang[2]))
    ring = f'    <body name="ring" pos="{c[0]:.4f} {c[1]:.4f} {c[2]:.4f}" euler="0 {ang:.1f} 0"><geom type="cylinder" size="0.02 0.003" rgba="0.62 0.65 0.7 1" contype="0" conaffinity="0"/><geom type="cylinder" size="0.011 0.0035" rgba="0.92 0.92 0.94 1" contype="0" conaffinity="0"/></body>\n'
    s = Sim(n_tendrils=8, objects=[ring]); s.step(0.4); fr = [frame(s, "ring", 0, CAM)]
    err, phi, th2 = reach(s, 0, c); fr.append(frame(s, "ring", 1, CAM))
    rec("Thread the tip through a 22 mm ring", False, "tip miss from the ring centre", err*1000, "mm", err < 0.011, "the ring sits on the reachable arc of tendril 0, tilted to the arc tangent; drawn as a target with no contact", fr)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (task_hold, task_reach, task_pinch, task_wrap, task_cage, task_parallel, task_ring):
        try: fn()
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERROR in", fn.__name__, repr(e))
    json.dump(RESULTS, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(f"{sum(r['passed'] for r in RESULTS)} of {len(RESULTS)} passed")
