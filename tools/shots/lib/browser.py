"""Chrome for Testing under Playwright: headless, or headed on a virtual display.

The User-Agent goes to Chrome as its own `--user-agent` flag. Playwright's
`user_agent` option also rewrites the User-Agent Client Hints (`Sec-CH-UA-*`),
and for a string that names no operating system it claims Windows. With the
flag, the hints report the machine the capture runs on.
"""
from playwright.sync_api import sync_playwright

from .env import chrome_path, chrome_version, playwright_version, proxy
from .recipes import DEFAULTS


class Browser:
    def __init__(self, use_proxy=True):
        self.path = chrome_path()
        self.version = chrome_version(self.path)
        self.playwright = sync_playwright().start()
        options = {"executable_path": self.path, "headless": True,
                   "args": [f"--user-agent={DEFAULTS['user_agent']}"]}
        if use_proxy and proxy():
            # Every request goes through the session's proxy, certificate checks on,
            # except this machine's own servers (a local Jupyter, the selftest), which
            # the proxy cannot reach. Playwright would otherwise send loopback through it.
            options["proxy"] = {"server": proxy(), "bypass": "localhost,127.0.0.1"}
        self._browser = self.playwright.chromium.launch(**options)
        self._display = None

    @property
    def label(self):
        return f"{self.version} (headless, Playwright {playwright_version()})"

    def context(self, fig):
        width, height = fig["window"]
        options = {"viewport": {"width": width, "height": height}, "device_scale_factor": fig["scale"],
                   "java_script_enabled": fig["javascript"], "locale": "en-US",
                   "timezone_id": "America/Denver"}
        if fig["user_agent"] != DEFAULTS["user_agent"]:
            options["user_agent"] = fig["user_agent"]   # a recipe's own; Playwright then writes its Client Hints
        return self._browser.new_context(**options)

    def display(self, width, height):
        """A virtual display at least width x height screen pixels, made on first use."""
        from .display import Display
        if self._display and not self._display.fits(width, height):
            self._display.close()
            self._display = None
        if self._display is None:
            self._display = Display(width, height)
        return self._display

    def close(self):
        self._browser.close()
        if self._display:
            self._display.close()
        self.playwright.stop()
