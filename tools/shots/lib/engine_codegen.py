"""The codegen engine: Playwright's recorder, the tool `playwright codegen` opens, fed real clicks.

For a figure whose subject is codegen (`engine: codegen`): the recording
browser, with the recorder's toolbar and the locator under the pointer, and
the Playwright Inspector with the Python it wrote.

The `playwright codegen` command itself can't run here: it launches
Playwright's own Chromium build, and the toolkit never runs `playwright
install`. So the engine does what the command does, in Chrome for Testing at
the pinned version: it launches the browser, turns on the recorder the
command turns on (the driver's `enableRecorder`: Python, recording), and
opens the page. The recorder opens the Inspector in the same browser build.
Clicks are real (xdotool), so the recorder writes a line for each, as it
would for a person.

It all runs in a child process (`python -m lib.engine_codegen job.json`),
whose Playwright driver opens both windows on the virtual display. Chrome
takes its scale from GDK_SCALE there, because the Inspector's window accepts
no switches.

Steps:

    - wait: {text: '...'} / {selector: '...'} / {url: '**/author/**'}
    - click: {selector: 'a.tag', text: 'change'}   a real click; the recorder writes a line.
          A click waits until `pause[0]` seconds have passed since the last page load.
    - click: {role: link, name: '(about)'}
    - scroll: {selector: 'h3', offset: 70}         not recorded, as a wheel isn't
    - pointer: {selector: 'h3.author-title'}       the real pointer: the recorder highlights
                                                   the element and shows its locator
    - settle: 1

Recipe keys it reads besides the usual ones:

    window: [800, 250]                 the recording browser's window
    inspector: {window: [800, 595], at: below}   or `at: right`
    https_upgrades: true               Chrome's HTTPS-Upgrades on, as in regular Chrome
    expect: {code: ['name="change"']}  lines the recorder must have written

The crop is in screen CSS pixels from the browser window's top-left corner,
so it can take in both windows. Text sizes: the page's, measured, and the
Inspector's, from its own stylesheet (code and interface sizes) and the
script it wrote, since the Inspector is out of reach of any client.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from .env import TOOL, playwright_version, proxy
from .recipes import CODEGEN_STEPS as STEPS

# Playwright 1.63.0's own `--disable-features` switch (server/chromium/chromiumSwitches.ts).
# `https_upgrades: true` replaces it with the same list less HttpsUpgrades, so Chrome upgrades a
# plain-http link or redirect to https, as regular Chrome does. If Playwright's list changes,
# the switch no longer matches, the upgrade stays off, and a recipe's `expect` fails the take.
PLAYWRIGHT_DISABLED_FEATURES = (
    "AvoidUnnecessaryBeforeUnloadCheckSync,DestroyProfileOnBrowserClose,DialMediaRouteProvider,"
    "GlobalMediaControls,HttpsUpgrades,LensOverlay,MediaRouter,PaintHolding,ThirdPartyStoragePartitioning,"
    "BlockOriginHeaderModificationOnRedirect,Translate,AutoDeElevate,OptimizationHints,msForceBrowserSignIn,"
    "msEdgeUpdateLaunchServicesPreferredVersion")
INSPECTOR_TITLE = "Playwright Inspector"


def inspector_sizes():
    """The Inspector's code and interface font sizes, in CSS pixels, from its own stylesheet."""
    import playwright
    assets = Path(playwright.__file__).parent / "driver" / "package" / "lib" / "vite" / "recorder" / "assets"
    sizes = {}
    for css in assets.glob("index-*.css"):
        text = css.read_text()
        for name, var in (("code", "--vscode-editor-font-size"), ("ui", "--vscode-font-size")):
            found = re.search(re.escape(var) + r":\s*([\d.]+)px", text)
            if found:
                sizes[name] = float(found.group(1))
    return sizes


def geometry(fig):
    """(browser window, inspector window and its position), in CSS pixels."""
    bw, bh = fig["window"]
    spec = fig.get("inspector") or {}
    iw, ih = spec.get("window", [bw, 600])
    ix, iy = (bw, 0) if spec.get("at", "below") == "right" else (0, bh)
    return (bw, bh), (iw, ih, ix, iy)


