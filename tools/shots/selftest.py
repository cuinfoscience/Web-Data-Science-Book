#!/usr/bin/env python3
"""Offline test of the guards, retries, and promote, against a local web server.

    tools/shots/run selftest

Needs the browser (bootstrap.sh) but no network: every page comes from a
server on 127.0.0.1, which Chrome reaches directly. Everything is written to a
temporary folder; the repository is not touched.
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import devtools as dt                   # noqa: E402  (to read a take's DevTools state)
from lib.headed import BARS, BARS_SLACK          # noqa: E402
from lib import robots                            # noqa: E402

PAGES = {
    "/ok": (200, "<title>Selftest</title><h1>Hello from the selftest</h1>"
                 + "<p>" + "A page with enough on it to photograph. " * 40 + "</p>"),
    "/gateway": (502, "<title>502 Bad Gateway</title><h1>Bad Gateway</h1>"),
    "/wayback": (200, "<title>Wayback Machine</title><p>Hrm.</p><p>Fail with status: 502 Bad Gateway</p>"),
    "/blocked": (403, "<title>Access denied</title><h1>Access denied</h1><p>You have been blocked.</p>"),
    "/blank": (200, "<title>Blank</title><body style='background:#fff'></body>"),
    "/tree": (200, "<!DOCTYPE html>\n<html>\n<head><title>Tree</title></head>\n<body>\n"
                   "<div id=\"outer\">\n  <section id=\"middle\">\n    <h1 id=\"target\">Inspect me</h1>\n"
                   "  </section>\n</div>\n<p>" + "Something to look at. " * 60 + "</p>\n</body>\n</html>\n"),
    # Elements at known places, for anchors and markers (all in CSS pixels).
    "/marks": (200, "<!DOCTYPE html><title>Marks</title><style>body{margin:0;font-family:sans-serif}"
                    "div,h1,p{position:absolute;margin:0}</style>"
                    "<h1 id='title' style='left:40px;top:30px;font-size:32px;line-height:40px'>Title here</h1>"
                    "<p style='left:40px;top:120px;width:400px;font-size:16px'>"
                    + "Words to measure, enough of them to count. " * 12 + "</p>"
                    "<div id='box' style='left:500px;top:120px;width:120px;height:80px;background:#ddd'>Box</div>"
                    "<div id='tall' style='left:680px;top:260px;width:60px;height:700px;background:#eef'></div>"),
    # Small text, as week-08's dropped infinite_scroll.png had: DevTools' 11 pixels at 100%.
    "/small": (200, "<!DOCTYPE html><title>Small</title><body style='margin:8px;font:11px sans-serif'>"
                    + "<p>quotes?page=2 {has_next: true, page: 2, quotes: [...]}</p>" * 30),
}
PAGES["/ua"] = PAGES["/ok"]
PAGES["/cookie"] = (200, "<title>Cookie</title><h1>A page that sets a cookie</h1>"
                         + "<p>" + "Something to look at. " * 40 + "</p>")
# A plain-text file as Chrome shows one: all of it in one <pre>, one text node.
PAGES["/plain"] = (200, "<!DOCTYPE html><title>Plain</title><body style='margin:0'>"
                        "<pre style='margin:0;font:16px monospace;line-height:20px'>"
                        + "\n".join(f"line {n}" for n in range(1, 121)) + "</pre>")
FLAKY = {"count": 0}      # /flaky works once, then answers 502
SEEN = {}                 # path: the headers of each request for it, in order
# What Chrome's User-Agent Client Hints should say on this machine.
PLATFORM = {"linux": '"Linux"', "darwin": '"macOS"', "win32": '"Windows"'}.get(sys.platform)


def sections(output):
    """A `capture` run's output, split by figure: {figure id: its lines}."""
    found, current = {}, None
    for text in output.splitlines():
        if text.startswith("ch-99/"):
            current = text.split("/", 1)[1].strip()
            found[current] = ""
        elif current:
            found[current] += text + "\n"
    return found


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        SEEN.setdefault(self.path, []).append({k.lower(): v for k, v in self.headers.items()})
        if self.path == "/flaky":
            FLAKY["count"] += 1
            status, body = PAGES["/ok"] if FLAKY["count"] == 1 else PAGES["/gateway"]
        else:
            status, body = PAGES.get(self.path, (404, "<title>Not found</title>"))
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if self.path == "/cookie":
            self.send_header("Set-Cookie", "visit=1; Path=/")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    tmp = Path(tempfile.mkdtemp(prefix="shots-selftest-"))
    for sub in ("recipes", "out", "images/ch-99"):
        (tmp / sub).mkdir(parents=True)
    (tmp / "recipes" / "ch-99.yml").write_text(f"""
chapter: ch-99
qmd: none.qmd
defaults: {{window: [800, 600], scale: 1, pause: [0, 0], settle: 0.2, timeout: 10, retries: 1}}
figures:
  - {{id: ok, kind: capture, url: "{base}/ok", expect: {{text: ["Hello from the selftest"]}}}}
  - {{id: gateway, kind: capture, url: "{base}/gateway"}}
  - {{id: wayback, kind: capture, url: "{base}/wayback"}}
  - {{id: blocked, kind: capture, url: "{base}/blocked"}}
  - {{id: refusal, kind: capture, url: "{base}/blocked", expect: {{status: 403, block: true}}}}
  - {{id: blank, kind: capture, url: "{base}/blank"}}
  - {{id: missing-text, kind: capture, url: "{base}/ok", expect: {{text: ["Not on the page"]}}}}
  - {{id: flaky, kind: capture, url: "{base}/flaky", retries: 0}}
  - {{id: ua, kind: capture, url: "{base}/ua"}}
  - id: headed-inspect
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    devtools: {{dock: right}}
    steps:
      - inspect: {{selector: '#target', selects: '^<h1'}}
      - tree: {{keys: [Left], until: '^<section', max: 6}}
    expect: {{text: ['Inspect me']}}
  - id: headed-network
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    devtools: {{dock: right, panel: network}}
    steps:
      - devtools_click: {{text: '^tree$'}}
      - devtools_wait: {{text: '^Headers$'}}
  - id: headed-second-visit
    kind: capture
    url: "{base}/cookie"
    mode: headed
    window: [900, 700]
    devtools: {{dock: bottom, size: 300, panel: network}}
    steps: [{{devtools_wait: {{text: '^cookie$'}}}}]
  - id: headed-first-visit
    kind: capture
    url: "{base}/cookie"
    mode: headed
    window: [900, 700]
    devtools: {{dock: bottom, size: 300, panel: network, first_visit: true}}
    steps:
      - devtools_click: {{text: '^cookie$'}}
      - devtools_wait: {{text: '^Headers$'}}
    crop: {{devtools: true}}
  # Each DevTools setting, read back from what DevTools drew.
  - id: headed-stacked
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 700]
    devtools: {{dock: bottom, size: 400, zoom: 1.25, layout: stacked, sidebar: 120}}
    steps: [{{inspect: {{selector: '#target', selects: '^<h1'}}}}]
  - id: headed-beside
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    devtools: {{dock: right, size: 450, layout: side-by-side, sidebar: 200}}
  - id: headed-left-hidden
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    devtools: {{dock: left, size: 380, sidebar: hidden}}
  - id: headed-columns
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 700]
    devtools: {{dock: bottom, size: 400, panel: network, overview: false, columns: {{waterfall: true, initiator: false}}}}
    steps: [{{devtools_wait: {{text: '^tree$'}}}}]
  - id: headed-too-tall
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 700]
    devtools: {{dock: bottom, size: 650}}
  - id: headed-expects-infobar
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    expect: {{infobar: true}}
  - id: headed-source
    kind: capture
    url: "view-source:{base}/tree"
    mode: headed
    window: [900, 600]
    steps:
      - wait: {{text: 'Inspect me'}}
    crop: {{between: ['body', 'td.line-number[value="7"]']}}
  - id: marks
    kind: capture
    url: "{base}/marks"
    steps: [{{wait: {{text: '(?i)^TITLE HERE$'}}}}]
    annotate:
      width_in: 4
      marks:
        - {{n: 1, at: {{selector: '#title', box: text}}}}
        - {{n: 2, shape: brace, at: {{selector: '#box'}}}}
        - {{n: 3, shape: bracket, at: {{selector: '#tall'}}, x: -4}}
        - {{label: 'by hand', at: {{xy: [100, 500]}}}}
  - id: marks-2x
    kind: capture
    url: "{base}/marks"
    scale: 2
    annotate: {{marks: [{{n: 1, at: {{selector: '#box'}}}}]}}
  - id: small-text
    kind: capture
    url: "{base}/small"
    window: [555, 400]
    targets: {{slides: {{width: 0.35}}}}
  - id: plain-lines
    kind: capture
    url: "{base}/plain"
    steps: [{{scroll: {{match: '^line 60$', in: 'pre', offset: 100}}}}]
    annotate:
      marks:
        - {{n: 1, at: {{match: '^line 60$', in: 'pre'}}}}
        - {{n: 2, at: {{match: '^line 61\\nline 62$', in: 'pre'}}}}
  - {{id: wide, kind: capture, url: "{base}/ok", window: [1000, 500]}}
  - {{id: wide-allowed, kind: capture, url: "{base}/ok", window: [1000, 500], oversize: "a test of the reason"}}
  - {{id: wide-small, kind: capture, url: "{base}/small", window: [1000, 500], oversize: "a test of the reason"}}
  - {{id: too-wide, kind: capture, url: "{base}/ok", window: [1100, 500]}}
  - id: joined
    kind: capture
    url: "{base}/ok"
    mode: composite
    window: [400, 300]
    parts: [{{label: One}}, {{label: Two, javascript: false}}]
    layout: {{gap: 10, pad: 5, label_px: 20}}
  - id: headed-marks
    kind: capture
    url: "{base}/tree"
    mode: headed
    window: [900, 600]
    devtools: {{dock: right}}
    steps: [{{inspect: {{selector: '#target', selects: '^<h1'}}}}]
    annotate:
      marks:
        - {{n: 1, at: {{devtools: {{row: '^<section'}}}}, side: left, x: 20}}
        - {{label: '← picked', at: {{devtools: {{selected: true}}}}, x: -4}}
        - {{n: 2, at: {{selector: '#target', box: text}}}}
""")
    env = dict(os.environ, SHOTS_RECIPES=str(tmp / "recipes"), SHOTS_OUT=str(tmp / "out"),
               SHOTS_IMAGES=str(tmp / "images"), SHOTS_BACKOFF="0,0,0")

    def shots(*args):
        run = subprocess.run([sys.executable, str(HERE / "shots.py"), *args], env=env,
                             capture_output=True, text=True, timeout=600)
        return run.returncode, run.stdout + run.stderr

    def newest(fid):
        logs = sorted((tmp / "out" / "ch-99" / fid).glob("*.json"), reverse=True)
        return json.loads(logs[0].read_text()) if logs else {}

    results = []

    def expect(name, condition, detail=""):
        condition = bool(condition)
        results.append(condition)
        print(f"  {'ok' if condition else 'FAIL':4}  {name}" + (f"  ({detail})" if detail and not condition else ""))

    print("capture")
    code, out = shots("capture", "ch-99", "--only", "ok", "gateway", "wayback", "blocked",
                      "refusal", "blank", "missing-text")
    expect("a run with failures exits non-zero", code == 1, out[-400:])
    expect("a normal page passes", newest("ok").get("ok") is True, str(newest("ok").get("problems")))
    gateway_dir = tmp / "out" / "ch-99" / "gateway"
    expect("a 502 is retried and then fails with no take",
           not list(gateway_dir.glob("*.png")) and "no usable take after 2 attempt(s)" in out, out[-600:])
    wb = newest("wayback")
    expect("a 200 page that says 'Fail with status' fails", wb.get("ok") is False
           and "Wayback Machine error" in " ".join(wb.get("problems", [])), str(wb.get("problems")))
    expect("...and was retried", len(wb.get("attempts", [])) == 2, str(wb.get("attempts")))
    bl = newest("blocked")
    expect("a 403 block page fails", bl.get("ok") is False and "HTTP status 403" in " ".join(bl.get("problems", [])))
    expect("...and is not retried", len(bl.get("attempts", [])) == 1)
    expect("a block page passes when the recipe expects one", newest("refusal").get("ok") is True,
           str(newest("refusal").get("problems")))
    expect("a blank page fails", "nearly blank" in " ".join(newest("blank").get("problems", [])))
    expect("missing expected text fails", "not found" in " ".join(newest("missing-text").get("problems", [])))
    expect("failed takes are named .FAILED.png", bl.get("image", "").endswith(".FAILED.png"))
    code, out = shots("capture", "ch-99", "--only", "ua")
    sent = (SEEN.get("/ua") or [{}])[-1]
    expect("requests carry the one User-Agent, and Client Hints that name this machine's system",
           sent.get("user-agent") == "Web Data Science/v1 brian.keegan@colorado.edu"
           and sent.get("sec-ch-ua-platform") == PLATFORM, str(sent))

    print("robots.txt")
    rules = ("User-agent: *\nDisallow: /private/\n\n"
             "User-agent: ClaudeBot\nUser-agent: Claude-User\nDisallow: /\n")
    agent = "Web Data Science/v1 brian.keegan@colorado.edu"
    found = robots.barred(rules, agent, "https://example.org/news/")
    expect("doctor reads a group for Claude's agents, though the capture's User-Agent falls under *",
           found == ["Claude-User", "ClaudeBot"], str(found))
    found = robots.barred(rules, agent, "https://example.org/private/page")
    expect("...and the capture's own User-Agent first; agents with no group of their own fall under *",
           found[:1] == [agent] and len(found) == 1 + len(robots.CLAUDE_AGENTS), str(found))

    print("promote")
    code, out = shots("capture", "ch-99", "--only", "flaky")
    expect("flaky: first capture passes", code == 0, out[-300:])
    code, out = shots("promote", "ch-99", "flaky")
    approved = tmp / "images" / "ch-99" / "flaky.png"
    expect("promote copies a passing take into images/", code == 0 and approved.exists(), out[-300:])
    before = approved.read_bytes()
    prov = json.loads((tmp / "images" / "ch-99" / "provenance.json").read_text())
    expect("promote records provenance", prov["figures"]["flaky"]["by"] == "tools/shots")
    expect("promote writes the IMAGES.md table",
           "shots:begin" in (tmp / "images" / "ch-99" / "IMAGES.md").read_text())
    code, out = shots("capture", "ch-99", "--only", "flaky")
    expect("flaky: a later 502 fails", code == 1, out[-300:])
    expect("...and leaves the approved image untouched", approved.read_bytes() == before)
    bad_take = newest("blocked")
    code, out = shots("promote", "ch-99", "blocked", "--take", str(Path(bad_take["image"])))
    expect("promote refuses a failed take", code == 1 and "refusing" in out, out[-300:])
    code, out = shots("check", "ch-99")
    expect("check finds the promoted image's provenance consistent", "has no provenance" not in out
           and "changed after" not in out, out[-400:])
    approved.write_bytes(before + b"tampered")
    code, out = shots("check", "ch-99")
    expect("check notices an image replaced by hand", code == 1 and "changed after" in out, out[-300:])

    print("anchors, markers, legibility, composites")
    code, out = captured = shots("capture", "ch-99", "--only", "marks", "marks-2x", "small-text", "joined",
                                 "wide", "wide-allowed", "wide-small", "too-wide")
    marks, marks2, small, joined = newest("marks"), newest("marks-2x"), newest("small-text"), newest("joined")
    said = sections(out)
    expect("a figure over 800x600 but within 1024x768 gets a warning that asks what clutter the room removes",
           "warn  shows 1000×500 CSS pixels, over 800×600 but within the relaxed 1024×768 limit; the book's column "
           "shows its text at 78% of its size on screen; allowed when the extra room removes clutter"
           in said.get("wide", "") and newest("wide").get("ok") is True, said.get("wide"))
    expect("...which a reason in its recipe allows, when its text passes (the relaxed limit)",
           "note  shows 1000×500" in said.get("wide-allowed", "")
           and "allowed: a test of the reason" in said.get("wide-allowed", ""), said.get("wide-allowed"))
    expect("...but not when its text is too small where it is shown, reason or not",
           "warn  shows 1000×500" in said.get("wide-small", "") and "but its text is too small (book"
           in said.get("wide-small", "") and "allowed:" not in said.get("wide-small", ""), said.get("wide-small"))
    expect("a figure beyond 1024x768 without a reason gets a warning",
           "warn  shows 1100×500 CSS pixels, over the relaxed 1024×768 limit" in said.get("too-wide", ""),
           said.get("too-wide"))
    expect("...and an 800x600 figure is within the limit", "marks" in said and "CSS pixels, over" not in said["marks"],
           said.get("marks"))

    def anchor(take, at):
        return ((take.get("anchors") or {}).get(json.dumps(at, sort_keys=True, separators=(",", ":"))) or {}).get("box")

    expect("a (?i) pattern works in a step (JavaScript has no inline flags)", marks.get("ok") is True,
           str(marks.get("problems")) + out[-300:])
    box = anchor(marks, {"selector": "#box"})
    expect("an anchor is recorded at capture, in the take's pixels", box == [500, 120, 620, 200], str(box))
    box2 = anchor(marks2, {"selector": "#box"})
    expect("...at scale 2 as well", box2 == [1000, 240, 1240, 400], str(box2))
    title = anchor(marks, {"selector": "#title", "box": "text"}) or [0, 0, 0, 0]
    expect("a text anchor is the text's own box, not the element's", 39 <= title[0] <= 41
           and title[2] < 300 and 28 <= title[1] and title[3] <= 72, str(title))
    expect("the take records its text sizes", (marks.get("text") or {}).get("median") == 16.0, str(marks.get("text")))
    code, out = shots("capture", "ch-99", "--only", "plain-lines")
    plain = newest("plain-lines")
    one = anchor(plain, {"match": "^line 60$", "in": "pre"}) or [0, 0, 0, 0]
    two = anchor(plain, {"match": "^line 61\\nline 62$", "in": "pre"}) or [0, 0, 0, 0]
    expect("a scroll step with `match` puts a line of a plain-text file at its offset",
           abs(one[1] - 100) <= 1, str(one) + out[-300:])
    expect("...and a `match` anchor is the matched lines' box, across line breaks",
           two[1] >= one[3] - 1 and 30 <= two[3] - two[1] <= 45 and two[2] - two[0] < 200, str(two))
    tex_tools = all(shutil.which(t) for t in ("pdflatex", "pdftocairo"))
    if tex_tools:
        stem = tmp / "out" / "ch-99" / "marks" / (Path(marks.get("image", "x.png")).name.removesuffix(".png") + ".annotated")
        drawn = Path(f"{stem}.pdf").exists() and Path(f"{stem}.png").exists() and Path(f"{stem}.json").exists()
        expect("markers are drawn to a PDF and a PNG beside the take", drawn, out[-400:])
        record = json.loads(Path(f"{stem}.json").read_text()) if drawn else {"marks": [], "warnings": [], "marker_px": 0}
        m, d = {r["mark"]: r for r in record["marks"]}, record["marker_px"]
        one = m.get(1, {}).get("center", [0, 0])
        expect("a marker sits beside its anchor, centered on it, `gap` pixels away",
               abs(one[0] - (title[2] + 4 + d / 2)) < 0.6 and abs(one[1] - (title[1] + title[3]) / 2) < 0.6,
               f"{one} vs text box {title}, marker {d}")
        expect("a brace spans its anchor, just past its side", m.get(2, {}).get("span") == [120, 200]
               and m.get(2, {}).get("line") == 624, str(m.get(2)))
        tex = Path(f"{stem}.tex").read_text() if drawn else ""
        expect("a bracket on something that runs past the picture's edge ends in an arrow",
               "-latex" in tex and m.get(3, {}).get("span", [0, 0])[1] > 600, str(m.get(3)))
        expect("a mark placed by hand (xy) is flagged", any("by hand" in w for w in record["warnings"]),
               str(record["warnings"]))
        with Image.open(f"{stem}.png") as img:
            expect("the PNG keeps the take's pixel size: 4 inches at one pixel per screenshot pixel",
                   abs(img.width - 4 * record.get("dpi", 0)) < 3 and img.width >= 800, f"{img.size} {record.get('dpi')}")
            left, top = (record.get("frame") or [0, 0])[:2]
            with Image.open(str(stem).removesuffix(".annotated") + ".png") as shot:   # the take, beside it
                region = (40, 120, 440, 300)             # the paragraph, where no mark is drawn
                moved = (region[0] - left, region[1] - top, region[2] - left, region[3] - top)
                same = ImageChops.difference(shot.convert("RGB").crop(region),
                                             img.convert("RGB").crop(moved)).getbbox() is None
            expect("...and its screenshot pixels unchanged, not resampled", same, f"frame {record.get('frame')}")
        code, out = shots("annotate", "ch-99", "marks")
        expect("annotate redraws markers from a take without capturing again", code == 0, out[-300:])
    else:
        print("  skip  marker drawing: pdflatex or pdftocairo missing (bash tools/shots/bootstrap.sh --tex)")
    expect("legibility: 11-pixel text in a 555-pixel crop on 35% of a slide is too small (week-08's case)",
           "slides 11.7 px (under 16)" in captured[1] and (small.get("text") or {}).get("p20") == 11.0,
           str(small.get("text")) + captured[1][-300:])
    expect("a composite joins its parts side by side, labeled", joined.get("ok") is True
           and joined.get("size") == [820, 340] and len(joined.get("parts") or []) == 2
           and joined["parts"][1]["javascript"] is False, str({k: joined.get(k) for k in ("ok", "size", "problems")}))

    print("promote and check, with markers and text sizes")
    code, out = shots("promote", "ch-99", "small-text")
    code, out = shots("promote", "ch-99", "wide")
    code, out = shots("promote", "ch-99", "wide-allowed")
    code, out = shots("check", "ch-99")
    expect("check fails a promoted image whose text is too small to read",
           code == 1 and "text too small to read: slides 11.7 px" in out, out[-400:])
    expect("check warns about an approved image over 800x600 whose recipe gives no reason",
           "warn  wide: shows 1000×500 CSS pixels, over 800×600 but within the relaxed 1024×768 limit" in out,
           out[-600:])
    expect("...and notes one within 1024x768 with a reason and legible text",
           "note  wide-allowed: shows 1000×500" in out and "allowed: a test of the reason" in out, out[-600:])
    if tex_tools:
        code, out = shots("promote", "ch-99", "marks")
        annotated = tmp / "images" / "ch-99" / "marks_annotated.png"
        expect("promote copies the annotated PNG and PDF", code == 0 and annotated.exists()
               and annotated.with_suffix(".pdf").exists(), out[-300:])
        code, out = shots("check", "ch-99")
        expect("check accepts the annotated files it recorded", "marks_annotated" not in out, out[-400:])
        annotated.write_bytes(annotated.read_bytes() + b"x")
        code, out = shots("check", "ch-99")
        expect("check notices an annotated image changed by hand", "marks_annotated.png changed" in out, out[-300:])
    code, out = shots("sheet", "ch-99")
    expect("sheet draws each newest take at the size it will be shown",
           code == 0 and (tmp / "out" / "ch-99" / "sheet-1.png").exists(), out[-300:])

    print("headed (virtual display, real input, DevTools)")
    if all(shutil.which(tool) for tool in ("Xvfb", "xdotool", "import")):
        code, out = shots("capture", "ch-99", "--only", "headed-inspect", "headed-network", "headed-source")
        inspect_take, network_take, source_take = newest("headed-inspect"), newest("headed-network"), newest("headed-source")
        expect("Inspect (DevTools' element picker) selects the element; the tree climbs by keyboard",
               inspect_take.get("ok") is True, str(inspect_take.get("problems")) + out[-300:])
        expect("the whole window is grabbed at its size", inspect_take.get("size") == [900, 600],
               str(inspect_take.get("size")))
        expect("DevTools opens the Network panel and a request is found and clicked by its text",
               network_take.get("ok") is True, str(network_take.get("problems")) + out[-300:])
        expect("View Source is cropped from the page top through a given line",
               source_take.get("ok") is True and 0 < source_take.get("size", [0, 0])[1] < 600,
               str(source_take.get("problems")) + str(source_take.get("size")))
        code, out = shots("capture", "ch-99", "--only", "headed-second-visit")
        second = SEEN.get("/cookie", [])
        expect("the Network panel's reload is a second visit: it sends the cookie the first load got",
               len(second) >= 2 and "visit=1" in second[-1].get("cookie", ""), str(second))
        expect("...and a headed browser's Client Hints name this machine's system too",
               second and second[-1].get("sec-ch-ua-platform") == PLATFORM, str(second[-1:]))
        SEEN.pop("/cookie", None)
        code, out = shots("capture", "ch-99", "--only", "headed-first-visit")
        first, take = SEEN.get("/cookie", []), newest("headed-first-visit")
        expect("with first_visit, the reload sends no cookie", take.get("ok") is True and len(first) >= 2
               and "cookie" not in first[-1], str(take.get("problems")) + str(first) + out[-300:])
        expect("crop: {devtools: true} is the docked DevTools pane alone",
               (take.get("size") or [0, 0])[0] == 900 and abs((take.get("size") or [0, 0])[1] - 300) <= 2,
               str(take.get("size")))
        code, out = shots("capture", "ch-99", "--only", "headed-marks")
        take = newest("headed-marks")
        row = anchor(take, {"devtools": {"row": "^<section"}})
        chosen = anchor(take, {"devtools": {"selected": True}})
        heading = anchor(take, {"selector": "#target", "box": "text"})
        expect("anchors in DevTools (a tree row, the selected row) and on the page are measured in one take",
               take.get("ok") is True and row and chosen and heading, str(take.get("problems")) + out[-300:])
        expect("...each where it is drawn: the rows in DevTools, right of the page's heading",
               bool(row and chosen and heading) and row[0] > heading[2] and chosen[0] > heading[2]
               and chosen[1] > row[1], f"row {row}, selected {chosen}, heading {heading}")
        expect("DevTools' own text is counted too, at its size (11 pixels at 100%)",
               "11" in ((take.get("text") or {}).get("sizes") or {}), str(take.get("text")))

        # Every setting the toolkit writes for DevTools, read back from what DevTools drew.
        print("  DevTools settings, read back")
        bars = inspect_take.get("bars") or 0
        expect("no infobar above the page: the bars are the tab strip and address bar alone "
               "(Chrome for Testing's notice is off)", 0 < bars <= BARS + BARS_SLACK, str(bars))
        code, out = shots("capture", "ch-99", "--only", "headed-stacked", "headed-beside", "headed-left-hidden",
                          "headed-columns", "headed-too-tall", "headed-expects-infobar")
        said = sections(out)

        def seen(fid):
            take = newest(fid)
            return take, dt.layout(take["devtools_seen"], take["scale"]) if take.get("devtools_seen") else {}

        take, got = seen("headed-stacked")
        styles = got.get("styles") or {}
        expect("zoom: DevTools is drawn at 125%", got.get("zoom") == 1.25, str(got))
        expect("dock and size: docked at the bottom, 400 pixels tall",
               got.get("dock") == "bottom" and abs((got.get("pane") or 0) - 400) <= 2, str(got))
        expect("layout and sidebar: the Styles pane under the tree, 120 pixels tall",
               styles.get("layout") == "stacked" and abs(styles.get("size", 0) - 120) <= 2, str(styles))
        expect("the \"What's new\" panel stays shut (releaseNoteVersionSeen)",
               (take.get("devtools_seen") or {}).get("whats_new") is False, str(take.get("devtools_seen")))
        expect("...and capture reports nothing out of place", "DevTools:" not in said.get("headed-stacked", ""),
               said.get("headed-stacked"))
        take, got = seen("headed-beside")
        styles = got.get("styles") or {}
        expect("docked right, 450 pixels wide, the Styles pane beside the tree at 200",
               got.get("dock") == "right" and abs((got.get("pane") or 0) - 450) <= 2
               and styles.get("layout") == "side-by-side" and abs(styles.get("size", 0) - 200) <= 2, str(got))
        take, got = seen("headed-left-hidden")
        styles = got.get("styles") or {}
        expect("docked left, 380 pixels wide; `hidden` leaves the Styles pane at its smallest, "
               "though DevTools stacks it here", got.get("dock") == "left" and abs((got.get("pane") or 0) - 380) <= 2
               and styles.get("layout") == "stacked" and styles.get("smallest") is True, str(got))
        take = newest("headed-columns")
        net = take.get("devtools_seen") or {}
        expect("Network: timeline hidden, Waterfall shown, Initiator hidden",
               net.get("panel") == "network" and net.get("overview") is False and net.get("waterfall") is True
               and "initiator" not in (net.get("columns") or []) and "name" in (net.get("columns") or []), str(net))
        # A Network take with no request open (an open one leaves only the Name column).
        default = newest("headed-second-visit").get("devtools_seen") or {}
        expect("...where DevTools' defaults are the other way round (read back from a Network take without them)",
               default.get("overview") is True and default.get("waterfall") is False
               and "initiator" in (default.get("columns") or []), str(default))
        expect("a setting DevTools doesn't honor is reported at capture (650 pixels asked, Chrome keeps less)",
               "DevTools: the pane is" in said.get("headed-too-tall", "") and "not 650" in said.get("headed-too-tall", ""),
               said.get("headed-too-tall"))
        wants = newest("headed-expects-infobar")
        expect("the infobar guard reads the browser's bars: a recipe expecting an infobar fails without one",
               wants.get("ok") is False and "expects an infobar" in " ".join(wants.get("problems", [])),
               str(wants.get("problems")))
    else:
        print("  skip  headed tests: Xvfb, xdotool, or ImageMagick missing (bash tools/shots/bootstrap.sh --headed)")

    server.shutdown()
    passed = sum(results)
    if passed == len(results):
        shutil.rmtree(tmp)
        print(f"{passed}/{len(results)} passed")
        return 0
    print(f"{passed}/{len(results)} passed; scratch folder kept for inspection: {tmp}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
