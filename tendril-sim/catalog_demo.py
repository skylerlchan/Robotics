"""Batch of scripted demos on the UR5e + 24-tendril bundle, one task spec each. Writes out/cat_<slug>.mp4, key frames and out/catalog_metrics.json."""
import json, math, os, subprocess, sys, time, traceback
import numpy as np, mujoco
import pick_demo as P
from pick_demo import Demo, roots, RINGS, N_T, OUT
OBJ = 'contype="3" conaffinity="3" friction="0.9 0.02 0.001"'
TARGET = '<geom name="target" type="cylinder" size="0.05 0.001" pos="0.55 -0.30 0.001" rgba="0.85 0.57 0.16 0.8" contype="0" conaffinity="0"/>'
def free(name, pos, geom, mass, rgba="0.24 0.44 0.88 1"): return f'<body name="{name}" pos="{pos}"><freejoint/><geom {geom} mass="{mass}" rgba="{rgba}" {OBJ}/></body>'
TASKS = [
 dict(slug="cup", name="Pick up a cup and place it", src="SHAP lift light object", kind="pickplace", obj="cup", inner_pre=70, force=8, grasp_z=0.29,
      world=free("cup", "0.55 0 0.0455", 'type="cylinder" size="0.04 0.045"', 0.25, "0.93 0.90 0.85 1") + TARGET),
 dict(slug="ball", name="Grasp a 70 mm ball and place it", src="ARAT grasp ball", kind="pickplace", obj="ball", inner_pre=70, force=8, grasp_z=0.262,
      world=free("ball", "0.55 0 0.036", 'type="sphere" size="0.035"', 0.15, "0.85 0.57 0.16 1") + TARGET),
 dict(slug="cube25", name="Pinch a 2.5 cm block and place it", src="ARAT grasp block 2.5 cm", kind="pickplace", obj="block", inner_pre=0, force=3, grasp_z=0.268,
      world=free("block", "0.55 0 0.0135", 'type="box" size="0.0125 0.0125 0.0125"', 0.02, "0.24 0.44 0.88 1") + TARGET),
 dict(slug="box", name="Pick a flat 60 by 40 by 30 mm box", src="Jebsen small common objects", kind="pickplace", obj="box", inner_pre=0, force=5, grasp_z=0.262,
      world=free("box", "0.55 0 0.0155", 'type="box" size="0.03 0.02 0.015"', 0.2, "0.24 0.44 0.88 1") + TARGET),
 dict(slug="heavy", name="Lift a 450 g can and place it", src="Jebsen large heavy cans", kind="pickplace", obj="can", inner_pre=70, force=14, grasp_z=0.29,
      world=free("can", "0.55 0 0.0555", 'type="cylinder" size="0.037 0.055"', 0.45, "0.55 0.52 0.50 1") + TARGET),
 dict(slug="stack", name="Stack a 5 cm block on another", src="Jebsen stacking checkers", kind="pickplace", obj="blockA", inner_pre=40, force=6, grasp_z=0.275, place_z_extra=0.05,
      world=free("blockA", "0.55 0 0.0255", 'type="box" size="0.025 0.025 0.025"', 0.06, "0.24 0.44 0.88 1") + free("blockB", "0.55 -0.30 0.0255", 'type="box" size="0.025 0.025 0.025"', 0.06, "0.85 0.57 0.16 1")),
 dict(slug="button", name="Press a large button", src="RoboCasa press button", kind="press", obj="button", press_z=0.297,
      world='<body name="bstand" pos="0.55 0 0.025"><geom type="cylinder" size="0.055 0.025" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body><body name="button" pos="0.55 0 0.06"><joint name="bslide" type="slide" axis="0 0 1" range="-0.02 0" stiffness="150" damping="2"/><geom type="cylinder" size="0.048 0.01" mass="0.02" rgba="0.70 0.23 0.18 1" ' + OBJ + '/></body>'),
 dict(slug="drawer", name="Open a drawer by its handle", src="RoboCasa open drawer", kind="drawer", obj="drawer", inner_pre=0, force=6, grasp_z=0.29 + 0.12,
      world='<body name="cabinet" pos="0.70 0 0.06"><geom type="box" size="0.16 0.14 0.06" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body>'
            '<body name="drawer" pos="0.55 0 0.135"><joint name="dslide" type="slide" axis="1 0 0" range="-0.18 0" damping="6"/><geom type="box" size="0.14 0.12 0.015" mass="0.4" rgba="0.82 0.80 0.77 1" ' + OBJ + '/>'
            '<geom type="cylinder" size="0.012 0.05" pos="-0.10 0 0.065" mass="0.05" rgba="0.55 0.52 0.50 1" ' + OBJ + '/></body>', grasp_xy=(0.45, 0.0)),
 dict(slug="knob", name="Turn a knob a quarter turn", src="RoboCasa twist knob", kind="knob", obj="knob", inner_pre=70, force=6, grasp_z=0.29,
      world='<body name="kstand" pos="0.55 0 0.015"><geom type="cylinder" size="0.05 0.015" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body><body name="knob" pos="0.55 0 0.075"><joint name="khinge" type="hinge" axis="0 0 1" damping="0.05"/><geom type="cylinder" size="0.025 0.045" mass="0.05" rgba="0.70 0.23 0.18 1" ' + OBJ + '/><geom type="box" size="0.004 0.02 0.004" pos="0 0 0.05" rgba="0.1 0.1 0.1 1" contype="0" conaffinity="0" mass="0.001"/></body>'),
]
ring_of = [i for i, (n, r, ph) in enumerate(RINGS) for _ in range(n)]
def close_rings(D, force, inner_pre, hold, max_deg=110):
    th = 0.0
    for k in range(90):
        th += 1.2
        for t, (rx, ry) in enumerate(roots):
            if ring_of[t] == 0 and inner_pre > 0: D.bend(t, math.atan2(ry, rx), math.radians(inner_pre))
            else: D.bend(t, math.atan2(ry, rx) + math.pi, math.radians(th*(0.35 if ring_of[t] == 0 else 1.0)))
        D.run(0.05, hold); n, f = D.contacts()
        if n >= 6 and f > force: break
        if th > max_deg: break
    D.run(0.5, hold); return th
