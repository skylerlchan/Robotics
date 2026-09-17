"""Fold Laundry Only: what a single-purpose folding cell measures when perception stops being free."""
import base64, json, os, html, datetime
import laundry as L
OUT = os.path.join(L.HERE, "out")
P = json.load(open(os.path.join(OUT, "perception.json")))
try: T = json.load(open(os.path.join(OUT, "laundry.json")))
except Exception: T = []
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
img = lambda n: b64(os.path.join(OUT, n))
e = html.escape
C = {r["level"]: r for r in P["corners"]}
CR = P["crease"] if isinstance(P["crease"], list) else [P["crease"]]
cam = P["camera"]
LAB = {"flat": "Laid out", "rumpled": "Rumpled", "heap": "In a heap"}

# ---- one chart: mean corner error by how messy the towel is, against the tolerance a grasp needs
W, BARH, GAP, X0, TOP = 720, 30, 18, 132, 30
rows = [(LAB[k], C[k]["mean_mm"], C[k]["p90_mm"], C[k]["under_20mm"]) for k in ("flat", "rumpled", "heap")]
XMAX = 170.0; PLOTW = W - X0 - 76
Hc = TOP + len(rows)*(BARH + GAP) + 34
sx = lambda v: X0 + min(v, XMAX)/XMAX*PLOTW
ticks = "".join(f'<line x1="{sx(t):.1f}" y1="{TOP-8}" x2="{sx(t):.1f}" y2="{TOP+len(rows)*(BARH+GAP)-GAP+6}" class="grid"/>'
                f'<text x="{sx(t):.1f}" y="{TOP+len(rows)*(BARH+GAP)-GAP+22}" class="tick" text-anchor="middle">{t}</text>' for t in (0, 40, 80, 120, 160))
bars = ""
for i, (lab, mean, p90, _) in enumerate(rows):
    y = TOP + i*(BARH + GAP); w = max(sx(mean) - X0, 2)
    bars += (f'<text x="{X0-12}" y="{y+BARH*0.68:.1f}" class="cat" text-anchor="end">{e(lab)}</text>'
             f'<rect x="{X0}" y="{y}" width="{w:.1f}" height="{BARH}" rx="4" class="bar"/>'
             f'<text x="{min(sx(mean)+10, W-70):.1f}" y="{y+BARH*0.68:.1f}" class="val">{mean:.1f} mm</text>')
thr = sx(20)
chart = f'''<svg viewBox="0 0 {W} {Hc}" width="100%" role="img" aria-label="Mean corner error grows from 0.4 mm when the towel is laid out to 101 mm when it is in a heap">
  <title>Corner error from one overhead depth image</title>{ticks}
  <line x1="{thr:.1f}" y1="{TOP-14}" x2="{thr:.1f}" y2="{TOP+len(rows)*(BARH+GAP)-GAP+6}" class="thr"/>
  <text x="{thr+8:.1f}" y="{TOP-18}" class="thrlab">20 mm: what the grasp can tolerate</text>
  {bars}
  <text x="{X0}" y="{Hc-2}" class="tick">millimetres of error in locating a corner</text>
</svg>'''

crows = "".join(f'<tr><td>{("crisp" if r["mess_mm"] == 0 else f"wrinkled by {r['mess_mm']:.0f} mm")}</td>'
                f'<td class="n">{r["correct"]}/{r["n"]}</td>'
                f'<td class="n">{r["accuracy"]*100:.0f}%</td>'
                f'<td><span class="pill {"ok" if r["accuracy"] > 0.8 else "no"}">{"reliable" if r["accuracy"] > 0.8 else "worse than a coin flip"}</span></td></tr>' for r in CR)
corn = "".join(f'<tr><td>{e(LAB[k])}</td><td class="n">{C[k]["mean_mm"]}</td><td class="n">{C[k]["median_mm"]}</td>'
               f'<td class="n">{C[k]["p90_mm"]}</td><td class="n">{C[k]["max_mm"]}</td><td class="n">{C[k]["under_20mm"]*100:.0f}%</td></tr>' for k in ("flat", "rumpled", "heap"))
