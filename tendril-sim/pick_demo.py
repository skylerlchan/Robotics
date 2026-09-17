"""Full-scale 24-tendril bundle on a UR5e: pick a bottle, carry it, place it. Scripted, measured, rendered to video."""
import json, math, os, subprocess, time
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); UR = os.path.join(HERE, "third_party", "mujoco_menagerie", "universal_robots_ur5e"); OUT = os.path.join(HERE, "out")
RINGS = [(6, 0.030, 0.0), (8, 0.058, math.pi/8), (10, 0.084, 0.0)]
N_V, PITCH, RAD, CR, MASS, T_MAX = 18, 0.0122, 0.006, 0.0042, 0.0015, 100.0
K_SOFT, K_JAM, D_SOFT, D_JAM = 1.0, 15.0, 0.01, 0.1
SKIN, TIP = "0.93 0.90 0.85 1", "0.55 0.52 0.50 1"
roots = [(r*math.cos(ph + 2*math.pi*k/n), r*math.sin(ph + 2*math.pi*k/n)) for n, r, ph in RINGS for k in range(n)]
N_T = len(roots)

def bundle_body():
    x = ['<body name="bundle" pos="0 0.1 0" quat="-1 1 0 0" childclass="tendril">',
         '  <site name="tool" pos="0 0 0" size="0.003" rgba="0 0 0 0"/>',
         '  <geom name="disc" type="cylinder" size="0.10 0.015" pos="0 0 0.015" rgba="0.82 0.80 0.77 1" mass="0.9"/>',
         '  <geom type="cylinder" size="0.099 0.002" pos="0 0 0.031" rgba="0.12 0.62 0.58 1" contype="0" conaffinity="0" mass="0.001"/>']
    for t, (rx, ry) in enumerate(roots):
        for c in range(3):
            ca = 2*math.pi*c/3; x.append(f'  <site name="t{t}_b_c{c}" pos="{rx + CR*math.cos(ca):.5f} {ry + CR*math.sin(ca):.5f} 0.03"/>')
    for t, (rx, ry) in enumerate(roots):
        x.append(f'  <body name="t{t}_v0" pos="{rx:.5f} {ry:.5f} 0.033">')
        for v in range(N_V):
            ind = "  " + "  "*(v+1)
            if v > 0: x.append(f'{ind}<body name="t{t}_v{v}" pos="0 0 {PITCH}">')
            x.append(f'{ind}  <joint name="t{t}_v{v}_x" axis="1 0 0"/>'); x.append(f'{ind}  <joint name="t{t}_v{v}_y" axis="0 1 0"/>')
            x.append(f'{ind}  <geom name="t{t}_g{v}" type="capsule" size="{RAD} {PITCH/2 - RAD*0.35:.5f}" pos="0 0 {PITCH/2:.4f}" mass="{MASS}" rgba="{TIP if v == N_V-1 else SKIN}"/>')
            for c in range(3):
                ca = 2*math.pi*c/3; x.append(f'{ind}  <site name="t{t}_v{v}_c{c}" pos="{CR*math.cos(ca):.5f} {CR*math.sin(ca):.5f} {PITCH/2:.4f}"/>')
            if v == N_V-1: x.append(f'{ind}  <site name="t{t}_tip" pos="0 0 {PITCH:.4f}"/>')
        for v in range(N_V-1, -1, -1): x.append("  " + "  "*(v+1) + "</body>")
    x.append("</body>"); return "\n".join(x)

DEFAULT_WORLD = '''
    <body name="bottle" pos="0.55 0 0.0605"><freejoint/><geom type="cylinder" size="0.02 0.06" mass="0.15" rgba="0.24 0.44 0.88 1" contype="3" conaffinity="3" friction="0.9 0.02 0.001"/></body>
    <geom name="target" type="cylinder" size="0.05 0.001" pos="0.55 -0.30 0.001" rgba="0.85 0.57 0.16 0.8" contype="0" conaffinity="0"/>'''
