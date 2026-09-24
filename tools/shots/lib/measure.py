"""What the browser knows at the moment of capture: where things are, and how big the text is.

Two measurements go into every take's log, both in the take's own pixels:

- **Anchors.** Each mark in a recipe's `annotate:` block points at something:
  a page element (`selector:` or `text:`), something in DevTools
  (`devtools: {row: ...}`, `{text: ...}`, `{css: ...}`, `{selected: true}`), or,
  as a last resort, a spot typed in by hand (`xy: [x, y]`, flagged for
  review). Its box is recorded here, so markers are placed from the take and
  follow the page when it is retaken.
- **Text sizes.** Every visible character inside the crop, by its computed
  font size. `lib/legibility.py` works out how tall that text will be in the
  book, on a slide, or in a handout.

Boxes are [left, top, right, bottom] in image pixels. A box can reach past the
image's edges: a card that continues below the crop has a bottom greater than
the image's height, and a bracket drawn on it says so.
"""
import json

from .steps import js_pattern, pattern

# Runs on the elements a locator matched. Returns each one's box in the page's
# CSS pixels: the element's own box, or the box of its text (one line or all).
_BOXES = r"""
(els, mode) => els.map(el => {
  const r = el.getBoundingClientRect();
  const own = [r.left, r.top, r.right, r.bottom];
  if (mode === 'element') return own;
  const range = document.createRange();
  range.selectNodeContents(el);
  let rects = [...range.getClientRects()].filter(q => q.width > 0 && q.height > 0);
  if (!rects.length) return own;
  if (mode === 'first-line') {
    const first = rects[0];
    rects = rects.filter(q => q.top < first.top + first.height / 2);
  }
  return [Math.min(...rects.map(q => q.left)), Math.min(...rects.map(q => q.top)),
          Math.max(...rects.map(q => q.right)), Math.max(...rects.map(q => q.bottom))];
})
"""

# Runs in the page, or in DevTools. Counts visible characters inside a region
# (CSS pixels), by the computed font size of the element that holds them.
# Reaches into open shadow roots, which DevTools is made of.
TEXT_SIZES = r"""
(region) => {
  const sizes = {};
  const styles = new Map();
  const style = el => { if (!styles.has(el)) styles.set(el, getComputedStyle(el)); return styles.get(el); };
  const visible = el => {
    for (let e = el; e; e = e.parentElement) {
      const s = style(e);
      if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') return false;
    }
    return true;
  };
  const walk = root => {
    const texts = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = texts.nextNode(); node; node = texts.nextNode()) {
      const chars = node.nodeValue.replace(/\s+/g, '').length;
      const el = node.parentElement;
      if (!chars || !el || !visible(el)) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      let inside = 0, total = 0;
      for (const q of range.getClientRects()) {
        total += q.width * q.height;
        const w = Math.min(q.right, region[2]) - Math.max(q.left, region[0]);
        const h = Math.min(q.bottom, region[3]) - Math.max(q.top, region[1]);
        if (w > 0 && h > 0) inside += w * h;
      }
      if (!inside) continue;
      const size = Math.round(parseFloat(style(el).fontSize) * 10) / 10;
      sizes[size] = (sizes[size] || 0) + chars * inside / total;
    }
    for (const el of root.querySelectorAll('*')) if (el.shadowRoot) walk(el.shadowRoot);
  };
  walk(document);
  return sizes;
}
"""

# Runs in DevTools. Finds Elements-tree rows whose own line matches a pattern
# (or the selected row), and returns each row's box: from the first ink of
# the disclosure triangle, or of the text where there is none, to the end of
# the row's first line. A marker's leader line stops short of that box.
#
# The triangle is a masked icon in a 14-pixel ::before box; where its ink
# starts inside that box was measured in DevTools 154 (the pinned version):
# 6.4 pixels for an open row's triangle, 8.1 for a closed row's.
_ROWS = r"""
((pattern, flags, selected) => {
  const INK = {open: 6.4, closed: 8.1};
  const re = pattern === null ? null : new RegExp(pattern, flags);
  const found = [];
  const walk = root => {
    for (const li of root.querySelectorAll('li[role="treeitem"]')) {
      if (selected && !li.classList.contains('selected')) continue;
      const text = (li.innerText || '').replace(/​/g, '').trim();
      if (!text || (re && !re.test(text))) continue;
      const range = document.createRange();
      range.selectNodeContents(li);
      const rects = [...range.getClientRects()].filter(q => q.width > 0 && q.height > 0);
      if (!rects.length) continue;
      const first = rects[0];
      const line = rects.filter(q => q.top < first.top + first.height / 2);
      const box = li.getBoundingClientRect();
      const s = getComputedStyle(li);
      let left = box.left + parseFloat(s.paddingLeft);
      if (li.classList.contains('parent')) {
        left += (parseFloat(getComputedStyle(li, '::before').marginLeft) || 0)
              + (li.classList.contains('expanded') ? INK.open : INK.closed);
      }
      found.push({box: [left, Math.min(...line.map(q => q.top)), Math.max(...line.map(q => q.right)),
                        Math.max(...line.map(q => q.bottom))], text: text.slice(0, 120)});
    }
    for (const el of root.querySelectorAll('*')) if (el.shadowRoot) walk(el.shadowRoot);
  };
  walk(document);
  return JSON.stringify({rows: found, dpr: devicePixelRatio});
})
"""