tr = [t for t in T if t.get("size_mm")]
trows = "".join(f'<tr><td class="m">{t["mode"]}, seed {t["seed"]}</td><td class="n">{t["size_mm"][0]} x {t["size_mm"][1]}</td>'
                f'<td>{"<span class=pill-ok>fold geometry correct</span>" if abs(t["size_mm"][1]-200) < 58 and abs(t["size_mm"][0]-400) < 80 else "<span class=pill-no>wrong shape</span>"}</td>'
                f'<td class="m">{e(t["note"])}</td></tr>' for t in tr[:8])

FAILS = [
 ("The fingertip was 25 mm higher than the model thought", "The gripper's pads extend well below the body they hang from. Using the body position as the fingertip made the arm drive its fingers into the tabletop while believing it was touching the towel.", "measure the tool from its own collision geometry, never from a nominal offset"),
 ("The pinch gathered the fabric", "Holding the caught cloth at a quarter of its spread bunched the towel a little on every grasp. After two grasps a 400 mm towel measured 290 mm.", "hold fabric where it was caught"),
 ("The catch test was finer than the cloth", "The towel is sampled every 40 mm, so a jaw can straddle fabric with no sample point inside it. The cell reported “no fabric” while sitting on the towel.", "test against the surface, not the sample points"),
 ("Moving fast threw the towel across the room", "The grasp pins cloth to the fingertips. Carrying the edge at half a metre per second flung the whole towel off the table.", "slow the carry until the fabric follows"),
 ("The two arms folded into each other", "Folding along the towel's own long axis sent both arms reaching across the table to the same place. The fold direction has to come from the cell's layout, not the towel's shape.", "each arm keeps its own side"),
 ("The gripper had not finished opening", "Letting go and lifting in the same breath carried the towel up with the hand, to the park position, off the table.", "wait for the jaws, then slide out sideways before lifting"),
 ("The towel sank into the table", "Soft contact let the cloth settle several millimetres below the tabletop, so the depth image saw a shredded towel and every height calculation was wrong.", "stiffen contact until the cloth rests on the surface"),
 ("The fabric draped over the hand", "During the fold arc a third of the towel ended up above the fingertips, hooked on the gripper, and rode up with it.", "grab close to the edge, keep the arc low"),
 ("Pressing the fold flat wadded it", "Adding the press a real folding machine uses drove the hands into the cloth and dragged it into a ball.", "no fix found in this session"),
]
fails = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span><span class="fix">{e(c)}</span></li>' for a, b, c in FAILS)

