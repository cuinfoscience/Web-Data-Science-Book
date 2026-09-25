"""The Selenium engine: the window `webdriver.Chrome()` opens, driven by Selenium alone.

For a figure whose subject is that window (`engine: selenium`), as chapter 8
teaches it: Selenium Manager finds Chrome for Testing at the pinned version and
its ChromeDriver, and Chrome opens headed on the virtual display with its own
bars, including Chrome for Testing's "only for automated testing" notice. The
toolkit adds nothing to the window: no DevTools, and no `--disable-infobars`.
ChromeDriver passes `--test-type`, so running as root with `--no-sandbox` adds
no warning of its own.

Every command goes through Selenium, so a caption can say "driven by Selenium".
The steps it runs:

    - wait: {text: 'Voyager'}              a regular expression in the page's text
    - wait: {selector: '#comic img'}       a CSS selector, displayed
    - scroll: {y: 400}   /   scroll: {selector: '#comic'}
    - pointer: {selector: '#comic img'}    rest the real pointer on it (a tooltip)
    - settle: 1.5

The crop is the whole window (the default), or `{top, left, width, height}`
in the window's CSS pixels, counted from its top-left corner. Only the page's
text is measured: Chrome's own bars aren't in the page.
"""
import os
import time

from PIL import Image

from . import guards, measure
from . import steps as page_steps
from .env import CHROME_VERSION, proxy
from .headed import BARS, BARS_SLACK
from .recipes import SELENIUM_STEPS as STEPS

# The navigation's HTTP status, which WebDriver doesn't report.
STATUS = """const n = performance.getEntriesByType('navigation')[0];
            return n && n.responseStatus ? n.responseStatus : null;"""


class Session:
    """One Selenium-driven Chrome for one attempt at one figure."""

    def __init__(self, fig, display):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        self.fig, self.display = fig, display
        self.W, self.H = fig["window"]
        self.S = fig["scale"]
        options = webdriver.ChromeOptions()
        options.browser_version = CHROME_VERSION          # Selenium Manager resolves it, as in the chapter
        args = ["--window-position=0,0", f"--window-size={self.W},{self.H}",
                f"--force-device-scale-factor={self.S}", f"--user-agent={fig['user_agent']}",
                "--no-first-run", "--no-default-browser-check"]
        if os.geteuid() == 0:
            args.append("--no-sandbox")                   # Chrome refuses root without it
        if proxy():
            args += [f"--proxy-server={proxy()}", "--proxy-bypass-list=localhost;127.0.0.1"]
        for arg in args:
            options.add_argument(arg)
        if not fig["javascript"]:
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.javascript": 2})
        self.driver = webdriver.Chrome(options=options, service=Service(env=display.env))
        self.driver.set_page_load_timeout(fig["timeout"])
        self.pointer_placed = False

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)

    def bars(self):
        """Height of the browser's own bars above the page, in CSS pixels."""
        return self.js("return window.outerHeight - window.innerHeight")

    def bars_problems(self, result):
        bars = result["bars"] = round(self.bars(), 1)
        infobar = bars > BARS + BARS_SLACK
        if (self.fig.get("expect") or {}).get("infobar"):
            return [] if infobar else ["the recipe expects an infobar above the page, and there is none"]
        if infobar:
            return [f"the browser's bars above the page are {bars:.0f} pixels tall, {bars - BARS:.0f} more than "
                    "its tab strip and address bar: an infobar is in the way"]
        return []

    # ------------------------------------------------------------- steps
    def _element(self, arg):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as ec
        from selenium.webdriver.support.ui import WebDriverWait
        if "selector" not in arg:
            raise page_steps.StepError(f"needs a selector: {arg!r}")
        try:
            return WebDriverWait(self.driver, self.fig["timeout"]).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, arg["selector"])))
        except Exception:
            raise page_steps.StepError(f"{arg['selector']!r} did not show within {self.fig['timeout']}s")

    def wait(self, arg):
        if "text" in arg:
            want = page_steps.pattern(arg["text"])
            deadline = time.monotonic() + self.fig["timeout"]
            while not want.search(self.text()):
                if time.monotonic() > deadline:
                    raise page_steps.StepError(f"text /{arg['text']}/ did not appear")
                time.sleep(0.3)
        else:
            self._element(arg)

    def scroll(self, arg):
        if "selector" in arg:
            self.js("arguments[0].scrollIntoView({block: 'start'})", self._element(arg))
        else:
            self.js("window.scrollBy(0, arguments[0])", arg.get("y", 0))
        time.sleep(0.4)

    def pointer(self, arg):
        """The real pointer on an element, so the page and Chrome see a person's hover."""
        box = self.js("const r = arguments[0].getBoundingClientRect(); return [r.x, r.y, r.width, r.height]",
                      self._element(arg))
        at = arg.get("at", (0.5, 0.5))
        top = self.bars()
        self.display.xdo("mousemove", round((box[0] + box[2] * at[0]) * self.S),
                         round((top + box[1] + box[3] * at[1]) * self.S))
        time.sleep(1.5)                      # a native tooltip takes a moment
        self.pointer_placed = True

    def run(self, log):
        for step in self.fig.get("steps") or []:
            (name, arg), = step.items()
            if name not in STEPS:
                raise page_steps.StepError(f"the selenium engine has no `{name}` step")
            if name == "settle":
                time.sleep(float(arg))
            else:
                getattr(self, name)(arg)
            log.append(name)

    # ------------------------------------------------------------- the picture
    def text(self):
        return self.js("return document.body ? document.body.innerText : ''") or ""

    def park(self):
        """Park the pointer in the page's bottom-left corner, where it points at nothing, unless a
        step placed it on purpose. (It starts at the screen's middle, over whatever is there.)"""
        if self.pointer_placed:
            return
        bottom = self.bars() + self.js("return innerHeight") - 3
        self.display.xdo("mousemove", 2 * self.S, round(bottom * self.S))
        time.sleep(1.0)                      # the link preview at the bottom fades out

    def crop_rect(self):
        crop = self.fig.get("crop") or {"window": True}
        S, W, H = self.S, self.W, self.H
        if crop.get("window"):
            return (0, 0, W * S, H * S)
        left, top = crop.get("left", 0), crop.get("top", 0)
        return (left * S, top * S, (left + crop.get("width", W - left)) * S, (top + crop.get("height", H - top)) * S)

    def measure(self, rect):
        """Sizes of the page's text inside the crop, in image pixels."""
        S, top = self.S, self.bars()
        width, height = self.js("return [innerWidth, innerHeight]")
        region = [max(0, rect[0] / S), max(0, rect[1] / S - top), min(width, rect[2] / S), min(height, rect[3] / S - top)]
        sizes = self.js(f"return ({measure.TEXT_SIZES})(arguments[0])", region) or {}
        return measure.summarize(measure.scaled(sizes, S))

    def grab(self, path, rect):
        raw = path.with_name(path.stem + ".raw.png")
        self.display.grab(raw)
        with Image.open(raw) as img:
            img.crop(rect).save(path)
        raw.unlink()
        return {"x": rect[0] / self.S, "y": rect[1] / self.S,
                "width": (rect[2] - rect[0]) / self.S, "height": (rect[3] - rect[1]) / self.S}

    def versions(self):
        caps = self.driver.capabilities
        return caps.get("browserVersion"), (caps.get("chrome") or {}).get("chromedriverVersion", "").split(" ")[0]

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


