"""Prototype lineup: different end effectors on identical UR5e arms, same task, same viewer.

Hands: 2f85 (Robotiq two-finger), suction (cup), leap (16-joint low-cost hand), allegro (16-joint), shadow (24-joint),
fist6 (six thick bead-and-rod fingers), bundle24 (the tendril bundle). Menagerie models are attached with MjSpec; the
custom ones are generated as standalone MJCF files in hands/.
"""
import math, os, numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); MEN = os.path.join(HERE, "third_party", "mujoco_menagerie"); UR = os.path.join(MEN, "universal_robots_ur5e")
HANDS_DIR = os.path.join(HERE, "hands")
SKIN, TIPC = "0.93 0.90 0.85 1", "0.55 0.52 0.50 1"

def tendril_hand_xml(name, rings, n_v, pitch, rad, cr, k_soft, t_max, mass, palm_r):
    """standalone MJCF: a palm disc with bead-and-rod fingers along +z, three cables each, position servos"""
    roots = [(r*math.cos(ph + 2*math.pi*k/n), r*math.sin(ph + 2*math.pi*k/n)) for n, r, ph in rings for k in range(n)]
    x = [f'<mujoco model="{name}"><compiler angle="radian" autolimits="true"/>',
         f'<default><default class="tendril"><joint type="hinge" limited="true" range="-0.663 0.663" damping="0.01" stiffness="{k_soft}" armature="1e-6"/>',
         '<geom condim="4" contype="1" conaffinity="2" friction="0.9 0.02 0.001" solref="0.004 1" solimp="0.92 0.97 0.001"/><site size="0.0005" rgba="0 0 0 0"/>',
         f'<tendon width="0.0005" rgba="0.85 0.57 0.16 0"/><position kp="60000" kv="120" ctrllimited="true" ctrlrange="0 0.5" forcelimited="true" forcerange="-{t_max} 0"/></default></default>',
         '<worldbody><body name="mount" childclass="tendril">',
         f'<geom name="disc" type="cylinder" size="{palm_r} 0.015" pos="0 0 0.015" rgba="0.82 0.80 0.77 1" mass="0.6"/>',
         f'<geom type="cylinder" size="{palm_r-0.002} 0.002" pos="0 0 0.031" rgba="0.12 0.62 0.58 1" contype="0" conaffinity="0" mass="0.001"/>']
    for t, (rx, ry) in enumerate(roots):
        for c in range(3):
            ca = 2*math.pi*c/3; x.append(f'<site name="t{t}_b_c{c}" pos="{rx + cr*math.cos(ca):.5f} {ry + cr*math.sin(ca):.5f} 0.03"/>')
    for t, (rx, ry) in enumerate(roots):
        x.append(f'<body name="t{t}_v0" pos="{rx:.5f} {ry:.5f} 0.033">')
        for v in range(n_v):
            if v > 0: x.append(f'<body name="t{t}_v{v}" pos="0 0 {pitch}">')
            x.append(f'<joint name="t{t}_v{v}_x" axis="1 0 0"/><joint name="t{t}_v{v}_y" axis="0 1 0"/>')
            x.append(f'<geom name="t{t}_g{v}" type="capsule" size="{rad} {pitch/2 - rad*0.35:.5f}" pos="0 0 {pitch/2:.4f}" mass="{mass}" rgba="{TIPC if v == n_v-1 else SKIN}"/>')
            for c in range(3):
                ca = 2*math.pi*c/3; x.append(f'<site name="t{t}_v{v}_c{c}" pos="{cr*math.cos(ca):.5f} {cr*math.sin(ca):.5f} {pitch/2:.4f}"/>')
        x.append("</body>"*n_v)
    x.append("</body></worldbody><tendon>")
    for t in range(len(roots)):
        for c in range(3): x.append(f'<spatial name="t{t}_c{c}" class="tendril"><site site="t{t}_b_c{c}"/>' + "".join(f'<site site="t{t}_v{v}_c{c}"/>' for v in range(n_v)) + "</spatial>")
    x.append("</tendon><actuator>" + "".join(f'<position name="t{t}_c{c}" class="tendril" tendon="t{t}_c{c}"/>' for t in range(len(roots)) for c in range(3)) + "</actuator></mujoco>")
    return "\n".join(x), roots

def suction_xml():
    return '''<mujoco model="suction"><compiler angle="radian"/><worldbody><body name="mount">
<geom type="cylinder" size="0.03 0.02" pos="0 0 0.02" rgba="0.36 0.37 0.40 1" mass="0.3"/>
<geom type="cylinder" size="0.012 0.05" pos="0 0 0.09" rgba="0.55 0.52 0.50 1" mass="0.1"/>
<geom name="cup" type="cylinder" size="0.022 0.008" pos="0 0 0.148" rgba="0.12 0.62 0.58 1" mass="0.02" condim="4" friction="1.2 0.02 0.001"/>
<site name="cup_site" pos="0 0 0.156" size="0.003" rgba="0 0 0 0"/></body></worldbody></mujoco>'''

