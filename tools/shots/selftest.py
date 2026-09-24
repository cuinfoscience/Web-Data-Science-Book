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
FLAKY = {"count": 0}      # /flaky works once, then answers 502


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/flaky":
            FLAKY["count"] += 1
            status, body = PAGES["/ok"] if FLAKY["count"] == 1 else PAGES["/gateway"]
        else:
            status, body = PAGES.get(self.path, (404, "<title>Not found</title>"))
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
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
    code, out = captured = shots("capture", "ch-99", "--only", "marks", "marks-2x", "small-text", "joined")
    marks, marks2, small, joined = newest("marks"), newest("marks-2x"), newest("small-text"), newest("joined")

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
    code, out = shots("check", "ch-99")
    expect("check fails a promoted image whose text is too small to read",
           code == 1 and "text too small to read: slides 11.7 px" in out, out[-400:])
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
