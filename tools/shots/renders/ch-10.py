"""Chapter 10's renders: the charts that the chapter's own code draws from Wikipedia's APIs.

    python tools/shots/renders/ch-10.py OUTDIR --contact EMAIL [--cache DIR]

Runs the code cells of ch-10-wikipedia.qmd, from "The Anatomy of an API Call" to
"Recommended Exercises", in order, as a reader would. The chapter's User-Agent
names `your-email@colorado.edu`; this script puts EMAIL in its place, because
Wikimedia's rate limits depend on a real contact. Each figure the code would show
is saved to OUTDIR, 1600 pixels wide (an 800-pixel frame at scale 2), under the
name its recipe in tools/shots/recipes/ch-10.yml gives:

    cu-monthly-edits.png      monthly edits to University of Colorado Boulder
    cu-daily-views.png        its daily pageviews, 2021 to September 2026
    cu-views-by-agent.png     its monthly pageviews by agent, 2024 to September 2026
    cu-boulder-combined.png   monthly views and edits, beside Boulder, Colorado

Every request waits 2 seconds after the one before. A 429 waits as long as its
`retry-after` header says, as the chapter's "Common Issues to Debug" advises; the
limits are shared by everyone on one network address, so a run can take a while.
With --cache, successful GET responses are kept in DIR, so a second run doesn't
repeat them. The cells' printed output goes to standard output.

Run it in the webdata environment, with mwclient installed (`pip install mwclient`),
then import each chart (tools/shots/README.md, "Hand captures"), naming the
programs that drew it:

    tools/shots/run import ch-10 cu-daily-views --file OUTDIR/cu-daily-views.png \\
        --by "Brian C. Keegan" --date YYYY-MM-DD --tool "matplotlib X.Y.Z with requests X.Y.Z"
"""
import argparse
import contextlib
import hashlib
import io
import json
import pickle
import re
import sys
import time
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

QMD = Path(__file__).resolve().parents[3] / "ch-10-wikipedia.qmd"
NAMES = ["cu-monthly-edits", "cu-daily-views", "cu-views-by-agent", "cu-boulder-combined"]
PLACEHOLDER = "your-email@colorado.edu"
PAUSE = 2.0

args = argparse.ArgumentParser()
args.add_argument("outdir", type=Path)
args.add_argument("--contact", required=True, help="the email address for the User-Agent")
args.add_argument("--cache", type=Path)
args = args.parse_args()
args.outdir.mkdir(parents=True, exist_ok=True)
if args.cache:
    args.cache.mkdir(parents=True, exist_ok=True)

last = [0.0]
real_request = requests.Session.request


def paced_request(self, method, url, **kw):
    """Every request, the chapter's and mwclient's: paced, and a 429 waited out."""
    key = None
    if args.cache and method.upper() == "GET":
        params = sorted((kw.get("params") or {}).items())
        key = args.cache / (hashlib.sha1(json.dumps([url, params], default=str).encode()).hexdigest() + ".pkl")
        if key.exists():
            return pickle.loads(key.read_bytes())
    for _ in range(6):
        time.sleep(max(0.0, PAUSE - (time.time() - last[0])))
        response = real_request(self, method, url, **kw)
        last[0] = time.time()
        if response.status_code != 429:
            break
        wait = int(response.headers.get("retry-after", "30"))
        print(f"[429: waiting {wait} s]", file=sys.stderr)
        time.sleep(wait + 1)
    if key and response.status_code == 200:
        key.write_bytes(pickle.dumps(response))
    return response


requests.Session.request = paced_request

shown = []


def save_figures(*_, **__):
    for number in plt.get_fignums():
        name = NAMES[len(shown)]
        plt.figure(number).savefig(args.outdir / f"{name}.png", dpi=200)
        shown.append(name)
        print(f"[saved {name}.png]", file=sys.stderr)
    plt.close("all")


plt.show = save_figures

text = QMD.read_text()
region = text[text.index("## The Anatomy of an API Call"):text.index("## Recommended Exercises")]
namespace, heading, failed = {}, "", False
for m in re.finditer(r"^(#{2,3} [^\n]+)$|^```\{python\}\n(.*?)^```", region, re.M | re.S):
    if m.group(1):
        heading = m.group(1)
        continue
    code = m.group(2).replace(PLACEHOLDER, args.contact)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(code, heading, "exec"), namespace)
        status = "ok"
    except Exception:
        status = "ERROR " + traceback.format_exc().strip().splitlines()[-1]
        failed = True
    print(f"===== {heading} :: {status}")
    print(out.getvalue(), end="")

if shown != NAMES:
    print(f"expected {len(NAMES)} figures, saved {shown}", file=sys.stderr)
    failed = True
sys.exit(1 if failed else 0)
