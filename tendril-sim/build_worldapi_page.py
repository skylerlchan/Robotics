"""World API page: the verbs, the loop, the conformance suite results with frames, a transcript, the log, and the honest limits."""
import base64, json, os, glob, html, datetime
import prototypes as P, worldapi as W
OUT = os.path.join(P.HERE, "out")
R = {}
for f in sorted(glob.glob(os.path.join(OUT, "worldapi_suite*.json")), key=lambda p: (not p.endswith("worldapi_suite.json"), os.path.getmtime(p))):
    for r in json.load(open(f)): R[r["slug"]] = r
R = {T["slug"]: R[T["slug"]] for T in W.TASKS if T["slug"] in R}
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
e = html.escape
passed = sum(r["passed"] for r in R.values()); n_calls = sum(len(r["calls"]) for r in R.values()); first_try = sum(1 for r in R.values() for c in r["calls"] if c["ok"] and c["attempts"] == 1); retried_ok = sum(1 for r in R.values() for c in r["calls"] if c["ok"] and c["attempts"] > 1)
log_n = 0; traj_n = 0; log_kb = 0
lp = os.path.join(OUT, "worldapi_log.jsonl")
if os.path.exists(lp):
    log_kb = os.path.getsize(lp)//1024
    for line in open(lp): rec = json.loads(line); log_n += 1; traj_n += len(rec["traj"])
# bundle results on the same tasks, from the earlier catalog run
B = {}
for f in glob.glob(os.path.join(OUT, "catalog_metrics*.json")):
    try:
        v = json.load(open(f)); v = v if isinstance(v, list) else [v]
        for r in v:
            if "slug" in r: B[r["slug"]] = r
    except Exception: pass
VERBS = [
 ("perceive()", "returns the scene graph: every object with kind, pose, bounding box, parts, joint state, what is graspable, what is held", "no action", "none"),
 ("grasp(name)", "picks the narrowest part that fits the 85 mm opening, sets the wrist yaw across it, descends, squeezes in proportion to the width, lifts 100 mm", "pads touching and the object rose more than 60 mm", "3 tries: rotate 90°, then go 6 mm deeper and squeeze harder"),
 ("place(name, at | on | xy)", "carries the held object over the target, lowers it until its bottom is 4 mm above the surface, opens, retreats", "within 25 mm of the target, bottom within 12 mm of the surface, nothing touching the hand", "2 tries; if it landed wrong it re-grasps and repeats"),
 ("release()", "opens the gripper", "always", "none"),
 ("press(name)", "closes the gripper into a fist, descends on the button 15 mm past its top", "the button's joint travelled at least 10 mm", "2 tries, 4 mm deeper"),
 ("open(name) / close(name)", "grasps the handle without lifting, drives the tool along the joint axis toward the far end of its range, lets go", "the joint moved at least 60 % of what was asked", "inherits grasp's 3 tries"),
 ("turn(name, deg)", "grasps the knob, rotates the wrist yaw by the angle, lets go", "the hinge turned at least 60 % of the angle", "inherits grasp's 3 tries"),
 ("push(name, dx, dy)", "closed fist beside the object on the far side, drives through by the distance plus 30 mm", "the object moved at least 70 % of the distance along the push", "2 tries from the new position"),
 ("go_to(xyz, yaw)", "moves the flange to a point with the tool pointing down", "within 8 mm", "none"),
 ("expect(pred)", "checks a predicate on the scene graph: at, on, open, pressed, turned, moved", "the predicate itself", "none"),
]
verbs_rows = "".join(f"<tr><td><code>{e(v)}</code></td><td>{e(w)}</td><td>{e(c)}</td><td class='m'>{e(r)}</td></tr>" for v, w, c, r in VERBS)
def chain(r): return " → ".join(f"{c['verb']}{'' if c['ok'] else ' ✗'}" for c in r["calls"])
suite_rows = "".join(f"<tr><td><b>{e(r['name'])}</b><div class='m'>{e(r['src'])}</div></td><td class='n'>{e(chain(r))}</td><td class='n'>{max((c['attempts'] for c in r['calls']), default=0)}</td><td><span class='pill {'ok' if r['passed'] else 'no'}'>{'PASS' if r['passed'] else 'FAIL'}</span></td><td class='m'>{e(r['calls'][-1]['detail'] if r['calls'] else r.get('error', ''))}</td></tr>" for r in R.values())
def frames(r):
    fs = [f for f in r["frames"] if os.path.exists(os.path.join(OUT, f))]
    caps = [c["verb"] for c in r["calls"] if c["verb"] != "expect"]
    return "".join(f"<figure><img src='{b64(os.path.join(OUT, f))}' alt='{e(r['slug'])} after {e(caps[i] if i < len(caps) else '')}'><figcaption>after <b>{e(caps[i] if i < len(caps) else '')}</b></figcaption></figure>" for i, f in enumerate(fs))