# registry: file, prefix, quaternion that turns the hand so it points along the tool axis (+z of the attachment site)
HANDS = {
  "2f85":     dict(file=os.path.join(MEN, "robotiq_2f85", "2f85.xml"), quat=(1, 0, 0, 0), label="Robotiq 2F-85 two-finger gripper", parts="1 motor, 2 fingers", cost="$5k"),
  "suction":  dict(file=os.path.join(HANDS_DIR, "suction.xml"), quat=(1, 0, 0, 0), label="Suction cup", parts="1 pump, 1 cup", cost="$300"),
  "leap":     dict(file=os.path.join(MEN, "leap_hand", "right_hand.xml"), quat=(1, 0, 0, 0), label="LEAP hand, 16 joints", parts="16 servos, printed", cost="$2k"),
  "allegro":  dict(file=os.path.join(MEN, "wonik_allegro", "right_hand.xml"), quat=(1, 0, 0, 0), label="Allegro hand, 16 joints", parts="16 motors", cost="$15k"),
  "shadow":   dict(file=os.path.join(MEN, "shadow_hand", "right_hand.xml"), quat=(1, 0, 0, 0), label="Shadow hand, 24 joints", parts="20 motors, 40 tendons", cost="$100k+"),
  "bloom":    dict(file=os.path.join(HANDS_DIR, "bloom.xml"), quat=(1, 0, 0, 0), label="Bloom: a closed orb that opens into six petals", parts="6 petals, 12 motors, 1 core", cost="$4k est."),
  "fist6":    dict(file=os.path.join(HANDS_DIR, "fist6.xml"), quat=(1, 0, 0, 0), label="Fist: six 20 mm bead-and-rod fingers", parts="48 beads, 6 rods, 18 cables", cost="$3k est."),
  "bundle24": dict(file=os.path.join(HANDS_DIR, "bundle24.xml"), quat=(1, 0, 0, 0), label="Tendril bundle, 24 fingers", parts="432 beads, 24 rods, 72 cables", cost="$8k est."),
}
def write_custom_hands():
    os.makedirs(HANDS_DIR, exist_ok=True)
    import bloom; bloom.build()
    open(os.path.join(HANDS_DIR, "suction.xml"), "w").write(suction_xml())
    x, _ = tendril_hand_xml("fist6", [(6, 0.045, 0.0)], n_v=8, pitch=0.015, rad=0.010, cr=0.007, k_soft=4.0, t_max=200.0, mass=0.006, palm_r=0.07); open(os.path.join(HANDS_DIR, "fist6.xml"), "w").write(x)
    x, _ = tendril_hand_xml("bundle24", [(6, 0.030, 0.0), (8, 0.058, math.pi/8), (10, 0.084, 0.0)], n_v=18, pitch=0.0122, rad=0.006, cr=0.0042, k_soft=1.0, t_max=100.0, mass=0.0015, palm_r=0.10); open(os.path.join(HANDS_DIR, "bundle24.xml"), "w").write(x)

WORLD_HEAD = '''<light pos="0.5 -0.6 1.6" dir="-0.2 0.3 -0.9" castshadow="true"/><light pos="-0.5 0.8 1.2" dir="0.4 -0.6 -0.7" castshadow="false" diffuse="0.35 0.35 0.35"/>
<geom name="floor" type="plane" size="4 4 0.01" material="grid" contype="3" conaffinity="3" friction="0.9 0.02 0.001"/>'''
def arm_spec_with_world(world_bodies, timestep=0.0005):
    """the UR5e file with a floor, lights and objects inserted as text, then loaded as a spec"""
    xml = open(os.path.join(UR, "ur5e.xml")).read()
    xml = xml.replace("<asset>", '<asset><texture name="grid" type="2d" builtin="checker" rgb1="0.88 0.89 0.91" rgb2="0.82 0.84 0.87" width="512" height="512"/><material name="grid" texture="grid" texrepeat="8 8" reflectance="0.05"/>', 1)
    xml = xml.replace("<worldbody>", "<worldbody>" + WORLD_HEAD + world_bodies, 1)
    xml = xml[:xml.index("  <keyframe>")] + "</mujoco>\n"
    xml = xml.replace('<option integrator="implicitfast"/>', f'<option timestep="{timestep}" integrator="implicitfast" cone="elliptic" impratio="5"/>')
    if "<visual>" not in xml: xml = xml.replace("<asset>", '<visual><global offwidth="1600" offheight="1000"/><quality shadowsize="4096"/><map znear="0.01"/></visual>\n  <asset>', 1)
    path = os.path.join(UR, f"_lineup_base_{os.getpid()}.xml"); open(path, "w").write(xml); spec = mujoco.MjSpec.from_file(path); os.remove(path); return spec

def hand_spec(hand):
    """load a hand file, zero any pose its root body carries, and return (spec, root_body)"""
    h = mujoco.MjSpec.from_file(HANDS[hand]["file"]); root = h.worldbody.bodies[0]
    root.pos = [0, 0, 0]; root.quat = [1, 0, 0, 0]; return h, root

