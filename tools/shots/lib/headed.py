"""Headed capture: a real Chrome window on a virtual display, DevTools included.

For figures that show browser UI: DevTools, View Source, menus. Each attempt
gets a fresh browser profile carrying the recipe's DevTools settings, a
window at a known place and size, and a debugging port for reading DevTools.

Steps a headed recipe can use, besides the page steps in lib/steps.py:

    - inspect: {selector: '#comic img'}   right-click the element, choose Inspect
          selects: 'id="comic"'             ...and wait until the selected node matches
    - tree: {keys: [Down, Right]}          keys in the Elements tree
    - tree: {keys: [Left], until: 'id="wm-ipp-base"', max: 12}
    - devtools_click: {text: '^Fetch/XHR$'}    find it in DevTools by its text, click it
    - devtools_wait: {text: 'quotes\\?page=4'}  wait until DevTools shows it
    - key: 'ctrl+f'   /   type: 'var data'  real keys, sent to the browser window
    - pointer: {selector: '#comic img'}    rest the real pointer on it (tooltips)

The pointer is parked outside the window before the screen is grabbed, unless
the last step placed it on purpose.
"""
import json
import re
import shutil
import socket
import time

from PIL import Image

from . import crop as page_crop
from . import devtools as dt
from . import guards, measure
from . import steps as page_steps
from .env import OUT, playwright_version, proxy


