"""A single-purpose laundry cell: two UR5e arms, one table, one towel, and nothing else to do.

The question is not whether folding is possible. It is what happens when perception stops being free.
Every trial runs identical physics, identical motions and identical skills, changing only what the machine knows:

  oracle  it is told the towel's exact outline and which edge is the free one (what a clean simulation demo assumes)
  depth   it gets one overhead depth image and works both out for itself (what a real cell gets)

Three starting conditions: laid out, lightly rumpled, thrown in a heap.

  python laundry.py trials 5                     all levels, both modes -> out/laundry.json and frames out/lau_*.png
  python laundry.py trials 5 flat rumpled        pick levels
  mjpython laundry.py live depth rumpled         watch one trial
"""
import os, sys, math, json, time, traceback, numpy as np, mujoco
import prototypes as P
HERE = P.HERE; OUT = os.path.join(HERE, "out")
ARMJ = ["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]
ARMA = ["shoulder_pan","shoulder_lift","elbow","wrist_1","wrist_2","wrist_3"]
HOME = [-1.5708, -1.5708, 1.5708, -1.5708, -1.5708, 0.0]
N = 11                      # the towel is an N x N grid of vertices
SP = 0.04                   # 40 mm between vertices -> a 400 mm square towel
SIDE = SP*(N - 1)
TABLE_Z = 0.10
CX, CY = 0.55, 0.0
ARM_B_X = 1.10
FLAT_AREA = SIDE*SIDE
CAM_Z = 1.00; CAM_FOVY = 45.0; CAM_PIX = 240
LEVELS = ("flat", "rumpled", "heap")
SIM_BUDGET = {"flat": 90.0, "rumpled": 150.0, "heap": 190.0}

def cell_xml(timestep=0.002):
    """the cell as text, because flexcomp is a compile-time element and cannot be built through MjSpec"""
    return f'''<mujoco model="laundry">
  <option timestep="{timestep}" integrator="implicitfast" cone="elliptic" impratio="5" solver="Newton" tolerance="1e-8"/>
  <visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/><map znear="0.01"/></visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.86 0.87 0.89" rgb2="0.80 0.82 0.85" width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="12 12" reflectance="0.04"/>
    <material name="tabletop" rgba="0.30 0.32 0.36 1" reflectance="0.02"/>
    <material name="towel" rgba="0.86 0.89 0.93 1"/>
  </asset>
  <worldbody>
    <light pos="0.55 -0.9 1.9" dir="0 0.4 -0.9" castshadow="true"/>
    <light pos="0.55 0.9 1.5" dir="0 -0.5 -0.8" castshadow="false" diffuse="0.3 0.3 0.3"/>
    <geom name="floor" type="plane" size="4 4 0.01" material="grid" contype="3" conaffinity="3"/>
    <geom name="table" type="box" size="0.34 0.34 {TABLE_Z/2}" pos="{CX} {CY} {TABLE_Z/2}" material="tabletop"
          contype="3" conaffinity="3" friction="0.9 0.02 0.001"/>
    <camera name="top" pos="{CX} {CY} {CAM_Z}" quat="1 0 0 0" fovy="{CAM_FOVY}"/>
    <flexcomp name="towel" type="grid" count="{N} {N} 1" spacing="{SP} {SP} {SP}" pos="{CX} {CY} {TABLE_Z + 0.30}"
              dim="2" mass="0.30" radius="0.005" material="towel">
      <edge equality="true" solref="0.005 1"/>
      <contact selfcollide="none" internal="false" contype="3" conaffinity="3" friction="0.9 0.02 0.001" solref="0.003 1" solimp="0.95 0.99 0.001"/>
    </flexcomp>
  </worldbody>
</mujoco>'''

def build(timestep=0.002):
    path = os.path.join(P.UR, f"_laundry_{os.getpid()}.xml"); open(path, "w").write(cell_xml(timestep))
    w = mujoco.MjSpec.from_file(path); os.remove(path)
    for i, (x, yaw) in enumerate([(0.0, 0.0), (ARM_B_X, math.pi)]):
        arm = mujoco.MjSpec.from_file(os.path.join(P.UR, "ur5e.xml")); P.attach_hand(arm, "2f85", "2f85/")
        fr = w.worldbody.add_frame(pos=[x, 0, 0], quat=[math.cos(yaw/2), 0, 0, math.sin(yaw/2)])
        w.attach(arm, prefix=f"a{i}/", frame=fr)
    return w

# ---------------------------------------------------------------- geometry
def hull(pts):
    pts = sorted(map(tuple, np.round(np.asarray(pts), 6)))
    if len(pts) < 3: return np.array(pts)
    def half(ps):
        out = []
        for p in ps:
            while len(out) >= 2 and (out[-1][0]-out[-2][0])*(p[1]-out[-2][1]) - (out[-1][1]-out[-2][1])*(p[0]-out[-2][0]) <= 0: out.pop()
            out.append(p)
        return out
    return np.array(half(pts)[:-1] + half(pts[::-1])[:-1])
def poly_area(p):
    if len(p) < 3: return 0.0
    x, y = p[:, 0], p[:, 1]; return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))/2)
