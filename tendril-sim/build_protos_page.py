"""Prototype lineup page: eight end effectors on identical arms, the same grasp, measured; plus what each buys and costs."""
import base64, json, os, datetime, html
import prototypes as P
OUT = os.path.join(P.HERE, "out"); import glob
R = {}
for f in sorted(glob.glob(os.path.join(OUT, "race*.json")), key=lambda p: (not p.endswith("race.json"), os.path.getmtime(p))):
    for k, v in json.load(open(f)).items(): R[k] = v
R = {h: R[h] for h in P.HANDS if h in R}
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
VERBS = {"2f85": "grasp, place, press, turn a knob, open drawers and doors, insert; not in-hand turning, not two objects, not wrap or cage",
         "suction": "pick anything with a flat clean top, fast and cheap; nothing with texture, holes or a curved top, no turning, no pressing hard",
         "leap": "everything the gripper does plus in-hand reorientation with a learned policy; 16 servos to keep alive",
         "allegro": "same verbs as LEAP at higher stiffness and price; the research standard for in-hand work",
         "shadow": "the most human-like motion, tendon driven; extraordinary cost and upkeep",
         "bloom": "power grasp of anything up to about 90 mm, cradle, cage, press with the closed dome, a camera looking out of the core between the petals; no fine pinch yet, no in-hand turning",
         "fist6": "power grasp, wrap, cradle, cage, six objects at once, zero-power hold; no fine pinch",
         "bundle24": "everything the fist does plus 24 at once and thin reach; the most parts and the look you did not want"}
