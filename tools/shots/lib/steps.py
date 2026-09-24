"""Run a recipe's steps. Every step waits for a condition; none sleeps blindly.

    - wait: {text: 'Saved [0-9,]+ times'}   a regular expression, found anywhere,
                                             including inside shadow DOM
    - wait: {selector: '#wm-ipp-base'}       a CSS selector, visible
    - wait: {network_idle: true}             no requests for half a second
    - hover: {selector: '...'}               or {text: '...'}, or {position: [x, y]}
    - click: {selector: '...'}               or {text: '...'}, or {position: [x, y]}
    - scroll: {selector: '...'}              into view; or {y: 400} to scroll by pixels
    - scroll: {selector: '...', offset: 175} so the element's top is 175 pixels below
                                             the window's top
    - press: 'Escape'                        a key
    - settle: 1.5                            seconds, for animation that has no end signal
    - scroll: {match: '^User-agent: \\*$', in: 'pre', offset: 180}
                                             so a match inside an element's text (lines of
                                             a plain-text file, in one <pre>) is 180 pixels
                                             below the window's top

Playwright's text and CSS locators reach inside open shadow roots, which the
Wayback Machine's toolbar and calendar use.

Headed figures (mode: headed) add steps that use real input and DevTools;
see lib/headed.py.
"""
import re
import time


class StepError(Exception):
    pass


def pattern(text):
    """A recipe's regular expression, ready for Playwright.

    Playwright hands patterns to JavaScript, which has no inline flags, so a
    leading `(?i)` becomes the ignore-case flag.
    """
    if text.startswith("(?i)"):
        return re.compile(text[4:], re.IGNORECASE)
    return re.compile(text)


def js_pattern(text):
    """(source, flags) for `new RegExp(source, flags)` in a page or in DevTools."""
    if text is None:
        return None, ""
    return (text[4:], "i") if text.startswith("(?i)") else (text, "")


# Runs on an element: the boxes of a pattern's matches inside its text, one box
# per match, in the viewport's CSS pixels. A plain-text file is one <pre> with one
# text node, so no element can stand for one of its lines; a match can. `^` and
# `$` match at each line. `mode` 'first-line' keeps a match's first line.
MATCH_BOXES = r"""
(el, [source, flags, mode]) => {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = [];
  let text = '';
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    nodes.push([n, text.length]);
    text += n.data;
  }
  const at = offset => {
    let i = nodes.length - 1;
    while (i > 0 && nodes[i][1] > offset) i--;
    return [nodes[i][0], offset - nodes[i][1]];
  };
  const re = new RegExp(source, 'gm' + flags);
  const boxes = [];
  for (let m = re.exec(text); m; m = re.exec(text)) {
    if (!m[0].length) { re.lastIndex++; continue; }
    const range = document.createRange();
    range.setStart(...at(m.index));
    range.setEnd(...at(m.index + m[0].length));
    let rects = [...range.getClientRects()].filter(q => q.width > 0 && q.height > 0);
    if (!rects.length) continue;
    if (mode === 'first-line') rects = rects.filter(q => q.top < rects[0].top + rects[0].height / 2);
    boxes.push([Math.min(...rects.map(q => q.left)), Math.min(...rects.map(q => q.top)),
                Math.max(...rects.map(q => q.right)), Math.max(...rects.map(q => q.bottom))]);
  }
  return boxes;
}
"""


def match_boxes(page, arg, mode="text", timeout=10000):
    """Boxes of `arg['match']` inside the element `arg['in']` names (the page's body by default)."""
    holder = page.locator(arg.get("in", "body")).first
    holder.wait_for(state="attached", timeout=timeout)
    source, flags = js_pattern(arg["match"])
    return holder.evaluate(MATCH_BOXES, [source, flags, mode])


def target(page, arg):
    if "selector" in arg:
        return page.locator(arg["selector"]).first
    if "text" in arg:
        return page.get_by_text(pattern(arg["text"])).first
    return None


_target = target


def run(page, fig, log, extra=None):
    """Run the recipe's steps. `extra` maps headed-only step names to handlers."""
    ms = fig["timeout"] * 1000
    extra = extra or {}
    for step in fig.get("steps") or []:
        (kind, arg), = step.items()
        started = time.monotonic()
        try:
            if kind in extra:
                extra[kind](arg)
            elif kind == "scroll" and "match" in arg:
                # Measure again after scrolling: a page can move as it scrolls (a header that
                # turns sticky leaves the flow), so correct until the match is at its offset.
                n = arg.get("nth", 0)
                for _ in range(3):
                    boxes = match_boxes(page, arg, timeout=ms)
                    if len(boxes) <= n:
                        raise StepError(f"/{arg['match']}/ matched {len(boxes)} time(s) in {arg.get('in', 'body')}")
                    dy = boxes[n][1] - arg.get("offset", 0)
                    if abs(dy) < 1:
                        break
                    page.evaluate("dy => window.scrollBy(0, dy)", dy)
            elif kind == "wait":
                if "text" in arg:
                    page.get_by_text(pattern(arg["text"])).first.wait_for(state="visible", timeout=ms)
                if "selector" in arg:
                    page.locator(arg["selector"]).first.wait_for(state=arg.get("state", "visible"), timeout=ms)
                if arg.get("network_idle"):
                    page.wait_for_load_state("networkidle", timeout=ms)
            elif kind in ("hover", "click"):
                target = _target(page, arg)
                if target is not None:
                    getattr(target, kind)(timeout=ms)
                elif "position" in arg:
                    x, y = arg["position"]
                    page.mouse.move(x, y)
                    if kind == "click":
                        page.mouse.click(x, y)
                    log.append({"note": f"{kind} by position {arg['position']}: no selector; check the take"})
                else:
                    raise StepError(f"{kind} needs selector, text, or position")
            elif kind == "scroll":
                if "selector" in arg and "offset" in arg:
                    element = page.locator(arg["selector"]).first
                    element.wait_for(state="attached", timeout=ms)
                    element.evaluate("(el, offset) => window.scrollTo(0, el.getBoundingClientRect().top"
                                     " + window.scrollY - offset)", arg["offset"])
                elif "selector" in arg:
                    page.locator(arg["selector"]).first.scroll_into_view_if_needed(timeout=ms)
                else:
                    page.mouse.wheel(0, arg.get("y", 0))
            elif kind == "press":
                page.keyboard.press(arg)
            elif kind == "settle":
                time.sleep(float(arg))
            else:
                raise StepError(f"step `{kind}` needs a headed browser (mode: headed)")
        except StepError:
            raise
        except Exception as e:  # Playwright's timeouts and misses
            raise StepError(f"step {kind} {arg!r} failed: {str(e).splitlines()[0]}")
        log.append({"step": kind, "arg": arg, "seconds": round(time.monotonic() - started, 1)})
