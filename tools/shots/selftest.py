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