class AnchorError(Exception):
    pass


def key(at):
    """A mark's anchor as a stable string, so a take's anchors can be looked up by recipe."""
    return json.dumps(at, sort_keys=True, separators=(",", ":"))


def hand_box(xy):
    """An anchor typed in by hand, in image pixels: a point [x, y] or a box [x, y, w, h]."""
    x, y, w, h = (list(xy) + [0, 0])[:4]
    return {"box": [x, y, x + w, y + h], "hand": True}


def shifted(box, dx, dy):
    """A box in screen or page pixels -> the take's pixels, whose corner is (dx, dy)."""
    return [round(box[0] - dx, 1), round(box[1] - dy, 1), round(box[2] - dx, 1), round(box[3] - dy, 1)]


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def pick(boxes, at, what):
    """One match (`nth`, from 0), a run of them (`nth: [first, last]`), or `all`, as one box."""
    if not boxes:
        raise AnchorError(f"anchor {what} matched nothing")
    if at.get("all"):
        return union(boxes)
    n = at.get("nth", 0)
    first, last = (n, n) if isinstance(n, int) else n
    if last >= len(boxes):
        raise AnchorError(f"anchor {what} has {len(boxes)} match(es), not {last + 1}")
    return union(boxes[first:last + 1])


def page_boxes(page, at, timeout=10):
    """Boxes of the page elements an anchor names, in the viewport's CSS pixels."""
    if "selector" in at:
        locator, mode, what = page.locator(at["selector"]), at.get("box", "element"), at["selector"]
    elif "text" in at:
        locator, mode, what = page.get_by_text(pattern(at["text"])), at.get("box", "text"), f"/{at['text']}/"
    else:
        raise AnchorError(f"not a page anchor: {at!r}")
    try:
        locator.first.wait_for(state="attached", timeout=timeout * 1000)
    except Exception:
        raise AnchorError(f"anchor {what} matched nothing")
    return pick(locator.evaluate_all(_BOXES, mode), at, what)


def devtools_boxes(frontend, spec):
    """Boxes of what a DevTools anchor names, in DevTools' CSS pixels, and DevTools' pixel ratio."""
    if "row" in spec or spec.get("selected"):
        source, flags = js_pattern(spec.get("row"))
        found = json.loads(frontend.evaluate(f"{_ROWS}({json.dumps(source)}, {json.dumps(flags)}, "
                                             f"{json.dumps(bool(spec.get('selected')))})"))
        what = "the selected row" if spec.get("selected") else f"row /{spec['row']}/"
        return pick([r["box"] for r in found["rows"]], spec, what), found["dpr"]
    found = frontend.find(spec.get("text"), spec.get("css"))
    boxes = [[b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]] for b in found["boxes"]]
    return pick(boxes, spec, f"/{spec.get('text')}/ {spec.get('css') or ''}".strip()), found["dpr"]


def summarize(sizes):
    """Text sizes (image pixels -> characters) as the numbers `check` uses.

    `p20` is the size that four in five characters reach or exceed: small print
    at the edges (a copyright line, a badge) does not decide a figure, but a
    figure whose main text is small cannot hide it.
    """
    pairs = sorted((float(s), c) for s, c in sizes.items() if c > 0)
    total = sum(c for _, c in pairs)
    if not total:
        return {"chars": 0}

    def quantile(q):
        seen = 0.0
        for size, count in pairs:
            seen += count
            if seen >= q * total:
                return round(size, 1)
        return round(pairs[-1][0], 1)

    return {"chars": round(total), "min": round(pairs[0][0], 1), "p20": quantile(0.2),
            "median": quantile(0.5),
            "sizes": {f"{s:g}": round(c) for s, c in pairs if round(c)}}


def merge(*histograms):
    out = {}
    for h in histograms:
        for size, chars in h.items():
            out[size] = out.get(size, 0) + chars
    return out


def scaled(sizes, factor):
    """CSS-pixel font sizes -> image pixels."""
    out = {}
    for size, chars in sizes.items():
        s = round(float(size) * factor, 1)
        out[s] = out.get(s, 0) + chars
    return out


def marks_anchors(fig):
    """The distinct anchors a recipe's marks name."""
    seen = {}
    for mark in (fig.get("annotate") or {}).get("marks") or []:
        if mark.get("at") is not None:
            seen[key(mark["at"])] = mark["at"]
    return list(seen.values())
