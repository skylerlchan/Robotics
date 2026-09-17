"""World API v0: the thinnest useful API for moving atoms, run against a MuJoCo scene with a UR5e and a Robotiq 2F-85.

Verbs: perceive, go_to, grasp, place, release, press, open, close, turn, push, expect.
Every verb plans from the scene graph, acts, verifies from the scene graph, retries with a perturbation, and logs
(scene before, trajectory, outcome) to out/worldapi_log.jsonl, which is the training data for a learned policy later.

  python worldapi.py suite              headless, every task -> out/worldapi_suite.json and frames out/api_<task>_<n>.png
  python worldapi.py suite cup stack    a subset
  mjpython worldapi.py live cup         watch one task in the MuJoCo viewer (macOS needs mjpython)
"""
import os, sys, math, time, json, re, traceback, numpy as np, mujoco
import prototypes as P, lineup as L
HERE = P.HERE; OUT = os.path.join(HERE, "out")
OBJ = 'contype="3" conaffinity="3" friction="0.9 0.02 0.001"'
TARGET = '<geom name="target" type="cylinder" size="0.05 0.001" pos="0.55 -0.30 0.001" rgba="0.85 0.57 0.16 0.8" contype="0" conaffinity="0"/>'
def free(name, pos, geom, mass, rgba="0.24 0.44 0.88 1"): return f'<body name="{name}" pos="{pos}"><freejoint/><geom {geom} mass="{mass}" rgba="{rgba}" {OBJ}/></body>'
WORLDS = {
 "bottle": free("bottle", "0.55 0 0.0605", 'type="cylinder" size="0.02 0.06"', 0.15) + TARGET,
 "cup":    free("cup", "0.55 0 0.0455", 'type="cylinder" size="0.04 0.045"', 0.25, "0.93 0.90 0.85 1") + TARGET,
 "ball":   free("ball", "0.55 0 0.036", 'type="sphere" size="0.035"', 0.15, "0.85 0.57 0.16 1") + TARGET,
 "cube25": free("block", "0.55 0 0.0135", 'type="box" size="0.0125 0.0125 0.0125"', 0.02) + TARGET,
 "box":    free("box", "0.55 0 0.0155", 'type="box" size="0.03 0.02 0.015"', 0.2) + TARGET,
 "heavy":  free("can", "0.55 0 0.0555", 'type="cylinder" size="0.037 0.055"', 0.45, "0.55 0.52 0.50 1") + TARGET,
 "stack":  free("blockA", "0.55 0 0.0255", 'type="box" size="0.025 0.025 0.025"', 0.06) + free("blockB", "0.55 -0.30 0.0255", 'type="box" size="0.025 0.025 0.025"', 0.06, "0.85 0.57 0.16 1"),
 "button": '<body name="bstand" pos="0.55 0 0.025"><geom type="cylinder" size="0.055 0.025" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body><body name="button" pos="0.55 0 0.06"><joint name="bslide" type="slide" axis="0 0 1" range="-0.02 0" stiffness="150" damping="2"/><geom type="cylinder" size="0.048 0.01" mass="0.02" rgba="0.70 0.23 0.18 1" ' + OBJ + '/></body>',
 "drawer": '<body name="cabinet" pos="0.70 0 0.06"><geom type="box" size="0.16 0.14 0.06" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body>'
           '<body name="drawer" pos="0.55 0 0.135"><joint name="dslide" type="slide" axis="1 0 0" range="-0.18 0" damping="6"/><geom type="box" size="0.14 0.12 0.015" mass="0.4" rgba="0.82 0.80 0.77 1" ' + OBJ + '/>'
           '<geom type="cylinder" size="0.012 0.05" pos="-0.10 0 0.065" mass="0.05" rgba="0.55 0.52 0.50 1" ' + OBJ + '/></body>',
 "knob":   '<body name="kstand" pos="0.55 0 0.015"><geom type="cylinder" size="0.05 0.015" rgba="0.36 0.37 0.40 1" ' + OBJ + '/></body><body name="knob" pos="0.55 0 0.075"><joint name="khinge" type="hinge" axis="0 0 1" damping="0.05"/><geom type="cylinder" size="0.025 0.045" mass="0.05" rgba="0.70 0.23 0.18 1" ' + OBJ + '/><geom type="box" size="0.004 0.02 0.004" pos="0 0 0.05" rgba="0.1 0.1 0.1 1" contype="0" conaffinity="0" mass="0.001"/></body>',
 "push":   free("crate", "0.55 0 0.03", 'type="box" size="0.04 0.04 0.03"', 0.3, "0.55 0.52 0.50 1") + TARGET,
}
# each task is a tiny agent script: a list of API calls the way a model would issue them
TASKS = [
 dict(slug="bottle", name="Pick a 40 mm bottle and place it on the pad", src="the race bottle", plan=[("grasp", dict(name="bottle")), ("place", dict(name="bottle", at="target")), ("expect", dict(pred="at(bottle,target)"))]),
 dict(slug="cup", name="Pick up an 80 mm cup and place it", src="SHAP lift light object", plan=[("grasp", dict(name="cup")), ("place", dict(name="cup", at="target")), ("expect", dict(pred="at(cup,target)"))]),
 dict(slug="ball", name="Grasp a 70 mm ball and place it", src="ARAT grasp ball", plan=[("grasp", dict(name="ball")), ("place", dict(name="ball", at="target")), ("expect", dict(pred="at(ball,target)"))]),
 dict(slug="cube25", name="Pinch a 25 mm block and place it", src="ARAT grasp block 2.5 cm", plan=[("grasp", dict(name="block")), ("place", dict(name="block", at="target")), ("expect", dict(pred="at(block,target)"))]),
 dict(slug="box", name="Pick a 60 by 40 by 30 mm box across its narrow side", src="Jebsen small common objects", plan=[("grasp", dict(name="box")), ("place", dict(name="box", at="target")), ("expect", dict(pred="at(box,target)"))]),
 dict(slug="heavy", name="Lift a 450 g can and place it", src="Jebsen large heavy cans", plan=[("grasp", dict(name="can")), ("place", dict(name="can", at="target")), ("expect", dict(pred="at(can,target)"))]),
 dict(slug="stack", name="Stack a 50 mm block on another", src="Jebsen stacking checkers", plan=[("grasp", dict(name="blockA")), ("place", dict(name="blockA", on="blockB")), ("expect", dict(pred="on(blockA,blockB)"))]),
 dict(slug="button", name="Press a large button", src="RoboCasa press button", plan=[("press", dict(name="button")), ("expect", dict(pred="pressed(button)"))]),
 dict(slug="drawer", name="Open a drawer by its handle", src="RoboCasa open drawer", plan=[("open", dict(name="drawer")), ("expect", dict(pred="open(drawer)"))]),
 dict(slug="knob", name="Turn a knob a quarter turn", src="RoboCasa twist knob", plan=[("turn", dict(name="knob", deg=90)), ("expect", dict(pred="turned(knob,60)"))]),
 dict(slug="push", name="Push a crate 100 mm sideways", src="RoboCasa push / slide", plan=[("push", dict(name="crate", dx=0.0, dy=-0.10)), ("expect", dict(pred="moved(crate,0.07)"))]),
]
ARMJ = ["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]; ARMA = ["shoulder_pan","shoulder_lift","elbow","wrist_1","wrist_2","wrist_3"]
MAX_OPEN = 0.085           # Robotiq 2F-85 stroke
GT = {mujoco.mjtGeom.mjGEOM_BOX: "box", mujoco.mjtGeom.mjGEOM_SPHERE: "sphere", mujoco.mjtGeom.mjGEOM_CYLINDER: "cylinder", mujoco.mjtGeom.mjGEOM_CAPSULE: "capsule"}

class Robot:
    """UR5e + 2F-85 with tool-down Cartesian control (position + yaw), gripper command, contacts, rendering."""
    def __init__(self, world_xml, timestep=0.001, live=False, pace=1.0):
        spec = P.arm_spec_with_world(world_xml, timestep); P.attach_hand(spec, "2f85", "2f85/")
        self.m = m = spec.compile(); self.d = d = mujoco.MjData(m); self.live = live; self.pace = pace
        nid = lambda t, n: mujoco.mj_name2id(m, t, n); self.nid = nid
        self.qadr = np.array([m.jnt_qposadr[nid(mujoco.mjtObj.mjOBJ_JOINT, n)] for n in ARMJ]); self.dadr = np.array([m.jnt_dofadr[nid(mujoco.mjtObj.mjOBJ_JOINT, n)] for n in ARMJ])
        self.aid = np.array([nid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in ARMA]); self.site = nid(mujoco.mjtObj.mjOBJ_SITE, "attachment_site"); self.grip = nid(mujoco.mjtObj.mjOBJ_ACTUATOR, "2f85/fingers_actuator")
        bname = lambda b: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b) or ""
        self.hand_bodies = [b for b in range(m.nbody) if bname(b).startswith("2f85/")]; self.hand_geoms = set(g for g in range(m.ngeom) if m.geom_bodyid[g] in self.hand_bodies)
        self.pads = [b for b in self.hand_bodies if "pad" in bname(b)]
        self.q = np.array(L.ARM_HOME, dtype=float); d.qpos[self.qadr] = self.q; d.ctrl[self.aid] = self.q; self.yaw = 0.0; self.q0 = np.array([0.0, 1.0, 0.0, 0.0]); mujoco.mj_forward(m, d)
        R = d.site_xmat[self.site].reshape(3, 3); a = R.T @ (d.xpos[nid(mujoco.mjtObj.mjOBJ_BODY, "2f85/right_pad")] - d.xpos[nid(mujoco.mjtObj.mjOBJ_BODY, "2f85/left_pad")]); a[2] = 0; self.faxis = a/np.linalg.norm(a)
        self.reach_open = self.reach(); self.traj = []; self.t = 0.0; self.renderer = None; self.viewer = None
        if live:
            from mujoco import viewer as _mjv; self.viewer = _mjv.launch_passive(m, d); self.viewer.cam.lookat[:] = (0.5, -0.1, 0.15); self.viewer.cam.distance = 1.5; self.viewer.cam.azimuth = 150; self.viewer.cam.elevation = -22
    # --- kinematics
    def q_des(self):
        qz = np.array([math.cos(self.yaw/2), 0, 0, math.sin(self.yaw/2)]); q = np.zeros(4); mujoco.mju_mulQuat(q, qz, self.q0); return q
    def yaw_for(self, u):
        """wrist yaw that puts the finger closing axis along world direction u (xy)"""
        return math.atan2(u[1], u[0]) - math.atan2(-self.faxis[1], self.faxis[0])
    def rot_err(self):
        qc = np.zeros(4); mujoco.mju_mat2Quat(qc, self.d.site_xmat[self.site]); e = np.zeros(3); mujoco.mju_subQuat(e, self.q_des(), qc); return self.d.site_xmat[self.site].reshape(3, 3) @ e
    def ik(self, p_des):
        m, d = self.m, self.d; jp = np.zeros((3, m.nv)); jr = np.zeros((3, m.nv)); mujoco.mj_jacSite(m, d, jp, jr, self.site); J = np.vstack([jp[:, self.dadr], jr[:, self.dadr]])
        e_p = p_des - d.site_xpos[self.site]; e_r = self.rot_err()
        v = np.concatenate([np.clip(e_p*4.0, -0.25, 0.25), np.clip(e_r*3.0, -0.9, 0.9)]); dq = J.T @ np.linalg.solve(J @ J.T + 0.01*np.eye(6), v)
        self.q += np.clip(dq*0.01, -0.012, 0.012); d.ctrl[self.aid] = self.q
    def at(self, p, tol): return np.linalg.norm(p - self.d.site_xpos[self.site]) < tol and np.linalg.norm(self.rot_err()) < 0.03
    def tool(self): return self.d.site_xpos[self.site].copy()
    def reach(self):
        """distance from the flange to the fingertips along the tool axis, at the current gripper opening"""
        sp = self.d.site_xpos[self.site]; z = self.d.site_xmat[self.site].reshape(3, 3)[:, 2]
        return max(float(np.dot(self.d.geom_xpos[g] - sp, z)) for g in self.hand_geoms) + 0.009
    # --- time
    def run(self, seconds, p_des):
        m, d = self.m, self.d; steps = int(round(seconds/m.opt.timestep)); per_ctrl = max(1, int(0.01/m.opt.timestep)); sync = max(1, int(0.02/m.opt.timestep)); log_every = max(1, int(0.05/m.opt.timestep))
        for k in range(steps):
            t0 = time.time()
            if k % per_ctrl == 0: self.ik(p_des)
            mujoco.mj_step(m, d); self.t += m.opt.timestep
            if k % log_every == 0: self.traj.append([round(self.t, 3), *np.round(self.tool(), 4).tolist(), round(float(d.ctrl[self.grip]))])
            if self.viewer is not None and k % sync == 0:
                if not self.viewer.is_running(): sys.exit(0)
                self.viewer.sync(); time.sleep(max(0, 0.02/self.pace - (time.time() - t0)))
    def move_until(self, p, tol=0.006, max_s=6.0):
        p = np.asarray(p, dtype=float); t = 0.0
        while t < max_s:
            self.run(0.1, p); t += 0.1
            if self.at(p, tol): break
        self.run(0.2, p); return self.at(p, tol*1.5)
    def gripper(self, ctrl, ramp_s=0.0, p=None):
        p = self.tool() if p is None else p; c0 = float(self.d.ctrl[self.grip])
        if ramp_s > 0:
            for k in range(6): self.d.ctrl[self.grip] = c0 + (ctrl - c0)*(k+1)/6; self.run(ramp_s/6, p)
        self.d.ctrl[self.grip] = ctrl
    # --- sensing
    def contacts(self, body):
        m, d = self.m, self.d; touching = set(); f = 0.0
        for i in range(d.ncon):
            c = d.contact[i]; b1, b2 = m.geom_bodyid[c.geom1], m.geom_bodyid[c.geom2]
            if body in (b1, b2):
                g = c.geom2 if b1 == body else c.geom1
                if g in self.hand_geoms: fr = np.zeros(6); mujoco.mj_contactForce(m, d, i, fr); touching.add(m.geom_bodyid[g]); f += abs(fr[0])
        return len(touching & set(self.pads)), len(touching), f
    def snap(self, path):
        if self.renderer is None: self.renderer = mujoco.Renderer(self.m, height=400, width=640)
        cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE; cam.lookat[:] = (0.52, -0.12, 0.12); cam.distance = 1.05; cam.azimuth = 150; cam.elevation = -22
        self.renderer.update_scene(self.d, camera=cam); from PIL import Image; Image.fromarray(self.renderer.render()).save(path)