class HeadedError(Exception):
    pass


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Session:
    """One headed browser for one attempt at one figure."""

    def __init__(self, browser, fig, display):
        self.fig, self.display = fig, display
        self.W, self.H = fig["window"]
        self.S = fig["scale"]
        self.devtools = fig.get("devtools")
        self.profile = OUT / ".profiles" / fig["id"]
        shutil.rmtree(self.profile, ignore_errors=True)
        (self.profile / "Default").mkdir(parents=True)
        if self.devtools:
            (self.profile / "Default" / "Preferences").write_text(json.dumps(dt.preferences(self.devtools)))
        self.port = _free_port()
        args = ["--window-position=0,0", f"--window-size={self.W},{self.H}",
                f"--force-device-scale-factor={self.S}", f"--remote-debugging-port={self.port}",
                "--no-first-run", "--no-default-browser-check"]
        if self.devtools:
            args.append("--auto-open-devtools-for-tabs")
        options = {"executable_path": browser.path, "headless": False, "no_viewport": True,
                   "env": display.env, "args": args, "user_agent": fig["user_agent"],
                   "java_script_enabled": fig["javascript"],
                   # No "controlled by automated test software" bar across the window.
                   "ignore_default_args": ["--enable-automation"]}
        if proxy():
            options["proxy"] = {"server": proxy(), "bypass": "localhost,127.0.0.1"}
        self.context = browser.playwright.chromium.launch_persistent_context(str(self.profile), **options)
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        self.frontend = None
        self.pointer_placed = False

    # ------------------------------------------------------------- geometry
    def _frontend(self):
        if self.frontend is None:
            self.frontend = dt.Frontend(self.port)
        return self.frontend

    def toolbar(self):
        """Height of the browser's own bars above the page, in DIPs."""
        if self.devtools:
            # Docked DevTools spans the whole area below the bars.
            found = self._frontend().find(css="body")
            return self.H - found["height"] * (found["dpr"] / self.S)
        return self.page.evaluate("window.outerHeight - window.innerHeight")

    def page_point(self, box, at=(0.5, 0.5)):
        top = self.toolbar()
        return (round((box["x"] + box["width"] * at[0]) * self.S),
                round((top + box["y"] + box["height"] * at[1]) * self.S))

    def devtools_point(self, box, dpr, at=(0.5, 0.5)):
        top = self.toolbar()
        return (round((box["x"] + box["w"] * at[0]) * dpr),
                round(top * self.S + (box["y"] + box["h"] * at[1]) * dpr))

    # ------------------------------------------------------------- steps
    def _box(self, arg):
        target = page_steps.target(self.page, arg)
        if target is None:
            raise page_steps.StepError(f"needs selector or text: {arg!r}")
        target.wait_for(state="visible", timeout=self.fig["timeout"] * 1000)
        target.scroll_into_view_if_needed(timeout=self.fig["timeout"] * 1000)
        box = target.bounding_box()
        if not box:
            raise page_steps.StepError(f"{arg!r} has no box on the page")
        return box

    PICKER = '[aria-label^="Select an element"]'

    def inspect(self, arg):
        """Select a page element in DevTools with real clicks.

        The default is DevTools' element picker (its "Select an element" button,
        then a click on the element), because each click can be checked. With
        `via: menu` it right-clicks and chooses Inspect instead; the context menu
        has no DOM to wait on, so that route cannot confirm the menu opened.
        """
        x, y = self.page_point(self._box(arg), arg.get("at", (0.5, 0.5)))
        front = self._frontend()
        pattern = arg.get("selects")
        chosen = ""
        for _ in range(2):                   # one retry, for a click DevTools missed
            if arg.get("via", "picker") == "picker":
                self.devtools_click({"css": self.PICKER})
                try:
                    front.wait_for(css=self.PICKER + '[aria-pressed="true"]', timeout=5)
                except dt.DevToolsError:
                    continue                 # the picker did not switch on; try again
                self.display.xdo("mousemove", x, y)
                time.sleep(0.4)
                self.display.xdo("click", 1)
            else:
                self.display.xdo("mousemove", x, y)
                time.sleep(0.3)
                self.display.xdo("click", 3)
                time.sleep(1.2)
                self.display.xdo("key", "Up")    # Inspect is the menu's last item
                self.display.xdo("key", "Return")
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                chosen = front.selected()
                if chosen and (not pattern or re.search(pattern, chosen)):
                    return
                time.sleep(0.3)
        raise page_steps.StepError(f"Inspect did not select {pattern or 'a node'} (selected: {chosen[:80]!r})")

    def ready(self):
        """Wait until the page has loaded and DevTools has drawn its Elements tree.

        DevTools selects <body> once the tree is ready; a pick made before that
        is undone when DevTools finishes loading.
        """
        try:
            self.page.wait_for_load_state("load", timeout=self.fig["timeout"] * 1000)
        except Exception:
            pass                             # a slow subresource; the tree check below decides
        self._frontend().wait_for(css='li[role="treeitem"].selected', timeout=self.fig["timeout"])

    def tree(self, arg):
        keys = arg if isinstance(arg, list) else arg.get("keys", [])
        until, limit = (None, 1) if isinstance(arg, list) else (arg.get("until"), arg.get("max", 1))
        front = self._frontend()
        time.sleep(0.8)                      # let DevTools finish revealing a just-picked node
        self.focus_tree()
        seen = [front.selected()[:40]]
        for _ in range(limit if until else 1):
            if until and re.search(until, seen[-1]):
                return
            for key in keys:
                self.display.xdo("key", key)
                time.sleep(0.35)
            seen.append(front.selected()[:40])
        if until and not re.search(until, front.selected()):
            path = " > ".join(dict.fromkeys(seen))     # each distinct selection, in order
            raise page_steps.StepError(f"the Elements tree never selected /{until}/ "
                                       f"(focus: {front.evaluate(self._FOCUSED)!r}; went: {path})")

    # The deepest focused element in DevTools, through its shadow roots.
    _FOCUSED = """(() => { let a = document.activeElement;
        while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
        return a ? (a.getAttribute('role') || a.tagName.toLowerCase()) : ''; })()"""

    def focus_tree(self):
        """Give the Elements tree keyboard focus, as a person would: click the selected row.

        The click lands in the empty right-hand end of the row. Clicking the
        node's own text could start editing its tag, which swallows the keys.
        """
        front = self._frontend()
        found = front.selected_row()
        if not found:
            raise page_steps.StepError("the Elements tree has no selected row")
        r, t = found["row"], found["tree"]
        right_end = {"x": t["x"] + t["w"] - 16, "y": r["y"], "w": 1, "h": r["h"]}
        x, y = self.devtools_point(right_end, found["dpr"], (0, 0.5))
        self.display.xdo("mousemove", x, y)
        time.sleep(0.2)
        self.display.xdo("click", 1)
        time.sleep(0.4)
        focused = front.evaluate(self._FOCUSED)
        if focused not in ("tree", "treeitem"):
            raise page_steps.StepError(f"the Elements tree did not take focus (focus is on {focused!r})")

    def devtools_click(self, arg):
        found = self._frontend().wait_for(arg.get("text"), arg.get("css"), timeout=self.fig["timeout"])
        x, y = self.devtools_point(found["boxes"][0], found["dpr"], arg.get("at", (0.5, 0.5)))
        self.display.xdo("mousemove", x, y)
        time.sleep(0.2)
        self.display.xdo("click", arg.get("button", 1))
        time.sleep(0.4)

    def devtools_wait(self, arg):
        self._frontend().wait_for(arg.get("text"), arg.get("css"), timeout=self.fig["timeout"])

    def key(self, arg):
        self.display.xdo("key", arg)
        time.sleep(0.3)

    def type_text(self, arg):
        self.display.xdo("type", "--delay", 40, arg)
        time.sleep(0.3)

    def pointer(self, arg):
        x, y = self.page_point(self._box(arg), arg.get("at", (0.5, 0.5)))
        self.display.xdo("mousemove", x, y)
        self.pointer_placed = True

    def open_panel(self):
        """Show the recipe's DevTools panel; for Network, reload so the log is complete."""
        panel = (self.devtools or {}).get("panel", "elements")
        if panel == "elements":
            return
        name = f"^{panel.capitalize()}$"
        self.devtools_click({"text": name})
        self._frontend().wait_for(text=name, css='[role="tab"][aria-selected="true"]',
                                  timeout=self.fig["timeout"])
        if panel == "network":
            self.page.reload(wait_until="domcontentloaded", timeout=self.fig["timeout"] * 1000)

    def handlers(self):
        return {"inspect": self.inspect, "tree": self.tree, "devtools_click": self.devtools_click,
                "devtools_wait": self.devtools_wait, "key": self.key, "type": self.type_text,
                "pointer": self.pointer}

    # ------------------------------------------------------------- the picture
    def crop_rect(self):
        """The crop, in screen pixels."""
        crop = self.fig.get("crop") or {"window": True}
        S, W, H = self.S, self.W, self.H
        if crop.get("window"):
            return (0, 0, W * S, H * S)
        if crop.get("content"):                       # below the browser's bars
            top = self.toolbar()
            height = crop.get("height", H - top)
            return (0, round(top * S), round(crop.get("width", W) * S), round((top + height) * S))
        if "between" in crop:                         # e.g. two View Source line numbers
            first, last = (self._box({"selector": s}) for s in crop["between"])  # top of one, bottom of the other
            pad = crop.get("pad", 0)
            x0, y0 = self.page_point(first, (0, 0))
            _, y1 = self.page_point(last, (0, 1))
            width = crop.get("width", self.page.evaluate("innerWidth"))
            return (max(0, x0 - pad * S), max(0, y0 - pad * S), round(width * S), y1 + pad * S)
        if "selector" in crop:
            box = self._box(crop)
            x, y, w, h = page_crop.around((box["x"], box["y"], box["width"], box["height"]), crop)
            x0, y0 = self.page_point({"x": x, "y": y, "width": w, "height": h}, (0, 0))
            return (max(0, x0), max(0, y0), x0 + round(w * S), y0 + round(h * S))
        left, top = crop.get("left", 0), crop.get("top", 0)
        return (left * S, top * S, (left + crop.get("width", W - left)) * S,
                (top + crop.get("height", H - top)) * S)

    def park(self):
        """Park the pointer in the page's bottom-left corner, unless a step placed it on purpose.

        The page sees the pointer leave whatever it was over, so hover styles and
        DevTools' node highlight clear. (Parking it outside the window, or over
        the tab strip, leaves them showing.) With DevTools docked at the bottom,
        the page's corner is above DevTools, not the window's.
        """
        if self.pointer_placed:
            return
        bottom = self.toolbar() + self.page.evaluate("innerHeight") - 5
        self.display.xdo("mousemove", 5 * self.S, round(bottom * self.S))
        time.sleep(1.0)

    def measure(self, rect):
        """Anchors and text sizes inside the crop, in image pixels; and any anchor that failed."""
        S, top = self.S, self.toolbar()
        anchors, problems = {}, []
        for at in measure.marks_anchors(self.fig):
            try:
                if "xy" in at:
                    anchors[measure.key(at)] = measure.hand_box(at["xy"])
                    continue
                if "devtools" in at:
                    box, dpr = measure.devtools_boxes(self._frontend(), at["devtools"])
                    screen = [box[0] * dpr, top * S + box[1] * dpr, box[2] * dpr, top * S + box[3] * dpr]
                else:
                    box = measure.page_boxes(self.page, at, timeout=self.fig["timeout"])
                    screen = [box[0] * S, (top + box[1]) * S, box[2] * S, (top + box[3]) * S]
                anchors[measure.key(at)] = {"box": measure.shifted(screen, rect[0], rect[1])}
            except (measure.AnchorError, dt.DevToolsError) as e:
                problems.append(str(e))
        width, height = self.page.evaluate("[innerWidth, innerHeight]")
        region = [max(0, rect[0] / S), max(0, rect[1] / S - top),
                  min(width, rect[2] / S), min(height, rect[3] / S - top)]
        sizes = measure.scaled(self.page.evaluate(measure.TEXT_SIZES, region), S)
        if self.devtools:
            front = self._frontend()
            dpr = front.evaluate("devicePixelRatio")
            region = [rect[0] / dpr, (rect[1] - top * S) / dpr, rect[2] / dpr, (rect[3] - top * S) / dpr]
            found = front.evaluate(f"({measure.TEXT_SIZES})({json.dumps(region)})")
            sizes = measure.merge(sizes, measure.scaled(found, dpr))
        return anchors, measure.summarize(sizes), problems

    def grab(self, path, rect):
        raw = path.with_name(path.stem + ".raw.png")
        self.display.grab(raw)
        with Image.open(raw) as img:
            img.crop(rect).save(path)
        raw.unlink()
        return {"x": rect[0] / self.S, "y": rect[1] / self.S,
                "width": (rect[2] - rect[0]) / self.S, "height": (rect[3] - rect[1]) / self.S}

    def close(self):
        if self.frontend:
            self.frontend.close()
        self.context.close()
        shutil.rmtree(self.profile, ignore_errors=True)