def build(world_extra=None, scene_name="pick_scene.xml"):
    xml = open(os.path.join(UR, "ur5e.xml")).read()
    defaults = f'''    <default class="tendril">
      <joint type="hinge" limited="true" range="-0.663 0.663" damping="{D_SOFT}" stiffness="{K_SOFT}" armature="1e-6"/>
      <geom condim="4" contype="1" conaffinity="2" friction="0.9 0.02 0.001" solref="0.004 1" solimp="0.92 0.97 0.001"/>
      <site size="0.0005" rgba="0 0 0 0"/>
      <tendon width="0.0005" rgba="0.85 0.57 0.16 0"/>
      <position kp="30000" kv="100" ctrllimited="true" ctrlrange="0 0.5" forcelimited="true" forcerange="-{T_MAX} 0"/>
    </default>
  </default>'''
    xml = xml.replace("  </default>\n\n  <asset>", defaults + "\n\n  <asset>", 1)
    assert 'class="tendril"' in xml, "default insertion failed"
    xml = xml.replace('<site name="attachment_site" pos="0 0.1 0" quat="-1 1 0 0"/>', '<site name="attachment_site" pos="0 0.1 0" quat="-1 1 0 0"/>\n' + bundle_body(), 1)
    world = '''
    <light pos="0.5 -0.6 1.6" dir="-0.2 0.3 -0.9" castshadow="true"/>
    <light pos="-0.5 0.8 1.2" dir="0.4 -0.6 -0.7" castshadow="false" diffuse="0.35 0.35 0.35"/>
    <geom name="floor" type="plane" size="2 2 0.01" material="grid" contype="3" conaffinity="3" friction="0.9 0.02 0.001"/>''' + (DEFAULT_WORLD if world_extra is None else world_extra)
    xml = xml.replace("<worldbody>", "<worldbody>" + world, 1)
    xml = xml.replace("<asset>", '<asset>\n    <texture name="grid" type="2d" builtin="checker" rgb1="0.88 0.89 0.91" rgb2="0.82 0.84 0.87" width="512" height="512"/>\n    <material name="grid" texture="grid" texrepeat="8 8" reflectance="0.05"/>', 1)
    tend = "  <tendon>\n" + "".join(f'    <spatial name="t{t}_c{c}" class="tendril"><site site="t{t}_b_c{c}"/>' + "".join(f'<site site="t{t}_v{v}_c{c}"/>' for v in range(N_V)) + "</spatial>\n" for t in range(N_T) for c in range(3)) + "  </tendon>\n"
    acts = "".join(f'    <position name="t{t}_c{c}" class="tendril" tendon="t{t}_c{c}"/>\n' for t in range(N_T) for c in range(3))
    xml = xml.replace("  <actuator>", tend + "  <actuator>", 1).replace("  </actuator>", acts + "  </actuator>", 1)
    xml = xml[:xml.index("  <keyframe>")] + "</mujoco>\n"
    xml = xml.replace('<option integrator="implicitfast"/>', '<option timestep="0.0005" integrator="implicitfast" cone="elliptic" impratio="5"/>')
    xml = xml.replace("<visual>", '<visual>\n    <global offwidth="1280" offheight="960"/>', 1) if "<visual>" in xml else xml.replace("<asset>", '<visual><global offwidth="1280" offheight="960"/><quality shadowsize="4096"/><map znear="0.01"/></visual>\n  <asset>', 1)
    path = os.path.join(UR, scene_name); open(path, "w").write(xml); return path

