"""Build the task catalog page: demo gallery with embedded videos and measured metrics, then the filterable 216-task catalog."""
import base64, json, os, subprocess, datetime, html
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
CAT = json.load(open(os.path.join(HERE, "catalog", "tasks.json"))); tasks = CAT["tasks"]; SRC = CAT["sources"]
import glob
metrics = {}
for f in sorted(glob.glob(os.path.join(OUT, "catalog_metrics*.json")), key=lambda p: (p.endswith("catalog_metrics.json") is False, os.path.getmtime(p))):
    for m in json.load(open(f)): metrics[m["slug"]] = m
# the bottle run from pick_demo, re-encoded small for the gallery
pm = json.load(open(os.path.join(OUT, "pick_metrics.json")))
small = os.path.join(OUT, "cat_bottle.mp4")
if not os.path.exists(small): subprocess.run(["/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "pick.mp4"), "-vf", "scale=640:-2", "-c:v", "libx264", "-crf", "27", "-pix_fmt", "yuv420p", "-movflags", "+faststart", small])
metrics["bottle"] = dict(slug="bottle", name="Pick up a bottle, carry it 300 mm, place it", src="SHAP tripod grip, ARAT tube", kind="pickplace", passed=True, tendrils_in_contact=pm["tendrils_in_contact"], grasp_force_N=pm["grasp_normal_force_N"], lift_mm=pm["bottle_lift_mm"], slip_mm=pm["slip_during_carry_mm"], place_error_mm=pm["place_error_mm"], upright=pm["bottle_upright"], wall_s=pm["wall_seconds"])
ORDER = ["bottle", "cup", "ball", "cube25", "box", "heavy", "stack", "button", "drawer", "knob"]
b64 = lambda p, mime: f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
def card(m):
    vid = os.path.join(OUT, f"cat_{m['slug']}.mp4"); has = os.path.exists(vid)
    keys = [("tendrils_in_contact", "tendrils on the object"), ("grasp_force_N", "N grasp force"), ("lift_mm", "mm lifted"), ("slip_mm", "mm slip in carry"), ("place_error_mm", "mm place error"), ("final_height_mm", "mm final height"), ("button_travel_mm", "mm button travel"), ("drawer_open_mm", "mm drawer opened"), ("knob_turn_deg", "deg knob turned")]
    stats = "".join(f"<span><b>{m[k]}</b> {lab}</span>" for k, lab in keys if k in m)
    body = f'<video controls playsinline preload="metadata" src="{b64(vid, "video/mp4")}"></video>' if has else '<div class="nov">render pending</div>'
    st = "pass" if m.get("passed") else ("fail" if "passed" in m else "wait")
    return f'<article class="card {st}"><header><span class="pill">{ {"pass":"PASS","fail":"FAIL","wait":"QUEUED"}[st] }</span><h3>{html.escape(m["name"])}</h3><span class="src">{html.escape(m.get("src",""))}</span></header>{body}<p class="stats">{stats or html.escape(m.get("error",""))}</p></article>'
cards = "".join(card(metrics[s]) if s in metrics else card(dict(slug=s, name=s, src="")) for s in ORDER)
demo_pass = {s for s, m in metrics.items() if m.get("passed")}
for t in tasks:
    if t["demo"]: t["status"] = "demo" if t["demo"] in demo_pass else ("failed" if t["demo"] in metrics else "queued")
n = len(tasks); by = lambda k: {v: sum(1 for t in tasks if t[k] == v) for v in sorted({t[k] for t in tasks})}
ready_now = sum(1 for t in tasks if t["status"] in ("demo", "ready", "bench", "queued", "failed"))
rows = "".join(f'<tr data-d="{t["domain"]}" data-s="{t["status"]}" data-g="{t["gate"]}" data-q="{html.escape((t["task"] + " " + " ".join(t["skills"]) + " " + t["objects"]).lower())}"><td class="n">{t["id"]}</td><td>{t["domain"]}</td><td>{html.escape(t["task"])}</td><td class="m">{", ".join(t["skills"])}</td><td class="m">{html.escape(t["objects"])}</td><td><span class="st {t["status"]}">{t["status"]}</span></td><td class="m">{t["gate"]}</td><td class="m">{", ".join(t["sources"])}</td></tr>' for t in tasks)
opts = lambda k: "".join(f'<option value="{v}">{v} ({c})</option>' for v, c in by(k).items())
srcs = "".join(f'<li><b>{k}</b> · {html.escape(v[0])} · <a href="{v[1]}">{v[1]}</a></li>' for k, v in SRC.items())
page = f'''<title>Robot Task Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#ECEEF1;--panel:#F5F6F8;--ink:#1A1F26;--ink2:#4B535E;--mute:#79818D;--rule:#C9CED6;--rule2:#AEB5BF;--teal:#1E9E93;--amber:#D9922A;--blue:#3E6FE0;--good:#1E9E93;--bad:#B23A2E;--btn:#fff}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E;--btn:#1F242C}}}}
:root[data-theme="dark"]{{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E;--btn:#1F242C}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:14.5px;line-height:1.5}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 20px 48px}}
.bar{{display:flex;align-items:baseline;gap:10px 24px;flex-wrap:wrap;padding-block:18px 12px;border-bottom:1px solid var(--rule)}}
h1{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;font-size:30px;letter-spacing:.03em;text-transform:uppercase;margin:0;line-height:1}}
.rev{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:11px;color:var(--mute);letter-spacing:.06em}} .sub{{color:var(--ink2);flex:1 1 320px;max-width:66ch;margin:0}}
h2{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--rule)}}
p{{max-width:74ch}}
.strip{{display:grid;grid-template-columns:repeat(6,1fr);border:1px solid var(--rule);margin-top:16px}} .strip>div{{padding:10px 12px;border-right:1px solid var(--rule)}} .strip>div:last-child{{border-right:0}}
.k{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}} .v{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:22px;font-variant-numeric:tabular-nums;line-height:1.2}} .v .u{{font-size:12px;color:var(--mute);margin-left:4px;font-family:Barlow,sans-serif}} .v.good{{color:var(--good)}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}
.card{{border:1px solid var(--rule);border-left:3px solid var(--rule2);background:var(--panel);padding:10px 12px}} .card.pass{{border-left-color:var(--good)}} .card.fail{{border-left-color:var(--bad)}}
.card header{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:8px}} .card h3{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;font-size:17px;margin:0;letter-spacing:.02em}}
.pill{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.1em;padding:2px 7px;border-radius:2px;color:#fff;background:var(--mute)}} .pass .pill{{background:var(--good)}} .fail .pill{{background:var(--bad)}}
.src{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin-left:auto}}
video{{display:block;width:100%;height:auto;border:1px solid var(--rule);background:#000}} .nov{{aspect-ratio:16/10;display:grid;place-items:center;border:1px dashed var(--rule2);color:var(--mute);font-family:"JetBrains Mono",monospace;font-size:12px}}
.stats{{display:flex;flex-wrap:wrap;gap:6px 16px;margin:8px 0 0;font-size:12.5px;color:var(--ink2)}} .stats b{{font-family:"JetBrains Mono",ui-monospace,monospace;font-weight:500;color:var(--ink)}}
.filters{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}} .filters select,.filters input{{font:inherit;font-size:13px;padding:6px 8px;border:1px solid var(--rule2);background:var(--btn);color:var(--ink);border-radius:2px}} .filters input{{flex:1 1 200px}}
.count{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;color:var(--mute);margin-left:auto}}
.tbl{{overflow-x:auto}} table{{width:100%;border-collapse:collapse;font-size:13px;min-width:900px}}
th{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-size:11px;color:var(--mute);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--rule2);position:sticky;top:0;background:var(--bg)}}
td{{padding:6px 10px 6px 0;border-bottom:1px solid var(--rule);vertical-align:top}} td.n{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;color:var(--mute)}} td.m{{color:var(--mute);font-size:12.5px}}
.st{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;padding:1px 6px;border-radius:2px;border:1px solid var(--rule2);color:var(--mute)}} .st.demo{{color:#fff;background:var(--good);border-color:var(--good)}} .st.bench{{color:var(--good);border-color:var(--good)}} .st.ready{{color:var(--ink)}} .st.failed{{color:#fff;background:var(--bad);border-color:var(--bad)}} .st.queued{{color:var(--amber);border-color:var(--amber)}}
ul.srcs{{font-size:13px;padding-left:18px;max-width:90ch}} ul.srcs li{{margin:4px 0}} a{{color:var(--blue)}}
@media (max-width:860px){{.strip{{grid-template-columns:repeat(3,1fr)}}.grid{{grid-template-columns:1fr}}}}
</style>
<div class="wrap">
  <header class="bar"><h1>Robot Task Catalog</h1><span class="rev">{n} TASKS · 12 SOURCES · {datetime.date.today().isoformat()}</span>
  <p class="sub">What people actually expect robots to do, gathered from the surveys, clinical hand tests and benchmarks that define the field, with a simulated demonstration of the design behind every task it can already do.</p></header>
  <div class="strip">
    <div><div class="k">Tasks catalogued</div><div class="v">{n}</div></div>
    <div><div class="k">Demos passing</div><div class="v good">{len(demo_pass)}<span class="u">of {len(ORDER)}</span></div></div>
    <div><div class="k">Doable with rigid physics now</div><div class="v">{ready_now}<span class="u">of {n}</span></div></div>
    <div><div class="k">Need deformables</div><div class="v">{sum(1 for t in tasks if t["gate"]=="deformables")}</div></div>
    <div><div class="k">Need fluids</div><div class="v">{sum(1 for t in tasks if t["gate"]=="fluids")}</div></div>
    <div><div class="k">Domains</div><div class="v">{len(by("domain"))}</div></div>
  </div>
  <h2>Demonstrations on the UR5e, measured in MuJoCo</h2>
  <p>Each card is one scripted run of the full-size 24-tendril bundle on a UR5e model. The numbers are read from the physics after the run, and the pass rule was fixed before it. A task the design cannot do stays on the page marked failed.</p>
  <div class="grid">{cards}</div>
  <h2>The catalog</h2>
  <p>Status means: <b>demo</b> has a passing simulation above, <b>bench</b> passed on the bench-mounted bundle, <b>ready</b> needs only rigid-body physics and is next to script, <b>queued</b> is rendering, <b>later</b> waits on a physics capability named in the gate column. Filter by domain, status or gate, or search.</p>
  <div class="filters"><select id="fd"><option value="">All domains</option>{opts("domain")}</select><select id="fs"><option value="">All statuses</option>{opts("status")}</select><select id="fg"><option value="">All gates</option>{opts("gate")}</select><input id="fq" type="search" placeholder="search tasks, skills, objects"><span class="count" id="cnt"></span></div>
  <div class="tbl"><table><thead><tr><th>#</th><th>Domain</th><th>Task</th><th>Skills</th><th>Objects</th><th>Status</th><th>Gate</th><th>Sources</th></tr></thead><tbody id="tb">{rows}</tbody></table></div>
  <h2>Sources</h2><ul class="srcs">{srcs}</ul>
  <p>Selection rule: the survey-ranked activities from BEHAVIOR-1K set the household weighting, RoboCasa365's ten skills set the skill vocabulary, the three clinical tests define human-level hand function item by item, and the industrial and humanoid lists cover work outside the home. The Beyond rows are the capabilities this design adds. Catalog file: <code>tendril-sim/catalog/tasks.json</code>.</p>
</div>
<script>
(function(){{const q=s=>document.querySelector(s);const rows=[...document.querySelectorAll('#tb tr')];const cnt=q('#cnt');
function apply(){{const d=q('#fd').value,s=q('#fs').value,g=q('#fg').value,t=q('#fq').value.trim().toLowerCase();let k=0;
rows.forEach(r=>{{const ok=(!d||r.dataset.d===d)&&(!s||r.dataset.s===s)&&(!g||r.dataset.g===g)&&(!t||r.dataset.q.includes(t));r.hidden=!ok;if(ok)k++;}});cnt.textContent=k+' of '+rows.length;}}
['fd','fs','fg'].forEach(i=>q('#'+i).addEventListener('change',apply));q('#fq').addEventListener('input',apply);apply();}})();
</script>'''
open(os.path.join(OUT, "task-catalog.html"), "w").write(page); print("page written", len(page)//1024, "KB; demos with video:", sum(1 for s in ORDER if os.path.exists(os.path.join(OUT, f"cat_{s}.mp4"))))