def screen_size(fig):
    (bw, bh), (iw, ih, ix, iy) = geometry(fig)
    return max(bw, ix + iw) * fig["scale"], max(bh, iy + ih) * fig["scale"]


# ----------------------------------------------------------------- the parent's side
def attempt(browser, fig, display, png):
    """One attempt, in a child process; returns a dict like lib/headed.py's."""
    job = png.with_suffix(".job.json")
    out = png.with_suffix(".result.json")
    job.write_text(json.dumps({"fig": fig, "png": str(png), "result": str(out), "chrome": browser.path,
                               "script": str(png.with_suffix(".recorded.py"))}, default=str))
    env = {**display.env, "GDK_SCALE": str(fig["scale"])}
    result = {"status": None, "problems": [], "temporary": False, "clip": None, "final_url": None,
              "steps": [], "error": None, "anchors": {}, "text": None}
    try:
        run = subprocess.run([sys.executable, "-m", "lib.engine_codegen", str(job)], cwd=TOOL, env=env,
                             capture_output=True, text=True, timeout=fig["timeout"] * 6 + 120)
    except subprocess.TimeoutExpired:
        result["error"] = "the codegen session did not finish in time"
        return result
    finally:
        job.unlink(missing_ok=True)
    if not out.exists():
        tail = (run.stderr or run.stdout).strip().splitlines()[-1:] or ["no output"]
        result["error"] = f"the codegen session failed: {tail[0][:300]}"
        return result
    result.update(json.loads(out.read_text()))
    out.unlink()
    return result


def label(browser):
    return f"{browser.version} (headed on Xvfb, Playwright {playwright_version()}'s recorder)"


