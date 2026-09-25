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
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import urllib.parse
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import devtools as dt                   # noqa: E402  (to read a take's DevTools state)
from lib.headed import BARS, BARS_SLACK          # noqa: E402
from lib import guards, robots                    # noqa: E402

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
    # A page that scrolls a panel, not the window, as Jupyter does.
    "/panel": (200, "<!DOCTYPE html><title>Panel</title><body style='margin:0;overflow:hidden'>"
                    "<div id='panel' style='position:absolute;top:0;left:0;width:800px;height:600px;"
                    "overflow-y:auto'><div style='height:1500px'></div>"
                    "<h2 id='deep' style='margin:0;line-height:30px'>Deep in the panel</h2>"
                    "<div style='height:1500px'></div></div></body>"),
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
# A site that checks the browser with a script, as EUR-Lex does: the first visit gets 202 and
# a script that sets a cookie and reloads; the reload, with the cookie, gets the page.
PAGES["/checked"] = (200, "<title>Checked</title><h1>Checked and reloaded</h1>"
                          + "<p>" + "Something to look at. " * 40 + "</p>")
CHECK = (202, "<title></title><script>document.cookie = 'checked=1; path=/'; location.reload();</script>")
# A page whose stylesheet the connection drops (as web.archive.org's did on 2026-09-25), and
# one whose stylesheet the server answers with a 404 (an archive that never saved it).
PAGES["/styled"] = (200, "<title>Styled</title><link rel='stylesheet' href='/drop.css'>"
                         "<h1>A styled page</h1><p>" + "Something to look at. " * 40 + "</p>")
PAGES["/styled-404"] = (200, "<title>Styled</title><link rel='stylesheet' href='/missing.css'>"
                             "<h1>A styled page</h1><p>" + "Something to look at. " * 40 + "</p>")
PAGES["/imaged"] = (200, "<title>Imaged</title><h1>A page with a picture</h1><img src='/picture-502.png'>"
                         "<p>" + "Something to look at. " * 40 + "</p>")
PAGES["/picture-502.png"] = (502, "Bad Gateway")
# Text in a closed shadow root, as the Wayback Machine's toolbar keeps its capture count.
PAGES["/closed-shadow"] = (200, "<title>Closed</title><h1>Outside the root</h1><div id='host'></div>"
                                "<script>document.getElementById('host').attachShadow({mode: 'closed'})"
                                ".innerHTML = '<p style=\"font-size:20px\">Inside a closed root</p>';</script>")
# Two pages a link joins, for codegen's recorder: a real click on the link becomes a line of Python.
PAGES["/links"] = (200, "<title>Links</title><h1>The first page</h1>"
                        "<p style='font-size:20px'><a href='/second'>Go to the second page</a></p>")
PAGES["/second"] = (200, "<title>Second</title><h1 style='margin-top:40px'>The second page</h1>"
                         "<p>" + "Something to look at. " * 20 + "</p>")
# Public DNS over HTTPS, as dns.google answers it: no address for the dead host, one for the refused host.
DNS = {"dead-host.test": {"Status": 3},
       "refused-host.test": {"Status": 0, "Answer": [{"name": "refused-host.test.", "type": 1, "data": "192.0.2.1"}]}}