def min_rect(pts):
    """minimum-area rectangle: returns (centre, long axis, short axis, half long, half short)"""
    h = hull(pts)
    if len(h) < 3: return np.array([CX, CY]), np.array([1.0, 0]), np.array([0, 1.0]), 0.0, 0.0
    best = None
    for i in range(len(h)):
        e = h[(i+1) % len(h)] - h[i]; a = math.atan2(e[1], e[0]); c, s = math.cos(-a), math.sin(-a)
        R = np.array([[c, -s], [s, c]]); q = h @ R.T; lo, hi = q.min(axis=0), q.max(axis=0)
        area = float((hi[0]-lo[0])*(hi[1]-lo[1]))
        if best is None or area < best[0]: best = (area, a, lo, hi)
    _, a, lo, hi = best; c, s = math.cos(a), math.sin(a)
    ex, ey = np.array([c, s]), np.array([-s, c])
    mid = (lo + hi)/2; centre = ex*mid[0] + ey*mid[1]
    hx, hy = (hi[0]-lo[0])/2, (hi[1]-lo[1])/2
    return (centre, ex, ey, hx, hy) if hx >= hy else (centre, ey, ex, hy, hx)
def rect_corners(centre, u, v, hu, hv):
    return np.array([centre + u*su*hu + v*sv*hv for su, sv in ((-1,-1), (1,-1), (1,1), (-1,1))])
def clamp(p):
    p = np.asarray(p, dtype=float).copy()
    p[0] = float(np.clip(p[0], CX-0.32, CX+0.32)); p[1] = float(np.clip(p[1], CY-0.32, CY+0.32))
    p[2] = float(np.clip(p[2], TABLE_Z-0.02, TABLE_Z+0.55)); return p

