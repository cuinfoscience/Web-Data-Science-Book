"""Draw numbered markers on a take, from the anchors recorded when it was captured.

A recipe's `annotate:` block lists marks. Each points `at` something the
browser measured (lib/measure.py), so a retake moves the markers with the page:

    annotate:
      width_in: 2.625          # printed width of the whole figure; sets the markers' scale
      size: small              # normal (11 pt) or small (8.5 pt) markers
      marks:
        - {n: 3, at: {selector: '.field--name-field-award-category-oscars', box: text}}
        - {n: 5, at: {selector: '.field--name-field-honoree-type', box: text}, column: a}
        - {n: 4, shape: brace, at: {selector: '.paragraph--type--award-honoree'}, x: 202}
        - {n: 1, shape: bracket, at: {selector: '.field--name-field-award-categories'}, x: -1}
        - {label: '← you clicked', at: {devtools: {selected: true}}, x: -4}

A mark's shape is one of:

- `marker` (the default with a number `n`): a numbered circle beside the thing,
  on its `side` (right, left, above, below), `gap` CSS pixels away. `x` or `y`
  pins the circle's center to a spot in the crop, in CSS pixels, counted from
  the right or bottom edge when negative. A dotted leader line joins a circle
  to its thing whenever they end up apart; `lead: false` or `true` decides.
- `brace`: a curly brace along the thing's side, spanning its height (or
  width); its number or label sits just past the brace's tip.
- `bracket`: an open bracket. When the thing continues past the picture's
  edge, the bracket runs on past the edge and ends in an arrow.
- `box`: a rounded box around the thing, with its number beside the box.
- `label` (the default without a number): text beside the thing. With a
  number too, the text comes first and the marker after it, as in
  "4 more honorees (4)". A label over the picture gets a white backing.

Markers that share a `column` line up on one line, just past the widest of
their things. Markers that would overlap on one line are spread apart evenly,
keeping their order, and get leader lines back to their things.

The output is a TikZ picture over the screenshot, in the course handouts'
marker style (styles/shotmarkers.sty). pdflatex builds a vector PDF for slides
and handouts. For the book's PNG, pdftocairo draws the marks alone on a
transparent page, laid over the screenshot's own pixels, which stay exactly as
captured.
"""
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from . import measure
from .env import ROOT, TOOL

PT_PER_IN = 72.27
MARKER_PT = {"normal": 11.0, "small": 8.5}
BRACE_PT = 4.0          # the brace's amplitude (handoutmarkers.sty)
ARM_PT = 2.0            # a bracket's short arm
TIP_PT = 1.0            # from a brace's or bracket's tip to its marker or label
SPACING_PT = 1.5        # between markers spread apart on one line
BEYOND_PT = 2.5         # how far a bracket's arrow reaches past the picture's edge
BOOK_WIDTH_IN = 778 / 96  # the book's column (778 CSS pixels in a 1280-pixel-wide window)
STYLES = TOOL / "styles"
ANCHORS = {"right": {"start": "west", "end": "east"}, "left": {"start": "west", "end": "east"},
           "below": {"start": "north", "end": "south"}, "above": {"start": "north", "end": "south"}}


class AnnotateError(Exception):
    pass


def _pin(value, scale, extent):
    return value * scale if value >= 0 else extent + value * scale


def _xy(horizontal, axis, across):
    return [axis, across] if horizontal else [across, axis]


def _spread(positions, spacing):
    """Push 1-D positions apart to at least `spacing`, keeping their order and each cluster's middle."""
    order = sorted(range(len(positions)), key=lambda i: positions[i])
    clusters = [[i] for i in order]

    def placed(cluster):
        middle = sum(positions[i] for i in cluster) / len(cluster)
        return [middle + (k - (len(cluster) - 1) / 2) * spacing for k in range(len(cluster))]

    merged = True
    while merged:
        merged = False
        for k in range(len(clusters) - 1):
            if placed(clusters[k])[-1] + spacing > placed(clusters[k + 1])[0] + 1e-6:
                clusters[k:k + 2] = [clusters[k] + clusters[k + 1]]
                merged = True
                break
    out = list(positions)
    for cluster in clusters:
        for i, p in zip(cluster, placed(cluster)):
            out[i] = p
    return out


