"""Run a recipe's steps. Every step waits for a condition; none sleeps blindly.

    - wait: {text: 'Saved [0-9,]+ times'}   a regular expression, found anywhere,
                                             including inside shadow DOM
    - wait: {selector: '#wm-ipp-base'}       a CSS selector, visible
    - wait: {network_idle: true}             no requests for half a second
    - hover: {selector: '...'}               or {text: '...'}, or {position: [x, y]}
    - click: {selector: '...'}               or {text: '...'}, or {position: [x, y]}
    - scroll: {selector: '...'}              into view; or {y: 400} to scroll by pixels
    - press: 'Escape'                        a key
    - settle: 1.5                            seconds, for animation that has no end signal

Playwright's text and CSS locators reach inside open shadow roots, which the
Wayback Machine's toolbar and calendar use.
"""
import re
import time


class StepError(Exception):
    pass


def _target(page, arg):
    if "selector" in arg:
        return page.locator(arg["selector"]).first
    if "text" in arg:
        return page.get_by_text(re.compile(arg["text"])).first
    return None


def run(page, fig, log):
    ms = fig["timeout"] * 1000
    for step in fig.get("steps") or []:
        (kind, arg), = step.items()
        started = time.monotonic()
        try:
            if kind == "wait":
                if "text" in arg:
                    page.get_by_text(re.compile(arg["text"])).first.wait_for(state="visible", timeout=ms)
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
                if "selector" in arg:
                    page.locator(arg["selector"]).first.scroll_into_view_if_needed(timeout=ms)
                else:
                    page.mouse.wheel(0, arg.get("y", 0))
            elif kind == "press":
                page.keyboard.press(arg)
            elif kind == "settle":
                time.sleep(float(arg))
        except StepError:
            raise
        except Exception as e:  # Playwright's timeouts and misses
            raise StepError(f"step {kind} {arg!r} failed: {str(e).splitlines()[0]}")
        log.append({"step": kind, "arg": arg, "seconds": round(time.monotonic() - started, 1)})