def attempt(browser, fig, display, png):
    """One attempt, as a dict like lib/headed.py's: status, problems, temporary, clip,
    final_url, steps, error, anchors, text, bars."""
    result = {"status": None, "problems": [], "temporary": False, "clip": None, "final_url": None,
              "steps": [], "error": None, "anchors": {}, "text": None, "bars": None}
    try:
        session = Session(fig, display)
    except Exception as e:
        result["error"] = f"Selenium could not start Chrome: {str(e).splitlines()[0]}"
        return result
    try:
        try:
            session.driver.get(fig["url"])
        except Exception as e:
            result["error"] = str(e).splitlines()[0]
            return result
        result["engine"] = {"name": "selenium", "selenium": selenium_version(),
                            **dict(zip(("browser", "chromedriver"), session.versions()))}
        status = result["status"] = session.js(STATUS)
        result["final_url"] = session.driver.current_url
        if guards.retryable(status=status):
            result.update(problems=[f"HTTP status {status}"], temporary=True)
            return result
        problems = result["problems"]
        problems += session.bars_problems(result)
        try:
            session.run(result["steps"])
        except page_steps.StepError as e:
            problems.append(str(e))
        time.sleep(fig["settle"])
        text = session.text()
        issues, result["temporary"] = guards.page_problems(status, session.driver.title, text,
                                                           fig.get("expect") or {})
        problems += issues
        for want in (fig.get("expect") or {}).get("text") or []:
            if not page_steps.pattern(want).search(text):
                problems.append(f"expected text /{want}/ not found")
        result["final_url"] = session.driver.current_url
        session.park()
        rect = session.crop_rect()
        result["text"] = session.measure(rect)
        result["clip"] = session.grab(png, rect)
        return result
    finally:
        session.close()


def selenium_version():
    import selenium
    return selenium.__version__


def label(browser):
    return f"{browser.version} (headed on Xvfb, driven by Selenium {selenium_version()})"

