"""The race: every prototype on its own UR5e, same bottle, same script: approach, descend, close, lift, hold. Measured per hand.

  mjpython race.py                 live, all seven
  mjpython race.py 2f85 leap fist6 live, a subset
  python race.py --headless        metrics to out/race.json and frames to out/race_*.png
"""
import os, sys, math, time, json, numpy as np, mujoco
import prototypes as P, lineup as L
HEADLESS = "--headless" in sys.argv; hands = [a for a in sys.argv[1:] if not a.startswith("--")] or list(P.HANDS)
ARMJ = ["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]; ARMA = ["shoulder_pan","shoulder_lift","elbow","wrist_1","wrist_2","wrist_3"]
w = L.build_lineup(hands, timestep=0.0005); m = w.compile(); d = mujoco.MjData(m)
N = len(hands); nid = lambda t, n: mujoco.mj_name2id(m, t, n)
class Arm:
    def __init__(self, i, hand):
        self.i, self.hand, self.p = i, hand, f"a{i}/"
        self.qadr = np.array([m.jnt_qposadr[nid(mujoco.mjtObj.mjOBJ_JOINT, self.p + n)] for n in ARMJ]); self.dadr = np.array([m.jnt_dofadr[nid(mujoco.mjtObj.mjOBJ_JOINT, self.p + n)] for n in ARMJ])
        self.aid = np.array([nid(mujoco.mjtObj.mjOBJ_ACTUATOR, self.p + n) for n in ARMA]); self.site = nid(mujoco.mjtObj.mjOBJ_SITE, self.p + "attachment_site")
        self.q = np.array(L.ARM_HOME, dtype=float); d.qpos[self.qadr] = self.q; d.ctrl[self.aid] = self.q; self.q_des = np.array([0.0, 1.0, 0.0, 0.0])
        self.hp = self.p + hand + "/"; self.hact = [a for a in range(m.nu) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, a) or "").startswith(self.hp)]
        self.bottle = nid(mujoco.mjtObj.mjOBJ_BODY, f"bottle{i}"); self.x0 = L.SPACING*i; self.length = P.mount_quat(hand)[1]
        self.hgeoms = [g for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]) or "").startswith(self.hp)]
        self.ten = [t for t in range(m.ntendon) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_TENDON, t) or "").startswith(self.hp)]; self.L0 = None
        if hand == "fist6": self.roots = P.tendril_hand_xml("x", [(6, 0.045, 0.0)], 8, 0.015, 0.010, 0.007, 4.0, 200.0, 0.006, 0.07)[1]; self.cr = 0.007; self.th_close = math.radians(70)
        elif hand == "bundle24": self.roots = P.tendril_hand_xml("x", [(6, 0.030, 0.0), (8, 0.058, math.pi/8), (10, 0.084, 0.0)], 18, 0.0122, 0.006, 0.0042, 1.0, 100.0, 0.0015, 0.10)[1]; self.cr = 0.0042; self.th_close = math.radians(60)
        self.tinfo = [(int(n[1:n.index("_")]), int(n[-1])) for n in ((mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_TENDON, t) or "").split("/")[-1] for t in self.ten)] if hand in ("fist6", "bundle24") else []
    def ik(self, p_des):
        jp = np.zeros((3, m.nv)); jr = np.zeros((3, m.nv)); mujoco.mj_jacSite(m, d, jp, jr, self.site); J = np.vstack([jp[:, self.dadr], jr[:, self.dadr]])
        e_p = p_des - d.site_xpos[self.site]; qc = np.zeros(4); mujoco.mju_mat2Quat(qc, d.site_xmat[self.site]); e_r = np.zeros(3); mujoco.mju_subQuat(e_r, self.q_des, qc); e_r = d.site_xmat[self.site].reshape(3,3) @ e_r
        v = np.concatenate([np.clip(e_p*4.0, -0.25, 0.25), np.clip(e_r*3.0, -0.8, 0.8)]); dq = J.T @ np.linalg.solve(J @ J.T + 0.01*np.eye(6), v)
        self.q += np.clip(dq*0.01, -0.012, 0.012); d.ctrl[self.aid] = self.q
    def at(self, p_des, tol=0.01): return np.linalg.norm(p_des - d.site_xpos[self.site]) < tol and abs(d.site_xmat[self.site].reshape(3,3)[2,2] + 1) < 0.02
    def contacts(self):
        n = set(); f = 0.0
        for i in range(d.ncon):
            c = d.contact[i]; b1, b2 = m.geom_bodyid[c.geom1], m.geom_bodyid[c.geom2]
            if self.bottle in (b1, b2):
                g = c.geom2 if b1 == self.bottle else c.geom1
                if g in self.hgeoms: fr = np.zeros(6); mujoco.mj_contactForce(m, d, i, fr); n.add(m.geom_bodyid[g]); f += abs(fr[0])
        return len(n), f
    # hand adapters: 0 = open, 1 = closed
    def hand_cmd(self, u):
        h = self.hand
        if h in ("2f85", "leap", "allegro", "shadow"): close_cmd(m, d, self.hp, h, u)
        elif h == "suction": self.suck = u > 0.5
        elif h == "bloom":
            for a in self.hact:
                k = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, a).split("/")[-1]
                d.ctrl[a] = (1.3*(1-u) - 0.08*u) if k.endswith("a1") else (-0.5*(1-u) + 0.4*u)     # open: petals splayed; closed: the orb pose with the lower petal segments curling in until they meet the object
        elif h in ("fist6", "bundle24"):
            if self.L0 is None: self.L0 = d.ten_length[self.ten].copy()
            for k, (ti, c) in enumerate(self.tinfo):
                rx, ry = self.roots[ti]; phi = math.atan2(ry, rx) + math.pi
                d.ctrl[self.hact[k]] = self.L0[k] - self.cr*self.th_close*u*math.cos(phi - 2*math.pi*c/3)
    def suction_step(self):
        if getattr(self, "suck", False):
            cup = nid(mujoco.mjtObj.mjOBJ_SITE, self.hp + "cup_site"); pc = d.site_xpos[cup]; top = d.xpos[self.bottle] + np.array([0, 0, 0.06]); e = pc - top
            if np.linalg.norm(e) < 0.02: F = np.clip(900*e - 6*d.cvel[self.bottle][3:], -25, 25); d.xfrc_applied[self.bottle, :3] = F
            else: d.xfrc_applied[self.bottle, :3] = 0
        else: d.xfrc_applied[self.bottle, :3] = 0
