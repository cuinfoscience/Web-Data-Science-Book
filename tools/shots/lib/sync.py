"""Sync: copy a figure into the course repository, with its notes (M4; the plan's §7.11).

    tools/shots/run sync ch-08 playwright-codegen --to slides/week-08/img --as codegen.png
    tools/shots/run sync course week08-js-off --to slides/week-08/img --as js_off.png
    tools/shots/run synced                     every copy against its record and its source

A chapter figure is copied as approved, from images/<chapter>/, with its
marked-up PNG and PDF when it has markers. A course-only figure is copied from
its newest passing take in out/course/, since `promote` keeps those out of
images/. The destination folder gets:

- the file, under `--as` (by default the figure's own name);
- a record in `shots.json` beside it: the figure, the file it was copied from
  and that file's textbook commit, both hashes, and the capture's page, date,
  browser, and User-Agent;
- a table in its `IMAGES.md`, generated from `shots.json`, between
  `<!-- shots:begin -->` and `<!-- shots:end -->`. Everything outside the
  markers is for people, and `make_stubs.py` keeps to its own markers;
- the size in `stubs.tsv`, when the file has a row there, and the stubs table
  redrawn.

`synced` reads every `shots.json` in the course repository and reports a copy
changed by hand, and a copy whose source has changed since it was copied.

The course repository is `--course`, or $SHOTS_COURSE, or `INFO4617-Fall2026`
beside this repository.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import provenance as prov
from .env import IMAGES, ROOT, rel

RECORD = "shots.json"
BEGIN = ("<!-- shots:begin: copies from the textbook's tools/shots, generated from shots.json;"
         " edits between these markers are replaced -->")
END = "<!-- shots:end -->"


class SyncError(Exception):
    pass


def course_repo(given=None):
    path = Path(given or os.environ.get("SHOTS_COURSE") or ROOT.parent / "INFO4617-Fall2026")
    if not (path / "slides").is_dir() and not (path / "handouts").is_dir():
        raise SyncError(f"no course repository at {path} (it has no slides/ or handouts/); "
                        "give its path with --course or $SHOTS_COURSE")
    return path


def _sha256(path):
    from .capture import sha256
    return sha256(path)


def _commit(path):
    """The commit that last changed a file, in the repository that holds it, or None if the file
    isn't committed as it is."""
    try:
        where = {"cwd": Path(path).parent, "capture_output": True, "text": True, "timeout": 30}
        status = subprocess.run(["git", "status", "--porcelain", "--", Path(path).name], **where)
        if status.returncode or status.stdout.strip():
            return None
        found = subprocess.run(["git", "log", "-1", "--format=%H", "--", Path(path).name], **where)
        return found.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              timeout=30).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def source(recipe, fig, take_path=None, annotated=False):
    """(files to copy [(source path, suffix)], provenance-like entry, commit) for a figure. With
    `annotated`, the marked-up PNG alone, as a handout that shows only it keeps it."""
    if annotated and recipe["course"]:
        raise SyncError("`--annotated` copies a chapter figure's marked-up PNG; a course figure's markers "
                        "stay with its take in out/")
    if recipe["course"]:
        from .capture import takes
        found = takes(recipe["chapter"], fig["id"])
        if take_path:
            found = [t for t in found if Path(t["image"]).name == Path(take_path).name]
        if not found:
            raise SyncError(f"{recipe['chapter']}/{fig['id']} has no passing take"
                            f"{' named ' + Path(take_path).name if take_path else ''}; capture it first")
        take = found[0]
        if take.get("recipe_sha256") != fig["recipe_sha256"]:
            raise SyncError(f"the recipe of {recipe['chapter']}/{fig['id']} changed after its newest take; "
                            "capture it again")
        image = ROOT / take["image"]
        # A take is not committed; the record names the recipe's commit and the take itself.
        return [(image, ".png")], prov.from_take(take), _head()
    data = prov.load(recipe["chapter"])
    entry = data["figures"].get(fig["id"])
    image = IMAGES / recipe["chapter"] / fig["file"]
    if not entry or not image.exists():
        raise SyncError(f"{recipe['chapter']}/{fig['id']} has no approved image; promote a take first")
    if entry.get("image_sha256") != _sha256(image):
        raise SyncError(f"{rel(image)} changed after its provenance was recorded; `check` says more")
    if annotated:
        if not entry.get("annotated"):
            raise SyncError(f"{recipe['chapter']}/{fig['id']} has no markers to copy")
        image = IMAGES / recipe["chapter"] / prov.annotated_name(fig["file"])
    commit = _commit(image)
    if not commit:
        raise SyncError(f"commit {rel(image)} first, so the copy's record can name the commit it came from")
    files = [(image, ".png")]
    if entry.get("annotated") and not annotated:
        marked = IMAGES / recipe["chapter"] / prov.annotated_name(fig["file"])
        files += [(marked, "_annotated.png"), (marked.with_suffix(".pdf"), "_annotated.pdf")]
    return files, entry, commit


def load_record(folder):
    try:
        return json.loads((folder / RECORD).read_text())
    except FileNotFoundError:
        return {"files": {}}


def table(record):
    rows = ["| File | Copy of | Captured | Source | How |", "|---|---|---|---|---|"]
    for name in sorted(record["files"]):
        r = record["files"][name]
        commit = f", textbook `{r['textbook_commit'][:7]}`" if r.get("textbook_commit") else ""
        extra = "".join(f" and `{x}`" for x in r.get("also", []))
        rows.append(f"| `{name}`{extra} | `{r['figure']}` ({r['copied_from']}{commit}) "
                    f"| {str(r.get('captured', ''))[:10]} | {r.get('url') or ''} | {prov._how(r)} |")
    return "\n".join(rows) + "\n"


