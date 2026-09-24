"""Load and check the recipe files: one YAML file per chapter in tools/shots/recipes/."""
import hashlib
import json
import re

import yaml

from .env import RECIPES, ROOT, rel

KINDS = {"capture", "render", "diagram", "illustration"}
MODES = {"headless", "headed", "composite"}
PAGE_STEPS = {"wait", "hover", "click", "scroll", "press", "settle"}
HEADED_STEPS = {"inspect", "tree", "devtools_click", "devtools_wait", "key", "type", "pointer"}
STEPS = PAGE_STEPS | HEADED_STEPS
CROPS = {"window", "full_page", "content", "between", "top", "left", "width", "height", "selector", "pad",
         "devtools"}
EXPECTS = {"status", "text", "selector", "block", "infobar"}
DEVTOOLS = {"dock", "panel", "zoom", "size", "sidebar", "layout", "overview", "columns", "first_visit"}
DEVTOOLS_LAYOUTS = {"side-by-side", "stacked", "auto"}
FIGURE_KEYS = {"id", "file", "kind", "section", "brief", "url", "mode", "engine", "steps", "expect", "crop",
               "javascript", "drifts", "legacy", "notes", "devtools", "window", "scale",
               "user_agent", "pause", "settle", "timeout", "retries",
               "annotate", "targets", "legibility", "parts", "layout", "oversize"}
ENGINES = {"playwright", "selenium", "codegen"}
# Annotation (lib/annotate.py): marks placed from what the browser measured.
ANNOTATE = {"width_in", "size", "border", "marks"}
MARK_KEYS = {"n", "at", "shape", "side", "gap", "x", "y", "lead", "column", "label"}
SHAPES = {"marker", "brace", "bracket", "box", "label"}
SIDES = {"right", "left", "above", "below"}
PAGE_AT = {"selector", "text", "box", "nth", "all"}
DEVTOOLS_AT = {"row", "selected", "text", "css", "nth", "all"}
BOX_MODES = {"element", "text", "first-line"}
# Where a figure is shown, for the legibility check (lib/legibility.py).
TARGETS = {"book", "slides", "handout"}
LEGIBILITY = {"skip"}
# A composite (mode: composite) joins captures of its parts side by side.
PART_KEYS = {"label", "url", "steps", "expect", "crop", "javascript", "window", "scale", "mode",
             "devtools", "settle", "timeout"}
LAYOUT = {"gap", "pad", "label_px"}
# Settings that decide how a take is drawn on or judged, not how it is captured.
# Changing them needs no new take, so they stay out of the recipe's hash. So does
# the brief: the request the figure answers, in words.
NOT_CAPTURE = ("brief", "legacy", "notes", "annotate", "targets", "legibility", "oversize")
DEFAULTS = {
    "user_agent": "Web Data Science/v1 brian.keegan@colorado.edu",
    "window": [800, 600],    # CSS pixels; the default limit on what a figure shows, 1024×768 relaxed (lib/legibility.py)
    "scale": 2,              # device pixels per CSS pixel
    "pause": [8, 30],        # seconds between page loads on one host
    "settle": 1.0,           # seconds to let rendering finish after the last step
    "timeout": 60,           # seconds any one wait may take
    "retries": 3,            # extra attempts after a 5xx or a dropped connection
    "mode": "headless",
    "javascript": True,
}


class RecipeError(Exception):
    pass


def chapters():
    return sorted(p.stem for p in RECIPES.glob("ch-*.yml"))