def splay(D, inner_pre):
    for t, (rx, ry) in enumerate(roots): D.bend(t, math.atan2(ry, rx), math.radians(inner_pre) if (ring_of[t] == 0 and inner_pre > 0) else 0.0)
def encode(D, slug):
    h, w = D.frames[0].shape[:2]; vid = os.path.join(OUT, f"cat_{slug}.mp4")
    ff = subprocess.Popen(["/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "30", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "27", "-movflags", "+faststart", vid], stdin=subprocess.PIPE)
    for fr in D.frames: ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); return os.path.getsize(vid)//1024
def run_task(T):
    t0 = time.time(); D = Demo(world_extra=T["world"], obj=T["obj"], scene_name=f"cat_{T['slug']}.xml", size=(640, 400)); m = dict(slug=T["slug"], name=T["name"], src=T["src"], kind=T["kind"])
    gx, gy = T.get("grasp_xy", (0.55, 0.0)); above = np.array([gx, gy, 0.44]); frames = []
    snap = lambda k: (D.snap(f"cat_{T['slug']}_{k}.png"), frames.append(f"cat_{T['slug']}_{k}.png"))
    if T["kind"] == "press":
        D.move_until(above, 0.01, 9.0); snap(0)
        for t in range(N_T): D.jam(t)                                                          # jammed sleeves make the tendrils stiff columns
        press = np.array([gx, gy, T["press_z"]]); D.move_until(press, 0.004, 5.0); D.run(1.0, press); snap(1)
        jid = mujoco.mj_name2id(D.m, mujoco.mjtObj.mjOBJ_JOINT, "bslide"); m["button_travel_mm"] = round(float(-D.d.qpos[D.m.jnt_qposadr[jid]])*1000, 1)
        D.move_until(above, 0.01, 5.0)
        for t in range(N_T): D.jam(t, False)
        snap(2); m["passed"] = m["button_travel_mm"] > 10
    else:
        splay(D, T["inner_pre"]); D.move_until(above, 0.01, 9.0); snap(0)
        grasp = np.array([gx, gy, T["grasp_z"]]); D.move_until(grasp, 0.006, 5.0); snap(1)
        p0 = D.d.xpos[D.bottle].copy(); th = close_rings(D, T["force"], T["inner_pre"], grasp); n, f = D.contacts(); m.update(tendrils_in_contact=n, grasp_force_N=round(f, 2), close_deg=round(th, 1))
        for t in range(N_T): D.jam(t)
        snap(2)
        if T["kind"] == "pickplace":
            rel0 = D.d.xpos[D.bottle] - D.d.site_xpos[D.tool]
            for k in range(30): D.run(0.1, grasp + np.array([0, 0, 0.18*(k+1)/30]))
            m["lift_mm"] = round(float(D.d.xpos[D.bottle][2] - p0[2])*1000, 1); snap(3)
            for k in range(40): D.run(0.1, np.array([gx, gy - 0.30*(k+1)/40, T["grasp_z"] + 0.18]))
            m["slip_mm"] = round(float(np.linalg.norm((D.d.xpos[D.bottle] - D.d.site_xpos[D.tool]) - rel0))*1000, 1); snap(4)
            pz = T["grasp_z"] + T.get("place_z_extra", 0.0)
            for k in range(25): D.run(0.1, np.array([gx, gy - 0.30, T["grasp_z"] + 0.18 - (T["grasp_z"] + 0.18 - pz)*(k+1)/25]))
            for t in range(N_T): D.jam(t, False)
            splay(D, T["inner_pre"]); D.run(1.2, np.array([gx, gy - 0.30, pz])); snap(5)
            for k in range(20): D.run(0.1, np.array([gx, gy - 0.30, pz + 0.15*(k+1)/20]))
            D.run(0.4, np.array([gx, gy - 0.30, pz + 0.15])); snap(6)
            p = D.d.xpos[D.bottle]; m["place_error_mm"] = round(float(np.hypot(p[0]-gx, p[1]-(gy-0.30)))*1000, 1); m["upright"] = bool(D.d.xmat[D.bottle].reshape(3,3)[2,2] > 0.9)
            m["final_height_mm"] = round(float(p[2])*1000, 1)
            m["passed"] = m["lift_mm"] > 100 and m["slip_mm"] < 20 and m["place_error_mm"] < 40 and (m["final_height_mm"] > 60 if T.get("place_z_extra") else True)
        elif T["kind"] == "drawer":
            for k in range(30): D.run(0.1, grasp + np.array([-0.16*(k+1)/30, 0, 0]))
            D.run(0.5, grasp + np.array([-0.16, 0, 0])); snap(3)
            jid = mujoco.mj_name2id(D.m, mujoco.mjtObj.mjOBJ_JOINT, "dslide"); m["drawer_open_mm"] = round(float(-D.d.qpos[D.m.jnt_qposadr[jid]])*1000, 1)
            for t in range(N_T): D.jam(t, False)
            splay(D, 0); D.run(0.8, grasp + np.array([-0.16, 0, 0])); D.move_until(grasp + np.array([-0.16, 0, 0.15]), 0.01, 4.0); snap(4); m["passed"] = m["drawer_open_mm"] > 100
        elif T["kind"] == "knob":
            q0 = D.q_des.copy()
            for k in range(30):
                a = math.radians(90)*(k+1)/30; qz = np.array([math.cos(a/2), 0, 0, math.sin(a/2)]); qd = np.zeros(4); mujoco.mju_mulQuat(qd, qz, q0); D.q_des = qd; D.run(0.1, grasp)
            D.run(0.5, grasp); snap(3)
            jid = mujoco.mj_name2id(D.m, mujoco.mjtObj.mjOBJ_JOINT, "khinge"); m["knob_turn_deg"] = round(abs(math.degrees(float(D.d.qpos[D.m.jnt_qposadr[jid]]))), 1)
            for t in range(N_T): D.jam(t, False)
            splay(D, T["inner_pre"]); D.run(0.8, grasp); D.q_des = q0; D.move_until(above, 0.01, 5.0); snap(4); m["passed"] = m["knob_turn_deg"] > 60
    m["frames"] = frames; m["sim_s"] = round(D.d.time, 1); m["wall_s"] = round(time.time()-t0, 1); m["video_kb"] = encode(D, T["slug"]); return m
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); only = sys.argv[1:]; results = []
    path = os.path.join(OUT, "catalog_metrics.json" if not only else "catalog_metrics_" + "_".join(only) + ".json")
    if os.path.exists(path) and not only: results = json.load(open(path))
    for T in TASKS:
        if only and T["slug"] not in only: continue
        try: r = run_task(T); print("PASS" if r["passed"] else "FAIL", T["slug"], json.dumps({k: v for k, v in r.items() if k not in ("frames", "name", "src", "kind")}), flush=True)
        except Exception as e: traceback.print_exc(); r = dict(slug=T["slug"], name=T["name"], src=T["src"], kind=T["kind"], passed=False, error=repr(e), frames=[]); print("ERROR", T["slug"], repr(e), flush=True)
        results = [x for x in results if x["slug"] != T["slug"]] + [r]; json.dump(results, open(path, "w"), indent=1)
    print(f"{sum(1 for r in results if r.get('passed'))} of {len(results)} passed")