class Demo:
    def __init__(self, world_extra=None, obj="bottle", scene_name="pick_scene.xml", size=(800, 540)):
        self.size = size; self.m = mujoco.MjModel.from_xml_path(build(world_extra, scene_name)); self.d = mujoco.MjData(self.m)
        J, A = mujoco.mjtObj.mjOBJ_JOINT, mujoco.mjtObj.mjOBJ_ACTUATOR
        jn = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
        self.qadr = np.array([self.m.jnt_qposadr[mujoco.mj_name2id(self.m, J, n)] for n in jn]); self.dadr = np.array([self.m.jnt_dofadr[mujoco.mj_name2id(self.m, J, n)] for n in jn])
        self.aid = np.array([mujoco.mj_name2id(self.m, A, n) for n in ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"]])
        self.a0 = mujoco.mj_name2id(self.m, A, "t0_c0")
        self.arm_q = np.array([-1.5708, -1.5708, 1.5708, -1.5708, -1.5708, 0.0]); self.d.qpos[self.qadr] = self.arm_q; self.d.ctrl[self.aid] = self.arm_q
        mujoco.mj_forward(self.m, self.d)
        self.L0 = self.d.ten_length.copy(); self.d.ctrl[self.a0:self.a0 + 3*N_T] = self.L0
        self.tool = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, "tool"); self.bottle = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, obj)
        self.jids = {t: [mujoco.mj_name2id(self.m, J, f"t{t}_v{v}_{ax}") for v in range(N_V) for ax in "xy"] for t in range(N_T)}
        self.q_des = np.array([0.0, 1.0, 0.0, 0.0]); self.frames = []; self.renderer = None; self.log = []
    def bend(self, t, phi, theta):
        for c in range(3): self.d.ctrl[self.a0 + 3*t + c] = self.L0[3*t + c] - CR*theta*math.cos(phi - 2*math.pi*c/3)
    def jam(self, t, on=True):
        for j in self.jids[t]:
            qa = self.m.jnt_qposadr[j]; da = self.m.jnt_dofadr[j]
            if on: self.m.jnt_stiffness[j] = K_SOFT + K_JAM; self.m.qpos_spring[qa] = K_JAM*self.d.qpos[qa]/(K_SOFT + K_JAM); self.m.dof_damping[da] = D_JAM
            else: self.m.jnt_stiffness[j] = K_SOFT; self.m.qpos_spring[qa] = 0.0; self.m.dof_damping[da] = D_SOFT
    def ik_step(self, p_des):
        jacp = np.zeros((3, self.m.nv)); jacr = np.zeros((3, self.m.nv)); mujoco.mj_jacSite(self.m, self.d, jacp, jacr, self.tool)
        J = np.vstack([jacp[:, self.dadr], jacr[:, self.dadr]])
        e_p = p_des - self.d.site_xpos[self.tool]; q_cur = np.zeros(4); mujoco.mju_mat2Quat(q_cur, self.d.site_xmat[self.tool]); e_r = np.zeros(3); mujoco.mju_subQuat(e_r, self.q_des, q_cur); e_r = self.d.site_xmat[self.tool].reshape(3, 3) @ e_r   # local to world
        v = np.concatenate([np.clip(e_p*4.0, -0.25, 0.25), np.clip(e_r*3.0, -0.8, 0.8)])
        dq = J.T @ np.linalg.solve(J @ J.T + 0.01*np.eye(6), v)
        self.arm_q += np.clip(dq*0.01, -0.012, 0.012); self.d.ctrl[self.aid] = self.arm_q
    def contacts(self):
        n = set(); f = 0.0
        for i in range(self.d.ncon):
            c = self.d.contact[i]; b1, b2 = self.m.geom_bodyid[c.geom1], self.m.geom_bodyid[c.geom2]
            if self.bottle in (b1, b2):
                other = c.geom2 if b1 == self.bottle else c.geom1; name = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_GEOM, other) or ""
                if name.startswith("t"): fr = np.zeros(6); mujoco.mj_contactForce(self.m, self.d, i, fr); n.add(name.split("_")[0]); f += abs(fr[0])
        return len(n), f
    def run(self, seconds, p_des, fps=30, tag=None):
        steps = int(seconds/self.m.opt.timestep); per_ctrl = int(0.01/self.m.opt.timestep); per_frame = int(1/fps/self.m.opt.timestep)
        for k in range(steps):
            if k % per_ctrl == 0: self.ik_step(p_des)
            mujoco.mj_step(self.m, self.d)
            if k % per_frame == 0: self.frames.append(self.render())
    def move_until(self, p_des, tol, max_s):
        t = 0.0
        while t < max_s:
            self.run(0.1, p_des); t += 0.1
            if np.linalg.norm(p_des - self.d.site_xpos[self.tool]) < tol and abs(self.d.site_xmat[self.tool].reshape(3,3)[2,2] + 1) < 0.01: break
        self.run(0.3, p_des)
    def render(self):
        if self.renderer is None: self.renderer = mujoco.Renderer(self.m, height=self.size[1], width=self.size[0])
        c = mujoco.MjvCamera(); c.type = mujoco.mjtCamera.mjCAMERA_FREE; c.lookat[:] = (0.45, -0.12, 0.18); c.distance = 1.25; c.azimuth = 250; c.elevation = -20
        self.renderer.update_scene(self.d, camera=c); return self.renderer.render().copy()
    def snap(self, name):
        from PIL import Image; Image.fromarray(self.frames[-1]).save(os.path.join(OUT, name))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); t0 = time.time(); D = Demo(); print("model: bodies", D.m.nbody, "dofs", D.m.nv, "actuators", D.m.nu)
    metrics = {}
    home = D.d.site_xpos[D.tool].copy(); above = np.array([0.55, 0.0, 0.42]); grasp = np.array([0.55, 0.0, 0.29])
    D.move_until(above, 0.01, 9.0); D.snap("pick_0_approach.png")                                   # arm brings the open bundle over the bottle
    D.move_until(grasp, 0.006, 5.0); D.snap("pick_1_descend.png")
    ring_of = [i for n, r, ph in RINGS for i in [RINGS.index((n, r, ph))]*n]
    th = 0.0
    for k in range(60):                                                                # close all rings until the bottle feels 8 N
        th += 1.2
        for t, (rx, ry) in enumerate(roots): D.bend(t, math.atan2(ry, rx) + math.pi, math.radians(th*(0.35 if ring_of[t] == 0 else 1.0)))
        D.run(0.05, grasp); n, f = D.contacts()
        if n >= 10 and f > 8.0: break
    D.run(0.5, grasp); n, f = D.contacts(); metrics["tendrils_in_contact"] = n; metrics["grasp_normal_force_N"] = round(f, 2); metrics["close_angle_deg"] = th
    for t in range(N_T): D.jam(t)
    D.snap("pick_2_grasp.png"); z0 = D.d.xpos[D.bottle][2]; rel0 = D.d.xpos[D.bottle] - D.d.site_xpos[D.tool]
    for k in range(30): D.run(0.1, grasp + np.array([0, 0, 0.18*(k+1)/30]))          # lift
    D.snap("pick_3_lift.png"); metrics["bottle_lift_mm"] = round((D.d.xpos[D.bottle][2] - z0)*1000, 1)
    for k in range(40): D.run(0.1, np.array([0.55, -0.30*(k+1)/40, 0.47]))            # carry
    rel1 = D.d.xpos[D.bottle] - D.d.site_xpos[D.tool]; metrics["slip_during_carry_mm"] = round(float(np.linalg.norm(rel1 - rel0))*1000, 1); D.snap("pick_4_carry.png")
    for k in range(25): D.run(0.1, np.array([0.55, -0.30, 0.47 - 0.18*(k+1)/25]))     # lower
    for t in range(N_T): D.jam(t, False); D.bend(t, 0.0, 0.0)                          # release
    D.run(1.2, np.array([0.55, -0.30, 0.29])); D.snap("pick_5_release.png")
    for k in range(20): D.run(0.1, np.array([0.55, -0.30, 0.29 + 0.15*(k+1)/20]))     # retreat
    D.run(0.5, np.array([0.55, -0.30, 0.44])); D.snap("pick_6_done.png")
    p = D.d.xpos[D.bottle]; metrics["place_error_mm"] = round(float(np.hypot(p[0]-0.55, p[1]+0.30))*1000, 1); metrics["bottle_upright"] = bool(D.d.xmat[D.bottle].reshape(3,3)[2,2] > 0.9)
    metrics["sim_seconds"] = round(D.d.time, 1); metrics["wall_seconds"] = round(time.time()-t0, 1); metrics["frames"] = len(D.frames)
    h, w = D.frames[0].shape[:2]; vid = os.path.join(OUT, "pick.mp4")
    ff = subprocess.Popen(["/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "30", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-movflags", "+faststart", vid], stdin=subprocess.PIPE)
    for fr in D.frames: ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait(); metrics["video_kb"] = os.path.getsize(vid)//1024
    json.dump(metrics, open(os.path.join(OUT, "pick_metrics.json"), "w"), indent=1); print(json.dumps(metrics, indent=1))
