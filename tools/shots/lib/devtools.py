"""DevTools: its settings, and reading its own page to find things on screen.

Settings go into the browser profile before launch (the keys the week-06
handout capture found: dock side, the open panel, split sizes, zoom, and the
"what's new" note marked as seen).

Docked DevTools is itself a web page (devtools://devtools/...). With the
browser's debugging port open, the toolkit reads that page's DOM, through its
shadow roots, to find where a panel, a request row, or a header name is
drawn, and clicks it for real with xdotool. No pixel offsets are typed in.

A key DevTools doesn't know fails silently, so every setting is read back:
`Frontend.state()` measures what DevTools drew (its zoom, where it docked and
how large, the Styles pane, the Network timeline and columns, a "What's new"
panel), and `compare()` says where that differs from the recipe. Each headed
take records the state, and `capture` reports the differences.
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
        # dragging the splitter and reading the profile back), one size per layout. Both are
        # written, because DevTools stacks the pane under the tree in a narrow window even when
        # the recipe gives no layout. It can't hide the pane: it ignores a hidden state and keeps
        # the pane at least 97 DevTools pixels wide beside the tree, or 57 tall under it (the
        # read-back found both). `hidden` asks for the smallest, whichever layout DevTools uses.
        size = 1 if devtools["sidebar"] in ("hidden", 0, False) else devtools["sidebar"]
        prefs["elements-panel-split-view-state"] = json.dumps({"vertical": {"size": size},
                                                               "horizontal": {"size": size}})
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


# Runs inside the DevTools page. What DevTools drew, in its own CSS pixels:
# the area it leaves for the page, the main panel shown, the Elements panel's
# tree/Styles split, the Network timeline and columns, and any "What's new".
_STATE = r"""
(() => {
  const all = [];
  const walk = (root) => { for (const el of root.querySelectorAll('*')) { all.push(el); if (el.shadowRoot) walk(el.shadowRoot); } };
  walk(document);
  const box = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect(), st = getComputedStyle(el);
    if (r.width < 1 || r.height < 1 || st.display === 'none' || st.visibility === 'hidden') return null;
    return [r.x, r.y, r.width, r.height].map(v => Math.round(v * 10) / 10);
  };
  const has = (el, c) => el.classList && el.classList.contains(c);
  const inside = (el, host) => { for (let n = el; n; n = n.parentNode || n.host) if (n === host) return true; return false; };
  const shown = (test) => all.filter(el => test(el) && box(el));
  const page = shown(el => has(el, 'device-mode-view'))[0];
  const tab = shown(el => has(el, 'tabbed-pane-header-tab') && has(el, 'selected') && /^tab-/.test(el.id)
                     && el.closest('.tabbed-pane-header')
                     && el.closest('.tabbed-pane-header').getAttribute('aria-label') === 'Main toolbar')[0];
  const panel = shown(el => has(el, 'panel') && has(el, 'elements'))[0];
  let elements = null;
  if (panel) {   // the outer split: the tree is its main side, Styles its sidebar
    const main = all.find(el => has(el, 'shadow-split-widget-main') && inside(el, panel) && box(el));
    const side = all.find(el => has(el, 'shadow-split-widget-sidebar') && inside(el, panel));
    elements = {main: box(main), sidebar: box(side)};
  }
  return JSON.stringify({
    dpr: devicePixelRatio, width: innerWidth, height: innerHeight,
    page_area: page ? box(page) : null,
    panel: tab ? tab.id.replace(/^tab-/, '') : null,
    elements,
    overview: shown(el => el.id === 'network-overview-panel').length > 0,
    columns: shown(el => el.tagName === 'TH' && /(\S+)-column\b/.test(el.className))
      .map(el => el.className.match(/(\S+)-column\b/)[1]),
    waterfall: shown(el => has(el, 'network-waterfall-view')).length > 0,
    whats_new: shown(el => el.id === 'tab-release-note' || (has(el, 'panel') && has(el, 'whats-new'))).length > 0,
  });
})()
"""

# The smallest Styles pane DevTools 154 draws, in DevTools pixels (read back).
SMALLEST = {"side-by-side": 97, "stacked": 57}


def layout(seen, scale):
    """Where DevTools docked and how large, and its Styles pane, in window (CSS) pixels.

    `seen` is `Frontend.state()`. DevTools' own pixels are the window's divided by
    its zoom: devicePixelRatio is the capture's scale times DevTools' zoom.
    """
    k = seen["dpr"] / scale
    out = {"zoom": round(k, 3), "dock": None, "pane": None, "styles": None}
    if seen.get("page_area"):
        x, y, w, h = seen["page_area"]
        dock = "left" if x > 1 else ("bottom" if w >= seen["width"] - 1 else "right")
        extent = {"bottom": seen["height"] - h, "right": seen["width"] - w, "left": x}[dock]
        out.update(dock=dock, pane=round(extent * k, 1))
    el = seen.get("elements") or {}
    main, side = el.get("main"), el.get("sidebar")
    if main and side:
        stacked = side[1] >= main[1] + main[3] - 2
        own = side[3] if stacked else side[2]
        name = "stacked" if stacked else "side-by-side"
        out["styles"] = {"layout": name, "size": round(own * k, 1), "smallest": own <= SMALLEST[name] + 2}
    elif main:
        out["styles"] = {"layout": None, "size": 0, "smallest": True}
    return out


def compare(devtools, seen, scale):
    """Where what DevTools drew differs from the recipe's `devtools:` block.

    Returns [(level, message)]: "warn" when DevTools didn't do what the recipe
    asks, "note" for something the recipe can't ask for (DevTools can't hide
    the Styles pane) or that a step may have changed on purpose.
    """
    if not seen or seen.get("error"):
        return [("warn", "its layout could not be read back" + (f": {seen['error']}" if seen else ""))]
    out, got = [], layout(seen, scale)
    zoom = float(devtools.get("zoom", 1.0))
    if abs(got["zoom"] - zoom) > 0.01:
        out.append(("warn", f"it is zoomed to {got['zoom']:.0%}, not {zoom:.0%}"))
    want = devtools.get("dock", "right")
    if got["dock"] is None:
        out.append(("warn", "it shows no area for the page, so its dock and size can't be read"))
    elif got["dock"] != want:
        out.append(("warn", f"it is docked {got['dock']}, not {want}"))
    elif "size" in devtools and abs(got["pane"] - devtools["size"]) > 2:
        shape = "tall" if want == "bottom" else "wide"
        out.append(("warn", f"the pane is {got['pane']:.0f} pixels {shape}, not {devtools['size']}"
                            + ("; Chrome keeps part of the page in view" if got["pane"] < devtools["size"] else "")))
    panel = devtools.get("panel", "elements")
    if seen.get("panel") != panel:
        out.append(("note", f"it shows the {seen.get('panel')} panel at the grab; the recipe opened {panel}"))
    styles = got["styles"]
    if styles:
        where = {"stacked": "under", "side-by-side": "beside"}
        if devtools.get("layout") in where and styles["layout"] and styles["layout"] != devtools["layout"]:
            out.append(("warn", f"the Styles pane is {where[styles['layout']]} the tree, "
                                f"not {where[devtools['layout']]} it"))
        asked = devtools.get("sidebar")
        shape = "tall" if styles["layout"] == "stacked" else "wide"
        if asked in ("hidden", 0, False):
            if not styles["smallest"]:
                out.append(("warn", f"the Styles pane is {styles['size']:.0f} pixels {shape}, not at its smallest"))
            elif styles["layout"]:
                out.append(("note", f"DevTools can't hide the Styles pane; it is at its smallest, "
                                    f"{styles['size']:.0f} pixels {shape}"))
        elif isinstance(asked, (int, float)) and abs(styles["size"] - asked) > 2:
            if not (styles["smallest"] and styles["size"] > asked):     # asked for less than DevTools allows
                out.append(("warn", f"the Styles pane is {styles['size']:.0f} pixels {shape}, not {asked}"))
    if seen.get("panel") == "network":
        if "overview" in devtools and seen["overview"] != bool(devtools["overview"]):
            out.append(("warn", f"the timeline is {'shown' if seen['overview'] else 'hidden'}, "
                                f"not {'shown' if devtools['overview'] else 'hidden'}"))
        columns = devtools.get("columns") or {}
        if not isinstance(columns, dict):
            columns = {name: True for name in columns}
        if set(seen["columns"]) <= {"name"} and not seen["waterfall"]:
            columns = {}            # a request is open: its details replace every column but Name
        for name, on in columns.items():
            there = seen["waterfall"] if name == "waterfall" else name in seen["columns"]
            if there != bool(on):
                out.append(("warn", f"the {name} column is {'shown' if there else 'hidden'}, "
                                    f"not {'shown' if on else 'hidden'}"))
    if seen.get("whats_new"):
        out.append(("warn", "it opened its \"What's new\" panel: `releaseNoteVersionSeen` no longer "
                            "matches this Chrome"))
    return out


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

    def state(self):
        """What DevTools drew (see _STATE); `layout()` and `compare()` read it."""
        return json.loads(self.evaluate(_STATE))

    def close(self):
        self._ws.close()
