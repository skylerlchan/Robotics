import time, numpy as np, mujoco, pick_demo
from PIL import Image
t0 = time.time(); D = pick_demo.Demo(); print("bodies", D.m.nbody, "nv", D.m.nv, "nu", D.m.nu, "build", round(time.time()-t0, 1), "s")
print("tool at home", D.d.site_xpos[D.tool].round(3), "arm q", D.arm_q.round(2))
target = np.array([0.55, 0.0, 0.42]); t0 = time.time(); D.run(3.0, target); print("after 1.5 s: tool", D.d.site_xpos[D.tool].round(3), "arm q", D.arm_q.round(2), "err mm", round(float(np.linalg.norm(target - D.d.site_xpos[D.tool])*1000), 1), "wall", round(time.time()-t0, 1), "s", "ncon", D.d.ncon); print("tool z-axis in world", D.d.site_xmat[D.tool].reshape(3,3)[:,2].round(3), "want 0 0 -1")
Image.fromarray(D.frames[-1]).save("out/pick_test.png"); print("frame saved")