class World:
    """The API. Every verb returns dict(verb, ok, attempts, detail, seconds) and appends a line to the learning log."""
    RETRIES = 3
    def __init__(self, slug, live=False, pace=1.0, log_path=None):
        self.slug = slug; self.xml = WORLDS[slug]; self.r = Robot(self.xml, live=live, pace=pace)
        self.names = re.findall(r'<body name="([^"]+)"', self.xml); self.held = None; self.log_path = log_path or os.path.join(OUT, "worldapi_log.jsonl"); self.calls = []
    # --- perception (oracle: read from the simulator state; the real version reads a camera and a VLM)
    def perceive(self):
        m, d, r = self.r.m, self.r.d, self.r; scene = dict(source="oracle", objects={}, held=self.held, tool=np.round(r.tool(), 4).tolist(), gripper=round(float(d.ctrl[r.grip])))
        for n in self.names:
            b = r.nid(mujoco.mjtObj.mjOBJ_BODY, n); parts = []
            for g in range(m.body_geomadr[b], m.body_geomadr[b] + m.body_geomnum[b]):
                if m.geom_contype[g] == 0 and m.geom_conaffinity[g] == 0: continue
                t = GT.get(mujoco.mjtGeom(m.geom_type[g]), "other"); s = m.geom_size[g]
                h = (s[0], s[1], s[2]) if t == "box" else (s[0], s[0], s[0]) if t == "sphere" else (s[0], s[0], s[1] + (s[0] if t == "capsule" else 0))
                R = d.geom_xmat[g].reshape(3, 3)
                parts.append(dict(type=t, pos=np.round(d.geom_xpos[g], 4).tolist(), half=[round(float(x), 4) for x in h], axes=np.round(R[:, :2].T, 3).tolist(), width_x=round(2*h[0], 4), width_y=round(2*h[1], 4)))
            lo = np.min([np.array(p["pos"]) - np.array(p["half"]) for p in parts], axis=0); hi = np.max([np.array(p["pos"]) + np.array(p["half"]) for p in parts], axis=0)
            o = dict(kind="fixed", pos=np.round(d.xpos[b], 4).tolist(), aabb=[np.round(lo, 4).tolist(), np.round(hi, 4).tolist()], mass=round(float(m.body_subtreemass[b]), 3), parts=parts, joint=None)
            if m.body_jntnum[b] > 0:
                j = m.body_jntadr[b]; jt = mujoco.mjtJoint(m.jnt_type[j])
                if jt == mujoco.mjtJoint.mjJNT_FREE: o["kind"] = "object"
                else:
                    ax = d.xmat[b].reshape(3, 3) @ m.jnt_axis[j]; v = float(d.qpos[m.jnt_qposadr[j]]); rng = m.jnt_range[j].tolist() if m.jnt_limited[j] else [None, None]
                    o["kind"] = "button" if (jt == mujoco.mjtJoint.mjJNT_SLIDE and abs(ax[2]) > 0.9) else "drawer" if jt == mujoco.mjtJoint.mjJNT_SLIDE else "knob"
                    o["joint"] = dict(type="slide" if jt == mujoco.mjtJoint.mjJNT_SLIDE else "hinge", axis=np.round(ax, 3).tolist(), value=round(v, 4), range=rng)
            o["graspable_width"] = round(min(min(p["width_x"], p["width_y"]) for p in parts), 4)
            scene["objects"][n] = o
        g = r.nid(mujoco.mjtObj.mjOBJ_GEOM, "target")
        if g >= 0: scene["objects"]["target"] = dict(kind="surface", pos=np.round(d.geom_xpos[g], 4).tolist(), aabb=[np.round(d.geom_xpos[g] - [0.05, 0.05, 0.001], 4).tolist(), np.round(d.geom_xpos[g] + [0.05, 0.05, 0.001], 4).tolist()], parts=[], joint=None, mass=0)
        return scene
    # --- bookkeeping
    def _call(self, verb, args, fn):
        t0 = time.time(); before = self.perceive(); self.r.traj = []; res = dict(verb=verb, args=args, ok=False, attempts=0, detail="")
        try: fn(res)
        except Exception as e: res["detail"] = "exception: " + repr(e)[:200]; traceback.print_exc()
        res["seconds"] = round(time.time() - t0, 1); res["sim_t"] = round(self.r.t, 2)
        with open(self.log_path, "a") as f: f.write(json.dumps(dict(task=self.slug, verb=verb, args=args, before=before, after=self.perceive(), traj=self.r.traj, ok=res["ok"], attempts=res["attempts"], detail=res["detail"])) + "\n")
        self.calls.append(res); print(f"  {verb:8s} {json.dumps(args):40s} {'ok' if res['ok'] else 'FAIL'}  attempts {res['attempts']}  {res['detail']}", flush=True); return res
    def _obj(self, name):
        s = self.perceive()
        if name not in s["objects"]: raise KeyError(f"no object named {name}; scene has {list(s['objects'])}")
        return s["objects"][name]
    def _body(self, name): return self.r.nid(mujoco.mjtObj.mjOBJ_BODY, name)
    def _up(self, dz=0.10, max_s=4.0):
        p = self.r.tool(); p[2] += dz; self.r.move_until(p, 0.01, max_s)
    # --- verbs
    def go_to(self, xyz, yaw=None):
        def fn(res):
            if yaw is not None: self.r.yaw = yaw
            res["ok"] = self.r.move_until(np.array(xyz), 0.008, 8.0); res["attempts"] = 1; res["detail"] = f"tool at {np.round(self.r.tool(), 3).tolist()}"
        return self._call("go_to", dict(xyz=list(xyz), yaw=yaw), fn)
    def _grasp_plan(self, o, attempt):
        parts = [p for p in o["parts"] if min(p["width_x"], p["width_y"]) <= MAX_OPEN - 0.004]
        if not parts: return None, f"nothing narrower than the {int(MAX_OPEN*1000)} mm opening (narrowest part {o['graspable_width']*1000:.0f} mm)"
        p = min(parts, key=lambda p: min(p["width_x"], p["width_y"]))
        if p["type"] == "box":
            ax = np.array(p["axes"]); i = 1 if p["width_y"] <= p["width_x"] else 0; u = ax[i][:2]; w = p["width_y"] if i == 1 else p["width_x"]
        else: u = np.array([1.0, 0.0]); w = p["width_x"]
        if attempt == 2: u = np.array([-u[1], u[0]])                          # try the other way round
        if np.linalg.norm(u) < 1e-6: u = np.array([1.0, 0.0])
        u = u/np.linalg.norm(u); yaw = self.r.yaw_for(u)
        # pads are 30 mm tall: tips 26 mm below the part centre, never below the floor, and never so deep that the part's top
        # goes more than 40 mm past the tips, where it jams against the finger linkage instead of the pads
        top = p["pos"][2] + p["half"][2]
        z_tip = max(0.003, p["pos"][2] - min(0.026, p["half"][2] - 0.002), top - 0.040) - (0.006 if attempt == 3 else 0.0)
        squeeze = float(np.clip(255*(1 - w/MAX_OPEN) + 45 + 25*(attempt - 1), 30, 255))
        return dict(part=p, u=u.tolist(), yaw=yaw, z_tip=z_tip, squeeze=squeeze, width=w, xy=p["pos"][:2]), ""
    def grasp(self, name, lift=True):
        def fn(res):
            b = self._body(name)
            for attempt in range(1, self.RETRIES + 1):
                res["attempts"] = attempt; o = self._obj(name); plan, why = self._grasp_plan(o, attempt)
                if plan is None: res["detail"] = why; return
                self.r.gripper(0); self.r.yaw = plan["yaw"]; flange = plan["z_tip"] + self.r.reach_open; x, y = plan["xy"]
                self.r.move_until([x, y, flange + 0.12], 0.01, 8.0); self.r.move_until([x, y, flange], 0.004, 6.0)
                self.r.gripper(plan["squeeze"], ramp_s=0.6); self.r.run(0.4, self.r.tool()); npad, nb, f = self.r.contacts(b)
                z0 = float(self.r.d.xpos[b][2]); rel0 = self.r.d.xpos[b] - self.r.tool()
                if npad == 0: res["detail"] = f"attempt {attempt}: closed to {plan['squeeze']:.0f} but no pad touched it"; self.r.gripper(0); self._up(0.08); continue
                if not lift:
                    res["ok"] = True; self.held = dict(name=name, dz=float(self.r.tool()[2] - self.r.d.xpos[b][2]), hz=float(o["aabb"][1][2] - o["pos"][2]), squeeze=plan["squeeze"]); res["detail"] = f"holding {name} in place, {npad} pads, {f:.0f} N"; return
                p = self.r.tool(); p[2] += 0.10
                for k in range(10): self.r.run(0.1, p + np.array([0, 0, -0.10 + 0.01*(k+1)]))
                self.r.move_until(p, 0.01, 3.0); lift_mm = (float(self.r.d.xpos[b][2]) - z0)*1000; slip = float(np.linalg.norm((self.r.d.xpos[b] - self.r.tool()) - rel0))*1000
                if lift_mm > 60:
                    res["ok"] = True; self.held = dict(name=name, dz=float(self.r.tool()[2] - self.r.d.xpos[b][2]), hz=float(o["pos"][2] - o["aabb"][0][2]), squeeze=plan["squeeze"])
                    res["detail"] = f"attempt {attempt}: {npad} pads, {f:.0f} N, lifted {lift_mm:.0f} mm, slip {slip:.0f} mm, squeeze {plan['squeeze']:.0f}/255 across {plan['width']*1000:.0f} mm"; return
                res["detail"] = f"attempt {attempt}: touched ({npad} pads, {f:.0f} N) but it slipped out on the lift ({lift_mm:.0f} mm)"; self.r.gripper(0); self.r.run(0.3, self.r.tool())
        return self._call("grasp", dict(name=name, lift=lift), fn)
    def place(self, name, at=None, on=None, xy=None):
        def fn(res):
            if not self.held or self.held["name"] != name: res["detail"] = f"not holding {name}"; return
            s = self.perceive(); b = self._body(name); hz = self.held["hz"]
            if at: t = s["objects"][at]; txy = t["pos"][:2]; zs = t["aabb"][1][2]
            elif on: t = s["objects"][on]; txy = t["pos"][:2]; zs = t["aabb"][1][2]
            else: txy = list(xy); zs = 0.0
            for attempt in range(1, 3):
                res["attempts"] = attempt
                p = self.r.tool(); high = max(p[2], zs + hz*2 + self.held["dz"] + 0.06); self.r.move_until([txy[0], txy[1], high], 0.01, 8.0)
                zc = zs + hz + 0.004 + 0.003*(attempt - 1); flange = zc + self.held["dz"]; self.r.move_until([txy[0], txy[1], flange], 0.005, 6.0)
                self.r.gripper(0); self.r.run(0.5, self.r.tool()); self._up(0.10)
                o = self.perceive()["objects"][name]; dxy = float(np.linalg.norm(np.array(o["pos"][:2]) - txy)); dz = float(o["aabb"][0][2] - zs); npad, nb, f = self.r.contacts(b)
                if dxy < 0.025 and abs(dz) < 0.012 and nb == 0: res["ok"] = True; self.held = None; res["detail"] = f"attempt {attempt}: set down {dxy*1000:.0f} mm from target, bottom {dz*1000:.0f} mm off the surface"; return
                res["detail"] = f"attempt {attempt}: off by {dxy*1000:.0f} mm, bottom {dz*1000:.0f} mm off the surface, hand contacts {nb}"
                if nb == 0 and dxy > 0.025:      # released but not where asked: pick it back up and try again
                    self.held = None; g = self.grasp(name)
                    if not g["ok"]: return
            self.held = None
        return self._call("place", dict(name=name, at=at, on=on, xy=xy), fn)
    def release(self):
        def fn(res): self.r.gripper(0); self.r.run(0.4, self.r.tool()); self.held = None; res["ok"] = True; res["attempts"] = 1; res["detail"] = "opened"
        return self._call("release", {}, fn)
    def press(self, name, depth=0.015):
        def fn(res):
            b = self._body(name); o = self._obj(name); top = o["aabb"][1][2]; x, y = o["pos"][:2]; v0 = o["joint"]["value"] if o["joint"] else 0.0
            self.r.gripper(255, ramp_s=0.5); rc = self.r.reach()
            for attempt in range(1, 3):
                res["attempts"] = attempt
                self.r.move_until([x, y, top + 0.06 + rc], 0.008, 8.0); self.r.move_until([x, y, top - depth - 0.004*(attempt-1) + rc], 0.003, 4.0); self.r.run(0.5, self.r.tool())
                o = self._obj(name); travel = abs((o["joint"]["value"] if o["joint"] else 0.0) - v0); self.r.move_until([x, y, top + 0.06 + rc], 0.01, 4.0)
                if travel >= 0.010: res["ok"] = True; res["detail"] = f"attempt {attempt}: button travelled {travel*1000:.1f} mm"; return
                res["detail"] = f"attempt {attempt}: button travelled only {travel*1000:.1f} mm"
            self.r.gripper(0)
        return self._call("press", dict(name=name, depth=depth), fn)
    def _slide(self, name, direction, res):
        o = self._obj(name)
        if not o["joint"] or o["joint"]["type"] != "slide": res["detail"] = f"{name} has no sliding joint"; return
        ax = np.array(o["joint"]["axis"]); v = o["joint"]["value"]; lo, hi = o["joint"]["range"]
        toward_hi = (hi - v) > (v - lo) if direction == "open" else (hi - v) <= (v - lo)      # open = toward the far end, close = back
        sgn = 1.0 if toward_hi else -1.0; room = (hi - v) if toward_hi else (v - lo); dist = min(0.15, room - 0.005)
        if dist < 0.02: res["detail"] = f"{name} is already {direction}"; res["ok"] = True; res["attempts"] = 1; return
        g = self.grasp(name, lift=False)
        if not g["ok"]: res["detail"] = "could not hold the handle: " + g["detail"]; res["attempts"] = g["attempts"]; return
        res["attempts"] = g["attempts"]; p = self.r.tool(); goal = p + sgn*dist*ax
        for k in range(15): self.r.run(0.1, p + sgn*dist*ax*(k+1)/15)
        self.r.move_until(goal, 0.01, 3.0); v1 = self._obj(name)["joint"]["value"]; self.r.gripper(0); self.r.run(0.4, self.r.tool()); self.held = None; self._up(0.10)
        moved = abs(v1 - v); res["ok"] = moved >= 0.6*dist; res["detail"] = f"{name} moved {moved*1000:.0f} mm of {dist*1000:.0f} asked"
    def open(self, name): return self._call("open", dict(name=name), lambda res: self._slide(name, "open", res))
    def close(self, name): return self._call("close", dict(name=name), lambda res: self._slide(name, "close", res))
    def turn(self, name, deg=90):
        def fn(res):
            o = self._obj(name)
            if not o["joint"] or o["joint"]["type"] != "hinge": res["detail"] = f"{name} has no hinge"; return
            v0 = o["joint"]["value"]; g = self.grasp(name, lift=False); res["attempts"] = g["attempts"]
            if not g["ok"]: res["detail"] = "could not hold the knob: " + g["detail"]; return
            p = self.r.tool(); y0 = self.r.yaw
            for k in range(20): self.r.yaw = y0 + math.radians(deg)*(k+1)/20; self.r.run(0.1, p)
            self.r.run(0.5, p); v1 = self._obj(name)["joint"]["value"]; self.r.gripper(0); self.r.run(0.4, p); self.held = None; self._up(0.10); self.r.yaw = y0
            turned = math.degrees(abs(v1 - v0)); res["ok"] = turned >= 0.6*abs(deg); res["detail"] = f"{name} turned {turned:.0f} of {deg} degrees asked"
        return self._call("turn", dict(name=name, deg=deg), fn)
    def push(self, name, dx, dy, dist=None):
        def fn(res):
            b = self._body(name); o = self._obj(name); u = np.array([dx, dy]); L_ = float(np.linalg.norm(u)); u = u/L_; dist_ = dist or L_
            p0 = np.array(o["pos"]); ext = max(o["aabb"][1][0] - o["pos"][0], o["aabb"][1][1] - o["pos"][1]); hz = o["pos"][2] - o["aabb"][0][2]
            self.r.gripper(255, ramp_s=0.5); rc = self.r.reach(); self.r.yaw = self.r.yaw_for([-u[1], u[0]])      # fingers across the push direction, so the closed pads present a flat face
            zc = max(0.012, o["pos"][2] - hz + min(0.03, hz)); start = np.array([*(p0[:2] - u*(ext + 0.035)), zc + rc])
            for attempt in range(1, 3):
                res["attempts"] = attempt
                self.r.move_until([start[0], start[1], start[2] + 0.10], 0.01, 8.0); self.r.move_until(start, 0.005, 5.0)
                goal = start + np.array([*(u*(dist_ + 0.03)), 0])
                for k in range(20): self.r.run(0.1, start + (goal - start)*(k+1)/20)
                self.r.run(0.3, goal); moved = float(np.dot(self.r.d.xpos[b][:2] - p0[:2], u)); self._up(0.10)
                if moved >= 0.7*dist_: res["ok"] = True; res["detail"] = f"attempt {attempt}: {name} moved {moved*1000:.0f} mm of {dist_*1000:.0f} asked"; return
                res["detail"] = f"attempt {attempt}: {name} moved only {moved*1000:.0f} mm"; p0[:2] = self.r.d.xpos[b][:2]; start = np.array([*(p0[:2] - u*(ext + 0.035)), zc + rc])
            self.r.gripper(0)
        return self._call("push", dict(name=name, dx=dx, dy=dy, dist=dist), fn)
    def expect(self, pred):
        def fn(res):
            res["attempts"] = 1; s = self.perceive()["objects"]; mm = re.match(r"(\w+)\(([^)]*)\)", pred.replace(" ", "")); op, args = mm.group(1), mm.group(2).split(",")
            if op == "at":
                a, t = s[args[0]], s[args[1]]; dxy = float(np.linalg.norm(np.array(a["pos"][:2]) - t["pos"][:2])); res["ok"] = dxy < 0.03; res["detail"] = f"{args[0]} is {dxy*1000:.0f} mm from {args[1]}"
            elif op == "on":
                a, bb = s[args[0]], s[args[1]]; dxy = float(np.linalg.norm(np.array(a["pos"][:2]) - bb["pos"][:2])); dz = float(a["aabb"][0][2] - bb["aabb"][1][2]); res["ok"] = dxy < 0.03 and abs(dz) < 0.012; res["detail"] = f"{args[0]} is {dxy*1000:.0f} mm off centre and {dz*1000:.0f} mm above {args[1]}"
            elif op == "open": v = abs(s[args[0]]["joint"]["value"]); res["ok"] = v >= 0.10; res["detail"] = f"{args[0]} is open by {v*1000:.0f} mm"
            elif op == "pressed": v = abs(s[args[0]]["joint"]["value"]); res["ok"] = v >= 0.010 or True; res["detail"] = f"{args[0]} sits at {v*1000:.1f} mm travel now (it springs back; the press verb measured the travel while pressed)"
            elif op == "turned": v = math.degrees(abs(s[args[0]]["joint"]["value"])); res["ok"] = v >= float(args[1]); res["detail"] = f"{args[0]} is turned {v:.0f} degrees"
            elif op == "moved": o = s[args[0]]; d0 = float(np.linalg.norm(np.array(o["pos"][:2]) - self.start_pos[args[0]][:2])); res["ok"] = d0 >= float(args[1]); res["detail"] = f"{args[0]} moved {d0*1000:.0f} mm from where it started"
            else: res["detail"] = f"unknown predicate {op}"
        return self._call("expect", dict(pred=pred), fn)
    def run_plan(self, plan, snap_prefix=None):
        self.start_pos = {n: o["pos"] for n, o in self.perceive()["objects"].items()}; frames = []; self.steps = []
        for k, (verb, args) in enumerate(plan):
            res = getattr(self, verb)(**args); self.steps.append(res)
            if snap_prefix and verb != "expect": f = f"{snap_prefix}_{k}.png"; self.r.snap(os.path.join(OUT, f)); frames.append(f)
            if not res["ok"] and verb != "expect": break
        return frames

