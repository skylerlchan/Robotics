"""Rev E tendril bundle in MuJoCo.

One repeated vertebra (12 mm diameter, 12 mm pitch, two hinges), three cables per tendril
routed through sites on every vertebra, tendon motors at the base, and a "jam" mode that
raises joint stiffness around the current pose to stand in for a layer-jamming sleeve.
"""
import json, math, os, sys, time
import numpy as np
import mujoco

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
N_VERT = 14          # vertebrae per tendril
PITCH = 0.012        # m
RAD = 0.006          # vertebra radius, m
CABLE_R = 0.0042     # cable radius from the axis, m
MASS = 0.0015        # kg per vertebra (PA12-GF30)
K_SOFT = 1.0         # N·m/rad per joint from a 1.4 mm nitinol backbone rod
K_JAM = 15.0         # N·m/rad with the layer-jamming sleeve under vacuum, taken as 15x the backbone
D_SOFT, D_JAM = 0.01, 0.1
T_MAX = 100.0        # N cable budget per cable, 1 mm Dyneema breaks near 1500 N


def build_model(n_tendrils=8, ring_r=0.04, objects=()):
    xml = [f"""<mujoco model="tendril_bundle">
  <option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic" impratio="5"/>
  <visual><global offwidth="1280" offheight="960"/><headlight ambient="0.45 0.45 0.45" diffuse="0.6 0.6 0.6" specular="0.1 0.1 0.1"/><quality shadowsize="4096"/><map znear="0.005"/></visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.86 0.88 0.9" rgb2="0.8 0.82 0.85" width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="12 12" reflectance="0.05"/>
  </asset>
  <default>
    <geom condim="4" friction="0.9 0.02 0.001" solref="0.004 1" solimp="0.92 0.97 0.001"/>
    <joint type="hinge" limited="true" range="-38 38" damping="{D_SOFT}" stiffness="{K_SOFT}" armature="1e-6"/>
    <tendon width="0.0005" rgba="0.85 0.57 0.16 1"/>
    <site size="0.0005" rgba="0 0 0 0"/>
    <position kp="60000" kv="120" ctrllimited="true" ctrlrange="0 0.4" forcelimited="true" forcerange="-{T_MAX} 0"/>
  </default>
  <worldbody>
    <light pos="0.3 0.4 0.8" dir="-0.3 -0.4 -0.8" castshadow="true"/>
    <light pos="-0.4 0.2 0.6" dir="0.4 -0.2 -0.6" castshadow="false" diffuse="0.35 0.35 0.35"/>
    <geom name="floor" type="plane" size="1 1 0.01" material="grid"/>
    <body name="base" pos="0 0 0.005">
      <geom type="cylinder" size="0.062 0.005" rgba="0.2 0.22 0.26 1"/>
      <geom type="cylinder" size="0.058 0.0002" pos="0 0 0.005" rgba="0.12 0.62 0.58 1" contype="0" conaffinity="0"/>
"""]
    for t in range(n_tendrils):
        a = 2*math.pi*t/n_tendrils
        x, y = ring_r*math.cos(a), ring_r*math.sin(a)
        for c in range(3):
            ca = 2*math.pi*c/3
            xml.append(f'      <site name="t{t}_b_c{c}" pos="{x + CABLE_R*math.cos(ca):.5f} {y + CABLE_R*math.sin(ca):.5f} 0.005"/>\n')
    xml.append("    </body>\n")
    for t in range(n_tendrils):
        a = 2*math.pi*t/n_tendrils
        x, y = ring_r*math.cos(a), ring_r*math.sin(a)
        hue = [(0.12,0.62,0.58),(0.85,0.57,0.16),(0.24,0.44,0.88),(0.7,0.23,0.18),(0.48,0.35,0.78),(0.24,0.75,0.36),(0.79,0.64,0.15),(0.9,0.28,0.3)][t % 8]
        rgba = f"{hue[0]} {hue[1]} {hue[2]} 1"
        indent = "    "
        xml.append(f'{indent}<body name="t{t}_v0" pos="{x:.5f} {y:.5f} 0.010">\n')
        for v in range(N_VERT):
            ind = indent + "  "*(v+1)
            if v > 0:
                xml.append(f'{ind}<body name="t{t}_v{v}" pos="0 0 {PITCH}">\n')
            xml.append(f'{ind}  <joint name="t{t}_v{v}_x" axis="1 0 0"/>\n{ind}  <joint name="t{t}_v{v}_y" axis="0 1 0"/>\n')
            xml.append(f'{ind}  <geom name="t{t}_g{v}" type="capsule" size="{RAD} {PITCH/2 - RAD*0.55:.5f}" pos="0 0 {PITCH/2:.4f}" mass="{MASS}" rgba="{rgba}"/>\n')
            for c in range(3):
                ca = 2*math.pi*c/3
                xml.append(f'{ind}  <site name="t{t}_v{v}_c{c}" pos="{CABLE_R*math.cos(ca):.5f} {CABLE_R*math.sin(ca):.5f} {PITCH/2:.4f}"/>\n')
            if v == N_VERT - 1:
                xml.append(f'{ind}  <site name="t{t}_tip" pos="0 0 {PITCH:.4f}" size="0.002" rgba="0.1 0.1 0.1 1"/>\n')
        for v in range(N_VERT - 1, -1, -1):
            xml.append(indent + "  "*(v+1) + "</body>\n")
    for o in objects:
        xml.append(o)
    xml.append("  </worldbody>\n  <tendon>\n")
    for t in range(n_tendrils):
        for c in range(3):
            sites = "".join(f'<site site="t{t}_v{v}_c{c}"/>' for v in range(N_VERT))
            xml.append(f'    <spatial name="t{t}_c{c}"><site site="t{t}_b_c{c}"/>{sites}</spatial>\n')
    xml.append("  </tendon>\n  <actuator>\n")
    for t in range(n_tendrils):
        for c in range(3):
            xml.append(f'    <position name="t{t}_c{c}" tendon="t{t}_c{c}"/>\n')
    xml.append("  </actuator>\n</mujoco>\n")
    return "".join(xml)