gallery = "".join(f"<div class='task'><h3>{e(r['name'])} <span class='pill {'ok' if r['passed'] else 'no'}'>{'PASS' if r['passed'] else 'FAIL'}</span></h3><div class='frames'>{frames(r)}</div><p class='m'>" + " · ".join(e(f"{c['verb']}: {c['detail']}") for c in r["calls"]) + "</p></div>" for r in R.values())
tr = R.get("cup") or next(iter(R.values()), None)
transcript = "".join(f"<span class='req'>&gt; {e(c['verb'])}({e(json.dumps({k: v for k, v in c['args'].items() if v is not None}))})</span>\n<span class='{'okc' if c['ok'] else 'noc'}'>&lt; {{\"ok\": {str(c['ok']).lower()}, \"attempts\": {c['attempts']}, \"detail\": \"{e(c['detail'])}\"}}</span>\n" for c in tr["calls"]) if tr else ""
cmp_rows = "".join(f"<tr><td>{e(r['name'])}</td><td><span class='pill {'ok' if r['passed'] else 'no'}'>{'PASS' if r['passed'] else 'FAIL'}</span></td><td>{('<span class=\"pill ' + ('ok' if B[s]['passed'] else 'no') + '\">' + ('PASS' if B[s]['passed'] else 'FAIL') + '</span>') if s in B else '<span class=m>not run</span>'}</td></tr>" for s, r in R.items())
mcp = json.dumps([{"name": "grasp", "description": "Pick up an object by name and hold it.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
                  {"name": "place", "description": "Set the held object down at a surface, on another object, or at xy.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "at": {"type": "string"}, "on": {"type": "string"}, "xy": {"type": "array"}}}},
                  {"name": "press", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}}}, {"name": "open", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}}}, {"name": "turn", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "deg": {"type": "number"}}}},
                  {"name": "perceive", "description": "Return the scene graph.", "input_schema": {"type": "object", "properties": {}}}, {"name": "expect", "input_schema": {"type": "object", "properties": {"pred": {"type": "string"}}}}], indent=1)
