"""DevTools: its settings, and reading its own page to find things on screen.

Settings go into the browser profile before launch (the keys the week-06
handout capture found: dock side, the open panel, split sizes, zoom, and the
"what's new" note marked as seen).

Docked DevTools is itself a web page (devtools://devtools/...). With the
browser's debugging port open, the toolkit reads that page's DOM, through its
shadow roots, to find where a panel, a request row, or a header name is
drawn, and clicks it for real with xdotool. No pixel offsets are typed in.
"""
import json
import math
import time
import urllib.request

from websockets.sync.client import connect

from .env import CHROME_VERSION

DOCKS = {"right", "bottom", "left"}
PANELS = {"elements", "network", "console", "sources"}


def preferences(devtools):
    """The profile's Default/Preferences for a recipe's `devtools:` block.

    DevTools 154 honors the dock side, split sizes, and zoom from here, but not
    the open panel; lib/headed.py clicks the panel's tab instead.
    """
    zoom = float(devtools.get("zoom", 1.0))
    prefs = {
        "currentDockState": json.dumps(devtools.get("dock", "right")),
        "panel-selectedTab": json.dumps(devtools.get("panel", "elements")),
        "releaseNoteVersionSeen": str(CHROME_VERSION),
    }
    if "size" in devtools:         # the DevTools pane's width (docked right or left) or height (bottom)
        axis = "horizontal" if devtools.get("dock") == "bottom" else "vertical"
        prefs["inspector-view.split-view-state"] = json.dumps({axis: {"size": devtools["size"]}})
    if "sidebar" in devtools:      # the Styles sidebar's width
        prefs["elements.styles.sidebar.width"] = json.dumps({"vertical": {"size": devtools["sidebar"]}})
    return {
        "devtools": {"preferences": prefs},
        # Chrome stores zoom as a level: factor = 1.2 ** level.
        "partition": {"per_host_zoom_levels": {"x": {"devtools": {"zoom_level": math.log(zoom) / math.log(1.2)}}}},
    }


# Runs inside the DevTools page. Finds visible elements whose text matches a
# pattern, innermost first, and returns their boxes in the page's CSS pixels.
_FIND = r"""
((pattern, flags, css) => {
  const re = pattern === null ? null : new RegExp(pattern, flags);
  const found = [];
  const walk = (root) => {
    for (const el of root.querySelectorAll('*')) {
      if (el.shadowRoot) walk(el.shadowRoot);
      if (css && !el.matches(css)) continue;
      const text = (el.innerText || el.textContent || '').trim();
      if (re && !re.test(text)) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 2 || r.height < 2 || r.bottom < 0 || r.top > innerHeight) continue;
      const style = getComputedStyle(el);
      if (style.visibility === 'hidden' || style.display === 'none') continue;
      found.push({x: r.x, y: r.y, w: r.width, h: r.height, len: text.length, text: text.slice(0, 200)});
    }
  };
  walk(document);
  found.sort((a, b) => a.len - b.len || a.w * a.h - b.w * b.h);
  return JSON.stringify({boxes: found.slice(0, 5), dpr: devicePixelRatio, width: innerWidth, height: innerHeight});
})
"""


class DevToolsError(Exception):
    pass


class Frontend:
    """The docked DevTools page of the one tab being captured."""

    def __init__(self, port, timeout=20):
        deadline = time.monotonic() + timeout
        while True:
            targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5))
            target = next((t for t in targets if t.get("url", "").startswith("devtools://")), None)
            if target:
                break
            if time.monotonic() > deadline:
                raise DevToolsError("DevTools did not open")
            time.sleep(0.3)
        self._ws = connect(target["webSocketDebuggerUrl"], max_size=None, open_timeout=10)
        self._id = 0

    def evaluate(self, expression):
        self._id += 1
        self._ws.send(json.dumps({"id": self._id, "method": "Runtime.evaluate",
                                  "params": {"expression": expression, "returnByValue": True}}))
        while True:
            message = json.loads(self._ws.recv(timeout=30))
            if message.get("id") == self._id:
                break
        result = message.get("result", {})
        if "exceptionDetails" in result:
            raise DevToolsError(f"DevTools script failed: {result['exceptionDetails'].get('text')}")
        return result.get("result", {}).get("value")

    def find(self, text=None, css=None, flags=""):
        """Boxes of visible elements matching text (a regex) and/or css, innermost first."""
        call = f"{_FIND}({json.dumps(text)}, {json.dumps(flags)}, {json.dumps(css)})"
        return json.loads(self.evaluate(call))

    def wait_for(self, text=None, css=None, timeout=30):
        deadline = time.monotonic() + timeout
        while True:
            found = self.find(text, css)
            if found["boxes"]:
                return found
            if time.monotonic() > deadline:
                raise DevToolsError(f"DevTools never showed {text or css!r}")
            time.sleep(0.4)

    def selected(self):
        """Text of the selected node in the Elements tree, or ''."""
        found = self.find(css='li[role="treeitem"].selected')
        texts = [box["text"] for box in found["boxes"] if box["text"]]
        return texts[0] if texts else ""

    def close(self):
        self._ws.close()
