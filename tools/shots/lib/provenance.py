"""images/<chapter>/provenance.json, and the table it writes into IMAGES.md.

provenance.json holds one entry per image: what kind of image it is, where it
came from, when, and how, plus a hash of the image so `check` notices a file
replaced by hand. IMAGES.md gets a generated table between two markers;
everything else in IMAGES.md is for people and is never touched.
"""
import json

from .env import IMAGES

BEGIN = ("<!-- shots:begin: generated from provenance.json by tools/shots;"
         " edits between these markers are replaced -->")
END = "<!-- shots:end -->"
KEEP = ("file", "kind", "url", "final_url", "status", "captured", "by", "method", "browser",
        "user_agent", "window", "scale", "javascript", "crop", "clip", "size",
        "recipe_sha256", "image_sha256", "note", "text", "parts")


def annotated_name(file):
    """The annotated image's file name: x-com-1999.png -> x-com-1999_annotated.png (.pdf beside it)."""
    return file.removesuffix(".png") + "_annotated.png"


def path(chapter):
    return IMAGES / chapter / "provenance.json"


def load(chapter):
    try:
        return json.loads(path(chapter).read_text())
    except FileNotFoundError:
        return {"chapter": chapter, "figures": {}}


def save(chapter, data):
    path(chapter).parent.mkdir(parents=True, exist_ok=True)
    path(chapter).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def from_take(take, annotated=None):
    """A take's provenance; `annotated` records the marked-up copy made from it, if any."""
    entry = {k: take[k] for k in KEEP if k in take}
    if annotated:
        entry["annotated"] = annotated
    return entry


def from_legacy(fig, image_sha256, size):
    """An image made before the toolkit existed, described by the recipe's `legacy:` block."""
    legacy = fig["legacy"]
    entry = {"file": fig["file"], "kind": fig["kind"], "url": fig.get("url"),
             "captured": str(legacy["captured"]), "by": "hand-run script, before tools/shots",
             "method": legacy["method"], "size": size, "image_sha256": image_sha256}
    if legacy.get("note"):
        entry["note"] = legacy["note"]
    return entry


def _how(entry):
    if entry.get("by") == "tools/shots":
        width, height = entry.get("window", ["?", "?"])
        browser = entry.get("browser", "").split(" (")[0]
        return f"tools/shots: {browser}, {width}×{height} at {entry.get('scale')}×"
    return f"{entry.get('by')}: {entry.get('method', '')}"


def table(data):
    rows = ["| File | Kind | Captured | Source | How |", "|---|---|---|---|---|"]
    for fid in sorted(data["figures"]):
        e = data["figures"][fid]
        name = f"`{e['file']}`" + (f" and `{annotated_name(e['file'])}`, `.pdf`" if e.get("annotated") else "")
        rows.append(f"| {name} | {e['kind']} | {str(e.get('captured', ''))[:10]} "
                    f"| {e.get('url') or ''} | {_how(e)} |")
    return "\n".join(rows) + "\n"


def write_images_md(chapter, qmd, data):
    """Update the generated table in images/<chapter>/IMAGES.md; returns what happened."""
    md = IMAGES / chapter / "IMAGES.md"
    block = f"{BEGIN}\n{table(data)}{END}\n"
    if not md.exists():
        md.write_text(
            f"# Images for {chapter}\n\n"
            f"Figures in `{qmd}`. `tools/shots` writes the table below from `provenance.json`\n"
            "and rewrites only what is between the two markers. Notes below the table are\n"
            "for people: what a figure shows that is easy to miss, and what a retake needs.\n\n"
            f"{block}\n## Notes\n")
        return "created IMAGES.md"
    old = md.read_text()
    lines = old.splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if l.startswith("<!-- shots:begin")]
    ends = [i for i, l in enumerate(lines) if l.startswith(END)]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        return "IMAGES.md has no shots markers (or unmatched ones); not touching it"
    new = "".join(lines[:starts[0]]) + block + "".join(lines[ends[0] + 1:])
    if new == old:
        return "IMAGES.md table unchanged"
    md.write_text(new)
    return "updated the IMAGES.md table"
