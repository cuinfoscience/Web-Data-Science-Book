"""Capture one figure: pace, load, run steps, guard, crop, screenshot, log.

Every take is written to tools/shots/out/<chapter>/<figure>/<UTC time>.png,
with a .json log beside it. A take that fails a guard is named
<UTC time>.FAILED.png. Nothing here writes to images/; `promote` does that.
"""
import datetime
import hashlib
import json
import os
import random
import re
import time
from urllib.parse import urlparse

from PIL import Image

from . import crop, guards, steps
from .env import OUT, rel

# Seconds before the 2nd, 3rd, and 4th attempt (selftest.py shortens them).
BACKOFF = [int(s) for s in os.environ.get("SHOTS_BACKOFF", "30,60,120").split(",")]
PACE_FILE = OUT / ".pacing.json"


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
    for pattern in expect.get("text") or []:
        if page.get_by_text(re.compile(pattern)).count() == 0:
            problems.append(f"expected text /{pattern}/ not found")
    for selector in expect.get("selector") or []:
        if page.locator(selector).count() == 0:
            problems.append(f"expected element {selector!r} not found")
    return problems


def _stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def capture(browser, fig, pacer, say=print):
    """Return the take's log (a dict). Raises PolicyBlock if the proxy refuses the host."""
    if fig["mode"] != "headless":
        later = {"headed": "M2", "composite": "M3"}.get(fig["mode"], "a later milestone")
        return {"ok": False, "skipped": f"mode `{fig['mode']}` arrives in milestone {later}"}
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
        context = browser.context(fig)
        page = context.new_page()
        try:
            try:
                response = page.goto(fig["url"], wait_until="domcontentloaded", timeout=fig["timeout"] * 1000)
            except Exception as e:
                error = str(e).splitlines()[0]
                attempt["error"] = error
                if guards.policy_block(error):
                    raise PolicyBlock(f"the proxy refused {urlparse(fig['url'].removeprefix('view-source:')).hostname} ({error})")
                if guards.retryable(error=error):
                    continue
                break
            status = response.status if response else None
            attempt["status"] = status
            if guards.retryable(status=status):
                attempt["result"] = "server error"
                continue
            problems, temporary = [], False
            steplog = []
            try:
                steps.run(page, fig, steplog)
            except steps.StepError as e:
                problems.append(str(e))
            attempt["steps"] = steplog
            time.sleep(fig["settle"])
            text = page.evaluate("() => document.body ? document.body.innerText : ''")
            page_issues, temporary = guards.page_problems(status, page.title(), text, fig.get("expect") or {})
            problems += page_issues + _expected(page, fig)
            try:
                rect, full = crop.clip(page, fig)
            except crop.CropError as e:
                problems.append(str(e))
                rect, full = None, False
            stamp = _stamp()
            png = folder / f"{stamp}.png"
            page.screenshot(path=str(png), clip=rect, full_page=full, animations="disabled")
            problems += guards.image_problems(png)
            if problems:
                failed = folder / f"{stamp}.FAILED.png"
                png.rename(failed)
                png = failed
            with Image.open(png) as img:
                size = list(img.size)
            take = {
                "ok": not problems, "problems": problems,
                "chapter": fig["chapter"], "figure": fig["id"], "file": fig["file"], "kind": fig["kind"],
                "url": fig["url"], "final_url": page.url, "status": status,
                "captured": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "by": "tools/shots", "browser": browser.label, "user_agent": fig["user_agent"],
                "window": fig["window"], "scale": fig["scale"], "javascript": fig["javascript"],
                "crop": fig.get("crop") or {"window": True}, "clip": rect, "size": size,
                "recipe_sha256": fig["recipe_sha256"], "image": rel(png), "image_sha256": sha256(png),
                "attempts": attempts,
            }
            png.with_suffix(".json").write_text(json.dumps(take, indent=2) + "\n")
            if problems and temporary and n < fig["retries"]:
                say(f"    attempt {n + 1}: {'; '.join(problems)}; will retry")
                continue
            return take
        finally:
            context.close()
    last = attempts[-1] if attempts else {}
    return {"ok": False, "problems": [f"no usable take after {len(attempts)} attempt(s): "
                                      f"{last.get('error') or last.get('result') or last.get('status')}"],
            "attempts": attempts}


def takes(chapter, fid, ok_only=True):
    """This figure's takes, newest first."""
    folder = OUT / chapter / fid
    found = []
    for log in sorted(folder.glob("*.json"), reverse=True):
        take = json.loads(log.read_text())
        if take.get("ok") or not ok_only:
            found.append(take)
    return found