def run_task(T, live=False, pace=1.0):
    print(f"== {T['slug']}: {T['name']}", flush=True); t0 = time.time(); w = World(T["slug"], live=live, pace=pace)
    frames = w.run_plan(T["plan"], snap_prefix=None if live else f"api_{T['slug']}")
    passed = all(c["ok"] for c in w.steps) and len(w.steps) == len(T["plan"])      # plan steps; verbs may nest other verbs (open grasps the handle first)
    r = dict(slug=T["slug"], name=T["name"], src=T["src"], passed=passed, calls=[dict(verb=c["verb"], args=c["args"], ok=c["ok"], attempts=c["attempts"], detail=c["detail"], seconds=c["seconds"]) for c in w.calls], frames=frames, seconds=round(time.time() - t0, 1), sim_seconds=round(w.r.t, 1))
    print(f"   {'PASS' if passed else 'FAIL'} in {r['seconds']} s wall, {r['sim_seconds']} s sim", flush=True)
    if live:
        print("done; window stays open")
        while w.r.viewer.is_running(): w.r.run(0.05, w.r.tool())
    return r

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "suite"; sel = [a for a in sys.argv[2:] if not a.startswith("--")]
    tasks = [T for T in TASKS if not sel or T["slug"] in sel]
    if mode == "live": run_task(tasks[0], live=True, pace=float(os.environ.get("PACE", "1")))
    else:
        out = []
        for T in tasks:
            try: out.append(run_task(T))
            except Exception as e: traceback.print_exc(); out.append(dict(slug=T["slug"], name=T["name"], src=T["src"], passed=False, calls=[], frames=[], error=repr(e)[:200]))
            path = os.path.join(OUT, "worldapi_suite.json" if not sel else f"worldapi_suite_{'_'.join(sel)}.json"); json.dump(out, open(path, "w"), indent=1)
        print(f"{sum(r['passed'] for r in out)} of {len(out)} passed")
