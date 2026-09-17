"""Build the pick-and-place page: embedded MP4, key frames and measured metrics."""
import base64, json, os, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "out")
M = json.load(open(os.path.join(OUT, "pick_metrics.json")))
b64 = lambda p, mime: f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
video = b64(os.path.join(OUT, "pick.mp4"), "video/mp4")
frames = [("approach", "Open bundle brought over the bottle"), ("descend", "Descends until the bottle sits inside the inner ring"), ("grasp", "All three rings close until the bottle feels 8 N, then every tendril jams"),
          ("lift", "Lift 180 mm"), ("carry", "Carry 300 mm sideways"), ("release", "Unjam, straighten, let go"), ("done", "Retreat")]
figs = "".join(f'<figure><img src="{b64(os.path.join(OUT, f"pick_{i}_{k}.png"), "image/png")}" alt="{c}"><figcaption>{i+1} · {c}</figcaption></figure>' for i, (k, c) in enumerate(frames))
held = M["bottle_lift_mm"] > 150 and M["slip_during_carry_mm"] < 15 and M["place_error_mm"] < 40 and M["bottle_upright"]
rows = [("Tendrils touching the bottle at grasp", M["tendrils_in_contact"], "of 24"), ("Total normal force on the bottle", M["grasp_normal_force_N"], "N"), ("Closing angle commanded", M["close_angle_deg"], "deg"),
        ("Bottle lift", M["bottle_lift_mm"], "mm, commanded 180"), ("Slip during the 300 mm carry", M["slip_during_carry_mm"], "mm"), ("Place error from the target", M["place_error_mm"], "mm"),
        ("Bottle upright after release", "yes" if M["bottle_upright"] else "no", ""), ("Simulated time", M["sim_seconds"], "s"), ("Wall-clock time on the M4 Pro", M["wall_seconds"], "s")]
table = "".join(f"<tr><td>{k}</td><td class='n'>{v}</td><td class='m'>{u}</td></tr>" for k, v, u in rows)
html = f'''<title>Pick and Place Sim</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#ECEEF1;--panel:#F5F6F8;--ink:#1A1F26;--ink2:#4B535E;--mute:#79818D;--rule:#C9CED6;--rule2:#AEB5BF;--teal:#1E9E93;--amber:#D9922A;--blue:#3E6FE0;--good:#1E9E93;--bad:#B23A2E}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}}}
:root[data-theme="dark"]{{--bg:#14171C;--panel:#1A1E24;--ink:#E6E9EE;--ink2:#B4BAC4;--mute:#7E8794;--rule:#2A303A;--rule2:#3A4250;--teal:#3FBFB3;--amber:#F0A93A;--blue:#6D93F5;--good:#3FBFB3;--bad:#E06A5E}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Barlow,"Helvetica Neue",Arial,sans-serif;font-size:15px;line-height:1.5}}
.wrap{{max-width:1040px;margin:0 auto;padding:0 20px 40px}}
.bar{{display:flex;align-items:baseline;gap:10px 24px;flex-wrap:wrap;padding-block:18px 12px;border-bottom:1px solid var(--rule)}}
h1{{font-family:"Barlow Condensed",Barlow,sans-serif;font-weight:600;font-size:30px;letter-spacing:.03em;text-transform:uppercase;margin:0;line-height:1}}
.rev{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:11px;color:var(--mute);letter-spacing:.06em}} .sub{{color:var(--ink2);flex:1 1 320px;max-width:64ch;margin:0}}
h2{{font-family:"Barlow Condensed",Barlow,sans-serif;font-size:14px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--rule)}}
p{{max-width:72ch}}
video{{display:block;width:100%;max-width:960px;height:auto;border:1px solid var(--rule);background:#000;margin-top:14px}}
.verdict{{display:inline-block;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;letter-spacing:.1em;padding:3px 9px;border-radius:2px;color:#fff;background:{"var(--good)" if held else "var(--bad)"};margin-top:12px}}
.frames{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}} figure{{margin:0}} .frames img{{display:block;width:100%;height:auto;border:1px solid var(--rule)}}
figcaption{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-top:4px}}
table{{width:100%;max-width:720px;border-collapse:collapse;font-size:13.5px}} td{{padding:7px 10px 7px 0;border-bottom:1px solid var(--rule);vertical-align:top}}
td.n{{font-family:"JetBrains Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;white-space:nowrap}} td.m{{color:var(--mute)}}
code{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;background:var(--panel);padding:1px 5px;border:1px solid var(--rule);border-radius:2px}}
@media (max-width:820px){{.frames{{grid-template-columns:1fr 1fr}}}}
</style>
<div class="wrap">
  <header class="bar"><h1>Pick and Place Sim</h1><span class="rev">REV E ON A UR5E · MUJOCO 3.13 · {datetime.date.today().isoformat()} · FULL SCALE, 24 TENDRILS</span>
  <p class="sub">The full-size bundle mounted on a UR5e model from MuJoCo Menagerie grabs a bottle, lifts it, carries it, and sets it down. Scripted control, measured outcome, rendered from the physics, not drawn.</p></header>
  <video controls playsinline preload="metadata" src="{video}"></video>
  <div class="verdict">{"HELD, CARRIED AND PLACED" if held else "DID NOT COMPLETE"}</div>
  <h2>What happens</h2>
  <p>The arm brings the bundle over a 40 mm bottle with all twenty-four tendrils straight, and descends so the bottle sits inside the inner ring. Then every ring bends inward toward the bottle until the contact sensors report eight newtons, the sleeves jam, and the arm lifts, carries the bottle 300 mm sideways, lowers it onto the target, unjams, straightens the tendrils and retreats. The arm is driven by a damped least-squares inverse kinematics loop on the bundle's base, the tendrils by the same cable-length control as the bench simulation.</p>
  <div class="frames">{figs}</div>
  <h2>Measured</h2>
  <table>{table}</table>
  <h2>Honest notes</h2>
  <p>The skin is the Rev F look: ivory sleeves, no visible cables, a warm grey palm with a teal ring. Tendrils do not collide with each other in this run, which is a simplification that keeps the step fast; bench tests will say whether neighbours rub. The bottle is rigid and dry, friction 0.9. The grasp is a whole-bundle squeeze, not a fingertip pinch, which is the natural grasp for this morphology and the one that showed the most force with the least precision needed. Code: <code>tendril-sim/pick_demo.py</code>, scene built into the Menagerie folder as <code>pick_scene.xml</code>.</p>
</div>'''
open(os.path.join(OUT, "pick-place.html"), "w").write(html); print("page written", len(html)//1024, "KB")