rows = "".join(f'<tr><td><b>{html.escape(P.HANDS[h]["label"])}</b></td><td class="n">{r["contacts"]}</td><td class="n">{r["force_N"]}</td><td class="n">{r["lift_mm"]}</td><td class="n">{r["slip_mm"]}</td><td><span class="pill {"ok" if r["held"] else "no"}">{"HELD" if r["held"] else "DROPPED"}</span></td><td class="m">{P.HANDS[h]["parts"]}</td><td class="m">{P.HANDS[h]["cost"]}</td></tr>' for h, r in R.items())
cards = "".join(f'<figure><img src="{b64(os.path.join(OUT, f"hero_{h}.png"))}" alt="{P.HANDS[h]["label"]}"><figcaption><b>{html.escape(P.HANDS[h]["label"])}</b><span>{html.escape(VERBS[h])}</span></figcaption></figure>' for h in R)
frames = "".join(f'<figure><img src="{b64(os.path.join(OUT, f"race_{k}.png"))}" alt="{c}"><figcaption>{c}</figcaption></figure>' for k, c in [("0_approach", "approach"), ("1_descend", "descend to grasp height"), ("2_close", "close"), ("3_lift", "lift 150 mm and hold")] if os.path.exists(os.path.join(OUT, f"race_{k}.png")))
held = sum(1 for r in R.values() if r["held"])
BL = R.get("bloom")
bloom_stills = "".join(f'<figure><img src="{b64(os.path.join(OUT, f"bloom_{k}.png"))}" alt="{c}"><figcaption>{c}</figcaption></figure>' for k, c in [("closed", "at rest: closed, 140 mm, nothing hanging"), ("mid", "opening: six petals, two hinges each"), ("open", "open: 180 mm across, ready to drop over an object"), ("open_top", "from below: the camera core looks out between the petals")] if os.path.exists(os.path.join(OUT, f"bloom_{k}.png")))
bloom_row = (f'<p class="meas"><b>Measured on the same bottle grasp as the rest:</b> {BL["contacts"]} bodies touching, {BL["force_N"]:.0f} N grip, {BL["lift_mm"]:.0f} mm lift, {BL["slip_mm"]:.0f} mm slip, <span class="pill {"ok" if BL["held"] else "no"}">{"HELD" if BL["held"] else "DROPPED"}</span>. The bottle hangs upright from the closed petals during the lift.</p>' if BL else "")
NUM = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine"}
page = f'''<title>Prototype Lineup</title>
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
p{{max-width:74ch}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}} figure{{margin:0}} .grid img,.strip img{{display:block;width:100%;height:auto;border:1px solid var(--rule)}}
figcaption{{font-size:13px;margin-top:6px}} figcaption b{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:16px;letter-spacing:.02em;display:block}} figcaption span{{color:var(--ink2)}}
.strip{{display:grid;grid-template-columns:1fr;gap:10px}} .strip figcaption{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}} th{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-size:11px;color:var(--mute);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--rule2)}}
td{{padding:7px 10px 7px 0;border-bottom:1px solid var(--rule);vertical-align:top}} td.n{{font-family:"JetBrains Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;white-space:nowrap}} td.m{{color:var(--mute);font-size:12.5px}}
.meas{{border-left:3px solid var(--teal);padding:6px 12px;background:var(--panel)}} .pill{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.1em;padding:2px 7px;border-radius:2px;color:#fff;background:var(--bad)}} .pill.ok{{background:var(--good)}}
code{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;background:var(--panel);padding:1px 5px;border:1px solid var(--rule);border-radius:2px}}
pre{{background:var(--panel);border:1px solid var(--rule);padding:10px 12px;overflow-x:auto;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px}}
@media (max-width:820px){{.grid{{grid-template-columns:1fr}}}}
</style>
<div class="wrap">
  <header class="bar"><h1>Prototype Lineup</h1><span class="rev">{len(R)} END EFFECTORS · SAME ARM, SAME BOTTLE, SAME SCRIPT · MUJOCO · {datetime.date.today().isoformat()}</span>
  <p class="sub">{NUM[len(R)].capitalize()} ways to end an arm, from a two-finger gripper to a closed orb that opens into petals, mounted on identical UR5e models and run through one grasp: approach, descend, close, lift, hold. Every number is read from the physics. Watch it live with one command.</p></header>
  <h2>New · The Bloom</h2>
  <p>A closed white sphere on the wrist, 140 mm across, nothing dangling. Six petals hinge at the wrist ring, each in two segments, twelve motors in all. It opens like an iris to about 180 mm, drops over an object, and closes around it from every side, so the object ends up inside a shell instead of between fingertips. A dark core at the ring holds the camera and looks out between the petals whenever they are open; the inside of each petal is where the camera-based tactile skin goes. Closed, it is a smooth dome that can press buttons and push things. It is a power grasp, cradle and cage device: no fine pinch and no in-hand turning, and nothing wider than about 90 mm fits. Two moulded shell parts repeated six times, one ring, one core.</p>
  <div class="grid">{bloom_stills}</div>
  {bloom_row}
  <h2>The race · {held} of {len(R)} held the bottle</h2>
  <table><tr><th>Prototype</th><th>Bodies touching</th><th>Grip force N</th><th>Lift mm</th><th>Slip mm</th><th>Result</th><th>Parts</th><th>Cost</th></tr>{rows}</table>
  <p>What the scripted close did to each hand, in one sentence: the gripper needed its target opening matched to the bottle before it stopped crushing and tilting it; the suction cup simply worked; the three human-shaped hands never got the bottle between fingers and palm, because a scripted side approach topples a standing bottle and a scripted curl flicks it, so they need a grasp planner or a learned policy, which is the same conclusion the RoboCasa365 results reach; the fist and the bundle closed on it from all sides and held; the Bloom dropped over it, closed, and lifted it upright.</p><p>The close command is scripted per hand: the gripper closes, the suction turns on, the three anthropomorphic hands curl to a fixed power-grasp pose, the fist and bundle shorten their inward cables, the Bloom folds its petals to the closed shape and lets the bottle stop them. Nothing is learned and nothing is tuned to the bottle beyond a grasp height set from each hand's measured length. A hand that dropped the bottle here is not a bad hand; it is a hand whose scripted close did not suit a 40 mm bottle, which is itself information about how much control each one needs.</p>
  <div class="strip">{frames}</div>
  <h2>The {NUM[len(R)]}, and what each buys</h2>
  <div class="grid">{cards}</div>
  <h2>See it live</h2>
  <pre>cd ~/Projects/research/Robotics/tendril-sim
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/mjpython race.py bloom      # the Bloom alone
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/mjpython race.py            # all of them
/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/mjpython race.py 2f85 leap fist6   # any subset, faster</pre>
  <p>Models: Robotiq 2F-85, LEAP, Allegro and Shadow are the published MuJoCo Menagerie models mounted with an automatically derived rotation; the suction cup, the fist and the bundle are generated by <code>prototypes.py</code>, the Bloom by <code>bloom.py</code>. Everything runs at 0.5 ms steps with the same contact settings.</p>
</div>'''
open(os.path.join(OUT, "prototypes.html"), "w").write(page); print("page written", len(page)//1024, "KB")