def close_cmd(model, data, prefix, hand, u=1.0):
    for a in range(model.nu):
        n = model.actuator(a).name
        if not n.startswith(prefix): continue
        lo, hi = model.actuator_ctrlrange[a]; k = n.split("/")[-1]
        if hand == "2f85": data.ctrl[a] = 165*u; continue
        if hand == "leap": frac = 0.0 if ("rot" in k or "cmc" in k) else (0.55 if "th" in k else 0.6)
        elif hand == "allegro": frac = 0.0 if (k.endswith("a0") and not k.startswith("th")) else (0.9 if k == "tha0" else 0.6)
        else: frac = 0.0 if ("WRJ" in k or "J4" in k or "LFJ5" in k) else (0.85 if "THJ4" in k else 0.5 if "THJ" in k else 0.7)
        data.ctrl[a] = lo + (hi - lo)*(0.5 if frac == 0.0 else frac*u)
CURL = {}
for h in set(hands):
    if h in ("leap", "allegro", "shadow"): CURL[h] = P.curl_direction(h, lambda mm, dd, pre, hh=h: close_cmd(mm, dd, pre, hh))[0]
arms = [Arm(i, h) for i, h in enumerate(hands)]; mujoco.mj_forward(m, d)
for a in arms: a.hand_cmd(0.0)
viewer = None
if not HEADLESS:
    import mujoco.viewer; viewer = mujoco.viewer.launch_passive(m, d); viewer.cam.lookat[:] = (L.SPACING*(N-1)/2, 0.3, 0.3); viewer.cam.distance = 1.6 + 0.55*N; viewer.cam.azimuth = 200; viewer.cam.elevation = -18
frames = []; renderer = None
def snap(tag):
    global renderer
    if HEADLESS:
        if renderer is None: renderer = mujoco.Renderer(m, height=500, width=1600)
        cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE; cam.lookat[:] = (L.SPACING*(N-1)/2, 0.35, 0.25); cam.distance = 1.2 + 0.5*N; cam.azimuth = 200; cam.elevation = -14
        renderer.update_scene(d, camera=cam); from PIL import Image; Image.fromarray(renderer.render()).save(os.path.join(P.HERE, "out", (f"race_{tag}.png" if len(hands) == len(P.HANDS) else f"race_{'_'.join(hands)}_{tag}.png")))