def write_images_md(folder, record):
    md = folder / "IMAGES.md"
    block = (f"{BEGIN}\nCopied here by the textbook's `tools/shots/run sync`; `tools/shots/run synced` "
             f"checks them.\n\n{table(record)}{END}\n")
    if not md.exists():
        md.write_text(f"# Images in `{folder.parent.name}/{folder.name}`\n\n{block}")
        return "created IMAGES.md"
    old = md.read_text()
    lines = old.splitlines(keepends=True)
    starts = [i for i, l in enumerate(lines) if l.startswith("<!-- shots:begin")]
    ends = [i for i, l in enumerate(lines) if l.startswith(END)]
    if len(starts) == 1 and len(ends) == 1 and starts[0] < ends[0]:
        new = "".join(lines[:starts[0]]) + block + "".join(lines[ends[0] + 1:])
    elif not starts and not ends:
        # Before the stubs table if there is one, since that table is the file's last section.
        stubs = next((i for i, l in enumerate(lines) if l.startswith("## Listed in `stubs.tsv`")), None)
        cut = stubs if stubs is not None else len(lines)
        head = "".join(lines[:cut]).rstrip("\n") + "\n\n"
        new = head + "## Copied by tools/shots\n\n" + block + ("\n" + "".join(lines[cut:]) if stubs is not None else "")
    else:
        return "IMAGES.md has unmatched shots markers; not touching it"
    if new == old:
        return "IMAGES.md table unchanged"
    md.write_text(new)
    return "updated the IMAGES.md table"


def update_stubs(folder, name, size):
    """Set the file's size in stubs.tsv, if it has a row; then redraw the stubs table."""
    tsv = folder / "stubs.tsv"
    if not tsv.exists():
        return None
    lines = tsv.read_text().splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        cells = line.rstrip("\n").split("\t")
        if len(cells) >= 3 and cells[0] == name and cells[1] != size:
            cells[1] = size
            lines[i] = "\t".join(cells) + "\n"
            changed = True
    if not changed:
        return None
    tsv.write_text("".join(lines))
    stubs = folder.parent.parent / "common" / "make_stubs.py"
    if stubs.exists():
        subprocess.run([sys.executable, str(stubs), str(folder.parent)], capture_output=True, timeout=120)
    return f"stubs.tsv: {name} is {size}"


def sync(recipe, fig, course, to, name=None, take=None, annotated=False):
    """Copy a figure into course/to; returns lines to print. `take` picks a course figure's take;
    `annotated` copies a chapter figure's marked-up PNG alone."""
    from PIL import Image
    folder = (course / to).resolve()
    if course.resolve() not in folder.parents:
        raise SyncError(f"--to {to} is outside the course repository")
    if not folder.is_dir():
        raise SyncError(f"no folder {to} in the course repository")
    files, entry, commit = source(recipe, fig, take, annotated)
    name = name or (prov.annotated_name(fig["file"]) if annotated else fig["file"])
    if not name.endswith(".png"):
        raise SyncError("`--as` names a .png file")
    record = load_record(folder)
    said, also = [], []
    for path, suffix in files:
        target = folder / (name[:-4] + suffix if suffix != ".png" else name)
        was = ("the same as the file already there" if target.exists() and _sha256(target) == _sha256(path)
               else "replacing a different file" if target.exists() else "new")
        shutil.copyfile(path, target)
        if suffix != ".png":
            also.append(target.name)
        said.append(f"copied {rel(path)} -> {target.relative_to(course)} ({was})")
    copied = folder / name
    with Image.open(copied) as img:
        size = f"{img.width}x{img.height}"
    keep = ("url", "final_url", "captured", "browser", "user_agent", "window", "scale", "size", "kind",
            "open_shadow", "engine", "by", "method", "imported", "redacted")
    record["files"][name] = {
        "figure": f"{recipe['chapter']}/{fig['id']}",
        "copied_from": rel(files[0][0]),
        "textbook_commit": commit,
        "source_sha256": _sha256(files[0][0]),
        "sha256": _sha256(copied),
        "synced": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        **{k: entry[k] for k in keep if k in entry},
        **({"also": also} if also else {}),
    }
    (folder / RECORD).write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    said.append(f"recorded in {(folder / RECORD).relative_to(course)}")
    said.append(write_images_md(folder, record))
    stub = update_stubs(folder, name, size)
    if stub:
        said.append(stub)
    return said


def synced(course):
    """[(level, text)] for every recorded copy in the course repository."""
    out = []
    for record_file in sorted(course.glob("*/*/img/" + RECORD)):
        folder = record_file.parent
        record = json.loads(record_file.read_text())
        for name, r in sorted(record["files"].items()):
            where = f"{folder.relative_to(course)}/{name}"
            copy = folder / name
            if not copy.exists():
                out.append(("bad", f"{where}: recorded, but missing"))
                continue
            if _sha256(copy) != r["sha256"]:
                out.append(("bad", f"{where}: changed by hand since it was copied from {r['figure']}"))
                continue
            src = ROOT / r["copied_from"]
            if not src.exists():
                out.append(("warn", f"{where}: its source, {r['copied_from']}, is gone (a take cleaned from out/?)"))
            elif _sha256(src) != r["source_sha256"]:
                out.append(("warn", f"{where}: {r['copied_from']} changed since it was copied; sync it again"))
            else:
                out.append(("good", f"{where}: as copied from {r['figure']}"))
    return out