def finger_direction(hand):
    """mount the hand on a bare arm, measure the direction from the attachment site to the farthest hand geoms, in the site frame"""
    arm = mujoco.MjSpec.from_file(os.path.join(UR, "ur5e.xml")); h, _ = hand_spec(hand); arm.attach(h, prefix=hand + "/", site=arm.site("attachment_site"))
    m = arm.compile(); d = mujoco.MjData(m); mujoco.mj_forward(m, d)
    s = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "attachment_site"); sp = d.site_xpos[s]; R = d.site_xmat[s].reshape(3, 3)
    pts = [R.T @ (d.geom_xpos[g] - sp) for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]) or "").startswith(hand + "/")]
    pts = np.array(pts); dist = np.linalg.norm(pts, axis=1); far = pts[dist >= 0.6*dist.max()]
    f = far.mean(axis=0); return f/np.linalg.norm(f), float(dist.max())

def mount_quat(hand):
    """quaternion that rotates the hand so its finger direction lies along the tool axis (+z of the site)"""
    f, length = finger_direction(hand)
    q = np.zeros(4); mujoco.mju_quatZ2Vec(q, f)            # rotates +z onto f
    qc = np.array([q[0], -q[1], -q[2], -q[3]])              # inverse: rotates f onto +z
    return qc, length

def attach_hand(arm, hand, prefix):
    """attach with the mounting rotation applied through a frame at the attachment site"""
    h, _ = hand_spec(hand); qfix, length = mount_quat(hand)
    site = arm.site("attachment_site"); wrist = arm.body("wrist_3_link")
    qs = np.array(site.quat, dtype=float); qs /= np.linalg.norm(qs); q = np.zeros(4); mujoco.mju_mulQuat(q, qs, qfix)
    fr = wrist.add_frame(pos=list(site.pos), quat=list(q)); arm.attach(h, prefix=prefix, frame=fr); return length

def curl_direction(hand, close_fn):
    """mount the hand alone, apply the closing command for 0.6 s, and return the direction the fingertips moved, in the site frame"""
    arm = mujoco.MjSpec.from_file(os.path.join(UR, "ur5e.xml")); attach_hand(arm, hand, hand + "/"); m = arm.compile(); d = mujoco.MjData(m)
    d.qpos[:6] = 0; mujoco.mj_forward(m, d)
    s = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "attachment_site"); R = d.site_xmat[s].reshape(3, 3); sp = d.site_xpos[s].copy()
    gs = [g for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]) or "").startswith(hand + "/")]
    pts = np.array([R.T @ (d.geom_xpos[g] - sp) for g in gs]); dist = np.linalg.norm(pts, axis=1); tips = [g for g, dd in zip(gs, dist) if dd >= 0.6*dist.max()]
    before = np.mean([R.T @ (d.geom_xpos[g] - sp) for g in tips], axis=0)
    close_fn(m, d, hand + "/")
    for _ in range(int(0.6/m.opt.timestep)): mujoco.mj_step(m, d)
    R = d.site_xmat[s].reshape(3, 3); sp = d.site_xpos[s]; after = np.mean([R.T @ (d.geom_xpos[g] - sp) for g in tips], axis=0)
    c = after - before; c[2] = 0; n = np.linalg.norm(c); return (c/n if n > 1e-6 else np.array([1.0, 0, 0])), float(n)

def build(hand, world_bodies, timestep=0.0005):
    """one UR5e with one hand at the origin, objects from world_bodies"""
    spec = arm_spec_with_world(world_bodies, timestep); attach_hand(spec, hand, hand + "/"); return spec

def obj_body(name, kind, pos, size, mass, rgba="0.24 0.44 0.88 1"):
    return f'<body name="{name}" pos="{pos}"><freejoint/><geom type="{kind}" size="{size}" mass="{mass}" rgba="{rgba}" contype="3" conaffinity="3" friction="0.9 0.02 0.001"/></body>'

if __name__ == "__main__":
    write_custom_hands()
    for hand in HANDS:
        try:
            spec = build(hand, obj_body("bottle", "cylinder", "0.55 0 0.0605", "0.02 0.06", 0.15)); m = spec.compile(); d = mujoco.MjData(m)
            d.qpos[[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)] for n in ["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]]] = [-1.5708,-1.5708,1.5708,-1.5708,-1.5708,0]
            mujoco.mj_forward(m, d)
            site = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "attachment_site"); sp = d.site_xpos[site]; R = d.site_xmat[site].reshape(3,3); z = R[:,2]
            reach = max((float(np.dot(d.geom_xpos[g] - sp, z)) for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith(hand + "/") or m.body_rootid[m.geom_bodyid[g]] != 0 and (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[g]) or "").startswith(hand + "/")), default=0)
            print(f"{hand:9s} bodies {m.nbody:4d} nu {m.nu:3d} hand length along tool z {reach*1000:6.1f} mm")
        except Exception as e: print(hand, "FAILED", repr(e)[:200])
