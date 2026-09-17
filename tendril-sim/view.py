"""Live 3D viewer. Watch the simulation run while you orbit, zoom and pause.

  mjpython view.py bottle            the UR5e + 24-tendril bundle picks up a bottle
  mjpython view.py cup|ball|cube25|box|heavy|stack|button|drawer|knob
  mjpython view.py bench hold|reach|pinch|wrap|cage|parallel|ring    the bench-mounted 8-tendril bundle
  mjpython view.py scene             the UR5e scene with nothing running; drag objects with the mouse

macOS needs mjpython (it ships with the mujoco package). Mouse: left-drag orbits, right-drag pans, scroll zooms,
double-click selects a body, Ctrl+right-drag applies a force to it. Space pauses.
"""
import os, sys, time, mujoco, mujoco.viewer
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PACE = float(os.environ.get("PACE", "1.0"))   # 1.0 = try to run in real time; the full-scale scene is heavier and will run slower than that

def attach_viewer(model, data, lookat, distance, azimuth, elevation):
    v = mujoco.viewer.launch_passive(model, data)
    v.cam.lookat[:] = lookat; v.cam.distance = distance; v.cam.azimuth = azimuth; v.cam.elevation = elevation
    return v

def hold_open(v, model, data):
    while v.is_running():
        t0 = time.time(); mujoco.mj_step(model, data); v.sync(); time.sleep(max(0, model.opt.timestep/PACE - (time.time()-t0)))

if len(sys.argv) < 2 or sys.argv[1] == "scene":
    xml = os.path.join(HERE, "third_party", "mujoco_menagerie", "universal_robots_ur5e", "pick_scene.xml")
    m = mujoco.MjModel.from_xml_path(xml); d = mujoco.MjData(m)
    m.opt.timestep = 0.001
    v = attach_viewer(m, d, (0.45, -0.12, 0.18), 1.25, 250, -20); hold_open(v, m, d)

elif sys.argv[1] == "bench":
    import sim, tasks
    task = sys.argv[2] if len(sys.argv) > 2 else "cage"
    orig_step = sim.Sim.step; orig_init = sim.Sim.__init__
    def new_init(self, *a, **k):
        orig_init(self, *a, **k)
        if not hasattr(sim, "_viewer"): sim._viewer = attach_viewer(self.model, self.data, (0.0, 0.0, 0.08), 0.46, 140, -24)
        self.viewer = sim._viewer; sim._last = self
    def new_step(self, seconds):
        n = int(seconds/self.model.opt.timestep); sync_every = int(0.02/self.model.opt.timestep)
        for i in range(n):
            t0 = time.time(); mujoco.mj_step(self.model, self.data)
            if i % sync_every == 0 and self.viewer.is_running(): self.viewer.sync(); time.sleep(max(0, 0.02/PACE - (time.time()-t0)))
    sim.Sim.__init__ = new_init; sim.Sim.step = new_step; sim.Sim.render = lambda self, path, **k: path
    getattr(tasks, "task_" + task)()
    print("task finished; window stays open. close it to exit.")
    hold_open(sim._viewer, sim._last.model, sim._last.data)

else:
    import pick_demo, catalog_demo
    slug = sys.argv[1]
    class LiveDemo(pick_demo.Demo):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.viewer = attach_viewer(self.m, self.d, (0.45, -0.12, 0.18), 1.25, 250, -20)
        def run(self, seconds, p_des, fps=30, tag=None):
            steps = int(seconds/self.m.opt.timestep); per_ctrl = int(0.01/self.m.opt.timestep); sync_every = int(0.02/self.m.opt.timestep)
            for k in range(steps):
                t0 = time.time()
                if k % per_ctrl == 0: self.ik_step(p_des)
                mujoco.mj_step(self.m, self.d)
                if k % sync_every == 0 and self.viewer.is_running(): self.viewer.sync(); time.sleep(max(0, 0.02/PACE - (time.time()-t0)))
        def snap(self, name): pass
    catalog_demo.Demo = LiveDemo; catalog_demo.encode = lambda D, slug: 0
    TASKS = catalog_demo.TASKS + [dict(slug="bottle", name="Pick up a bottle, carry it, place it", src="SHAP", kind="pickplace", obj="bottle", inner_pre=0, force=8, grasp_z=0.29, world=pick_demo.DEFAULT_WORLD)]
    T = next(t for t in TASKS if t["slug"] == slug); m = catalog_demo.run_task(T); print({k: v for k, v in m.items() if k != "frames"})
    print("task finished; window stays open. close it to exit.")
    import gc
    for obj in gc.get_objects():
        if isinstance(obj, LiveDemo): hold_open(obj.viewer, obj.m, obj.d); break