class Cell:
    def __init__(self, seed=0, live=False, timestep=0.002, pace=1.0):
        self.spec = build(timestep); self.m = m = self.spec.compile(); self.d = mujoco.MjData(m)
        self.live = live; self.pace = pace; self.t = 0.0; self.renderer = None; self.dren = None; self.viewer = None
        nid = lambda t, n: mujoco.mj_name2id(m, t, n); self.nid = nid
        self.vb = np.array([nid(mujoco.mjtObj.mjOBJ_BODY, f"towel_{i}") for i in range(N*N)])
        assert self.vb.min() >= 0
        self.vq = np.array([m.jnt_qposadr[m.body_jntadr[b]] for b in self.vb])
        self.vd = np.array([m.jnt_dofadr[m.body_jntadr[b]] for b in self.vb])
        self.vp0 = m.body_pos[self.vb].copy()
        self.corner_ids = [0, N-1, N*N-1, N*(N-1)]
        self.arms = {p: Arm(self, p) for p in ("a0", "a1")}
        self.rng = np.random.default_rng(seed); self.seed = seed; self.cloud = None; self.budget = 1e9
    # ---- towel state
    def verts(self): return self.d.xpos[self.vb].copy()
    def footprint(self): return poly_area(hull(self.verts()[:, :2]))
    def coverage(self): return self.footprint()/FLAT_AREA
    def on_table(self):
        v = self.verts(); return bool(np.all(np.abs(v[:, 0]-CX) < 0.335) and np.all(np.abs(v[:, 1]-CY) < 0.335))
    def set_vert(self, i, p):
        self.d.qpos[self.vq[i]:self.vq[i]+3] = np.asarray(p) - self.vp0[i]; self.d.qvel[self.vd[i]:self.vd[i]+3] = 0
    def crumple(self, level="heap"):
        rest = self.vp0[:, :2] - [CX, CY]
        if level == "flat": ang, k, jit, drop = self.rng.uniform(-0.26, 0.26), 1.0, 0.0, 0.006
        elif level == "rumpled": ang, k, jit, drop = self.rng.uniform(-0.5, 0.5), self.rng.uniform(0.80, 0.92), 0.014, 0.05
        else: ang, k, jit, drop = self.rng.uniform(0, 2*math.pi), self.rng.uniform(0.35, 0.7), 0.022, 0.16
        c, s = math.cos(ang), math.sin(ang); r = (rest @ np.array([[c, -s], [s, c]]).T)*k
        if jit: r = r + self.rng.normal(0, jit, r.shape)
        off = self.rng.uniform(-0.03, 0.03, 2)
        z = np.full(N*N, TABLE_Z + drop) + (self.rng.normal(0, 0.03, N*N) if level == "heap" else 0.0)
        pos = np.c_[r + [CX + off[0], CY + off[1]], z]
        for i in range(N*N): self.set_vert(i, pos[i])
        for a in self.arms.values(): a.go_home()
        mujoco.mj_forward(self.m, self.d); self.step({"flat": 1.2, "rumpled": 1.8}.get(level, 2.6))
    # ---- time
    def out_of_time(self): return self.t > self.budget
    def step(self, seconds, targets=None):
        m, d = self.m, self.d; n = int(round(seconds/m.opt.timestep))
        per = max(1, int(0.008/m.opt.timestep)); syn = max(1, int(0.02/m.opt.timestep))
        for k in range(n):
            t0 = time.time()
            if k % per == 0:
                for p, a in self.arms.items():
                    if targets and p in targets: a.hold_at = np.asarray(targets[p], dtype=float); a.ik(a.hold_at)
                    else: a.hold()
            mujoco.mj_step(m, d); self.t += m.opt.timestep
            for a in self.arms.values(): a.pin()
            if self.viewer is not None and k % syn == 0:
                if not self.viewer.is_running(): sys.exit(0)
                self.viewer.sync(); time.sleep(max(0, 0.02/self.pace - (time.time()-t0)))
    def move(self, targets, tol=0.012, max_s=4.0, clamped=True):
        if clamped: targets = {p: clamp(q) for p, q in targets.items()}
        t = 0.0
        while t < max_s and not self.out_of_time():
            self.step(0.1, targets); t += 0.1
            if all(self.arms[p].at(q, tol) for p, q in targets.items()): break
        self.step(0.12, targets); return all(self.arms[p].at(q, tol*1.7) for p, q in targets.items())
    def park(self):
        """straight up first, then out to the side: sweeping sideways at table height bulldozes the towel"""
        self.move({p: clamp([a.tip()[0], a.tip()[1], 0.46]) for p, a in self.arms.items()}, 0.05, 1.4)
        out = {p: np.array([float(np.clip(a.tip()[0], 0.18, 0.92)), 0.46 if p == "a0" else -0.46, 0.50]) for p, a in self.arms.items()}
        self.move(out, 0.07, 1.8, clamped=False)
    # ---- perception
    def depth_cloud(self):
        if self.dren is None:
            self.dren = mujoco.Renderer(self.m, height=CAM_PIX, width=CAM_PIX); self.dren.enable_depth_rendering()
        self.dren.update_scene(self.d, camera="top"); z = self.dren.render()
        f = 0.5*CAM_PIX/math.tan(math.radians(CAM_FOVY)/2); rr, cc = np.mgrid[0:CAM_PIX, 0:CAM_PIX]
        X = CX + (cc - (CAM_PIX-1)/2)*z/f; Y = CY - (rr - (CAM_PIX-1)/2)*z/f; Z = CAM_Z - z
        ok = (Z > TABLE_Z + 0.004) & (Z < TABLE_Z + 0.22) & (np.abs(X-CX) < 0.33) & (np.abs(Y-CY) < 0.33)
        self.cloud = np.c_[X[ok], Y[ok], Z[ok]] if ok.sum() >= 30 else None
        return self.cloud
    def observe(self, mode):
        """what the machine believes about the towel: its outline, its highest point, and which edge is free"""
        if mode == "oracle":
            v = self.verts(); pts = v[:, :2]; top = v[np.argmax(v[:, 2])]
        else:
            c = self.depth_cloud()
            if c is None: return None
            pts = c[:, :2]; top = c[np.argmax(c[:, 2])]
        centre, u, vv, hu, hv = min_rect(pts)
        return dict(centre=centre, u=u, v=vv, hu=hu, hv=hv, corners=rect_corners(centre, u, vv, hu, hv), top=top,
                    free=self.free_side(mode, centre, vv, hv))
    def free_side(self, mode, centre, v, hv):
        """which edge across the short axis is the open edge rather than the folded crease"""
        if mode == "oracle":
            c = self.verts()[self.corner_ids][:, :2] - centre         # the towel's true corners lie on the free edge
            return 1.0 if float(np.mean(c @ v)) >= 0 else -1.0
        c = self.cloud
        if c is None or hv < 0.02: return 1.0
        s = (c[:, :2] - centre) @ v; band = 0.30*hv
        hi = c[s > hv - band, 2]; lo = c[s < -hv + band, 2]
        if len(hi) < 8 or len(lo) < 8: return 1.0
        # measured, not assumed: the crease edge sits LOWER than the free edge, because the top layer ramps down
        # into the fold while the free edge keeps its full thickness. The margin is about 2.6 mm: under one pixel.
        return 1.0 if float(hi.mean()) > float(lo.mean()) else -1.0
    # ---- rendering
    def snap(self, name):
        if self.renderer is None: self.renderer = mujoco.Renderer(self.m, height=520, width=780)
        c = mujoco.MjvCamera(); c.type = mujoco.mjtCamera.mjCAMERA_FREE
        c.lookat[:] = (CX, CY, TABLE_Z); c.distance = 1.15; c.azimuth = 138; c.elevation = -32
        self.renderer.update_scene(self.d, camera=c)
        from PIL import Image; Image.fromarray(self.renderer.render()).save(os.path.join(OUT, name)); return name

