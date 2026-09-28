"""Capture one figure: pace, load, run steps, guard, measure, crop, screenshot, log.

Every take is written to tools/shots/out/<chapter>/<figure>/<UTC time>.png,
with a .json log beside it. A take that fails a guard is named
<UTC time>.FAILED.png. Nothing here writes to images/; `promote` does that.

The log records what the browser knew at the moment of capture, in the
take's own pixels: the box of everything the recipe's marks point at, and the
sizes of the text inside the crop (lib/measure.py). Markers are drawn from the
first (lib/annotate.py); the legibility check reads the second.
"""
import datetime
import hashlib
import json
import os
import random
import re
import time
from urllib.parse import urlparse

from PIL import Image, ImageDraw, ImageFont

from . import crop, guards, measure, steps
from .env import OUT, ROOT, rel
from .recipes import part_figure

# Seconds before the 2nd, 3rd, and 4th attempt (selftest.py shortens them).
BACKOFF = [int(s) for s in os.environ.get("SHOTS_BACKOFF", "30,60,120").split(",")]
PACE_FILE = OUT / ".pacing.json"
LABEL_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


class PolicyBlock(Exception):
    """The session's proxy refused the host: report it, never retry."""


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


class Pacer:
    """Keep page loads on one host 8-30 seconds apart, across runs as well."""

    def __init__(self):
        try:
            self.last = json.loads(PACE_FILE.read_text())
        except (OSError, ValueError):
            self.last = {}

    def wait(self, url, pause):
        host = urlparse(url.removeprefix("view-source:")).hostname or ""
        if host in ("localhost", "127.0.0.1"):
            return 0.0
        due = self.last.get(host, 0) + random.uniform(*pause)
        delay = max(0.0, due - time.time())
        time.sleep(delay)
        self.last[host] = time.time()
        PACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PACE_FILE.write_text(json.dumps(self.last))
        return delay


def _expected(page, fig):
    problems = []
    expect = fig.get("expect") or {}
    for text in expect.get("text") or []:
        if page.get_by_text(steps.pattern(text)).count() == 0:
            problems.append(f"expected text /{text}/ not found")
    for selector in expect.get("selector") or []:
        if page.locator(selector).count() == 0:
            problems.append(f"expected element {selector!r} not found")
    return problems


