"""Launch Chrome for Testing under Playwright. Headless only in milestone M1."""
from playwright.sync_api import sync_playwright

from .env import chrome_path, chrome_version, playwright_version, proxy


class Browser:
    def __init__(self, use_proxy=True):
        self.path = chrome_path()
        self.version = chrome_version(self.path)
        self._pw = sync_playwright().start()
        options = {"executable_path": self.path, "headless": True}
        if use_proxy and proxy():
            # Every request goes through the session's proxy, certificate checks on,
            # except this machine's own servers (a local Jupyter, the selftest), which
            # the proxy cannot reach. Playwright would otherwise send loopback through it.
            options["proxy"] = {"server": proxy(), "bypass": "localhost,127.0.0.1"}
        self._browser = self._pw.chromium.launch(**options)

    @property
    def label(self):
        return f"{self.version} (headless, Playwright {playwright_version()})"

    def context(self, fig):
        width, height = fig["window"]
        return self._browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=fig["scale"],
            user_agent=fig["user_agent"],
            java_script_enabled=fig["javascript"],
            locale="en-US",
            timezone_id="America/Denver",
        )

    def close(self):
        self._browser.close()
        self._pw.stop()