def _anchor(anchors, at, i):
    # A spot typed in by hand needs no measuring, so a changed `xy` needs no new take.
    entry = measure.hand_box(at["xy"]) if "xy" in at else anchors.get(measure.key(at))
    if entry is None:
        raise AnnotateError(f"mark {i + 1}: {measure.key(at)} was not measured in this take; "
                            "capture again after changing what a mark points at")
    return entry["box"], entry.get("hand", False)


def layout(spec, anchors, size, scale, unit):
    """Every mark's geometry in image pixels, the marker's diameter, and warnings.

    `unit` is inches per image pixel: markers have a size in points, so their
    size in pixels depends on how large the figure is printed.
    """
    W, H = size
    px = lambda pt: pt / PT_PER_IN / unit            # noqa: E731  points -> image pixels
    d = px(MARKER_PT[spec.get("size", "normal")])
    items, warnings = [], []
    for i, mark in enumerate(spec.get("marks") or []):
        box, hand = _anchor(anchors, mark["at"], i)
        if hand:
            warnings.append(f"mark {i + 1} is placed by hand (xy): check it after every retake")
        l, t, r, b = box
        shape = mark.get("shape", "marker" if "n" in mark else "label")
        side = mark.get("side", "right")
        out = 1 if side in ("right", "below") else -1
        horizontal = side in ("left", "right")
        extent_axis, extent_across = (W, H) if horizontal else (H, W)
        gap = mark.get("gap", 4) * scale
        pin_axis = mark.get("x") if horizontal else mark.get("y")
        pin_across = mark.get("y") if horizontal else mark.get("x")
        edge = {"right": r, "left": l, "below": b, "above": t}[side]
        middle = (t + b) / 2 if horizontal else (l + r) / 2
        item = {"mark": i + 1, "n": mark.get("n"), "shape": shape, "side": side, "box": box,
                "label": mark.get("label"), "column": mark.get("column"), "lead": mark.get("lead"),
                "horizontal": horizontal, "out": out}
        if shape == "label":
            if pin_axis is not None:
                where, item["align"] = _pin(pin_axis, scale, extent_axis), "end" if pin_axis < 0 else "start"
            else:
                where, item["align"] = edge + out * gap, "start" if out > 0 else "end"
            across = _pin(pin_across, scale, extent_across) if pin_across is not None else middle
            item["text_at"] = _xy(horizontal, where, across)
            items.append(item)
            continue
        if shape in ("brace", "bracket"):
            line = _pin(pin_axis, scale, extent_axis) if pin_axis is not None else edge + out * gap
            lo, hi = (t, b) if horizontal else (l, r)
            item["before"] = shape == "bracket" and lo < -0.5      # the thing continues past an edge
            item["after"] = shape == "bracket" and hi > extent_across + 0.5
            lo = -px(BEYOND_PT) if item["before"] else max(lo, 0)
            hi = extent_across + px(BEYOND_PT) if item["after"] else min(hi, extent_across)
            tip = line + out * (px(BRACE_PT) if shape == "brace" else 0)
            item.update(line=line, span=[lo, hi])
            axis, across = tip + out * (px(TIP_PT) + d / 2), (lo + hi) / 2
            if item["label"]:              # the label starts just past the tip; the marker follows it
                if pin_across is not None:
                    across = _pin(pin_across, scale, extent_across)
                item["text_at"], item["align"] = _xy(horizontal, tip + out * px(TIP_PT), across), \
                    "start" if out > 0 else "end"
        elif shape == "box":
            item["rect"] = [l - gap, t - gap, r + gap, b + gap]
            axis, across = edge + out * (2 * gap + d / 2), middle
        else:
            axis, across = edge + out * (gap + d / 2), middle
        if pin_axis is not None and shape in ("marker", "box"):
            axis = _pin(pin_axis, scale, extent_axis)
        if pin_across is not None:
            across = _pin(pin_across, scale, extent_across)
        item.update(axis=axis, across=across, start=_xy(horizontal, edge + out * gap, middle))
        items.append(item)

    placed = [it for it in items if "axis" in it and it["n"] is not None and "text_at" not in it]
    # A column is one line, just past the widest thing in it.
    columns = {}
    for it in placed:
        if it["column"] is not None:
            columns.setdefault(it["column"], []).append(it)
    for members in columns.values():
        line = (max if members[0]["out"] > 0 else min)(it["axis"] for it in members)
        for it in members:
            it["axis"] = line
    # Markers on one line that would overlap are spread apart.
    groups = []
    for it in sorted(placed, key=lambda it: (it["horizontal"], it["axis"])):
        group = next((g for g in groups if g[0]["horizontal"] == it["horizontal"]
                      and abs(g[0]["axis"] - it["axis"]) < d), None)
        if group:
            group.append(it)
        else:
            groups.append([it])
    for group in groups:
        if len(group) > 1:
            for it, p in zip(group, _spread([it["across"] for it in group], d + px(SPACING_PT))):
                it["across"] = p
    # A marker that would touch another mark's brace or bracket moves back toward its own thing.
    clear = px(SPACING_PT)
    for it in placed:
        for other in items:
            if other is it or other["shape"] not in ("brace", "bracket") or other["horizontal"] != it["horizontal"]:
                continue
            lo, hi = other["span"]
            if not lo - d / 2 <= it["across"] <= hi + d / 2:
                continue
            reach = [other["line"], other["line"] + other["out"] * (px(BRACE_PT) if other["shape"] == "brace" else 0)]
            near, far = min(reach) - clear, max(reach) + clear
            if it["axis"] + d / 2 > near and it["axis"] - d / 2 < far:
                it["axis"] = near - d / 2 if it["out"] > 0 else far + d / 2
    for it in placed:
        it["center"] = _xy(it["horizontal"], it["axis"], it["across"])
        if it["shape"] == "marker":
            near = _xy(it["horizontal"], it["axis"] - it["out"] * d / 2, it["across"])
            apart = ((near[0] - it["start"][0]) ** 2 + (near[1] - it["start"][1]) ** 2) ** 0.5
            if it["lead"] if it["lead"] is not None else apart > max(d / 2, 1.0):
                it["lead_line"] = [it["start"], near]
    for k, it in enumerate(placed):
        for other in placed[k + 1:]:
            apart = ((it["center"][0] - other["center"][0]) ** 2 + (it["center"][1] - other["center"][1]) ** 2) ** 0.5
            if apart < d * 0.98:
                warnings.append(f"markers {it['n']} and {other['n']} overlap")
    return items, d, warnings


