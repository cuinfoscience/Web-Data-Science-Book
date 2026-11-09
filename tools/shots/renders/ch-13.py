"""Chapter 13's render: the chart that the chapter's own code draws from Wikipedia's leads.

    python tools/shots/renders/ch-13.py OUTDIR --contact EMAIL [--data-url URL] [--cache DIR]

Runs the code cells of ch-13-ai-apis.qmd that "Embeddings and Retrieval" and
"Retrieval-Augmented Extraction" need, in order, as a reader would: the two
setup cells of "Storing Both Keys", the line that sets MODELS in "One Request,
One JSON Object", and every cell from "Embeddings and Retrieval" to "Tools,
MCP, and Skills". It skips the Datalab and Boulder cells, which cost money and
aren't needed here, so DATALAB_KEY may be unset; OPENROUTER_KEY must be set.
pdfplumber, which the setup cell imports, is replaced by an empty stand-in.

The chapter's User-Agent names `your-email@colorado.edu`; this script puts
EMAIL in its place. --data-url replaces the chapter's address for the saved
Wikipedia data (the `main` branch on GitHub) with another, such as a branch's
raw address before it is merged. The figure the code would show is saved to
OUTDIR, 1600 pixels wide (an 800-pixel frame at scale 2), under the name its
recipe in tools/shots/recipes/ch-13.yml gives:

    lead-similarity.png    each January 1 lead's similarity to the current lead

Requests to Wikipedia wait 2 seconds after the one before, and a 429 waits as
long as its `retry-after` header says. With --cache, successful GET responses
are kept in DIR, so a second run doesn't repeat them (Wikipedia rate-limits).
The cells' printed output goes to standard output, with the key's value
replaced by <KEY>, so it can be pasted into the chapter's comments.

Run it in the webdata environment, then import the chart (tools/shots/README.md,
"Hand captures"), naming the programs that drew it:

    tools/shots/run import ch-13 lead-similarity --file OUTDIR/lead-similarity.png \\
        --by NAME --date YYYY-MM-DD --tool "matplotlib X.Y.Z with requests X.Y.Z"
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import pickle
import re
import sys
import time
import traceback
import types
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

QMD = Path(__file__).resolve().parents[3] / "ch-13-ai-apis.qmd"
NAMES = ["lead-similarity"]
PLACEHOLDER = "your-email@colorado.edu"
DATA = "https://raw.githubusercontent.com/cuinfoscience/Web-Data-Science-Book/main/data/ch-13/wikipedia/"
PAUSE = 2.0

args = argparse.ArgumentParser()
args.add_argument("outdir", type=Path)
args.add_argument("--contact", required=True, help="the email address for the User-Agent")
args.add_argument("--data-url", default=DATA, help="where the saved Wikipedia data is, ending in /")
args.add_argument("--cache", type=Path)
args = args.parse_args()
args.outdir.mkdir(parents=True, exist_ok=True)
if args.cache:
    args.cache.mkdir(parents=True, exist_ok=True)

last = [0.0]
real_request = requests.Session.request


def paced_request(self, method, url, **kw):
    """Every request: GETs cached if asked, Wikipedia's paced, and a 429 waited out."""
    key = None
    if args.cache and method.upper() == "GET":
        params = sorted((kw.get("params") or {}).items())
        key = args.cache / (hashlib.sha1(json.dumps([url, params], default=str).encode()).hexdigest() + ".pkl")
        if key.exists():
            return pickle.loads(key.read_bytes())
    for _ in range(6):
        if "wikipedia.org" in url:
            time.sleep(max(0.0, PAUSE - (time.time() - last[0])))
        response = real_request(self, method, url, **kw)
        if "wikipedia.org" in url:
            last[0] = time.time()
        if response.status_code != 429:
            break
        wait = int(response.headers.get("retry-after", "30"))
        print(f"[429 from {url[:40]}: waiting {wait} s]", file=sys.stderr)
        time.sleep(wait + 1)
    if key and response.status_code == 200:
        key.write_bytes(pickle.dumps(response))
    return response


requests.Session.request = paced_request
sys.modules.setdefault("pdfplumber", types.ModuleType("pdfplumber"))

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
cell = re.compile(r"^```\{python\}\n(.*?)^```", re.M | re.S)
setup = text[text.index("### Storing Both Keys"):text.index("## Document Understanding with Datalab")]
cells = [("### Storing Both Keys", m.group(1)) for m in cell.finditer(setup)]
cells.append(("MODELS", re.search(r"^MODELS = .*$", text, re.M).group(0)))
region = text[text.index("## Embeddings and Retrieval"):text.index("## Tools, MCP, and Skills")]
heading = ""
for m in re.finditer(r"^(#{2,3} [^\n]+)$|^```\{python\}\n(.*?)^```", region, re.M | re.S):
    if m.group(1):
        heading = m.group(1)
    else:
        cells.append((heading, m.group(2)))

key = os.environ.get("OPENROUTER_KEY") or "<no key>"
namespace, failed = {}, False
for heading, code in cells:
    code = code.replace(PLACEHOLDER, args.contact).replace(DATA, args.data_url)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(code, heading, "exec"), namespace)
        status = "ok"
    except Exception:
        status = "ERROR " + traceback.format_exc().strip().splitlines()[-1]
        failed = True
    print(f"===== {heading} :: {status}")
    print(out.getvalue().replace(key, "<KEY>"), end="")

if shown != NAMES:
    print(f"expected {len(NAMES)} figures, saved {shown}", file=sys.stderr)
    failed = True
sys.exit(1 if failed else 0)
