"""One close-up per prototype: the hand alone on its arm at the home pose, framed from the finger side, with a bottle beside it for scale."""
import os, sys, numpy as np, mujoco
from PIL import Image
import prototypes as P, lineup as L
OUT = os.path.join(P.HERE, "out")
def render(hand):
    spec = P.build(hand, P.obj_body("bottle", "cylinder", "-0.13 0.66 0.0605", "0.02 0.06", 0.15))
    spec.visual.headlight.ambient[:] = (0.4, 0.4, 0.42); spec.visual.headlight.diffuse[:] = (0.4, 0.4, 0.4)
    m = spec.compile(); d = mujoco.MjData(m)
    for j, n in enumerate(["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]):
        d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]] = L.ARM_HOME[j]
    mujoco.mj_forward(m, d)
    s = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "attachment_site"); sp = d.site_xpos[s].copy(); z = d.site_xmat[s].reshape(3, 3)[:, 2]
    r = mujoco.Renderer(m, height=750, width=1000)
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    length = P.mount_quat(hand)[1]
    cam.lookat[:] = sp + z*min(length, 0.22)*0.5; cam.distance = 0.55 + 0.6*min(length, 0.4); cam.azimuth = 135; cam.elevation = -18
    r.update_scene(d, camera=cam); Image.fromarray(r.render()).save(os.path.join(OUT, f"hero_{hand}.png"))
    print(hand, "hero rendered, length", round(length*1000), "mm")
if __name__ == "__main__":
    P.write_custom_hands()
    for hand in (sys.argv[1:] or list(P.HANDS)): render(hand)