class Arm:
    """UR5e + 2F-85 driven in Cartesian space, tool down, with a cloth picker at the fingertips."""
    def __init__(self, cell, prefix):
        self.c = cell; self.p = prefix + "/"; m = cell.m; nid = cell.nid
        self.qadr = np.array([m.jnt_qposadr[nid(mujoco.mjtObj.mjOBJ_JOINT, self.p + n)] for n in ARMJ])
        self.dadr = np.array([m.jnt_dofadr[nid(mujoco.mjtObj.mjOBJ_JOINT, self.p + n)] for n in ARMJ])
        self.aid = np.array([nid(mujoco.mjtObj.mjOBJ_ACTUATOR, self.p + n) for n in ARMA])
        self.site = nid(mujoco.mjtObj.mjOBJ_SITE, self.p + "attachment_site")
        self.grip = nid(mujoco.mjtObj.mjOBJ_ACTUATOR, self.p + "2f85/fingers_actuator")
        self.pads = [nid(mujoco.mjtObj.mjOBJ_BODY, self.p + f"2f85/{s}_pad") for s in ("left", "right")]
        self.qd = np.array([0.0, 1.0, 0.0, 0.0]); self.held = []; self.hold_at = None; self.go_home()
        mujoco.mj_forward(m, cell.d); d = cell.d
        hg = [g for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]) or "").startswith(self.p + "2f85/")]
        zax = d.site_xmat[self.site].reshape(3, 3)[:, 2]
        self.reach = max(float(np.dot(d.geom_xpos[g] - d.site_xpos[self.site], zax)) + float(m.geom_rbound[g]) for g in hg) - 0.012
    def go_home(self):
        d = self.c.d; self.q = np.array(HOME, dtype=float); d.qpos[self.qadr] = self.q
        d.ctrl[self.aid] = self.q; d.ctrl[self.grip] = 0; self.held = []; self.hold_at = None
    def tip(self):
        """the point between the jaws where fabric is actually caught, measured from the gripper's real extent"""
        d = self.c.d; return d.site_xpos[self.site] + d.site_xmat[self.site].reshape(3, 3)[:, 2]*self.reach
    def ik(self, tip_des):
        c = self.c; m, d = c.m, c.d
        p_des = np.asarray(tip_des) + np.array([0, 0, d.site_xpos[self.site][2] - self.tip()[2]])
        jp = np.zeros((3, m.nv)); jr = np.zeros((3, m.nv)); mujoco.mj_jacSite(m, d, jp, jr, self.site)
        J = np.vstack([jp[:, self.dadr], jr[:, self.dadr]])
        e_p = p_des - d.site_xpos[self.site]
        qc = np.zeros(4); mujoco.mju_mat2Quat(qc, d.site_xmat[self.site]); e_r = np.zeros(3)
        mujoco.mju_subQuat(e_r, self.qd, qc); e_r = d.site_xmat[self.site].reshape(3, 3) @ e_r
        v = np.concatenate([np.clip(e_p*5.0, -0.35, 0.35), np.clip(e_r*3.0, -0.9, 0.9)])
        dq = J.T @ np.linalg.solve(J @ J.T + 0.012*np.eye(6), v)
        self.q += np.clip(dq*0.016, -0.03, 0.03); d.ctrl[self.aid] = self.q
    def at(self, tip_des, tol=0.012): return float(np.linalg.norm(np.asarray(tip_des) - self.tip())) < tol
    def hold(self):
        if self.hold_at is not None: self.ik(self.hold_at)
    # a pinch catches whatever lies between the jaws when they close: a box, not a point
    def jaws(self):
        d = self.c.d; R = d.site_xmat[self.site].reshape(3, 3)
        ax = d.xpos[self.pads[1]] - d.xpos[self.pads[0]]; ax = ax - R[:, 2]*float(np.dot(ax, R[:, 2]))
        n = np.linalg.norm(ax); ax = ax/n if n > 1e-9 else R[:, 0]
        return ax, np.cross(R[:, 2], ax), R[:, 2]
    def pick(self, span=0.048, width=0.030, depth=0.030):   # the towel is sampled every 40 mm, so the catch box spans half a cell
        ax, pp, zz = self.jaws(); t = self.tip(); v = self.c.verts(); r = v - t
        idx = np.where((np.abs(r @ ax) < span) & (np.abs(r @ pp) < width) & (np.abs(r @ zz) < depth))[0]
        if len(idx) == 0: return False
        self.c.d.ctrl[self.grip] = 200; self.held = [(int(i), v[i] - t) for i in idx]; return True
    def drop(self): self.held = []; self.c.d.ctrl[self.grip] = 0
    def pin(self):
        if not self.held: return
        t = self.tip()
        for i, off in self.held: self.c.set_vert(i, t + off)   # hold the caught fabric where it was caught, do not gather it in