def _problems(chapter, raw):
    out = []
    if not isinstance(raw, dict) or raw.get("chapter") != chapter:
        return [f"top level must be a mapping with `chapter: {chapter}`"]
    seen = set()
    for n, f in enumerate(raw.get("figures") or [], 1):
        where = f"figure {n} ({f.get('id', '?')})" if isinstance(f, dict) else f"figure {n}"
        if not isinstance(f, dict):
            out.append(f"{where}: not a mapping")
            continue
        for key in set(f) - FIGURE_KEYS:
            out.append(f"{where}: unknown key `{key}`")
        fid = f.get("id", "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(fid)):
            out.append(f"{where}: `id` must be lowercase words joined by hyphens")
        if fid in seen:
            out.append(f"{where}: duplicate id")
        seen.add(fid)
        if f.get("kind") not in KINDS:
            out.append(f"{where}: `kind` must be one of {sorted(KINDS)}")
        if f.get("kind") == "capture" and not f.get("url"):
            out.append(f"{where}: a capture needs a `url`")
        if f.get("mode", "headless") not in MODES:
            out.append(f"{where}: `mode` must be one of {sorted(MODES)}")
        if f.get("engine", "playwright") not in ENGINES:
            out.append(f"{where}: `engine` must be one of {sorted(ENGINES)}")
        out += [f"{where}: {p}" for p in _step_problems(f.get("steps"), f.get("mode") == "headed")]
        for key in set(f.get("devtools") or {}) - DEVTOOLS:
            out.append(f"{where}: unknown devtools key `{key}`")
        if (f.get("devtools") or {}).get("layout", "auto") not in DEVTOOLS_LAYOUTS:
            out.append(f"{where}: devtools `layout` is one of {sorted(DEVTOOLS_LAYOUTS)}")
        if f.get("devtools") and f.get("mode") != "headed":
            out.append(f"{where}: `devtools` needs `mode: headed`")
        if (f.get("devtools") or {}).get("first_visit") and f["devtools"].get("panel") != "network":
            out.append(f"{where}: devtools `first_visit` needs `panel: network`")
        if (f.get("crop") or {}).get("devtools") and not f.get("devtools"):
            out.append(f"{where}: `crop: {{devtools: true}}` needs a `devtools:` block")
        for key in set(f.get("crop") or {}) - CROPS:
            out.append(f"{where}: unknown crop key `{key}`")
        for key in set(f.get("expect") or {}) - EXPECTS:
            out.append(f"{where}: unknown expect key `{key}`")
        if (f.get("expect") or {}).get("infobar") and f.get("mode") != "headed":
            out.append(f"{where}: `expect: {{infobar: true}}` is for a headed figure, the only kind with browser bars")
        out += [f"{where}: {p}" for p in _annotate_problems(f)]
        for key in set(f.get("targets") or {}) - TARGETS:
            out.append(f"{where}: unknown target `{key}` (one of {sorted(TARGETS)})")
        for key in set(f.get("legibility") or {}) - LEGIBILITY:
            out.append(f"{where}: unknown legibility key `{key}`")
        if "oversize" in f and not (isinstance(f["oversize"], str) and f["oversize"].strip()):
            out.append(f"{where}: `oversize` is the reason a figure shows more than 800×600, as a sentence "
                       "(up to 1024×768: the clutter the extra room removes)")
        if "brief" in f and not (isinstance(f["brief"], str) and f["brief"].strip()):
            out.append(f"{where}: `brief` is the request the figure answers, in sentences")
        out += [f"{where}: {p}" for p in _composite_problems(f)]
    return out


def _step_problems(steps, headed):
    out = []
    for step in steps or []:
        if not (isinstance(step, dict) and len(step) == 1 and next(iter(step)) in STEPS):
            out.append(f"each step is one of {sorted(STEPS)}, as `- wait: {{...}}`")
        elif next(iter(step)) in HEADED_STEPS and not headed:
            out.append(f"step `{next(iter(step))}` needs `mode: headed`")
    return out


def _composite_problems(f):
    if f.get("mode") != "composite":
        return ["`parts` and `layout` need `mode: composite`"] if f.get("parts") or f.get("layout") else []
    out = []
    parts = f.get("parts")
    if not isinstance(parts, list) or len(parts) < 2:
        return ["`mode: composite` needs two or more `parts`"]
    for n, part in enumerate(parts, 1):
        if not isinstance(part, dict) or not part.get("label"):
            out.append(f"part {n} needs a `label`")
            continue
        out += [f"part {n}: unknown key `{k}`" for k in set(part) - PART_KEYS]
        if part.get("mode", "headless") not in ("headless", "headed"):
            out.append(f"part {n}: `mode` is headless or headed")
        out += [f"part {n}: {p}" for p in _step_problems(part.get("steps"), part.get("mode") == "headed")]
    out += [f"unknown layout key `{k}`" for k in set(f.get("layout") or {}) - LAYOUT]
    return out


def _at_problems(at, headed):
    if not isinstance(at, dict) or len(set(at) & {"selector", "text", "devtools", "xy"}) != 1:
        return ["`at` names one of selector, text, devtools, or xy"]
    out = []
    if "xy" in at:
        xy = at["xy"]
        if not (isinstance(xy, list) and len(xy) in (2, 4) and all(isinstance(v, (int, float)) for v in xy)):
            out.append("`xy` is [x, y] or [x, y, width, height], in image pixels")
        out += [f"`xy` takes no other keys (not `{k}`)" for k in set(at) - {"xy"}]
    elif "devtools" in at:
        spec = at["devtools"]
        if not headed:
            out.append("a DevTools anchor needs `mode: headed`")
        if not isinstance(spec, dict) or not set(spec) & {"row", "selected", "text", "css"}:
            out.append("`devtools` names a row, the selected row, text, or css")
        else:
            out += [f"unknown devtools anchor key `{k}`" for k in set(spec) - DEVTOOLS_AT]
        out += [f"unknown anchor key `{k}`" for k in set(at) - {"devtools"}]
    else:
        out += [f"unknown anchor key `{k}`" for k in set(at) - PAGE_AT]
        if at.get("box", "element") not in BOX_MODES:
            out.append(f"`box` is one of {sorted(BOX_MODES)}")
    return out


def _annotate_problems(f):
    spec = f.get("annotate")
    if spec is None:
        return []
    if not isinstance(spec, dict):
        return ["`annotate` must be a mapping"]
    out = [f"unknown annotate key `{k}`" for k in set(spec) - ANNOTATE]
    if spec.get("size", "normal") not in ("normal", "small"):
        out.append("annotate `size` is normal or small")
    if f.get("mode") == "composite":
        out.append("marks on a composite are not supported")
    for n, mark in enumerate(spec.get("marks") or [], 1):
        where = f"mark {n}"
        if not isinstance(mark, dict):
            out.append(f"{where}: not a mapping")
            continue
        out += [f"{where}: unknown key `{k}`" for k in set(mark) - MARK_KEYS]
        shape = mark.get("shape", "marker" if "n" in mark else "label")
        if shape not in SHAPES:
            out.append(f"{where}: `shape` is one of {sorted(SHAPES)}")
        if mark.get("side", "right") not in SIDES:
            out.append(f"{where}: `side` is one of {sorted(SIDES)}")
        if "n" not in mark and not mark.get("label"):
            out.append(f"{where}: needs a number `n`, a `label`, or both")
        if "at" not in mark:
            out.append(f"{where}: needs `at`, the thing it points to")
        else:
            out += [f"{where}: {p}" for p in _at_problems(mark["at"], f.get("mode") == "headed")]
    return out


def load(chapter):
    path = RECIPES / f"{chapter}.yml"
    if not path.exists():
        raise RecipeError(f"no recipe file {rel(path)}")
    raw = yaml.safe_load(path.read_text())
    problems = _problems(chapter, raw)
    if problems:
        raise RecipeError(f"{rel(path)}:\n  " + "\n  ".join(problems))
    base = {**DEFAULTS, **(raw.get("defaults") or {})}
    figures = []
    for f in raw.get("figures") or []:
        fig = {**base, **f}
        fig.setdefault("file", f"{f['id']}.png")
        fig["chapter"] = chapter
        # The figure's own recipe, defaults included, so a changed default counts too.
        text = json.dumps({k: v for k, v in fig.items() if k not in NOT_CAPTURE},
                          sort_keys=True, default=str)
        fig["recipe_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        figures.append(fig)
    qmd = raw.get("qmd") or next((p.name for p in sorted(ROOT.glob(f"{chapter}-*.qmd"))), None)
    return {"chapter": chapter, "qmd": qmd, "figures": figures, "path": path,
            "course": bool(raw.get("course"))}


def figure(recipe, fid):
    for fig in recipe["figures"]:
        if fig["id"] == fid:
            return fig
    raise RecipeError(f"{recipe['chapter']} has no figure `{fid}`")


def part_figure(fig, n):
    """Part n (from 0) of a composite, as a figure of its own."""
    part = fig["parts"][n]
    sub = {k: v for k, v in fig.items() if k not in ("parts", "layout", "annotate", "steps", "expect", "crop")}
    sub.update({k: v for k, v in part.items() if k != "label"})
    sub.update({"id": f"{fig['id']}-part{n + 1}", "mode": part.get("mode", "headless"),
                "label": part["label"]})
    return sub
