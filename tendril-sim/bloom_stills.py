"""Hero stills of the Bloom on its own, hanging from the wrist as mounted: closed orb, opening, open, and the view up into the open iris."""
import os, numpy as np, mujoco
from PIL import Image
import bloom
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
bloom.build()
spec = mujoco.MjSpec.from_file(os.path.join(HERE, "hands", "bloom.xml"))
spec.visual.global_.offwidth = 1400; spec.visual.global_.offheight = 1000
spec.visual.quality.shadowsize = 8192
spec.visual.headlight.ambient[:] = (0.45, 0.45, 0.47); spec.visual.headlight.diffuse[:] = (0.35, 0.35, 0.35); spec.visual.headlight.specular[:] = (0.15, 0.15, 0.15)
spec.bodies[1].quat = [0, 1, 0, 0]                       # wrist up, orb hanging down, as it sits on the arm
key = spec.worldbody.add_light(pos=[0.5, -0.6, 0.5], dir=[-0.5, 0.6, -0.6], diffuse=[0.75, 0.75, 0.72], specular=[0.4, 0.4, 0.4], castshadow=True)
fill = spec.worldbody.add_light(pos=[-0.6, 0.4, 0.2], dir=[0.6, -0.4, -0.3], diffuse=[0.3, 0.32, 0.36], specular=[0, 0, 0], castshadow=False)
for l in (key, fill):
    try: l.type = mujoco.mjtLightType.mjLIGHT_DIRECTIONAL
    except AttributeError: l.directional = True
spec.add_texture(name="sky", type=mujoco.mjtTexture.mjTEXTURE_SKYBOX, builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT, rgb1=[0.86, 0.88, 0.9], rgb2=[0.62, 0.65, 0.7], width=512, height=512)
spec.add_texture(name="floor", type=mujoco.mjtTexture.mjTEXTURE_2D, builtin=mujoco.mjtBuiltin.mjBUILTIN_FLAT, rgb1=[0.9, 0.9, 0.89], rgb2=[0.9, 0.9, 0.89], width=64, height=64)
spec.add_material(name="floor", textures=["", "floor"], reflectance=0.12)
spec.worldbody.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[2, 2, 0.1], pos=[0, 0, -0.30], material="floor")
m = spec.compile(); d = mujoco.MjData(m)
r = mujoco.Renderer(m, height=1000, width=1400)
def pose(prox, dist):
    for i in range(bloom.N):
        d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"p{i}_j1")]] = prox
        d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"p{i}_j2")]] = dist
    mujoco.mj_forward(m, d)
def shot(name, az, el, dist=0.42, look=(0, 0, -0.05)):
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = look; cam.distance = dist; cam.azimuth = az; cam.elevation = el
    r.update_scene(d, camera=cam); Image.fromarray(r.render()).save(os.path.join(OUT, f"bloom_{name}.png"))
pose(0.0, 0.0);   shot("closed", 140, -14)
pose(0.55, -0.2); shot("mid", 140, -22, dist=0.46)
pose(1.3, -0.5);  shot("open", 140, -18, dist=0.52)
pose(1.3, -0.5);  shot("open_top", 140, 62, dist=0.5, look=(0, 0, -0.02))   # from below, looking up into the open iris at the core
print("stills written")