# ---------------------------------------------------------------- skills
def grab_at(cell, arm, xy):
    """descend onto the fabric at xy and pinch; returns whether anything was caught"""
    a = cell.arms[arm]; v = cell.verts()
    near = v[np.argmin(np.linalg.norm(v[:, :2] - np.asarray(xy)[:2], axis=1))]
    cell.move({arm: np.array([xy[0], xy[1], max(near[2], TABLE_Z) + 0.12])}, 0.02, 2.2)
    cell.move({arm: np.array([xy[0], xy[1], max(near[2] - 0.004, TABLE_Z - 0.014)])}, 0.008, 2.2)
    return a.pick()
def carry(cell, moves, height=0.14, steps=40, settle=0.4, dwell=0.075):
    """carry fingertips along a lifted arc to their targets, both arms together.
       Slowly: the fabric is pinned to the fingertips, so a fast arc flings the towel off the table."""
    starts = {p: cell.arms[p].tip().copy() for p in moves}
    for k in range(1, steps+1):
        u = k/steps; tg = {}
        for p, goal in moves.items():
            s = starts[p]; g = np.asarray(goal); q = s + (g - s)*u
            q[2] = max(q[2], (1-u)*s[2] + u*g[2]) + height*math.sin(math.pi*u); tg[p] = q
        cell.step(dwell, tg)
        if cell.out_of_time(): break
    cell.move({p: np.asarray(g) for p, g in moves.items()}, 0.012, 1.2); cell.step(settle)
