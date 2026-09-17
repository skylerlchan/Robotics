"""Build the results page from out/results.json and the rendered frames (PNG data URIs)."""
import base64, json, os, datetime
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
R = json.load(open(os.path.join(OUT, "results.json")))
def uri(name):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(OUT, name), "rb").read()).decode()
passed = sum(r["passed"] for r in R)
rows = []
for r in R:
    imgs = "".join(f'<figure><img src="{uri(f)}" alt="{r["name"]}, frame {i+1}"><figcaption>{["start","action","result"][i] if len(r["frames"])==3 else ["start","result"][i]}</figcaption></figure>' for i, f in enumerate(r["frames"]))
    rows.append(f'''<article class="task {"pass" if r["passed"] else "fail"}">
  <header><span class="pill">{"PASS" if r["passed"] else "FAIL"}</span><h3>{r["name"]}</h3><span class="lvl {"beyond" if r["level"]=="beyond-human" else ""}">{r["level"]}</span></header>
  <div class="frames">{imgs}</div>
  <p class="metric"><b>{r["metric"]}</b> <span class="val">{r["value"]:.3g} {r["unit"]}</span></p>
  <p class="note">{r["note"]}</p>
</article>''')
html = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "page_template.html")).read()
html = html.replace("{{TASKS}}", "\n".join(rows)).replace("{{PASSED}}", str(passed)).replace("{{TOTAL}}", str(len(R))).replace("{{DATE}}", datetime.date.today().isoformat())
open(os.path.join(OUT, "tendril-sim.html"), "w").write(html); print("page written", len(html)//1024, "KB")
