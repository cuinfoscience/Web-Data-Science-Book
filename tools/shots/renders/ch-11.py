"""Chapter 11's renders: the charts that the chapter's own code draws from the Census, FRED, EIA, and Congress.gov APIs.

    python tools/shots/renders/ch-11.py OUTDIR --contact EMAIL

Runs the code cells of ch-11-government.qmd, from "API Key Management" to
"Recommended Exercises", in order, as a reader would. It skips the cell that reads
keys from `api_keys.json`, the alternative to environment variables, so the keys
come from CENSUS_KEY, FRED_KEY, EIA_KEY, and DATAGOV_KEY. The chapter's
User-Agent names `your-email@colorado.edu`; this script puts EMAIL in its place.
Each figure the code would show is saved to OUTDIR, 1600 pixels wide (an
800-pixel frame at scale 2), under the name its recipe in
tools/shots/recipes/ch-11.yml gives:

    housing-boulder-longmont.png   housing units by decade built, two cities
    cpi-denver-national.png        annual inflation, Denver area and the nation
    co-generation-mix.png          Colorado's generation by source
    colorado-bills-stages.png      the delegation's bills, by how far each got
    state-electricity-bills.png    homes' electricity bills against income, by state

Every request waits 1 second after the one before. The cells' printed output goes
to standard output, with any key's value replaced by <KEY>, so that the output
can be pasted into the chapter's comments.

Run it in the webdata environment, then import each chart (tools/shots/README.md,
"Hand captures"), naming the programs that drew it:

    tools/shots/run import ch-11 cpi-denver-national --file OUTDIR/cpi-denver-national.png \\
        --by NAME --date YYYY-MM-DD --tool "matplotlib X.Y.Z with requests X.Y.Z"
"""
import argparse
import contextlib
import io
import os
import re
import sys
import time
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

QMD = Path(__file__).resolve().parents[3] / "ch-11-government.qmd"
NAMES = ["housing-boulder-longmont", "cpi-denver-national", "co-generation-mix",
         "colorado-bills-stages", "state-electricity-bills"]
PLACEHOLDER = "your-email@colorado.edu"
KEYS = ["CENSUS_KEY", "FRED_KEY", "EIA_KEY", "DATAGOV_KEY"]
PAUSE = 1.0

args = argparse.ArgumentParser()
args.add_argument("outdir", type=Path)
args.add_argument("--contact", required=True, help="the email address for the User-Agent")
args = args.parse_args()
args.outdir.mkdir(parents=True, exist_ok=True)

missing = [k for k in KEYS if not os.environ.get(k)]
if missing:
    sys.exit(f"not set: {', '.join(missing)}")
secrets = [os.environ[k] for k in KEYS]


def scrub(text):
    """The output with every key's value replaced, so that none reaches the chapter."""
    for secret in secrets:
        text = text.replace(secret, "<KEY>")
    return text


last = [0.0]
real_request = requests.Session.request


def paced_request(self, method, url, **kw):
    """Every request the chapter's code makes, at most one a second."""
    time.sleep(max(0.0, PAUSE - (time.time() - last[0])))
    response = real_request(self, method, url, **kw)
    last[0] = time.time()
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
start = text.index("## API Key Management")
end = text.index("## Recommended Exercises")
region = text[start:end]
namespace, heading, failed = {}, "", False
for m in re.finditer(r"^(#{2,3} [^\n]+)$|^```\{python\}\n(.*?)^```", region, re.M | re.S):
    if m.group(1):
        heading = m.group(1)
        continue
    code = m.group(2)
    if "api_keys.json" in code:
        print(f"===== {heading} :: skipped (api_keys.json)")
        continue
    code = code.replace(PLACEHOLDER, args.contact)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(code, heading, "exec"), namespace)
        status = "ok"
    except Exception:
        status = "ERROR " + scrub(traceback.format_exc().strip().splitlines()[-1])
        failed = True
    print(f"===== {heading} :: {status}")
    print(scrub(out.getvalue()), end="")

if shown != NAMES:
    print(f"expected {len(NAMES)} figures, saved {shown}", file=sys.stderr)
    failed = True
sys.exit(1 if failed else 0)
