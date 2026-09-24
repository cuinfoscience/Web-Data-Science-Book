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
# The Elements panel's layout: the Styles pane beside the tree, or under it. DevTools'
# default ("auto") stacks them in a narrow window, where Styles can squeeze the tree out.
LAYOUTS = {"side-by-side": "right", "stacked": "bottom", "auto": "auto"}


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
    if "layout" in devtools:       # Styles beside the tree (side-by-side) or under it (stacked)
        prefs["sidebar-position"] = json.dumps(LAYOUTS[devtools["layout"]])
    if "sidebar" in devtools:      # the Styles pane's size: its width beside the tree, its height under it
        # DevTools 154 keeps the tree/Styles split in `elements-panel-split-view-state` (found by
        # dragging the splitter and reading the profile back). It honors the size but ignores a
        # hidden state at 800 px; `layout: stacked, sidebar: 1` leaves the tree the whole width.
        # `hidden` also writes the older key, which hid the pane in the Oscars figure's wide DevTools.
        axis = "horizontal" if devtools.get("layout") == "stacked" else "vertical"
        if devtools["sidebar"] in ("hidden", 0, False):
            hidden = {"size": 300, "showMode": "OnlyMain"}
            prefs["elements.styles.sidebar.width"] = json.dumps({"vertical": hidden, "horizontal": hidden})
            prefs["elements-panel-split-view-state"] = json.dumps({axis: {"size": 100, "showMode": "OnlyMain"}})
        else:
            prefs["elements-panel-split-view-state"] = json.dumps({axis: {"size": devtools["sidebar"]}})
    if "overview" in devtools:     # the Network panel's timeline above the request list
        prefs["network-log-show-overview"] = json.dumps(bool(devtools["overview"]))
    if devtools.get("columns"):    # Network columns to show, [waterfall], or {waterfall: true, initiator: false}
        columns = devtools["columns"]
        if not isinstance(columns, dict):
            columns = {name: True for name in columns}
        prefs["network-log-columns"] = json.dumps(
            {name: {"visible": bool(on), "title": name.replace("-", " ").title()} for name, on in columns.items()})
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
      // DevTools breaks attributes with zero-width spaces (class=​"field"); match without them.
      const text = (el.innerText || el.textContent || '').replace(/​/g, '').trim();
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

    def find(self, text=None, css=None):
        """Boxes of visible elements matching text (a regex) and/or css, innermost first."""
        if text is not None and text.startswith("(?i)"):    # JavaScript has no inline flags
            text, flags = text[4:], "i"
        else:
            flags = ""
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

    _SELECTED_ROW = r"""
    (() => {
      const walk = (root) => {
        for (const el of root.querySelectorAll('li[role="treeitem"].selected')) {
          const tree = el.closest('[role="tree"]');
          const r = el.getBoundingClientRect();
          if (tree && r.width > 1 && r.height > 1 && (el.innerText || '').trim()) {
            const t = tree.getBoundingClientRect();
            return {row: {x: r.x, y: r.y, w: r.width, h: r.height},
                    tree: {x: t.x, y: t.y, w: t.width, h: t.height}};
          }
        }
        for (const el of root.querySelectorAll('*')) {
          if (el.shadowRoot) { const found = walk(el.shadowRoot); if (found) return found; }
        }
        return null;
      };
      const found = walk(document);
      return JSON.stringify(found && Object.assign(found, {dpr: devicePixelRatio}));
    })()
    """

    def selected_row(self):
        """The Elements tree's selected row and the tree it sits in, or None."""
        return json.loads(self.evaluate(self._SELECTED_ROW))

    def selected(self):
        """Text of the selected node in the Elements tree, or ''."""
        found = self.find(css='li[role="treeitem"].selected')
        texts = [box["text"] for box in found["boxes"] if box["text"]]
        return texts[0] if texts else ""

    def close(self):
        self._ws.close()
