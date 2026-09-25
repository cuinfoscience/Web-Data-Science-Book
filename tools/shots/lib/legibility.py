"""How tall a figure's text will be where it is shown, and whether that is enough.

A take's log holds the sizes of the text inside its crop, in the take's own
pixels (lib/measure.py). Each place a figure is shown scales it:

- **book:** the HTML book's column is 778 CSS pixels wide in a 1280-pixel-wide
  window; an image narrower than that is shown at its own width. Every
  chapter figure is shown there unless its recipe says `targets: {book: false}`.
- **slides:** `targets: {slides: {width: 0.8}}` is the fraction of the text
  width the figure fills on a 16:9 course slide, judged on a slide shown
  1920 pixels wide.
- **handout:** `targets: {handout: {width_in: 5.04}}` is its printed width.

The size judged is `p20`, the size that four in five characters reach or
exceed, so a copyright line does not fail a figure but small main text does.
The starting thresholds come from the toolkit plan: 11 pixels in the book and
16 on a 1920-pixel slide. Week 08's `infinite_scroll.png`, dropped because no
one could read it on its slide, measures 11.7 there. For print, 6 points is
the usual floor for small print.

Before any of that, a first and soft limit on how much of the screen a figure
shows. By default it is 800×600 CSS pixels (1600×1200 image pixels at the
default scale of 2): a capture no wider than the book's column keeps its text
at about the size it had on screen, while a whole 1680-pixel window shrinks it
to less than half. A figure may relax to 1024×768 when the extra room removes
clutter (rows that wrap, columns cut short with "…", panels squeezed together)
and its text still passes everywhere it is shown; its recipe says what the room
removes: `oversize: "at 800 pixels wide the Network columns are cut short"`.
Beyond 1024×768 a recipe needs a reason too. Going over is a warning, not an
error; text too small to read is the error, judged above.
"""
BOOK_PX = 778
SLIDE_PX = 1920
SLIDE_TEXT = 398.34 / 455.24     # the course decks' text width over paper width (beamer, 16:9)
PT_PER_IN = 72.27
THRESHOLDS = {"book": 11.0, "slides": 16.0, "handout": 6.0}
UNITS = {"book": "px", "slides": "px", "handout": "pt"}
SOFT_LIMIT = (800, 600)          # CSS pixels a figure shows by default
RELAXED_LIMIT = (1024, 768)      # ...and at most, when the room removes clutter and the text still passes


def region(entry):
    """The part of the screen a take or an image shows, in CSS pixels: its size over its scale.
    Images made before the toolkit record no scale; they were captured at 1x."""
    scale = entry.get("scale") or 1
    return round(entry["size"][0] / scale), round(entry["size"][1] / scale)


def _within(limit, width, height):
    return width <= limit[0] and height <= limit[1]


def oversize(entry):
    """'' within 800×600; otherwise what the figure shows, which limit that is within or over,
    and what the book's column does to its text."""
    width, height = region(entry)
    if _within(SOFT_LIMIT, width, height):
        return ""
    soft, relaxed = "{}×{}".format(*SOFT_LIMIT), "{}×{}".format(*RELAXED_LIMIT)
    if _within(RELAXED_LIMIT, width, height):
        said = f"shows {width}×{height} CSS pixels, over {soft} but within the relaxed {relaxed} limit"
    else:
        said = f"shows {width}×{height} CSS pixels, over the relaxed {relaxed} limit"
    if width > BOOK_PX:
        said += f"; the book's column shows its text at {round(100 * BOOK_PX / width)}% of its size on screen"
    return said


def size_verdict(fig, entry, results):
    """The soft limit's verdict on a take or an approved image: None within 800×600, otherwise
    ("note" or "warn", message). `results` are its legibility results (judge()).

    Up to 1024×768, a figure needs both conditions of the relaxed limit: a reason in `oversize:`
    (the clutter the extra room removes) and text that passes at every target. An image whose text
    was never measured can't show the second. Beyond 1024×768, a figure needs a reason."""
    said = oversize(entry)
    if not said:
        return None
    reason = fig.get("oversize")
    if _within(RELAXED_LIMIT, *region(entry)):
        small = [r for r in results if not r[-1]]
        if small and not (fig.get("legibility") or {}).get("skip"):
            return "warn", (f"{said}, but its text is too small ({describe(small)}); the relaxed limit is only "
                            "for text that passes wherever the figure is shown: go back to 800×600, or zoom "
                            "the page or DevTools")
        if entry.get("text") is None:
            return "warn", (f"{said}, but its text was never measured, so the relaxed limit can't be confirmed; "
                            "retake it with tools/shots")
        if reason:
            return "note", f"{said}; allowed: {reason}"
        return "warn", (f"{said}; allowed when the extra room removes clutter (rows that wrap, columns cut short "
                        "with \"…\", squeezed panels): say what it removes in `oversize:`, or crop to "
                        + "{}×{}".format(*SOFT_LIMIT))
    if reason:
        return "note", f"{said}; allowed: {reason}"
    return "warn", (f"{said}: crop to what the text discusses, or zoom DevTools, rather than widen the window "
                    "(or say why in `oversize:`)")


def targets(fig):
    """Where this figure is shown: {name: settings}."""
    wanted = dict(fig.get("targets") or {})
    if fig["chapter"].startswith("ch-") and "book" not in wanted:
        wanted["book"] = True
    return {name: (setting if isinstance(setting, dict) else {}) for name, setting in wanted.items()
            if setting not in (False, None)}


def scales(fig, width, annotated=None):
    """Image pixels -> the target's unit, for each target. `width` is the image's width in pixels;
    `annotated` is an annotation record, whose figure is shown in the image's place."""
    out = {}
    shown = width
    if annotated:
        shown = annotated["width_in"] / annotated["unit_in"]       # the annotated figure's width, in image pixels
    for name, setting in targets(fig).items():
        if name == "book":
            display = min(setting.get("width_px", BOOK_PX), shown)
            out[name] = display / shown
        elif name == "slides":
            out[name] = setting.get("width", 1.0) * SLIDE_PX * SLIDE_TEXT / shown
        elif name == "handout":
            width_in = setting.get("width_in") or (annotated or {}).get("width_in")
            if width_in:
                out[name] = width_in * PT_PER_IN / shown
    return out


def judge(fig, text, width, annotated=None):
    """[(target, size there, threshold, unit, ok)] for a take's or an image's text sizes. A hand
    capture's size is the one its recipe declares (lib/hand.py), since no page is left to measure."""
    if not text or not (text.get("chars") or text.get("declared")):
        return []
    size = text["p20"]
    return [(name, round(size * factor, 1), THRESHOLDS[name], UNITS[name], size * factor >= THRESHOLDS[name])
            for name, factor in scales(fig, width, annotated).items()]


def describe(results):
    return ", ".join(f"{name} {size:g} {unit} ({'ok' if ok else f'under {limit:g}'})"
                     for name, size, limit, unit, ok in results)