FLAKY = {"count": 0}      # /flaky works once, then answers 502
# A CDX-style API: five captures, paged by `limit`, with a resume key when more wait (as
# web.archive.org's CDX server answers with showResumeKey=true).
CDX_ROWS = [["com,example)/a.gif", "20000801000000", "404"], ["com,example)/a.gif", "20000901000000", "404"],
            ["com,example)/b.gif", "20000401000000", "200"], ["com,example)/b.gif", "20000801000000", "404"],
            ["com,example)/c.gif", "20000901000000", "404"]]
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
        path, _, query = self.path.partition("?")
        kind = "text/html; charset=utf-8"
        if path == "/drop.css":        # no response at all: Chrome reports ERR_EMPTY_RESPONSE
            self.close_connection = True
            return
        if path == "/resolve":
            args = urllib.parse.parse_qs(query)
            answer = DNS.get(args["name"][0], {"Status": 3})
            if args.get("type", ["A"])[0] != "A":
                answer = {"Status": answer["Status"]}           # no IPv6 addresses
            status, body, kind = 200, json.dumps(answer), "application/dns-json"
        elif path == "/cdx":
            args = urllib.parse.parse_qs(query)
            limit, start = int(args.get("limit", ["1000"])[0]), int(args.get("resumeKey", ["0"])[0])
            rows = [["urlkey", "timestamp", "statuscode"]] + CDX_ROWS[start:start + limit]
            if args.get("showResumeKey", [""])[0] == "true" and start + limit < len(CDX_ROWS):
                rows += [[], [str(start + limit)]]
            status, body, kind = 200, json.dumps(rows), "application/json"
        elif path == "/check":
            status, body = PAGES["/checked"] if "checked=1" in (self.headers.get("Cookie") or "") else CHECK
        elif self.path == "/flaky":
            FLAKY["count"] += 1
            status, body = PAGES["/ok"] if FLAKY["count"] == 1 else PAGES["/gateway"]
        else:
            status, body = PAGES.get(self.path, (404, "<title>Not found</title>"))
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        if self.path == "/cookie":
            self.send_header("Set-Cookie", "visit=1; Path=/")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class RefusingProxy(socketserver.BaseRequestHandler):
    """A proxy that opens no tunnels: every CONNECT gets 502, as the session's proxy answers
    both for a host whose name doesn't resolve and for one its policy refuses."""
    def handle(self):
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self.request.recv(4096)
            if not chunk:
                return
            data += chunk
        self.request.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    refusing = socketserver.ThreadingTCPServer(("127.0.0.1", 0), RefusingProxy)
    threading.Thread(target=refusing.serve_forever, daemon=True).start()
    with socket.socket() as s:               # a port nothing listens on: a host that doesn't answer
        s.bind(("127.0.0.1", 0))
        closed = s.getsockname()[1]
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
  - {{id: dropped-style, kind: capture, url: "{base}/styled", expect: {{text: ['A styled page']}}}}
  - {{id: missing-style, kind: capture, url: "{base}/styled-404", expect: {{text: ['A styled page']}}}}
  - {{id: dropped-allowed, kind: capture, url: "{base}/styled", expect: {{text: ['A styled page'], all_files: false}}}}
  - {{id: image-502, kind: capture, url: "{base}/imaged", expect: {{text: ['A page with a picture']}}}}
  - {{id: crop-missing, kind: capture, url: "{base}/ok", crop: {{between: ['#not-on-the-page', 'h1']}}}}
  - {{id: shadow-closed, kind: capture, url: "{base}/closed-shadow", expect: {{text: ['Inside a closed root']}}}}
  - {{id: shadow-opened, kind: capture, url: "{base}/closed-shadow", open_shadow: true,
      steps: [{{wait: {{text: 'Inside a closed root'}}}}], expect: {{text: ['Inside a closed root']}}}}
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
  - {{id: band, kind: capture, url: "{base}/marks", crop: {{between: ['#title', '#box']}}}}
  - id: scroll-within
    kind: capture
    url: "{base}/panel"
    steps: [{{scroll: {{selector: '#deep', offset: 100, within: '#panel'}}}}]
    expect: {{text: ['Deep in the panel']}}
    annotate: {{marks: [{{n: 1, at: {{selector: '#deep'}}}}]}}
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
  - id: joined-column
    kind: capture
    url: "{base}/ok"
    mode: composite
    window: [400, 300]
    parts: [{{label: One}}, {{label: Two}}]
    layout: {{direction: column, gap: 10, pad: 5, label_px: 20}}
  - {{id: dead-host, kind: capture, url: "http://127.0.0.1:{closed}/",
      expect: {{error: 'ERR_CONNECTION_REFUSED', text: ['refused to connect']}}}}
  - {{id: dead-host-loads, kind: capture, url: "{base}/ok", expect: {{error: 'ERR_CONNECTION_REFUSED'}}}}
  - {{id: rechecked, kind: capture, url: "{base}/check", steps: [{{wait: {{text: 'Checked and reloaded'}}}}]}}
  - {{id: tunnel-dead, kind: capture, url: "https://dead-host.test/", expect: {{error: 'ERR_TUNNEL_CONNECTION_FAILED'}}}}
  - {{id: tunnel-refused, kind: capture, url: "https://refused-host.test/",
      expect: {{error: 'ERR_TUNNEL_CONNECTION_FAILED'}}}}
  - {{id: tunnel-unexpected, kind: capture, url: "https://other-host.test/"}}
  - id: evidence-paged
    kind: capture
    url: "{base}/ok"
    evidence:
      - id: paged
        claim: "a.gif was captured only as 404s"
        url: "{base}/cdx"
        params: {{url: 'example.com/', output: json, limit: 2, showResumeKey: 'true'}}
        page: resume_key
        summary: {{group_by: urlkey, count: statuscode}}
      - id: runs
        claim: "the statuses change three times"
        url: "{base}/cdx"
        params: {{url: 'example.com/', output: json, limit: 10}}
        summary: {{runs: statuscode}}
  - id: evidence-capped
    kind: capture
    url: "{base}/ok"
    evidence:
      - {{id: capped, claim: "a query cut short", url: "{base}/cdx", params: {{url: 'example.com/', output: json, limit: 5}}}}
  - id: evidence-unfollowed
    kind: capture
    url: "{base}/ok"
    evidence:
      - {{id: unfollowed, claim: "a resume key left unfollowed", url: "{base}/cdx",
          params: {{url: 'example.com/', output: json, limit: 2, showResumeKey: 'true'}}}}
  - id: selenium-window
    kind: capture
    url: "{base}/tree"
    mode: headed
    engine: selenium
    window: [700, 500]
    steps: [{{wait: {{selector: '#target'}}}}]
    expect: {{infobar: true, text: ['Inspect me']}}
  - id: codegen-recorded
    kind: capture
    url: "{base}/links"
    mode: headed
    engine: codegen
    window: [700, 300]
    inspector: {{window: [700, 450], at: below}}
    steps:
      - click: {{role: link, name: 'Go to the second page'}}
      - wait: {{url: '**/second'}}
      - pointer: {{selector: 'h1', at: [0.1, 0.5]}}
    expect: {{text: ['The second page'], code: ['get_by_role("link", name="Go to the second page").click()']}}
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
    code, out = shots("capture", "ch-99", "--only", "dropped-style", "missing-style", "dropped-allowed")
    ds = newest("dropped-style")
    expect("a stylesheet whose connection dropped fails the take, though the text is all there",
           ds.get("ok") is False and "didn't load" in " ".join(ds.get("problems", [])), str(ds.get("problems")))
    expect("...and is retried", len(ds.get("attempts", [])) == 2, str(ds.get("attempts")))
    expect("a stylesheet the server answers with a 404 is the page as it is",
           newest("missing-style").get("ok") is True, str(newest("missing-style").get("problems")))
    da = newest("dropped-allowed")
    expect("a recipe that accepts lost files passes, and its log names them",
           da.get("ok") is True and "didn't load" in " ".join(da.get("dropped", [])), str(da.get("problems")))
    code, out = shots("capture", "ch-99", "--only", "image-502")
    im = newest("image-502")
    expect("an image the server answers with a 502 fails the take, and it is retried",
           im.get("ok") is False and "HTTP 502" in " ".join(im.get("problems", []))
           and len(im.get("attempts", [])) == 2, str(im.get("problems")) + str(im.get("attempts")))
    code, out = shots("capture", "ch-99", "--only", "crop-missing")
    cm = newest("crop-missing")
    expect("a crop whose element isn't on the page fails the take and the run goes on",
           code == 1 and cm.get("ok") is False and "matched nothing visible" in " ".join(cm.get("problems", []))
           and "Traceback" not in out, str(cm.get("problems")) + out[-300:])
    code, out = shots("capture", "ch-99", "--only", "shadow-closed", "shadow-opened")
    sc, so = newest("shadow-closed"), newest("shadow-opened")
    expect("text in a closed shadow root is out of every selector's reach",
           sc.get("ok") is False and "not found" in " ".join(sc.get("problems", [])), str(sc.get("problems")))
    expect("`open_shadow: true` opens it: the step waits for its text, the guard finds it, and the log says so",
           so.get("ok") is True and so.get("open_shadow") is True, str(so.get("problems")))
    expect("...and the text measure counts it (20 pixels, beside the heading's 32)",
           20.0 in [float(k) for k in ((so.get("text") or {}).get("sizes") or {})], str(so.get("text")))
    lost = guards.dropped([("stylesheet", "https://web.archive.org/x.css", "net::ERR_ABORTED")])
    expect("an aborted stylesheet is a lost one, worth another try", lost[0] and lost[1] is True, str(lost))
    kept = guards.dropped([("image", "https://example.org/a.png", "net::ERR_ABORTED"),
                           ("script", "https://example.org/a.js", "net::ERR_ABORTED")])
    expect("...but an aborted image or script is the page cancelling it", kept == ([], False), str(kept))
    served = guards.dropped([("image", "https://web.archive.org/a.gif", "HTTP 502")])
    expect("a 5xx answer is a lost file, worth another try", served[0] and served[1] is True, str(served))

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
    found = robots.findings("api.example.org", "User-agent: *\nDisallow: /\n", agent,
                            [("json", "https://api.example.org/v1/forecast", True),
                             ("page", "https://api.example.org/about", False)])
    expect("a disallowed API response marked api_client is a note; a disallowed page is still a warning",
           [level for level, _, _ in found] == ["note", "warn"] and "API client" in found[0][1], str(found))

    print("engines (recipe rules)")
    from lib import recipes as recipe_rules
    bad = recipe_rules._problems("ch-98", {"chapter": "ch-98", "figures": [
        {"id": "a", "kind": "capture", "url": "https://example.org/", "engine": "selenium",
         "steps": [{"inspect": {"selector": "img"}}]},
        {"id": "b", "kind": "capture", "url": "https://example.org/", "mode": "headed", "engine": "codegen",
         "crop": {"devtools": True}},
        {"id": "c", "kind": "capture", "url": "https://example.org/", "inspector": {"window": [800, 400]}}]})
    expect("an engine needs a real window: `mode: headed`", any("(a)" in b and "mode: headed" in b for b in bad), bad)
    expect("...and runs only its own steps (the selenium engine has no `inspect`)",
           any("(a)" in b and "no `inspect` step" in b for b in bad), bad)
    expect("...and crops the window by its edges alone", any("(b)" in b and "not `devtools`" in b for b in bad), bad)
    expect("`inspector` belongs to the codegen engine", any("(c)" in b and "engine: codegen" in b for b in bad), bad)

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

    print("refusals and dead hosts")
    code, out = shots("capture", "ch-99", "--only", "dead-host", "dead-host-loads", "rechecked")
    dead, loaded, rechecked = newest("dead-host"), newest("dead-host-loads"), newest("rechecked")
    expect("a figure of a host that doesn't answer is Chrome's own error page, and the take records the error",
           dead.get("ok") is True and dead.get("status") is None
           and "ERR_CONNECTION_REFUSED" in (dead.get("error") or ""),
           str({k: dead.get(k) for k in ("ok", "status", "error", "problems")}) + out[-300:])
    expect("...and fails if the page loads after all", loaded.get("ok") is False
           and "expected the page not to load" in " ".join(loaded.get("problems", [])), str(loaded.get("problems")))
    expect("a page that checks the browser with a script (202, then a reload) is recorded at the status of "
           "the page it shows, and the first status is kept",
           rechecked.get("ok") is True and rechecked.get("status") == 200 and rechecked.get("first_status") == 202,
           str({k: rechecked.get(k) for k in ("ok", "status", "first_status", "problems")}) + out[-300:])
    # Behind a proxy, a host whose name doesn't resolve and a host the proxy refuses fail alike,
    # with ERR_TUNNEL_CONNECTION_FAILED. Public DNS (here, a stand-in for dns.google) tells them apart.
    loopback = "127.0.0.1,localhost"
    tunnel_env = dict(env, HTTPS_PROXY=f"http://127.0.0.1:{refusing.server_address[1]}",
                      https_proxy=f"http://127.0.0.1:{refusing.server_address[1]}",
                      SHOTS_DOH=f"{base}/resolve", NO_PROXY=loopback, no_proxy=loopback)
    run = subprocess.run([sys.executable, str(HERE / "shots.py"), "capture", "ch-99", "--only", "tunnel-dead",
                          "tunnel-refused", "tunnel-unexpected"], env=tunnel_env, capture_output=True, text=True,
                         timeout=600)
    said = sections(run.stdout + run.stderr)
    tunnel = newest("tunnel-dead")
    expect("behind a proxy, a tunnel failure is photographed as a dead host only when public DNS has no address "
           "for it", tunnel.get("ok") is True and (tunnel.get("dns") or {}).get("rcode") == "NXDOMAIN",
           str({k: tunnel.get(k) for k in ("ok", "dns", "error", "problems")}) + str(said.get("tunnel-dead")))
    expect("...and is a policy block when public DNS resolves it: reported, with no take left behind",
           "which public DNS resolves (192.0.2.1): a policy, not a dead host" in said.get("tunnel-refused", "")
           and not list((tmp / "out" / "ch-99" / "tunnel-refused").glob("*.png")), said.get("tunnel-refused"))
    expect("a tunnel failure the recipe doesn't expect is a policy block, as before",
           "the proxy refused other-host.test" in said.get("tunnel-unexpected", ""), said.get("tunnel-unexpected"))
    doctor = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import shots; "
                             "sys.exit(shots.doctor_chapter('ch-99'))", str(HERE)],
                            env=tunnel_env, capture_output=True, text=True, timeout=300)
    said = doctor.stdout + doctor.stderr
    expect("doctor asks public DNS about a host its figure expects not to answer, as capture does",
           "dead-host.test: doesn't answer, and public DNS has no address for it (NXDOMAIN)" in said
           and "refused-host.test: doesn't answer, but public DNS resolves it (192.0.2.1)" in said
           and "other-host.test: the proxy refused it" in said, said[-900:])
    found = robots.crawl_delay("User-agent: *\nCrawl-delay: 10\nDisallow: /search\n", agent)
    expect("doctor reads the Crawl-delay robots.txt asks of the capture's User-Agent (EUR-Lex asks for 10 seconds)",
           found == 10.0, str(found))

    print("anchors, markers, legibility, composites")
    code, out = captured = shots("capture", "ch-99", "--only", "marks", "marks-2x", "small-text", "joined",
                                 "joined-column", "wide", "wide-allowed", "wide-small", "too-wide", "scroll-within",
                                 "band")
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
    band = newest("band")
    expect("a crop `between` two elements is the band from the top of one to the bottom of the other",
           band.get("ok") is True and band.get("size") == [800, 170], str({k: band.get(k) for k in ("ok", "size")}))
    deep = anchor(newest("scroll-within"), {"selector": "#deep"}) or [0, 0, 0, 0]
    expect("a scroll step with `within` scrolls that panel, putting the element at its offset",
           deep[1] == 100 and deep[3] == 130, str(deep))
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
    column = newest("joined-column")
    expect("...or one above the next (`direction: column`), each labeled below it",
           column.get("ok") is True and column.get("size") == [410, 680],
           str({k: column.get(k) for k in ("ok", "size", "problems")}))

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

    print("evidence (the queries behind a caption)")
    code, out = shots("evidence", "ch-99", "--only", "evidence-paged")
    record = {e["id"]: e for e in json.loads((tmp / "images" / "ch-99" / "provenance.json").read_text())
              .get("evidence", {}).get("evidence-paged", [])}
    paged, runs = record.get("paged") or {}, record.get("runs") or {}
    expect("a paged query follows its resume keys to the end: 5 rows in 3 requests, complete",
           code == 0 and paged.get("rows") == 5 and len(paged.get("requests") or []) == 3 and paged.get("complete"),
           str(paged)[:300] + out[-300:])
    expect("...and its summary counts each capture's status by URL",
           (paged.get("summary") or {}).get("groups") == {"com,example)/a.gif": {"404": 2},
                                                          "com,example)/b.gif": {"200": 1, "404": 1},
                                                          "com,example)/c.gif": {"404": 1}}, str(paged.get("summary")))
    expect("a summary of runs: each stretch of one status, with its first and last timestamps",
           (runs.get("summary") or {}).get("runs") == [["404", "20000801000000", "20000901000000", 2],
                                                       ["200", "20000401000000", "20000401000000", 1],
                                                       ["404", "20000801000000", "20000901000000", 2]],
           str(runs.get("summary")))
    md = (tmp / "images" / "ch-99" / "IMAGES.md").read_text() if (tmp / "images" / "ch-99" / "IMAGES.md").exists() else ""
    expect("the evidence is listed in IMAGES.md, beside the figures", "Evidence behind the captions" in md
           and "`paged`" in md, md[-400:])
    code, out = shots("evidence", "ch-99", "--only", "evidence-capped")
    expect("a page that returns exactly its limit, with no way to page, fails",
           code == 1 and "returned exactly its limit" in out, out[-300:])
    code, out = shots("evidence", "ch-99", "--only", "evidence-unfollowed")
    expect("...and so does a page whose resume key the query doesn't follow",
           code == 1 and "resume key" in out and "doesn't follow" in out, out[-300:])
    code, out = shots("check", "ch-99")
    expect("check warns about a figure whose evidence was never run to its end",
           "evidence-capped: evidence `capped` has not been run" in out, out[-600:])
    expect("...and not about one whose evidence is recorded", "evidence-paged: evidence" not in out, out[-600:])
    recipe_file = tmp / "recipes" / "ch-99.yml"
    recipe_file.write_text(recipe_file.read_text().replace("limit: 2, showResumeKey: 'true'}\n        page: resume_key",
                                                           "limit: 3, showResumeKey: 'true'}\n        page: resume_key"))
    code, out = shots("check", "ch-99")
    expect("...and warns again when the query changes after it ran", "evidence `paged`: the query changed" in out,
           out[-600:])
    recipe_file.write_text(recipe_file.read_text().replace('claim: "the statuses change three times"',
                                                           'claim: "the statuses change twice"'))
    code, out = shots("check", "ch-99")
    expect("...or when its claim is reworded, so the claim on record is the one checked",
           "evidence `runs`: the claim changed" in out, out[-600:])

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

        print("  engines: the tool is the figure's subject")
        code, out = shots("capture", "ch-99", "--only", "selenium-window", "codegen-recorded")
        take = newest("selenium-window")
        engine = take.get("engine") or {}
        expect("selenium: webdriver.Chrome() opens Chrome for Testing, which Selenium drives to the page",
               take.get("ok") is True and engine.get("name") == "selenium" and engine.get("chromedriver"),
               str(take.get("problems")) + str(engine) + out[-300:])
        expect("...its window keeps Chrome for Testing's own notice (the engine adds no --disable-infobars)",
               (take.get("bars") or 0) > BARS + BARS_SLACK, str(take.get("bars")))
        expect("...the whole window is grabbed at its size, and the page's text measured",
               take.get("size") == [700, 500] and (take.get("text") or {}).get("chars", 0) > 0,
               str(take.get("size")) + str(take.get("text")))
        take = newest("codegen-recorded")
        recorded = take.get("recorded") or ""
        expect("codegen: a real click on a link becomes a line in the script the recorder writes",
               take.get("ok") is True and 'get_by_role("link", name="Go to the second page").click()' in recorded
               and f'page.goto("{base}/links")' in recorded, str(take.get("problems")) + recorded[-300:] + out[-300:])
        expect("...both windows are grabbed, the Inspector below the browser",
               take.get("size") == [700, 750], str(take.get("size")))
        sizes = (take.get("text") or {}).get("sizes") or {}
        expect("...and the Inspector's code counts at the size its stylesheet sets (14 pixels)",
               "14" in sizes, str(take.get("text")))
    else:
        print("  skip  headed tests: Xvfb, xdotool, or ImageMagick missing (bash tools/shots/bootstrap.sh --headed)")

    server.shutdown()
    refusing.shutdown()
    passed = sum(results)
    if passed == len(results):
        shutil.rmtree(tmp)
        print(f"{passed}/{len(results)} passed")
        return 0
    print(f"{passed}/{len(results)} passed; scratch folder kept for inspection: {tmp}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