def release(cell, arms, away=None):
    """let go, slide the fingers out sideways, then lift. Lifting straight up carries the draped towel with the hand."""
    for p in arms: cell.arms[p].drop()
    cell.step(0.6)
    if away is not None:
        a2 = np.array([away[0], away[1], 0.0], dtype=float)
        cell.move({p: cell.arms[p].tip() + a2*0.10 for p in arms}, 0.02, 1.8)
        cell.step(0.25)
    cell.move({p: cell.arms[p].tip() + [0, 0, 0.06] for p in arms}, 0.06, 1.0)
    cell.move({p: cell.arms[p].tip() + [0, 0, 0.12] for p in arms}, 0.06, 1.2)

def lift_and_lay(cell, mode, rec):
    """pick the highest point of the heap, lift the towel clear so gravity opens it, lay it down while dragging it taut"""
    cell.park(); o = cell.observe(mode)
    if o is None: return cell.coverage()
    top = o["top"]; arm = "a0" if top[0] < CX else "a1"
    if not grab_at(cell, arm, top[:2]):
        cell.park(); rec.append(dict(step="lift", ok=False, why="closed on the highest point and caught no fabric", coverage=round(cell.coverage(), 3)))
        return cell.coverage()
    cell.move({arm: np.array([CX, CY, TABLE_Z + 0.44])}, 0.03, 2.2); cell.step(0.7)
    off = 0.17 if arm == "a0" else -0.17
    cell.move({arm: np.array([CX - off, CY, TABLE_Z + 0.07])}, 0.03, 1.8)
    cell.move({arm: np.array([CX + off, CY, TABLE_Z - 0.002])}, 0.02, 1.8)
    release(cell, [arm]); cell.park()
    rec.append(dict(step="lift", ok=True, why="lifted the towel by its highest point and laid it out", coverage=round(cell.coverage(), 3)))
    return cell.coverage()

def spread(cell, mode, rec, max_drags=3, goal=0.86):
    """drag the corners of the seen outline out to a canonical square until the towel lies flat"""
    tgt = rect_corners(np.array([CX, CY]), np.array([1.0, 0]), np.array([0, 1.0]), SIDE/2, SIDE/2)
    drags = 0
    for it in range(max_drags):
        if cell.out_of_time(): break
        cell.park(); cov = cell.coverage()
        if cov >= goal: break
        o = cell.observe(mode)
        if o is None: break
        got = o["corners"]; best = None
        for k in range(4):
            r = np.roll(got, k, axis=0); c = float(np.linalg.norm(r - tgt, axis=1).sum())
            if best is None or c < best[0]: best = (c, r)
        asg = best[1]; err = np.linalg.norm(asg - tgt, axis=1); j = int(np.argmax(err))
        if err[j] < 0.025: break
        arm = "a0" if asg[j][0] < CX else "a1"
        if not grab_at(cell, arm, asg[j]):
            rec.append(dict(step=f"spread{it}", ok=False, why="pinched at a corner of the outline and caught no fabric", coverage=round(cov, 3)))
            cell.step(0.2); continue
        drags += 1
        d = tgt[j] - asg[j]; d = d/max(np.linalg.norm(d), 1e-6)
        carry(cell, {arm: np.array([tgt[j][0], tgt[j][1], TABLE_Z + 0.008])}, height=0.10, steps=30)
        release(cell, [arm], away=d)
        rec.append(dict(step=f"spread{it}", ok=True, why=f"pulled a corner {err[j]*1000:.0f} mm out to where it belongs", coverage=round(cell.coverage(), 3)))
    cell.park(); return cell.coverage(), drags