# ---------- objects ----------
def post(x, y, r=0.015, h=0.05):
    return f'    <body name="post" pos="{x} {y} {h}"><geom type="cylinder" size="{r} {h}" rgba="0.62 0.65 0.7 1"/></body>\n'
def ball(x, y, r=0.025, m=0.05):
    return f'    <body name="ball" pos="{x} {y} {0.01 + r + 0.001}"><freejoint/><geom type="sphere" size="{r}" mass="{m}" rgba="0.9 0.86 0.78 1"/></body>\n'
def cube(x, y, s=0.01, m=0.012):
    return f'    <body name="cube" pos="{x} {y} {0.01 + s + 0.001}"><freejoint/><geom type="box" size="{s} {s} {s}" mass="{m}" rgba="0.85 0.57 0.16 1"/></body>\n'
def bottle(x, y, r=0.02, L=0.11, m=0.15):
    return f'    <body name="bottle" pos="{x} {y} {r + 0.0005}"><freejoint/><geom type="cylinder" size="{r} {L/2}" euler="0 90 0" mass="{m}" rgba="0.7 0.23 0.18 1"/></body>\n'


class Sim:
    def __init__(self, n_tendrils=8, ring_r=0.04, objects=()):
        self.n = n_tendrils
        self.model = mujoco.MjModel.from_xml_string(build_model(n_tendrils, ring_r, objects))
        self.data = mujoco.MjData(self.model)
        self.jids = {t: [mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, f"t{t}_v{v}_{ax}") for v in range(N_VERT) for ax in "xy"] for t in range(n_tendrils)}
        self.tips = {t: mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, f"t{t}_tip") for t in range(n_tendrils)}
        self.renderer = None
        self.jammed = set()
        mujoco.mj_forward(self.model, self.data)
        self.L0 = self.data.ten_length.copy()
        self.data.ctrl[:] = self.L0

    # cable length targets for a constant-curvature bend: total angle theta (rad) toward direction phi (base frame)
    def bend(self, t, phi, theta, slack=0.0):
        for c in range(3):
            ca = 2*math.pi*c/3
            self.data.ctrl[3*t + c] = self.L0[3*t + c] - CABLE_R*theta*math.cos(phi - ca) + slack

    def slack(self, t, amount=0.02):
        for c in range(3): self.data.ctrl[3*t + c] = self.L0[3*t + c] + amount

    def jam(self, t, on=True):
        # the sleeve adds K_JAM about the pose at the moment of jamming; the backbone keeps pulling toward straight.
        # one joint spring in MuJoCo, so use the combined stiffness with the reference that gives the same net moment
        m = self.model
        for j in self.jids[t]:
            qa = m.jnt_qposadr[j]; da = m.jnt_dofadr[j]
            if on:
                m.jnt_stiffness[j] = K_SOFT + K_JAM; m.qpos_spring[qa] = K_JAM*self.data.qpos[qa]/(K_SOFT + K_JAM); m.dof_damping[da] = D_JAM
            else:
                m.jnt_stiffness[j] = K_SOFT; m.qpos_spring[qa] = 0.0; m.dof_damping[da] = D_SOFT
        (self.jammed.add if on else self.jammed.discard)(t)

    def tip(self, t):
        return self.data.site_xpos[self.tips[t]].copy()

    def step(self, seconds):
        n = int(seconds / self.model.opt.timestep)
        for _ in range(n): mujoco.mj_step(self.model, self.data)

    def body_pos(self, name):
        return self.data.xpos[mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, name)].copy()

    def render(self, path, cam=None, w=720, h=520):
        if self.renderer is None: self.renderer = mujoco.Renderer(self.model, height=h, width=w)
        c = mujoco.MjvCamera(); c.type = mujoco.mjtCamera.mjCAMERA_FREE
        c.lookat[:] = (cam or {}).get("lookat", (0.0, 0.0, 0.09)); c.distance = (cam or {}).get("distance", 0.42)
        c.azimuth = (cam or {}).get("azimuth", 135); c.elevation = (cam or {}).get("elevation", -22)
        self.renderer.update_scene(self.data, camera=c)
        img = self.renderer.render()
        from PIL import Image
        Image.fromarray(img).save(path)
        return path


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        s = Sim(n_tendrils=8)
        print("bodies", s.model.nbody, "dofs", s.model.nv, "tendons", s.model.ntendon, "actuators", s.model.nu)
        t0 = time.time(); s.step(0.5); print(f"settle 0.5 s sim in {time.time()-t0:.2f} s; tip0 {s.tip(0).round(4)}")
        s.bend(0, 0.0, math.radians(120)); s.step(1.5); p = s.tip(0); print("120 deg arc toward +x: tip0", p.round(4), "tensions", (-s.data.actuator_force[0:3]).round(1))
        s.jam(0); s.slack(0); s.step(1.5); print("jammed then cables slack: tip0", s.tip(0).round(4))
        s.jam(0, False); s.step(1.5); print("unjammed, still slack: tip0", s.tip(0).round(4))
        os.makedirs(OUT, exist_ok=True); print(s.render(os.path.join(OUT, "smoke.png")))