def _stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _measure_headless(page, fig, rect, full):
    """Anchors and text sizes, in the take's pixels. Page boxes are in the viewport's
    CSS pixels; the image starts at the clip's corner, or at the page's for a full page."""
    scale = fig["scale"]
    if full:
        sx, sy, width, height = page.evaluate(
            "[scrollX, scrollY, document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
        ox, oy, region = -sx, -sy, [-sx, -sy, width - sx, height - sy]
    else:
        ox, oy = rect["x"], rect["y"]
        region = [ox, oy, ox + rect["width"], oy + rect["height"]]
    anchors, problems = {}, []
    for at in measure.marks_anchors(fig):
        if "xy" in at:
            anchors[measure.key(at)] = measure.hand_box(at["xy"])
            continue
        try:
            box = measure.page_boxes(page, at, timeout=fig["timeout"])
        except measure.AnchorError as e:
            problems.append(str(e))
            continue
        anchors[measure.key(at)] = {"box": measure.shifted([v * scale for v in box], ox * scale, oy * scale)}
    sizes = measure.scaled(page.evaluate(measure.TEXT_SIZES, region), scale)
    return anchors, measure.summarize(sizes), problems


def _result():
    return {"status": None, "problems": [], "temporary": False, "clip": None, "final_url": None,
            "steps": [], "error": None, "anchors": {}, "text": None}


# `open_shadow: true`: a shadow root the page asks to have closed is made open instead,
# before any of the page's scripts run. A closed root is drawn like any other, but no
# selector reaches it, Playwright's included, so no step could wait for its text and the
# text measure couldn't count it. The Wayback Machine's toolbar is one (chapter 7).
OPEN_SHADOW = """(() => {
  const attach = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (init) {
    return attach.call(this, Object.assign({}, init, {mode: 'open'}));
  };
})();"""


def _headless(browser, fig, png):
    """One headless attempt, as a dict: status, problems, temporary (worth retrying),
    clip, final_url, steps, error (the page never loaded), anchors, and text."""
    result = _result()
    context = browser.context(fig)
    if fig.get("open_shadow"):
        context.add_init_script(OPEN_SHADOW)
    page = context.new_page()
    expect = fig.get("expect") or {}
    # The status of each document the tab loads. A site that checks the browser with a
    # script answers the first visit (EUR-Lex: 202) and then reloads the page it shows.
    loaded = []
    page.on("response", lambda r: loaded.append(r.status)
            if r.request.is_navigation_request() and r.frame == page.main_frame else None)
    # The page's own files that failed (guards.dropped): no answer at all, or a server
    # error. Chrome also fails a file it refused after an answer, such as a stylesheet
    # that got a 404, which is the page as it is; so an answered request counts only
    # when the answer was a 5xx.
    host, failed, answered = urlparse(fig["url"]).hostname, [], set()
    own = lambda request: request.resource_type in guards.DRAWN and urlparse(request.url).hostname == host
    page.on("response", lambda r: answered.add(r.request))
    page.on("response", lambda r: failed.append((r.request.resource_type, r.url, f"HTTP {r.status}"))
            if r.status >= 500 and own(r.request) else None)
    page.on("requestfailed", lambda r: failed.append((r.resource_type, r.url, r.failure))
            if own(r) and r not in answered else None)
    try:
        try:
            response = page.goto(fig["url"], wait_until="domcontentloaded", timeout=fig["timeout"] * 1000)
        except Exception as e:
            result["error"] = str(e).splitlines()[0]
            if not guards.expected_error(expect, result["error"]):
                return result
            response = None        # Chrome draws its own error page, the figure's subject,
            try:                   # which loads just after the navigation fails
                page.wait_for_url(re.compile(r"^chrome-error://"), timeout=fig["timeout"] * 1000)
            except Exception:
                pass               # a blank take fails its guards below

        status = result["status"] = response.status if response else None
        result["final_url"] = page.url
        if guards.retryable(status=status):
            result.update(problems=[f"HTTP status {status}"], temporary=True)
            return result
        problems = result["problems"]
        try:
            steps.run(page, fig, result["steps"])
        except steps.StepError as e:
            problems.append(str(e))
        time.sleep(fig["settle"])
        if status is not None and loaded and loaded[-1] != status:
            result["first_status"], status = status, loaded[-1]
            result["status"] = status
        text = page.evaluate("() => document.body ? document.body.innerText : ''")
        issues, result["temporary"] = guards.page_problems(status, page.title(), text, expect)
        lost, lost_temporary = guards.dropped(failed)
        if expect.get("all_files", True) is False:
            # The recipe accepts a page that loses a few files (judged by eye on the
            # contact sheet); the take's log still names them.
            result["dropped"], lost = lost, []
        # A dropped file is worth another try, unless the page itself is wrong.
        result["temporary"] = result["temporary"] or (bool(lost) and lost_temporary and not issues)
        problems += issues + lost + _expected(page, fig)
        result["final_url"] = page.url
        try:
            rect, full = crop.clip(page, fig)
        except crop.CropError as e:
            problems.append(str(e))
            rect, full = None, False
        if rect or full:
            result["anchors"], result["text"], missed = _measure_headless(page, fig, rect, full)
            problems += missed
        try:
            page.screenshot(path=str(png), clip=rect, full_page=full, animations="disabled")
        except Exception as e:
            # A crop outside the window, for one: a failed take to retry, not a crash of the run.
            problems.append(f"the screenshot failed: {str(e).splitlines()[0]}")
            result["temporary"] = True
        result["clip"] = rect
        return result
    finally:
        context.close()


def capture(browser, fig, pacer, say=print):
    """Return the take's log (a dict). Raises PolicyBlock if the proxy refuses the host."""
    from . import engine_codegen, engine_selenium, headed
    if fig["mode"] == "composite":
        return _composite(browser, fig, pacer, say)
    engine = fig.get("engine", "playwright")
    folder = OUT / fig["chapter"] / fig["id"]
    folder.mkdir(parents=True, exist_ok=True)
    attempts = []
    for n in range(fig["retries"] + 1):
        if n:
            wait = BACKOFF[min(n - 1, len(BACKOFF) - 1)]
            say(f"    waiting {wait}s before attempt {n + 1}")
            time.sleep(wait)
        attempt = {"attempt": n + 1, "paced_seconds": round(pacer.wait(fig["url"], fig["pause"]), 1)}
        attempts.append(attempt)
        stamp = _stamp()
        png = folder / f"{stamp}.png"
        if engine == "codegen":
            display = browser.display(*engine_codegen.screen_size(fig))
            result = engine_codegen.attempt(browser, fig, display, png)
            label = engine_codegen.label(browser)
        elif engine == "selenium":
            display = browser.display(fig["window"][0] * fig["scale"], fig["window"][1] * fig["scale"])
            result = engine_selenium.attempt(browser, fig, display, png)
            label = engine_selenium.label(browser)
        elif fig["mode"] == "headed":
            display = browser.display(fig["window"][0] * fig["scale"], fig["window"][1] * fig["scale"])
            result = headed.attempt(browser, fig, display, png)
            label = headed.label(browser)
        else:
            result = _headless(browser, fig, png)
            label = browser.label
        status, problems, error = result["status"], result["problems"], result["error"]
        attempt.update({k: v for k, v in (("status", status), ("first_status", result.get("first_status")),
                                          ("steps", result["steps"]), ("error", error)) if v})
        host = urlparse(fig["url"].removeprefix("view-source:")).hostname
        expected = guards.expected_error(fig.get("expect"), error)
        if error and not expected:
            if guards.policy_block(error):
                raise PolicyBlock(f"the proxy refused {host} ({error})")
            if guards.retryable(error=error):
                continue
            break
        if expected and guards.policy_block(error):
            # Behind the proxy, a dead host and a refused one look alike to Chrome. Public DNS
            # tells them apart: only a name with no address is photographed as a dead host.
            try:
                attempt["dns"] = guards.lookup(host, fig["user_agent"])
            except Exception as e:
                problems.append(f"can't tell a dead host from a refused one: public DNS didn't answer "
                                f"({str(getattr(e, 'reason', e))})")
            else:
                if not guards.dead_host(attempt["dns"]):
                    png.unlink(missing_ok=True)        # Chrome's page says nothing true about the host
                    raise PolicyBlock(f"the proxy refused {host}, which public DNS resolves "
                                      f"({', '.join(attempt['dns']['addresses'])}): a policy, not a dead host")
        if guards.retryable(status=status):
            attempt["result"] = "server error"
            continue
        if not png.exists():
            attempt["result"] = "; ".join(problems + ["no image was taken"])
            if result["temporary"] and n < fig["retries"]:
                continue
            return {"ok": False, "problems": problems + ["no image was taken"], "attempts": attempts}
        problems += guards.image_problems(png)
        if problems:
            failed = folder / f"{stamp}.FAILED.png"
            png.rename(failed)
            png = failed
        take = _log(fig, png, problems, status, result["final_url"], label, result["clip"], attempts)
        take.update(anchors=result["anchors"], text=result["text"])
        # A page reloaded after a script check, or never loaded: what the browser met first.
        take.update({k: v for k, v in (("first_status", result.get("first_status")), ("error", error),
                                       ("dns", attempt.get("dns"))) if v})
        # Headed takes: the browser's bars above the page, what DevTools drew (read back), and the
        # versions an engine ran (Chrome and ChromeDriver under Selenium), and the script codegen wrote.
        take.update({k: result[k] for k in ("bars", "devtools_seen", "engine", "recorded") if result.get(k) is not None})
        if result.get("dropped"):
            take["dropped"] = result["dropped"]      # files lost on a page whose recipe accepts that
        _write(take, png)
        if problems and result["temporary"] and n < fig["retries"]:
            say(f"    attempt {n + 1}: {'; '.join(problems)}; will retry")
            continue
        return take
    last = attempts[-1] if attempts else {}
    return {"ok": False, "problems": [f"no usable take after {len(attempts)} attempt(s): "
                                      f"{last.get('error') or last.get('result') or last.get('status')}"],
            "attempts": attempts}


def _log(fig, png, problems, status, final_url, label, clip, attempts):
    with Image.open(png) as img:
        size = list(img.size)
    return {
        "ok": not problems, "problems": problems,
        "chapter": fig["chapter"], "figure": fig["id"], "file": fig["file"], "kind": fig["kind"],
        "url": fig.get("url"), "final_url": final_url, "status": status,
        "captured": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "by": "tools/shots", "browser": label, "user_agent": fig["user_agent"],
        "window": fig["window"], "scale": fig["scale"], "javascript": fig["javascript"],
        "mode": fig["mode"], "devtools": fig.get("devtools"),
        "crop": fig.get("crop") or {"window": True}, "clip": clip, "size": size,
        "recipe_sha256": fig["recipe_sha256"], "image": rel(png), "image_sha256": sha256(png),
        "attempts": attempts, **({"open_shadow": True} if fig.get("open_shadow") else {}),
    }


def _write(take, png):
    png.with_suffix(".json").write_text(json.dumps(take, indent=2) + "\n")


def _composite(browser, fig, pacer, say):
    """Capture each part as a figure of its own, then join them side by side, labeled."""
    parts = []
    for n in range(len(fig["parts"])):
        sub = {**part_figure(fig, n), "recipe_sha256": fig["recipe_sha256"]}
        say(f"  part {n + 1}: {sub['label']}")
        take = capture(browser, sub, pacer, say)
        if not take.get("ok"):
            return {"ok": False, "problems": [f"part {n + 1} ({sub['label']}): "
                                              + "; ".join(take.get("problems") or ["failed"])]}
        take["label"] = sub["label"]
        parts.append(take)
    folder = OUT / fig["chapter"] / fig["id"]
    folder.mkdir(parents=True, exist_ok=True)
    png = folder / f"{_stamp()}.png"
    join([ROOT / p["image"] for p in parts], [p["label"] for p in parts], fig.get("layout") or {},
         fig["scale"], png)
    problems = guards.image_problems(png)
    take = _log(fig, png, problems, parts[0]["status"], parts[0]["final_url"], parts[0]["browser"], None,
                [a for p in parts for a in p["attempts"]])
    take["parts"] = [{k: p.get(k) for k in ("label", "image", "image_sha256", "url", "javascript", "status",
                                            "first_status", "error", "dns", "dropped", "open_shadow") if k in p}
                     for p in parts]
    sizes = measure.merge(*[{float(s): c for s, c in ((p.get("text") or {}).get("sizes") or {}).items()}
                            for p in parts])
    take["text"] = measure.summarize(sizes)
    _write(take, png)
    return take


def join(images, labels, layout, scale, out):
    """Place images side by side on white, or one above the next (`direction: column`),
    each labeled below it, inside a thin gray frame."""
    gap, pad = layout.get("gap", 28) * scale, layout.get("pad", 14) * scale
    size = layout.get("label_px", 28) * scale
    font = ImageFont.truetype(LABEL_FONT, size)
    panels = [Image.open(p).convert("RGB") for p in images]
    tallest = max(p.height for p in panels)
    label_h = round(size * 1.5)
    column = layout.get("direction", "row") == "column"
    if column:
        width = max(p.width for p in panels) + 2 * pad
        height = sum(p.height + label_h for p in panels) + gap * (len(panels) - 1) + 2 * pad
    else:
        width = sum(p.width for p in panels) + gap * (len(panels) - 1) + 2 * pad
        height = tallest + label_h + 2 * pad
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    x = y = pad
    for panel, label in zip(panels, labels):
        sheet.paste(panel, (x, y))
        below = y + (panel.height if column else tallest) + label_h / 2
        draw.text((x + panel.width / 2, below), label, fill="black", font=font, anchor="mm")
        if column:
            y += panel.height + label_h + gap
        else:
            x += panel.width + gap
    draw.rectangle([0, 0, width - 1, height - 1], outline=(200, 200, 200), width=max(1, scale))
    sheet.save(out)


def takes(chapter, fid, ok_only=True):
    """This figure's takes, newest first."""
    folder = OUT / chapter / fid
    found = []
    for log in sorted(folder.glob("*.json"), reverse=True):
        take = json.loads(log.read_text())
        if take.get("ok") or not ok_only:
            found.append(take)
    return found