def fold_axes(o):
    """the towel folds across the axis pointing away from the arms, so each arm keeps its own side and never
       reaches across the table into the other one. f = direction of travel, g = the edge the two arms share."""
    u, v, hu, hv = o["u"], o["v"], o["hu"], o["hv"]
    f, hf, g, hg = (u, hu, v, hv) if abs(u[1]) >= abs(v[1]) else (v, hv, u, hu)
    if f[1] < 0: f = -f
    return f, hf, g, hg

def fold(cell, mode, which, rec):
    """fold in half across f: carry the two corners of one edge onto the two corners of the opposite edge.
       Which edge to take matters: taking the folded crease instead of the free edge undoes the previous fold."""
    o = cell.observe(mode)
    if o is None: rec.append(dict(step=f"fold{which}", ok=False, why="the camera saw no towel")); return False, "nothing seen"
    c = o["centre"]; f, hf, g, hg = fold_axes(o)
    sign = cell.free_side(mode, c, f, hf) if which == 2 else 1.0    # the first fold has no crease yet, either edge will do
    inset = min(0.022, hf*0.30)                                    # grab just inside the edge: on the edge half the jaw is over bare table
    src = sorted([c + g*sd*hg*0.88 + f*sign*(hf - inset) for sd in (-1, 1)], key=lambda p: p[0])
    dst = sorted([c + g*sd*hg*0.88 - f*sign*(hf - inset) for sd in (-1, 1)], key=lambda p: p[0])
    arms = ("a0", "a1")
    got = {arm: grab_at(cell, arm, src[k]) for k, arm in enumerate(arms)}
    if not all(got.values()):
        release(cell, arms); cell.park()
        rec.append(dict(step=f"fold{which}", ok=False, why="an arm closed on bare table instead of the towel edge"))
        return False, "missed the edge"
    carry(cell, {arm: np.array([dst[k][0], dst[k][1], TABLE_Z + 0.016]) for k, arm in enumerate(arms)}, height=0.13, steps=46, settle=0.8)
    release(cell, arms, away=-f*sign); cell.park(); cell.step(1.2)                                                  # let the arch collapse before measuring
    _, _, _, HU, HV = min_rect(cell.verts()[:, :2]); long_mm, short_mm = HU*2000, HV*2000
    want = SIDE*1000/2 if which == 1 else SIDE*1000/4
    ok = abs(short_mm - want) < (58 if which == 1 else 46) and cell.on_table()
    rec.append(dict(step=f"fold{which}", ok=bool(ok), coverage=round(cell.coverage(), 3),
                    why=f"towel is now {long_mm:.0f} by {short_mm:.0f} mm, wanted a short side near {want:.0f}"))
    return ok, f"{long_mm:.0f} x {short_mm:.0f} mm"