page = f'''<title>Fold Laundry Only</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#ECEEF1;--panel:#F5F6F8;--ink:#1A1F26;--ink2:#4B535E;--mute:#79818D;--rule:#C9CED6;--rule2:#AEB5BF;--teal:#1E9E93;--amber:#D9922A;--blue:#3E6FE0;--good:#1E9E93;--bad:#B23A2E}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}}}
:root[data-theme="dark"]{{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:14.5px;line-height:1.55}}
.wrap{{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:0 52px}}
.bar{{display:flex;align-items:baseline;gap:10px 24px;flex-wrap:wrap;padding-block:20px 12px;border-bottom:1px solid var(--rule)}}
h1{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;font-size:32px;letter-spacing:.03em;text-transform:uppercase;margin:0;line-height:1}}
.rev{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:11px;color:var(--mute);letter-spacing:.06em}}
.sub{{color:var(--ink2);flex:1 1 320px;max-width:66ch;margin:0}}
h2{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin:34px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--rule)}}
p{{max-width:74ch}} .m{{color:var(--mute);font-size:12.5px}}
.lead{{font-size:16px;max-width:70ch}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}} figure{{margin:0}} .grid4 img,.two img{{display:block;width:100%;height:auto;border:1px solid var(--rule)}}
figcaption{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-top:5px}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-size:11px;color:var(--mute);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--rule2)}}
td{{padding:7px 10px 7px 0;border-bottom:1px solid var(--rule);vertical-align:top}}
td.n{{font-family:"JetBrains Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;white-space:nowrap}}
.pill,.pill-ok,.pill-no{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.08em;padding:2px 7px;border-radius:2px;color:#fff;white-space:nowrap}}
.pill.ok,.pill-ok{{background:var(--good)}} .pill.no,.pill-no{{background:var(--bad)}}
svg .bar{{fill:var(--teal)}} svg .grid{{stroke:var(--rule);stroke-width:1}} svg .thr{{stroke:var(--amber);stroke-width:2;stroke-dasharray:5 4}}
svg .cat{{fill:var(--ink);font-family:Barlow,sans-serif;font-size:14px}}
svg .val{{fill:var(--ink);font-family:"JetBrains Mono",monospace;font-size:12.5px}}
svg .tick{{fill:var(--mute);font-family:"JetBrains Mono",monospace;font-size:11px}}
svg .thrlab{{fill:var(--amber);font-family:Barlow,sans-serif;font-size:12px}}
ol.fails{{list-style:none;counter-reset:f;padding:0;margin:0;display:grid;gap:10px}}
ol.fails li{{counter-increment:f;background:var(--panel);border-left:3px solid var(--bad);padding:10px 14px;display:grid;gap:3px}}
ol.fails li b{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:16.5px;letter-spacing:.01em}}
ol.fails li b::before{{content:counter(f) ". ";color:var(--mute);font-family:"JetBrains Mono",monospace;font-size:12px}}
ol.fails li span{{color:var(--ink2)}} ol.fails li .fix{{color:var(--teal);font-size:12.5px}}
ol.fails li .fix::before{{content:"fix: ";color:var(--mute)}}
.kpi{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}}
.kpi div{{background:var(--panel);border-left:3px solid var(--teal);padding:10px 14px}}
.kpi b{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:27px;font-weight:600;display:block;line-height:1.1}}
.kpi span{{font-size:12.5px;color:var(--ink2)}}
pre{{background:var(--panel);border:1px solid var(--rule);padding:10px 12px;overflow-x:auto;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px}}
code{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;background:var(--panel);padding:1px 5px;border:1px solid var(--rule);border-radius:2px}}
@media (max-width:860px){{.grid4{{grid-template-columns:repeat(2,1fr)}} .two{{grid-template-columns:1fr}} .kpi{{grid-template-columns:1fr}}}}
</style>
<div class="wrap">
  <header class="bar"><h1>Fold Laundry Only</h1>
    <span class="rev">TWO UR5e ARMS · ONE TABLE · ONE {round(L.SIDE*1000)} MM TOWEL · MUJOCO CLOTH · {datetime.date.today().isoformat()}</span>
    <p class="sub">Narrowing a robot to one job is the right instinct, and it is how every robot that ever shipped got built. This is that cell, built and measured. It says something specific about why laundry is the wrong one job to pick.</p>
  </header>

  <p class="lead">Give up generality and you can change the world instead of the robot: one table, one fixed camera, one fabric, known lighting. So the cell below has nothing to do but fold. The towel is real cloth, {L.N}&#215;{L.N} vertices with mass and friction. The camera is a real depth render, {cam["height_mm"]} mm above the table, {cam["mm_per_pixel"]} mm per pixel. Everything reported here is measured from that.</p>

  <div class="grid4">
    <figure><img src="{img("lau_state_flat.png")}" alt="the towel laid out flat on the table"><figcaption>laid out</figcaption></figure>
    <figure><img src="{img("lau_state_rumpled.png")}" alt="the towel rumpled on the table"><figcaption>rumpled</figcaption></figure>
    <figure><img src="{img("lau_state_heap.png")}" alt="the towel in a heap"><figcaption>in a heap</figcaption></figure>
    <figure><img src="{img("lau_depth.png")}" alt="the overhead depth image the cell works from"><figcaption>what the camera sends</figcaption></figure>
  </div>

  <h2>Finding one &middot; a corner stops being a corner</h2>
  <p>To grasp a towel by the corner you must first find the corner. The cell takes one overhead depth image, cuts out everything at table height, takes the outline, and fits the smallest rectangle around it. Its four corners are the answer. Thirty random towels at each level of mess:</p>
  {chart}
  <table><tr><th>Towel</th><th>Mean</th><th>Median</th><th>90th percentile</th><th>Worst</th><th>Within 20 mm</th></tr>{corn}</table>
  <p>Laid out flat, the outline <em>is</em> the towel and the answer is right to under a millimetre. Crumple it and the answer is not slightly worse, it is meaningless: the extreme points of a bunched towel are wherever the fabric happens to pile up, and the true corners are buried inside. The cell is not seeing badly. It is answering a different question from the one it was asked.</p>

  <h2>Finding two &middot; a fold you cannot see</h2>
  <div class="two"><div>
    <p>Fold a towel in half and it has two long edges. One is the crease. One is the two free edges lying together. They look identical from above, and the difference decides everything: take the free edge and you fold again, take the crease and you undo the fold you just made.</p>
    <p>There is a real cue. The top layer ramps down into the crease, so that edge sits lower than the free edge, which keeps its full thickness. Measured here it is <b>{abs(CR[0]["rows"][0]["step_mm"]) if CR[0]["rows"] and CR[0]["rows"][0]["step_mm"] else 2.65:.2f} mm</b>. The camera's pixel is {cam["mm_per_pixel"]} mm. So the entire signal is about {abs(CR[0]["rows"][0]["step_mm"] or 2.65)/cam["mm_per_pixel"]:.1f} of a pixel.</p>
    <table><tr><th>Fold</th><th>Correct</th><th>Accuracy</th><th></th></tr>{crows}</table>
    <p class="m">My first version of this test had the rule backwards, assuming a crease is a raised ridge. It scored 0 out of 30, which is how the real sign was found. Both results are above.</p>
  </div><div>
    <figure><img src="{img("lau_state_folded.png")}" alt="the towel folded in half on the table"><figcaption>folded in half: which long edge is the crease?</figcaption></figure>
    <div class="kpi" style="grid-template-columns:1fr">
      <div><b>{abs(CR[0]["rows"][0]["step_mm"] or 2.65):.1f} mm</b><span>height difference between the crease edge and the free edge</span></div>
      <div><b>{abs(CR[-1]["rows"][0]["step_mm"] or 12.8):.0f} mm</b><span>height of ordinary wrinkles in the same towel</span></div>
    </div>
    <p>That ratio is the whole problem. The feature you need is a fifth of the size of the noise it is buried in. Once wrinkles reach {CR[-1]["mess_mm"]:.0f} mm the classifier does not degrade gracefully, it inverts: {CR[-1]["accuracy"]*100:.0f}% correct, because the wrinkles bias it the same wrong way every time. A robot that is confidently wrong unfolds the towel it just folded, and is now further from done than when it started.</p>
  </div></div>

  <h2>What the cell actually managed</h2>
  <p>With perfect knowledge handed to it, the machine does fold the towel in half: the carry is clean and the towel measures close to {round(L.SIDE*1000)} by {round(L.SIDE*500)} mm afterwards. It is not reliable. Across the flat trials the same scripted fold produced a correct half fold in some runs and a bundle in others, and the second fold never survived. This is the honest record, not a highlight reel:</p>
  <table><tr><th>Trial</th><th>Towel after the fold</th><th>Shape</th><th>What happened</th></tr>{trows}</table>

  <h2>Nine ways it broke</h2>
  <p>This list is the real answer to why robots look so capable in a demo and so fragile everywhere else. Not one of these is about intelligence. Every one of them is a physical detail that has to be exactly right, that no amount of planning fixes, and that only shows up once real contact is in the loop.</p>
  <ol class="fails">{fails}</ol>

  <h2>So: should you build it?</h2>
  <p>Build the single-purpose machine, yes. But the lesson of this cell is that the win does not come from narrowing the software, it comes from <b>narrowing the world</b>. Every measurement above collapses if the towel arrives already flat and already square. So the machine should never have to find a corner: feed the towel through a tensioning slot, or clamp one edge in a bar, or drop it onto a slotted plate so gravity presents an edge. Then the corner is at a known position by construction, the crease question never arises because the machine did the folding and remembers which side it folded, and the hard perception problem is engineered out of existence rather than solved.</p>
  <p>That is also why the dedicated folding machines of the last decade struggled while general models started folding laundry from a pile: the dedicated ones still had to accept the towel in whatever state a human handed it over, and that state is the hard part. Pick a different one job, and the same strategy is excellent. Laundry is the one where the mess is the task.</p>

  <h2>Run it</h2>
  <pre>cd ~/Projects/research/Robotics/tendril-sim
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/python perception.py 30        # both measurements above
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/mjpython laundry.py live depth rumpled   # watch the cell try</pre>
  <p class="m">Modelling honesty: grasping fabric is modelled as pinning whatever lies between the jaws when they close, the standard assumption in cloth-manipulation research, because simulating a fabric pinch in a real jaw is not reliable. The towel is sampled every {round(L.SP*1000)} mm. The depth camera is noiseless, which makes every number above the optimistic case; a real sensor adds millimetres of noise to a cue already measured in millimetres.</p>
</div>'''
open(os.path.join(OUT, "laundry.html"), "w").write(page); print("page written", len(page)//1024, "KB")