_ARROWS = {"←": r"$\leftarrow$", "→": r"$\rightarrow$", "↑": r"$\uparrow$", "↓": r"$\downarrow$"}


def _tex(text):
    """A label's text for TeX: its special characters escaped, its arrows as TeX's."""
    out = []
    for ch in str(text):
        if ch in "&%$#_{}":
            out.append("\\" + ch)
        else:
            out.append({"\\": r"\textbackslash{}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
                       .get(ch) or _ARROWS.get(ch) or ch)
    return "".join(out)


def _n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _p(point):
    return f"({_n(point[0])},{_n(point[1])})"


def unit_sp(unit):
    """Inches per pixel as TeX scaled points. TeX keeps a decimal length to 1/65536 of its
    unit, so `0.0048427in` would become 317/65536 in: 0.3% off, and every pixel blurred."""
    return round(unit * PT_PER_IN * 65536)


def render(items, image, size, unit, spec, frame):
    """The standalone TikZ source: the screenshot (unless `image` is None), then each mark over it.

    `frame` (left, top, right, bottom, in whole image pixels) is the page: it
    holds the screenshot and any mark that hangs past its edges, so the marks
    drawn alone line up pixel for pixel with the screenshot in the PNG.
    """
    W, H = size
    small = spec.get("size", "normal") == "small"
    marker = "small marker" if small else "marker"
    lead = "marker thin lead" if small else "marker lead"
    arm = ARM_PT / PT_PER_IN / unit
    rule = 0.4 / PT_PER_IN / unit / 2              # half the frame's 0.4-point line, in pixels
    out = [
        r"% Written by tools/shots (lib/annotate.py) from a take and its recipe.",
        r"\documentclass[border=0pt]{standalone}",
        r"\makeatletter\def\input@path{{" + str(STYLES) + r"/}}",
        r"\newcommand\shotsbbox{\pgfpointanchor{current bounding box}{south west}%",
        r"  \pgf@xa=\pgf@x \pgf@ya=\pgf@y \pgfpointanchor{current bounding box}{north east}%",
        r"  \typeout{SHOTS-BBOX \the\pgf@xa\space\the\pgf@ya\space\the\pgf@x\space\the\pgf@y}}",
        r"\makeatother",
        r"\usepackage[scaled=0.92]{helvet}",
        r"\usepackage{graphicx}",
        r"\usepackage{shotmarkers}",
        r"\begin{document}",
        rf"\setlength{{\unitlength}}{{{unit_sp(unit)}sp}}% one pixel of the screenshot",
        r"\begin{tikzpicture}[x=\unitlength,y=-\unitlength]",
        rf"  \path ({frame[0]},{frame[1]}) rectangle ({frame[2]},{frame[3]});",
    ]
    if image:        # no inner or outer separation, so the screenshot's corner is exactly at (0,0)
        out.append(rf"  \node[anchor=north west,inner sep=0,outer sep=0] at (0,0) "
                   rf"{{\includegraphics[width={W}\unitlength]{{{image}}}}};")
    if spec.get("border", True):                  # drawn inside the picture's edge, not across it
        out.append(rf"  \draw[black!25] ({_n(rule)},{_n(rule)}) rectangle ({_n(W - rule)},{_n(H - rule)});")
    for it in items:
        out.append(f"  % mark {it['mark']}: {it['shape']}" + (f" {it['n']}" if it["n"] is not None else ""))
        if it["shape"] in ("brace", "bracket"):
            (lo, hi), line = it["span"], it["line"]
            pt = (lambda a: (line, a)) if it["horizontal"] else (lambda a: (a, line))
            if it["shape"] == "brace":
                # TikZ draws a brace's tip on the left of the direction of travel; y points down here.
                ends = (lo, hi) if (it["out"] > 0) == it["horizontal"] else (hi, lo)
                out.append(rf"  \draw[marker brace] {_p(pt(ends[0]))} -- {_p(pt(ends[1]))};")
            else:
                back = (lambda a: (line - it["out"] * arm, a)) if it["horizontal"] else \
                    (lambda a: (a, line - it["out"] * arm))
                path = ([] if it["before"] else [back(lo)]) + [pt(lo), pt(hi)] + ([] if it["after"] else [back(hi)])
                tips = ("latex" if it["before"] else "") + "-" + ("latex" if it["after"] else "")
                style = "marker bracket" + ("," + tips if tips != "-" else "")
                out.append(rf"  \draw[{style}] " + " -- ".join(_p(q) for q in path) + ";")
        if it["shape"] == "box":
            x0, y0, x1, y1 = it["rect"]
            out.append(rf"  \draw[marker box] {_p((x0, y0))} rectangle {_p((x1, y1))};")
        if it.get("lead_line"):
            out.append(rf"  \draw[{lead}] {_p(it['lead_line'][0])} -- {_p(it['lead_line'][1])};")
        if "text_at" in it:
            x, y = it["text_at"]
            style = "marker label on" if 0 <= x <= W and 0 <= y <= H else "marker label"
            text = _tex(it["label"])
            if it["n"] is not None:
                text += rf" \tikz[baseline=-0.6ex]\node[{marker}]{{{it['n']}}};"
            out.append(rf"  \node[{style},anchor={ANCHORS[it['side']][it['align']]}] at {_p((x, y))} {{{text}}};")
        elif "center" in it:
            out.append(rf"  \node[{marker}] at {_p(it['center'])} {{{it['n']}}};")
    out += [r"  \shotsbbox", r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(out)


def _pdflatex(tex, folder, unit):
    """Build the PDF; return it and the drawing's extent (left, top, right, bottom) in image pixels."""
    (folder / "figure.tex").write_text(tex)
    run = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "figure.tex"],
                         cwd=folder, capture_output=True, text=True, timeout=180)
    pdf = folder / "figure.pdf"
    if run.returncode or not pdf.exists():
        errors = [line for line in run.stdout.splitlines() if line.startswith("!")]
        raise AnnotateError("pdflatex failed: " + ("; ".join(errors[:3]) or run.stdout[-300:]))
    found = re.search(r"SHOTS-BBOX (\S+)pt (\S+)pt (\S+)pt (\S+)pt", (folder / "figure.log").read_text())
    x0, y0, x1, y1 = (float(v) for v in found.groups())
    pt = unit_sp(unit) / 65536                  # points per image pixel, as TeX has it
    return pdf, (x0 / pt, -y1 / pt, x1 / pt, -y0 / pt)    # TikZ's y points up; the image's down


