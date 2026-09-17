"""Seven prototypes on seven UR5e arms in one scene, one bottle each. Static render for orientation checks, and the base for the live race."""
import os, sys, math, numpy as np, mujoco
import prototypes as P
SPACING = 0.9
ARM_HOME = [-1.5708, -1.5708, 1.5708, -1.5708, -1.5708, 0.0]
def build_lineup(hands, object_xml=None, timestep=0.0005):
    P.write_custom_hands()
    world = P.arm_spec_with_world("", timestep)             # gives us floor, lights, options, and one arm we will not use
    # start a clean world: floor and lights only, then attach arm+hand copies at spaced frames
    w = mujoco.MjSpec(); w.modelname = "lineup"
    w.option.timestep = timestep; w.option.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST; w.option.cone = mujoco.mjtCone.mjCONE_ELLIPTIC; w.option.impratio = 5
    w.visual.global_.offwidth = 1600; w.visual.global_.offheight = 1000; w.visual.quality.shadowsize = 4096
    tex = w.add_texture(name="grid", type=mujoco.mjtTexture.mjTEXTURE_2D, builtin=mujoco.mjtBuiltin.mjBUILTIN_CHECKER, rgb1=[0.88,0.89,0.91], rgb2=[0.82,0.84,0.87], width=512, height=512)
    mat = w.add_material(name="grid", texrepeat=[16, 16], reflectance=0.05); mat.textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "grid"
    w.worldbody.add_light(pos=[2.5, -0.8, 2.2], dir=[-0.3, 0.3, -0.9], castshadow=True); w.worldbody.add_light(pos=[1.0, 1.5, 1.6], dir=[0.1, -0.7, -0.7], castshadow=False, diffuse=[0.35,0.35,0.35])
    w.worldbody.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[6, 6, 0.01], material="grid", contype=3, conaffinity=3, friction=[0.9, 0.02, 0.001])
    for i, hand in enumerate(hands):
        x = SPACING*i
        arm = mujoco.MjSpec.from_file(os.path.join(P.UR, "ur5e.xml"))
        arm_txt = None
        P.attach_hand(arm, hand, hand + "/")
        frame = w.worldbody.add_frame(pos=[x, 0, 0])
        w.attach(arm, prefix=f"a{i}/", frame=frame)
        b = w.worldbody.add_body(name=f"bottle{i}", pos=[x + 0.55, 0, 0.0605]); b.add_freejoint()
        b.add_geom(type=mujoco.mjtGeom.mjGEOM_CYLINDER, size=[0.02, 0.06, 0], mass=0.15, rgba=[0.24,0.44,0.88,1], contype=3, conaffinity=3, friction=[0.9,0.02,0.001])
    return w
if __name__ == "__main__":
    hands = list(P.HANDS)
    w = build_lineup(hands); m = w.compile(); d = mujoco.MjData(m)
    for i in range(len(hands)):
        for j, n in enumerate(["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]):
            d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"a{i}/{n}")]] = ARM_HOME[j]
    mujoco.mj_forward(m, d)
    r = mujoco.Renderer(m, height=560, width=1600); cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = (SPACING*3, 0.15, 0.35); cam.distance = 4.2; cam.azimuth = 200; cam.elevation = -12
    r.update_scene(d, camera=cam); from PIL import Image; Image.fromarray(r.render()).save(os.path.join(P.HERE, "out", "lineup.png"))
    cam.lookat[:] = (SPACING*3, 0.15, 0.45); cam.distance = 2.2; cam.azimuth = 200; cam.elevation = -8
    for i, hand in enumerate(hands):
        cam.lookat[:] = (SPACING*i - 0.13, 0.49, 0.42); cam.distance = 0.9; cam.azimuth = 160; cam.elevation = -15
        r.update_scene(d, camera=cam); Image.fromarray(r.render()).save(os.path.join(P.HERE, "out", f"lineup_{hand}.png"))
    print("bodies", m.nbody, "nu", m.nu, "rendered")