# ----------------------------------------------------------------- the child's side
class Session:
    def __init__(self, job):
        from playwright.sync_api import sync_playwright
        self.fig, self.job = job["fig"], job
        self.S = self.fig["scale"]
        (self.bw, self.bh), (self.iw, self.ih, self.ix, self.iy) = geometry(self.fig)
        self.pw = sync_playwright().start()
        args = ["--window-position=0,0", f"--window-size={self.bw},{self.bh}",
                f"--user-agent={self.fig['user_agent']}"]
        options = {"executable_path": job["chrome"], "headless": False, "args": args}
        if self.fig.get("https_upgrades"):
            options["ignore_default_args"] = ["--disable-features=" + PLAYWRIGHT_DISABLED_FEATURES]
            args.append("--disable-features=" + PLAYWRIGHT_DISABLED_FEATURES.replace("HttpsUpgrades,", ""))
        if proxy():
            options["proxy"] = {"server": proxy(), "bypass": "localhost,127.0.0.1"}
        self.browser = self.pw.chromium.launch(**options)
        self.context = self.browser.new_context(no_viewport=True, java_script_enabled=self.fig["javascript"])
        # What `playwright codegen --target python` turns on; the recorder writes its script here.
        self.context._sync(self.context._impl_obj._channel.send("enableRecorder", None, {
            "language": "python", "mode": "recording", "outputFile": job["script"],
            "launchOptions": {"headless": False}, "contextOptions": {}, "handleSIGINT": False}))
        self.page = self.context.new_page()           # recorded, as the command's first page is
        self.last_load = 0.0
        self.pointer_placed = False

    def xdo(self, *args):
        return subprocess.run(["xdotool", *[str(a) for a in args]], capture_output=True, text=True,
                              timeout=60, check=True).stdout.strip()

    def place_inspector(self):
        """Put the Inspector's window where the recipe says: below the browser, or to its right."""
        deadline = time.monotonic() + self.fig["timeout"]
        while True:
            found = subprocess.run(["xdotool", "search", "--name", INSPECTOR_TITLE], capture_output=True,
                                   text=True, timeout=30).stdout.split()
            if found:
                break
            if time.monotonic() > deadline:
                names = [self._name(w) for w in subprocess.run(["xdotool", "search", "--name", "."],
                                                              capture_output=True, text=True).stdout.split()]
                raise subprocess.CalledProcessError(1, "xdotool", f"no window named {INSPECTOR_TITLE!r} "
                                                                   f"(windows: {sorted(set(names))})")
            time.sleep(0.5)
        wid = found[-1]
        self.xdo("windowsize", wid, self.iw * self.S, self.ih * self.S)
        self.xdo("windowmove", wid, self.ix * self.S, self.iy * self.S)
        time.sleep(1.0)

    def _name(self, wid):
        return subprocess.run(["xdotool", "getwindowname", wid], capture_output=True, text=True).stdout.strip()

    def bars(self):
        return self.page.evaluate("outerHeight - innerHeight")

    def box(self, arg):
        from . import steps as page_steps
        if "role" in arg:
            target = self.page.get_by_role(arg["role"], name=arg.get("name"), exact=True)
        elif "selector" in arg and "text" in arg:
            target = self.page.locator(arg["selector"], has_text=page_steps.pattern(arg["text"]))
        else:
            target = page_steps.target(self.page, arg)
        if target is None:
            raise page_steps.StepError(f"needs role and name, selector, or text: {arg!r}")
        target = target.first
        target.wait_for(state="visible", timeout=self.fig["timeout"] * 1000)
        target.scroll_into_view_if_needed(timeout=self.fig["timeout"] * 1000)
        return target.bounding_box()

    def screen_point(self, box, at=(0.5, 0.5)):
        top = self.bars()
        return (round((box["x"] + box["width"] * at[0]) * self.S),
                round((top + box["y"] + box["height"] * at[1]) * self.S))

    def loaded(self):
        self.page.wait_for_load_state("load", timeout=self.fig["timeout"] * 1000)
        self.last_load = time.monotonic()

    # ------------------------------------------------------------- steps
    def wait(self, arg):
        from . import steps as page_steps
        if "url" in arg:
            self.page.wait_for_url(arg["url"], timeout=self.fig["timeout"] * 1000)
            self.loaded()
        elif "text" in arg:
            self.page.get_by_text(page_steps.pattern(arg["text"])).first.wait_for(timeout=self.fig["timeout"] * 1000)
        else:
            self.page.locator(arg["selector"]).first.wait_for(timeout=self.fig["timeout"] * 1000)

    def click(self, arg):
        rest = self.fig["pause"][0] - (time.monotonic() - self.last_load)
        if rest > 0:
            time.sleep(rest)                  # page loads on one host, `pause[0]` seconds apart
        x, y = self.screen_point(self.box(arg), arg.get("at", (0.5, 0.5)))
        self.xdo("mousemove", x, y)
        time.sleep(0.6)                       # the recorder highlights what is under the pointer
        self.xdo("click", 1)
        time.sleep(0.5)

    def scroll(self, arg):
        box = self.box(arg)
        self.page.evaluate("dy => window.scrollBy(0, dy)", box["y"] - arg.get("offset", 0))
        time.sleep(0.5)

    def pointer(self, arg):
        x, y = self.screen_point(self.box(arg), arg.get("at", (0.5, 0.5)))
        self.xdo("mousemove", x, y)
        time.sleep(1.5)                       # the locator appears under the element
        self.pointer_placed = True

    def run(self, log):
        for step in self.fig.get("steps") or []:
            (name, arg), = step.items()
            if name == "settle":
                time.sleep(float(arg))
            else:
                getattr(self, name)(arg)
            log.append(name)

    # ------------------------------------------------------------- the picture
    def park(self):
        """Park the pointer over the Inspector's lower panel, outside the page: over the page, the
        recorder would highlight whatever it rested on."""
        if not self.pointer_placed:
            self.xdo("mousemove", round((self.ix + self.iw / 2) * self.S), round((self.iy + self.ih - 20) * self.S))
            time.sleep(1.0)

    def crop_rect(self):
        crop = self.fig.get("crop") or {}
        width, height = max(self.bw, self.ix + self.iw), max(self.bh, self.iy + self.ih)
        left, top = crop.get("left", 0), crop.get("top", 0)
        return (left * self.S, top * self.S, (left + crop.get("width", width - left)) * self.S,
                (top + crop.get("height", height - top)) * self.S)

    def page_sizes(self, rect):
        """Sizes of the page's text inside the crop, in image pixels."""
        from . import measure
        S, top = self.S, self.bars()
        width, height = self.page.evaluate("[innerWidth, innerHeight]")
        region = [max(0, rect[0] / S), max(0, rect[1] / S - top), min(width, rect[2] / S),
                  min(height, rect[3] / S - top)]
        return measure.scaled(self.page.evaluate(measure.TEXT_SIZES, region), S)

    def inspector_text(self, rect, script):
        """The Inspector's code and toolbar, if the crop reaches its window: its sizes from its own
        stylesheet, and as many characters as the script it wrote."""
        known = inspector_sizes()
        if not known.get("code") or not (rect[2] / self.S > self.ix and rect[3] / self.S > self.iy):
            return {}
        code = sum(len(line.replace(" ", "")) for line in script.splitlines())
        return {round(known["code"] * self.S, 1): code,
                round(known.get("ui", known["code"]) * self.S, 1): len("RecordTarget:Library")}

    def grab(self, png, rect):
        from PIL import Image
        raw = Path(png).with_suffix(".raw.png")
        subprocess.run(["import", "-display", os.environ["DISPLAY"], "-window", "root", str(raw)],
                       check=True, capture_output=True, timeout=60)
        with Image.open(raw) as img:
            img.crop(rect).save(png)
        raw.unlink()
        return {"x": rect[0] / self.S, "y": rect[1] / self.S,
                "width": (rect[2] - rect[0]) / self.S, "height": (rect[3] - rect[1]) / self.S}

    def close(self):
        try:
            self.context.close()
            self.browser.close()
        finally:
            self.pw.stop()


