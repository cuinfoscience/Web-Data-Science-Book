"""Hand captures: a person's screenshot of a page the toolkit can't load, imported as a take (M4).

    tools/shots/run import course issue-form --file issue.png --by "A. Person" \
        --date 2026-09-28 --browser "Chrome 141 on macOS 15"

Some pages only a person can show, such as a form behind a login: the toolkit
never signs in. The recipe describes the figure as it does any other, with
`mode: hand` and a `hand:` block that says why a person takes it and what they do:

    - id: issue-form
      kind: capture
      mode: hand
      url: https://github.com/OWNER/REPO/issues/new?template=revision.yml
      hand:
        why: the form needs a signed-in GitHub account, and the toolkit never signs in
        steps: >
          Sign in, open the URL in a window whose page is 800 CSS pixels wide, and take a
          screenshot of the window. Read window.devicePixelRatio in the console: it is `scale`.
        text_px: 14      # the form's text, in CSS pixels, from DevTools' Computed pane
      scale: 2           # the screenshot's pixels per CSS pixel: the page's devicePixelRatio
      crop: {top: 86, left: 0, width: 800, height: 480}
      redact:
        - {box: [700, 90, 100, 40], why: the signed-in account's avatar and menu}

`crop` and each `redact` box are in the screenshot's CSS pixels, counted from its
top-left corner: its pixels divided by `scale`. Both use that one frame, so a
redaction stays on what it hides when the crop changes.

`import` makes a take in out/, as `capture` does, so `sheet`, `promote`, and
`sync` treat it like any other:

- it blacks out each `redact` box, then crops;
- it converts the image to sRGB from the screenshot's own color profile (a
  Mac's is Display P3) and writes a new PNG, which leaves the screenshot's
  metadata behind: its PNG text and EXIF, where a computer's name can hide;
- it places the recipe's marks, which on a screenshot can only be `xy`, in the
  take's pixels;
- it records the text size the recipe declares as the take's text, marked as
  declared, so the legibility check can judge it; no page is left to measure;
- it records who took the screenshot, on what day, in what browser, and the
  screenshot's SHA-256. The screenshot itself isn't kept.

Nothing reads a screenshot's text, so nothing finds a name or an address that
the redactions missed. Look at the take on the contact sheet before promoting it.
"""
import datetime
import io
import math
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw

from . import guards, measure
from .capture import _stamp, _write, sha256
from .env import OUT, rel

HAND = {"why", "steps", "text_px"}
REDACT = {"box", "why"}
EDGES = {"window", "top", "left", "width", "height"}
# A figure's settings that mean something only when the toolkit loads the page itself.
LOADING = ("steps", "expect", "devtools", "parts", "layout", "open_shadow", "inspector", "https_upgrades")


class HandError(Exception):
    pass


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def problems(f):
    """Recipe problems with a hand capture (`mode: hand`), or with its keys on another figure."""
    if f.get("mode") != "hand":
        out = []
        if "hand" in f:
            out.append("`hand:` describes a screenshot a person takes: it needs `mode: hand`")
        if "redact" in f:
            out.append("`redact` boxes are for `mode: hand`; crop a capture to what the text discusses instead")
        return out
    out = []
    if f.get("kind") != "capture":
        out.append("a screenshot a person takes is `kind: capture`")
    spec = f.get("hand")
    if not isinstance(spec, dict):
        out.append("`mode: hand` needs a `hand:` block: `why` a person takes it, and the text's size, `text_px`")
        spec = {}
    out += [f"unknown hand key `{k}`" for k in set(spec) - HAND]
    if spec and not (isinstance(spec.get("why"), str) and spec["why"].strip()):
        out.append("`hand: {why: ...}` says why a person takes it (a login, for one)")
    if spec and not (_number(spec.get("text_px")) and spec["text_px"] > 0):
        out.append("`hand: {text_px: N}` is the CSS size of the text a reader needs, from DevTools' Computed "
                   "pane, so the legibility check can judge it")
    out += [f"`{key}` has no meaning for a screenshot a person takes" for key in LOADING if key in f]
    if f.get("engine", "playwright") != "playwright":
        out.append("`engine` has no meaning for a screenshot a person takes")
    out += [f"a hand capture crops by `top`, `left`, `width`, and `height`, not `{key}`"
            for key in set(f.get("crop") or {}) - EDGES]
    for n, mark in enumerate((f.get("annotate") or {}).get("marks") or [], 1):
        if isinstance(mark, dict) and isinstance(mark.get("at"), dict) and "xy" not in mark["at"]:
            out.append(f"mark {n}: a screenshot has no page to find things in; place its marks with `xy`")
    redact = f.get("redact") or []
    if not isinstance(redact, list):
        return out + ["`redact` is a list of boxes, each {box: [left, top, width, height], why: ...}"]
    for n, r in enumerate(redact, 1):
        if not isinstance(r, dict):
            out.append(f"redact {n}: not a mapping")
            continue
        out += [f"redact {n}: unknown key `{k}`" for k in set(r) - REDACT]
        box = r.get("box")
        if not (isinstance(box, list) and len(box) == 4 and all(_number(v) for v in box)
                and box[2] > 0 and box[3] > 0):
            out.append(f"redact {n}: `box` is [left, top, width, height] in the screenshot's CSS pixels")
        if not (isinstance(r.get("why"), str) and r["why"].strip()):
            out.append(f"redact {n}: `why` says what the box hides (an avatar, a name)")
    return out


