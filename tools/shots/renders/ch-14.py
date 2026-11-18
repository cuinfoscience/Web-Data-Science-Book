"""Chapter 14's render: the chart that the chapter's own code draws from the collected forecasts.

    python tools/shots/renders/ch-14.py OUTDIR --contact EMAIL [--data-url URL] [--collector FILE]

Runs the code cells of ch-14-automation.qmd from "One Request by Hand" to
"Other Places to Run a Schedule", in order, as a reader would, in a new empty
folder under OUTDIR (one cell writes forecasts-test.csv there). Every request
goes to api.weather.gov, which needs no key. The chapter's User-Agent names
`your-email@colorado.edu`; this script puts EMAIL in its place, as the NWS asks.
--data-url replaces the chapter's address for the saved series (data/ch-14/ on
the `main` branch on GitHub) with another: a branch's raw address before it is
merged, or a local file. The figure the code would show is saved to OUTDIR,
1600 pixels wide (an 800-pixel frame at scale 2), under the name its recipe in
tools/shots/recipes/ch-14.yml gives:

    afternoon-forecasts.png    each day's 3 p.m. forecast temperature, by hours ahead

With --collector, it also runs that copy of collector.py twice in a second
empty folder, as "Running It" shows (EMAIL in place of the placeholder), and
prints what each run printed and the file's line count.

The cells' printed output goes to standard output, under a line naming each
cell's section, so that it can be pasted into the chapter's comments. A cell
that ends in an error prints the error's last line; "Stopping Loudly on an
Error" expects one.

Run it in the webdata environment, then import the chart (tools/shots/README.md,
"Hand captures"), naming the programs that drew it:

    tools/shots/run import ch-14 afternoon-forecasts --file OUTDIR/afternoon-forecasts.png \\
        --by NAME --date YYYY-MM-DD --tool "matplotlib X.Y.Z with pandas X.Y.Z and requests X.Y.Z"
"""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

QMD = Path(__file__).resolve().parents[3] / "ch-14-automation.qmd"
NAMES = ["afternoon-forecasts"]
PLACEHOLDER = "your-email@colorado.edu"
DATA = "https://raw.githubusercontent.com/cuinfoscience/Web-Data-Science-Book/main/data/ch-14/forecasts.csv"
# The one cell whose error is the lesson
EXPECTED_ERRORS = {"### Stopping Loudly on an Error"}

args = argparse.ArgumentParser()
args.add_argument("outdir", type=Path)
args.add_argument("--contact", required=True, help="the email address for the User-Agent")
args.add_argument("--data-url", default=DATA, help="where the saved series is: a URL or a local path")
args.add_argument("--collector", type=Path, help="a copy of collector.py to run twice, as 'Running It' does")
args.add_argument("--fill", metavar="HEADING", help="write the outputs into the chapter's cells, from this heading on")
args = args.parse_args()
args.outdir = args.outdir.resolve()
args.outdir.mkdir(parents=True, exist_ok=True)
data = args.data_url if "://" in args.data_url else str(Path(args.data_url).resolve())

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
region = text[text.index("## One Request by Hand"):text.index("## Other Places to Run a Schedule")]
cells, heading = [], ""
for m in re.finditer(r"^(#{2,3} [^\n]+)$|^```\{python\}\n(.*?)^```", region, re.M | re.S):
    if m.group(1):
        heading = m.group(1)
    else:
        cells.append((heading, m.group(2)))

failed = False
work = Path(tempfile.mkdtemp(prefix="cells-", dir=args.outdir))
os.chdir(work)
namespace = {}
results = []
for heading, code in cells:
    code = code.replace(PLACEHOLDER, args.contact).replace(DATA, data)
    out = io.StringIO()
    error = None
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(code, heading, "exec"), namespace)
        status = "ok"
    except Exception:
        error = traceback.format_exc().strip().splitlines()[-1]
        status = "ERROR " + error
        if heading not in EXPECTED_ERRORS:
            failed = True
    print(f"===== {heading} :: {status}")
    print(out.getvalue(), end="")
    results.append(out.getvalue() + (error + "\n" if error else ""))

if args.fill:
    # Write each cell's output into the chapter as its closing comment lines, from the named
    # heading on, replacing the comment lines that already end the cell
    body = QMD.read_text()
    start = body.index("## One Request by Hand")
    spans = [m.span(1) for m in re.finditer(r"^```\{python\}\n(.*?)^```", body[start:], re.M | re.S)]
    spans = [(a + start, b + start) for a, b in spans][:len(cells)]
    begin = body.index(args.fill)
    for (a, b), result in reversed(list(zip(spans, results))):
        if a < begin or not result.strip():
            continue
        lines = body[a:b].rstrip("\n").split("\n")
        while lines and lines[-1].lstrip().startswith("#"):
            lines.pop()
        comments = ["# " + line if line.strip() else "#" for line in result.rstrip("\n").split("\n")]
        body = body[:a] + "\n".join(lines + comments) + "\n" + body[b:]
    QMD.write_text(body)
    print(f"[filled outputs from {args.fill!r} on]", file=sys.stderr)

if args.collector:
    runs = Path(tempfile.mkdtemp(prefix="collector-", dir=args.outdir))
    script = args.collector.read_text().replace(PLACEHOLDER, args.contact)
    (runs / "collector.py").write_text(script)
    print("===== Running It")
    for _ in range(2):
        done = subprocess.run([sys.executable, "collector.py"], cwd=runs, capture_output=True, text=True)
        print(done.stdout + done.stderr, end="")
        failed = failed or done.returncode != 0
    lines = (runs / "forecasts.csv").read_text().count("\n")
    print(f"{lines} forecasts.csv")

if shown != NAMES:
    print(f"expected {len(NAMES)} figures, saved {shown}", file=sys.stderr)
    failed = True
sys.exit(1 if failed else 0)