def main(job):
    from . import guards, measure
    from . import steps as page_steps
    fig = job["fig"]
    page_sizes = rect = None
    result = {"status": None, "problems": [], "temporary": False, "clip": None, "final_url": None,
              "steps": [], "error": None, "anchors": {}, "text": None,
              "engine": {"name": "codegen", "playwright": playwright_version(), "language": "python",
                         "inspector": {"window": list(geometry(fig)[1][:2]),
                                       "at": (fig.get("inspector") or {}).get("at", "below")}}}
    script = Path(job["script"])
    session = Session(job)
    try:
        try:
            response = session.page.goto(fig["url"], wait_until="load", timeout=fig["timeout"] * 1000)
            session.last_load = time.monotonic()
        except Exception as e:
            result["error"] = str(e).splitlines()[0]
            return result
        status = result["status"] = response.status if response else None
        if guards.retryable(status=status):
            result.update(problems=[f"HTTP status {status}"], temporary=True)
            return result
        problems = result["problems"]
        try:
            session.place_inspector()
            session.run(result["steps"])
        except page_steps.StepError as e:
            problems.append(str(e).splitlines()[0])
        except subprocess.CalledProcessError as e:
            problems.append(str(e.output or e).splitlines()[0])
        except Exception as e:                        # a Playwright wait that timed out
            problems.append(f"step failed: {str(e).splitlines()[0]}")
        time.sleep(fig["settle"])
        text = session.page.evaluate("() => document.body ? document.body.innerText : ''")
        issues, result["temporary"] = guards.page_problems(status, session.page.title(), text,
                                                           {k: v for k, v in (fig.get("expect") or {}).items()
                                                            if k != "code"})
        problems += issues
        for want in (fig.get("expect") or {}).get("text") or []:
            if session.page.get_by_text(page_steps.pattern(want)).count() == 0:
                problems.append(f"expected text /{want}/ not found")
        result["final_url"] = session.page.url
        session.park()
        rect = session.crop_rect()
        result["clip"] = session.grab(job["png"], rect)
        page_sizes = session.page_sizes(rect)
        return result
    finally:
        session.close()
        # The recorder writes its whole script when the browser closes.
        written = script.read_text() if script.exists() else ""
        result["recorded"] = written
        if page_sizes is not None:
            result["text"] = measure.summarize(measure.merge(page_sizes, session.inspector_text(rect, written)))
        for want in (fig.get("expect") or {}).get("code") or []:
            if want not in written:
                result["problems"].append(f"the recorder did not write {want!r}")
        script.unlink(missing_ok=True)
        Path(job["result"]).write_text(json.dumps(result))


if __name__ == "__main__":
    main(json.loads(Path(sys.argv[1]).read_text()))