page = f'''<title>World API</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#ECEEF1;--panel:#F5F6F8;--ink:#1A1F26;--ink2:#4B535E;--mute:#79818D;--rule:#C9CED6;--rule2:#AEB5BF;--teal:#1E9E93;--amber:#D9922A;--blue:#3E6FE0;--good:#1E9E93;--bad:#B23A2E}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}}}
:root[data-theme="dark"]{{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:14.5px;line-height:1.5}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 20px 48px}}
.bar{{display:flex;align-items:baseline;gap:10px 24px;flex-wrap:wrap;padding-block:18px 12px;border-bottom:1px solid var(--rule)}}
h1{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;font-size:30px;letter-spacing:.03em;text-transform:uppercase;margin:0;line-height:1}}
.rev{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:11px;color:var(--mute);letter-spacing:.06em}} .sub{{color:var(--ink2);flex:1 1 320px;max-width:66ch;margin:0}}
h2{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--rule)}}
h3{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:17px;font-weight:600;letter-spacing:.02em;margin:18px 0 8px;display:flex;align-items:center;gap:10px}}
p{{max-width:74ch}} .m{{color:var(--mute);font-size:12.5px}}
.loop{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0 4px}} .loop span{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:15px;letter-spacing:.06em;text-transform:uppercase;padding:6px 12px;border:1px solid var(--rule2);background:var(--panel)}} .loop i{{color:var(--mute);font-style:normal}} .loop span.hot{{border-color:var(--teal);color:var(--teal)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}} th{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-size:11px;color:var(--mute);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--rule2)}}
td{{padding:7px 10px 7px 0;border-bottom:1px solid var(--rule);vertical-align:top}} td.n{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;white-space:nowrap}}
.pill{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.1em;padding:2px 7px;border-radius:2px;color:#fff;background:var(--bad);white-space:nowrap}} .pill.ok{{background:var(--good)}}
code{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;background:var(--panel);padding:1px 5px;border:1px solid var(--rule);border-radius:2px;white-space:nowrap}}
pre{{background:var(--panel);border:1px solid var(--rule);padding:10px 12px;overflow-x:auto;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;line-height:1.5}} pre .req{{color:var(--blue)}} pre .okc{{color:var(--good)}} pre .noc{{color:var(--bad)}}
.frames{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}} figure{{margin:0}} figure img{{display:block;width:100%;height:auto;border:1px solid var(--rule)}} figcaption{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-top:4px}}
.task{{padding:8px 0 14px;border-bottom:1px solid var(--rule)}} .task p{{max-width:none;margin:8px 0 0}}
.kpi{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:10px 0}} .kpi div{{background:var(--panel);border-left:3px solid var(--teal);padding:8px 12px}} .kpi b{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:26px;font-weight:600;display:block;line-height:1.1}} .kpi span{{font-size:12.5px;color:var(--ink2)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media (max-width:820px){{.frames{{grid-template-columns:1fr}} .kpi{{grid-template-columns:repeat(2,1fr)}} .two{{grid-template-columns:1fr}}}}
</style>
<div class="wrap">
  <header class="bar"><h1>World API</h1><span class="rev">V0 · {len(VERBS)} VERBS · UR5e + ROBOTIQ 2F-85 · MUJOCO · {datetime.date.today().isoformat()}</span>
  <p class="sub">The connector for the physical world, in the shape aside gives the browser: a scene graph you can read, a handful of verbs you can call, and a loop underneath that verifies every call and retries it. The hand is the cheapest one that exists. The loop is the product.</p></header>
  <h2>The loop</h2>
  <div class="loop"><span>perceive</span><i>→</i><span>plan</span><i>→</i><span>act</span><i>→</i><span class="hot">verify</span><i>→</i><span class="hot">retry</span><i>→</i><span>log</span></div>
  <p>Every verb reads the scene graph, plans from geometry, acts, reads the scene graph again to check that the world changed the way it should, and tries again with a perturbation if it did not. Each call is appended to a log with the scene before, the tool trajectory, and the outcome. A browser gives aside the DOM for free; here the scene graph is read from the simulator, which is the one part a real robot has to earn with a camera and a vision model.</p>
  <h2>Verbs</h2>
  <table><tr><th>Call</th><th>What it does</th><th>How it verifies</th><th>Retry</th></tr>{verbs_rows}</table>
  <h2>Conformance suite · {passed} of {len(R)} tasks passed</h2>
  <div class="kpi"><div><b>{passed}/{len(R)}</b><span>tasks passed end to end</span></div><div><b>{first_try}/{n_calls}</b><span>verb calls succeeded first try</span></div><div><b>{retried_ok}</b><span>calls rescued by a retry</span></div><div><b>{sum(r.get('sim_seconds', 0) for r in R.values()):.0f} s</b><span>simulated, in {sum(r.get('seconds', 0) for r in R.values()):.0f} s of wall time</span></div></div>
  <table><tr><th>Task</th><th>Calls</th><th>Max tries</th><th>Result</th><th>Last detail</th></tr>{suite_rows}</table>
  <h2>Every task, frame by frame</h2>
  {gallery}
  <h2>A transcript</h2>
  <p>What the caller sees for the cup task. This is the whole interface: a verb in, a verdict out, and the reason in plain words.</p>
  <pre>{transcript}</pre>
  <div class="two"><div>
  <h2>Same tasks, gripper against the bundle</h2>
  <table><tr><th>Task</th><th>2F-85 via the API</th><th>24-tendril bundle, scripted</th></tr>{cmp_rows}</table>
  <p class="m">Both are scripted, so this compares hardware plus planner, not learning. The bundle needed a bespoke script per task; the gripper needs one verb per task.</p>
  </div><div>
  <h2>What the log holds</h2>
  <p>{log_n} verb records, {traj_n} trajectory samples, {log_kb} KB in <code>out/worldapi_log.jsonl</code>. Each record: task, verb, arguments, the scene graph before and after, the tool path at 20 Hz with the gripper command, the verdict and the attempts. This is the shape of a demonstration dataset. Swap the scripted planner for a policy trained on it and the verbs, the suite, and the log all stay the same.</p>
  <h2>Honest limits</h2>
  <p>Perception is an oracle: the scene graph comes from simulator state, so these numbers are an upper bound for the planner and say nothing about a camera. The planner is geometric, not learned. Objects are simple shapes on a floor. What carries over is the contract: the verbs, the verification rules, the retry policy, and the log format.</p>
  </div></div>
  <h2>As tools for a model</h2>
  <pre>{e(mcp)}</pre>
  <h2>See it live</h2>
  <pre>cd ~/Projects/research/Robotics/tendril-sim
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/mjpython worldapi.py live cup       # watch one task
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/python worldapi.py suite            # rerun everything, headless</pre>
</div>'''
open(os.path.join(OUT, "world-api.html"), "w").write(page); print("page written", len(page)//1024, "KB")