def attempt(browser, fig, display, png):
    """One headed attempt, as a dict: status, problems, temporary, clip, final_url, steps,
    error, anchors, text (see capture._headless)."""
    session = Session(browser, fig, display)
    result = {"status": None, "problems": [], "temporary": False, "clip": None, "final_url": None,
              "steps": [], "error": None, "anchors": {}, "text": None}
    try:
        try:
            response = session.page.goto(fig["url"], wait_until="domcontentloaded",
                                         timeout=fig["timeout"] * 1000)
        except Exception as e:
            result["error"] = str(e).splitlines()[0]
            return result
        status = result["status"] = response.status if response else None
        result["final_url"] = session.page.url
        if guards.retryable(status=status):
            result.update(problems=[f"HTTP status {status}"], temporary=True)
            return result
        problems = result["problems"]
        try:
            if session.devtools:
                session.ready()
                session.open_panel()
            page_steps.run(session.page, fig, result["steps"], extra=session.handlers())
        except (page_steps.StepError, dt.DevToolsError) as e:
            problems.append(str(e))
        time.sleep(fig["settle"])
        text = session.page.evaluate("() => document.body ? document.body.innerText : ''")
        issues, result["temporary"] = guards.page_problems(status, session.page.title(), text,
                                                           fig.get("expect") or {})
        problems += issues
        expect = fig.get("expect") or {}
        for text in expect.get("text") or []:
            if session.page.get_by_text(page_steps.pattern(text)).count() == 0:
                problems.append(f"expected text /{text}/ not found")
        result["final_url"] = session.page.url
        try:
            session.park()
            rect = session.crop_rect()
            result["anchors"], result["text"], missed = session.measure(rect)
            problems += missed
            result["clip"] = session.grab(png, rect)
        except (page_steps.StepError, page_crop.CropError) as e:
            problems.append(f"crop failed: {e}")
        return result
    finally:
        session.close()


def label(browser):
    return f"{browser.version} (headed on Xvfb, Playwright {playwright_version()})"