def tools_missing():
    return [t for t in ("pdflatex", "pdftocairo") if not shutil.which(t)]


def annotate_sha256(fig):
    return hashlib.sha256(json.dumps(fig.get("annotate"), sort_keys=True, default=str).encode()).hexdigest()


def stem_for(take):
    """Where a take's annotated files go: beside it, as <UTC time>.annotated.{pdf,png,tex,json}."""
    image = ROOT / take["image"]
    return image.with_name(image.name.removesuffix(".png") + ".annotated")


def build(fig, take, stem=None):
    """Draw the recipe's marks on a take. Writes <stem>.pdf, .png, .tex, and .json; returns the record."""
    missing = tools_missing()
    if missing:
        raise AnnotateError(f"annotation needs {', '.join(missing)}; run  bash tools/shots/bootstrap.sh --tex")
    stem = Path(stem or stem_for(take))
    spec = fig["annotate"]
    (W, H), scale = take["size"], take["scale"]
    width_in = float(spec.get("width_in", BOOK_WIDTH_IN))
    frame = (0, 0, W, H)
    unit = width_in / W
    with tempfile.TemporaryDirectory(prefix="shots-annotate-") as tmp:
        folder = Path(tmp)
        shutil.copyfile(ROOT / take["image"], folder / "take.png")
        # The page is the frame: the picture plus any mark hanging past its edges, squared to
        # whole pixels. Markers have a size in points, so their size in pixels depends on the
        # scale, and the frame (so the scale) on them: grow the frame until everything fits.
        for _ in range(8):
            items, d, warnings = layout(spec, take.get("anchors") or {}, (W, H), scale, unit)
            tex = render(items, "take.png", (W, H), unit, spec, frame)
            pdf, extent = _pdflatex(tex, folder, unit)
            need = (min(frame[0], math.floor(extent[0] + 0.01)), min(frame[1], math.floor(extent[1] + 0.01)),
                    max(frame[2], math.ceil(extent[2] - 0.01)), max(frame[3], math.ceil(extent[3] - 0.01)))
            if need == frame:
                break
            frame = need
            unit = width_in / (frame[2] - frame[0])
        else:
            raise AnnotateError("the markers' layout did not settle; check the marks for ones far outside the picture")
        stem.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, f"{stem}.pdf")
        Path(f"{stem}.tex").write_text(tex.replace("{take.png}", "{" + Path(take["image"]).name + "}"))
        # The PNG: the marks alone, drawn on a transparent page of the frame's size, laid over
        # the screenshot's own pixels. (Through TeX, the screenshot would be resampled: pdfTeX
        # writes an image's scale with five decimals, so it lands a fraction of a pixel off.)
        _pdflatex(render(items, None, (W, H), unit, spec, frame), folder, unit)
        subprocess.run(["pdftocairo", "-png", "-transp", "-singlefile", "-scale-to-x", str(frame[2] - frame[0]),
                        "-scale-to-y", str(frame[3] - frame[1]), str(folder / "figure.pdf"), str(folder / "marks")],
                       check=True, capture_output=True, timeout=180)
        with Image.open(ROOT / take["image"]) as shot, Image.open(folder / "marks.png") as marks:
            page = Image.new("RGBA", marks.size, "white")
            page.paste(shot.convert("RGBA"), (-frame[0], -frame[1]))
            Image.alpha_composite(page, marks.convert("RGBA")).convert("RGB").save(f"{stem}.png")
    record = {
        "image": take["image"], "image_sha256": take["image_sha256"],
        "width_in": round((frame[2] - frame[0]) * unit, 4), "unit_in": unit, "dpi": round(1 / unit, 2),
        "frame": list(frame), "marker_px": round(d, 1),
        "annotate_sha256": annotate_sha256(fig),
        "marks": [{k: v for k, v in it.items()
                   if k in ("mark", "n", "shape", "box", "center", "lead_line", "line", "span", "text_at", "label")}
                  for it in items],
        "warnings": warnings,
    }
    Path(f"{stem}.json").write_text(json.dumps(record, indent=2) + "\n")
    return record