def trial(seed, mode, level="flat", live=False, snaps=False, pace=1.0):
    t0 = time.time(); cell = Cell(seed=seed + 100*LEVELS.index(level), live=live, pace=pace); cell.budget = SIM_BUDGET[level]
    if live:
        from mujoco import viewer as V
        cell.viewer = V.launch_passive(cell.m, cell.d)
        cell.viewer.cam.lookat[:] = (CX, CY, TABLE_Z); cell.viewer.cam.distance = 1.5
        cell.viewer.cam.azimuth = 138; cell.viewer.cam.elevation = -30
    rec = []; frames = []; tag = f"lau_{level}_{mode}_{seed}"
    cell.crumple(level); start_cov = cell.coverage()
    if snaps: frames.append(cell.snap(tag + "_0.png"))
    o = cell.observe(mode); truth = cell.verts()[cell.corner_ids][:, :2]
    corner_err = float("nan"); free_ok = None
    if o is not None:
        a = min(float(np.linalg.norm(np.roll(o["corners"], k, axis=0) - truth, axis=1).mean()) for k in range(4))
        b = min(float(np.linalg.norm(np.roll(o["corners"][::-1], k, axis=0) - truth, axis=1).mean()) for k in range(4))
        corner_err = min(a, b)*1000
    if level != "flat":
        for _ in range(2 if level == "heap" else 1):
            if cell.coverage() >= 0.6 or cell.out_of_time(): break
            lift_and_lay(cell, mode, rec)
        cov, drags = spread(cell, mode, rec, max_drags=3 if level == "heap" else 2)
    else:
        cov, drags = cell.coverage(), 0
    if snaps: frames.append(cell.snap(tag + "_1.png"))
    f1 = f2 = False; note = "never lay flat enough to fold"
    if cov >= 0.76 and not cell.out_of_time():
        f1, n1 = fold(cell, mode, 1, rec)
        if snaps: frames.append(cell.snap(tag + "_2.png"))
        if f1 and not cell.out_of_time():
            oo = cell.observe(mode)                       # did it work out which edge is free? compare with the truth
            if oo is not None:
                ff, hff, _, _ = fold_axes(oo)
                free_ok = bool(cell.free_side(mode, oo["centre"], ff, hff) == cell.free_side("oracle", oo["centre"], ff, hff))
            f2, n2 = fold(cell, mode, 2, rec); note = n2
            if snaps: frames.append(cell.snap(tag + "_3.png"))
        elif f1: note = "ran out of time after the first fold"
        else: note = "first fold failed: " + n1
    _, _, _, HU, HV = min_rect(cell.verts()[:, :2]); long_mm, short_mm = HU*2000, HV*2000
    ok = bool(f1 and f2 and abs(long_mm - SIDE*1000) < 80 and abs(short_mm - SIDE*1000/4) < 46 and cell.on_table())
    r = dict(seed=seed, mode=mode, level=level, passed=ok, start_coverage=round(start_cov, 3),
             corner_error_mm=round(corner_err, 1), free_edge_right=free_ok, smoothed_coverage=round(cov, 3),
             drags=drags, fold1=bool(f1), fold2=bool(f2), size_mm=[round(long_mm), round(short_mm)], note=note,
             steps=rec, frames=frames, seconds=round(time.time()-t0, 1), sim_seconds=round(cell.t, 1))
    print(f"  {level:8s} {mode:6s} seed {seed} {'PASS' if ok else 'FAIL'}  corner err {corner_err:5.1f} mm  "
          f"free edge {str(free_ok):5s}  cov {start_cov:.2f}->{cov:.2f}  {long_mm:.0f}x{short_mm:.0f}  {r['seconds']}s  {note}", flush=True)
    if live:
        print("done; the window stays open")
        while cell.viewer.is_running(): cell.step(0.05)
    return r

if __name__ == "__main__":
    if sys.argv[1:2] == ["live"]:
        trial(int(os.environ.get("SEED", "0")), sys.argv[2] if len(sys.argv) > 2 else "depth",
              sys.argv[3] if len(sys.argv) > 3 else "rumpled", live=True, pace=float(os.environ.get("PACE", "1")))
    else:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        levels = [a for a in sys.argv[3:] if a in LEVELS] or list(LEVELS)
        out = []
        for level in levels:
            for mode in ("oracle", "depth"):
                for s in range(n):
                    try: out.append(trial(s, mode, level, snaps=(s == 0)))
                    except Exception as ex:
                        traceback.print_exc(); out.append(dict(seed=s, mode=mode, level=level, passed=False, error=repr(ex)[:200], steps=[], frames=[]))
                    json.dump(out, open(os.path.join(OUT, "laundry.json"), "w"), indent=1)
        print()
        for level in levels:
            for mode in ("oracle", "depth"):
                g = [r for r in out if r["mode"] == mode and r["level"] == level]
                if g: print(f"{level:8s} {mode:6s}: {sum(r['passed'] for r in g)}/{len(g)} folded", flush=True)