def _date(text):
    """The day (or moment) a screenshot was taken, as ISO text; never in the future."""
    try:
        value = datetime.date.fromisoformat(text)
        day = value
    except (TypeError, ValueError):
        try:
            value = datetime.datetime.fromisoformat(text)
        except (TypeError, ValueError):
            raise HandError(f"--date {text!r} is neither a day (YYYY-MM-DD) nor an ISO time")
        day = value.date()
    if day > datetime.date.today() + datetime.timedelta(days=1):       # a day's slack for time zones
        raise HandError(f"--date {text} is in the future")
    return value.isoformat()


def _flatten(img):
    """RGB on white, in sRGB: from the screenshot's own color profile when it has one."""
    rgba = img.convert("RGBA")
    flat = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba).convert("RGB")
    icc = img.info.get("icc_profile")
    if not icc:
        return flat, None
    try:
        source = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        name = ImageCms.getProfileDescription(source).strip()
        return ImageCms.profileToProfile(flat, source, ImageCms.createProfile("sRGB"), outputMode="RGB"), name
    except (ImageCms.PyCMSError, OSError, ValueError) as e:
        return flat, f"a profile that couldn't be read ({e}); colors kept as they were"


def _pixels(box, scale):
    """[left, top, width, height] in CSS pixels -> [left, top, right, bottom] in image pixels, outward."""
    x, y, w, h = box
    return [math.floor(x * scale), math.floor(y * scale), math.ceil((x + w) * scale), math.ceil((y + h) * scale)]


def _crop_box(fig, width, height):
    """The crop as [left, top, width, height] in the screenshot's CSS pixels."""
    crop, S = fig.get("crop") or {}, fig["scale"]
    if not crop or crop.get("window"):
        return [0, 0, width / S, height / S]
    left, top = crop.get("left", 0), crop.get("top", 0)
    return [left, top, crop.get("width", width / S - left), crop.get("height", height / S - top)]


def run(fig, file, by, date, browser=None):
    """Import a person's screenshot as a take of `fig`; returns the take's log. Raises HandError when
    the screenshot can't be read or used as the recipe says."""
    if not (by or "").strip():
        raise HandError("--by names the person who took the screenshot")
    captured = _date(date)
    file = Path(file)
    try:
        with Image.open(file) as img:
            img.load()
            kind = img.format
            flat, color = _flatten(img)
    except (OSError, ValueError) as e:
        raise HandError(f"can't read {file.name} as an image ({e})")
    if kind != "PNG":
        raise HandError(f"{file.name} is a {kind}; import a PNG, since a JPEG's compression blurs text")
    S, (W, H) = fig["scale"], flat.size
    crop = _crop_box(fig, W, H)
    rect = [round(crop[0] * S), round(crop[1] * S), round((crop[0] + crop[2]) * S), round((crop[1] + crop[3]) * S)]
    if rect[2] > W or rect[3] > H:
        raise HandError(f"the crop reaches {crop[0] + crop[2]:g}×{crop[1] + crop[3]:g} CSS pixels, past the "
                        f"screenshot's {W / S:g}×{H / S:g} at scale {S:g}. Is `scale` the page's devicePixelRatio "
                        "when the screenshot was taken?")
    draw, redacted = ImageDraw.Draw(flat), []
    for r in fig.get("redact") or []:
        box = _pixels(r["box"], S)
        draw.rectangle([box[0], box[1], box[2] - 1, box[3] - 1], fill="black")
        hides = box[0] < rect[2] and box[2] > rect[0] and box[1] < rect[3] and box[3] > rect[1]
        redacted.append({"box": r["box"], "why": r["why"], **({} if hides else {"outside_crop": True})})
    shot = flat.crop(rect)
    # The pixels alone, in a new image: the screenshot's text chunks and EXIF stay behind, and the
    # PNG is untagged sRGB, as a capture's is.
    shot = Image.frombytes("RGB", shot.size, shot.tobytes())
    folder = OUT / fig["chapter"] / fig["id"]
    folder.mkdir(parents=True, exist_ok=True)
    png = folder / f"{_stamp()}.png"
    shot.save(png)
    problems = guards.image_problems(png)
    if problems:
        failed = png.with_name(png.stem + ".FAILED.png")
        png.rename(failed)
        png = failed
    how = "screenshot by hand" + (f" in {browser}" if browser else "") + "; imported by tools/shots"
    if redacted:
        how += f", {len(redacted)} area{'' if len(redacted) == 1 else 's'} blacked out"
    text_px = fig["hand"]["text_px"]
    take = {
        "ok": not problems, "problems": problems,
        "chapter": fig["chapter"], "figure": fig["id"], "file": fig["file"], "kind": fig["kind"],
        "url": fig.get("url"), "final_url": None, "status": None,
        "captured": captured,
        "imported": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "by": by.strip(), "method": how, **({"browser": browser} if browser else {}),
        "window": fig["window"], "scale": S, "mode": "hand", "crop": fig.get("crop") or {"window": True},
        "clip": {"x": rect[0] / S, "y": rect[1] / S, "width": (rect[2] - rect[0]) / S,
                 "height": (rect[3] - rect[1]) / S},
        "size": list(shot.size), "recipe_sha256": fig["recipe_sha256"], "image": rel(png),
        "image_sha256": sha256(png), "attempts": [],
        "raw": {"sha256": sha256(file), "size": [W, H], **({"color": color} if color else {})},
        "redacted": redacted,
        "anchors": {measure.key(at): measure.hand_box(at["xy"]) for at in measure.marks_anchors(fig) if "xy" in at},
        # No page to measure: the size the recipe declares, in the take's pixels, stands in for p20.
        "text": {"declared": text_px, "p20": round(text_px * S, 1)},
    }
    _write(take, png)
    return take