def run(seconds, targets):
    steps = int(seconds/m.opt.timestep); per_ctrl = int(0.01/m.opt.timestep); sync_every = int(0.02/m.opt.timestep)
    for k in range(steps):
        t0 = time.time()
        if k % per_ctrl == 0:
            for a, p in zip(arms, targets): a.ik(p)
        for a in arms: a.suction_step()
        mujoco.mj_step(m, d)
        if viewer is not None and k % sync_every == 0:
            if not viewer.is_running(): sys.exit(0)
            viewer.sync(); time.sleep(max(0, 0.02 - (time.time()-t0)))
def move_until(targets, tol, max_s):
    t = 0.0
    while t < max_s:
        run(0.1, targets); t += 0.1
        if all(a.at(p, tol) for a, p in zip(arms, targets)): break
    run(0.3, targets)
bottle_top, bottle_mid = 0.12, 0.06
def grasp_z(a):
    if a.hand == "suction": return bottle_top + a.length - 0.004
    if a.hand == "bundle24": return 0.03 + a.length
    if a.hand == "fist6": return 0.035 + a.length
    if a.hand == "bloom": return bottle_top + 0.045                     # bowl ceiling 15 mm above the bottle top; the petal tips close around the bottle's middle
    if a.hand == "2f85": return bottle_mid + 0.01 + a.length - 0.030   # pad centres just above the bottle's middle
    return bottle_mid + a.length - 0.055          # finger middles at the bottle's middle
def grasp_xy(a):
    if a.hand in CURL:
        c = CURL[a.hand]; cw = np.array([c[0], -c[1], 0.0])            # site frame to world at the tool-down orientation
        return np.array([a.x0 + 0.55, 0.0]) - 0.10*cw[:2]               # start 100 mm to the finger side, then slide in until touching
    return np.array([a.x0 + 0.55, 0.0])
above = [np.array([*grasp_xy(a), grasp_z(a) + 0.15]) for a in arms]; grasp = [np.array([*grasp_xy(a), grasp_z(a)]) for a in arms]
move_until(above, 0.01, 10.0); snap("0_approach")
move_until(grasp, 0.006, 6.0); snap("1_descend")
# anthropomorphic hands: slide toward the bottle along the curl direction until the hand touches it
for step in range(16):
    moving = False
    for j, a in enumerate(arms):
        if a.hand in CURL and a.contacts()[0] == 0:
            c = CURL[a.hand]; cw = np.array([c[0], -c[1], 0.0]); grasp[j] = grasp[j] + 0.005*cw; moving = True
    if not moving: break
    run(0.15, grasp)
for k in range(20):
    for a in arms: a.hand_cmd((k+1)/20)
    run(0.1, grasp)
run(0.8, grasp); snap("2_close")
res = {}
for a in arms: n, f = a.contacts(); res[a.hand] = dict(contacts=n, force_N=round(f, 2), z0=float(d.xpos[a.bottle][2]), rel0=(d.xpos[a.bottle] - d.site_xpos[a.site]).tolist())
for k in range(30): run(0.1, [g + np.array([0, 0, 0.15*(k+1)/30]) for g in grasp])
run(2.0, [g + np.array([0, 0, 0.15]) for g in grasp]); snap("3_lift")
for a in arms:
    r = res[a.hand]; r["lift_mm"] = round((float(d.xpos[a.bottle][2]) - r["z0"])*1000, 1); r["slip_mm"] = round(float(np.linalg.norm((d.xpos[a.bottle] - d.site_xpos[a.site]) - np.array(r["rel0"])))*1000, 1)
    r["held"] = r["lift_mm"] > 100; del r["z0"]; del r["rel0"]
print(json.dumps(res, indent=1)); json.dump(res, open(os.path.join(P.HERE, "out", "race.json" if len(hands) == len(P.HANDS) else "race_" + "_".join(hands) + ".json"), "w"), indent=1)
if viewer is not None:
    print("race finished; window stays open.")
    while viewer.is_running(): t0 = time.time(); mujoco.mj_step(m, d); viewer.sync(); time.sleep(max(0, m.opt.timestep - (time.time()-t0)))
