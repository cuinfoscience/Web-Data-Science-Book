"""Load and check the recipe files: one YAML file per chapter in tools/shots/recipes/."""
import hashlib
import json
import re

import yaml

from .env import RECIPES, ROOT, rel

KINDS = {"capture", "render", "diagram", "illustration"}
MODES = {"headless", "headed", "composite"}
STEPS = {"wait", "hover", "click", "scroll", "press", "settle"}
CROPS = {"window", "full_page", "top", "left", "width", "height", "selector", "pad"}
EXPECTS = {"status", "text", "selector", "block"}
FIGURE_KEYS = {"id", "file", "kind", "section", "url", "mode", "steps", "expect", "crop",
               "javascript", "drifts", "legacy", "notes", "devtools", "window", "scale",
               "user_agent", "pause", "settle", "timeout", "retries"}
DEFAULTS = {
    "user_agent": "Web Data Science/v1 brian.keegan@colorado.edu",
    "window": [1280, 800],   # CSS pixels
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
        for step in f.get("steps") or []:
            if not (isinstance(step, dict) and len(step) == 1 and next(iter(step)) in STEPS):
                out.append(f"{where}: each step is one of {sorted(STEPS)}, as `- wait: {{...}}`")
        for key in set(f.get("crop") or {}) - CROPS:
            out.append(f"{where}: unknown crop key `{key}`")
        for key in set(f.get("expect") or {}) - EXPECTS:
            out.append(f"{where}: unknown expect key `{key}`")
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
        text = json.dumps({k: v for k, v in fig.items() if k not in ("legacy", "notes")},
                          sort_keys=True, default=str)
        fig["recipe_sha256"] = hashlib.sha256(text.encode()).hexdigest()
        figures.append(fig)
    qmd = raw.get("qmd") or next((p.name for p in sorted(ROOT.glob(f"{chapter}-*.qmd"))), None)
    return {"chapter": chapter, "qmd": qmd, "figures": figures, "path": path}


def figure(recipe, fid):
    for fig in recipe["figures"]:
        if fig["id"] == fid:
            return fig
    raise RecipeError(f"{recipe['chapter']} has no figure `{fid}`")
