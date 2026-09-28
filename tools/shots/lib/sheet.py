"""Contact sheets: each figure's newest take, drawn at the size each target shows it.

    tools/shots/run sheet ch-05            -> tools/shots/out/ch-05/sheet-1.png, ...

For the agent's own review before a pull request, and for the pull request
itself: one look shows whether a marker covers what it points at, and
whether the text can be read in the book's column, on a slide, and on paper.
Each target is drawn at its real size: the book's column at 778 pixels, a
slide's share of a 1920-pixel-wide slide, a handout at 96 pixels per inch
(a printed page seen at 100%). The measured text size and the verdict are
written over each one.
"""
from PIL import Image, ImageDraw, ImageFont

from . import legibility
from .env import OUT, ROOT

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WIDTH, PAGE, MARGIN, GAP = 1920, 3000, 32, 28
SCREEN_DPI = 96


def _widths(fig, image_w, annotated):
    """Pixel width of each target's rendering."""
    shown = annotated["width_in"] / annotated["unit_in"] if annotated else image_w
    out = {}
    for name, setting in legibility.targets(fig).items():
        if name == "book":
            out[name] = min(setting.get("width_px", legibility.BOOK_PX), shown)
        elif name == "slides":
            out[name] = setting.get("width", 1.0) * legibility.SLIDE_PX * legibility.SLIDE_TEXT
        elif name == "handout":
            width_in = setting.get("width_in") or (annotated or {}).get("width_in")
            if width_in:
                out[name] = width_in * SCREEN_DPI
    return {k: max(40, round(v)) for k, v in out.items()}


def blocks(entries):
    """entries: (fig, take, annotated record or None, image path). Yields one image per figure."""
    font, bold = ImageFont.truetype(FONT, 20), ImageFont.truetype(BOLD, 24)
    for fig, take, annotated, path in entries:
        verdicts = {name: (size, limit, unit, ok) for name, size, limit, unit, ok in
                    legibility.judge(fig, take.get("text"), take["size"][0], annotated)}
        with Image.open(path) as img:
            img = img.convert("RGB")
            widths = _widths(fig, take["size"][0], annotated) or {"take": min(img.width, WIDTH - 2 * MARGIN)}
            tiles = []
            for name, width in widths.items():
                height = round(img.height * width / img.width)
                tile = img.resize((width, height), Image.LANCZOS)
                size, limit, unit, ok = verdicts.get(name, (None, None, "", True))
                caption = name if size is None else \
                    f"{name}: text {size:g} {unit} ({'ok' if ok else f'under {limit:g}'})"
                tiles.append((tile, caption, ok))
        rows, row, used = [], [], MARGIN
        for tile in tiles:
            if row and used + tile[0].width > WIDTH - MARGIN:
                rows.append(row)
                row, used = [], MARGIN
            row.append(tile)
            used += tile[0].width + GAP
        rows.append(row)
        shows = "{}×{}".format(*legibility.region(take))
        title = (f"{fig['chapter']}/{fig['id']}  ·  {take['captured'][:16]}Z  ·  "
                 f"{take['size'][0]}×{take['size'][1]} pixels, {shows} CSS")
        if annotated:
            title += f"  ·  annotated at {annotated['width_in']:g} in"
            if annotated.get("warnings"):
                title += "  ·  " + "; ".join(annotated["warnings"])
        verdict = legibility.size_verdict(
            fig, take, legibility.judge(fig, take.get("text"), take["size"][0], annotated))
        note = verdict[1] if verdict else ""
        height = MARGIN + 40 + (30 if note else 0) + sum(max(t.height for t, _, _ in r) + 40 + GAP for r in rows)
        block = Image.new("RGB", (WIDTH, height), "white")
        draw = ImageDraw.Draw(block)
        draw.text((MARGIN, MARGIN), title, fill="black", font=bold)
        y = MARGIN + 40
        if note:                         # the soft limit on what a figure shows: gray when allowed
            draw.text((MARGIN, y), note, fill=(110, 110, 110) if verdict[0] == "note" else (190, 0, 0), font=font)
            y += 30
        for r in rows:
            x = MARGIN
            for tile, caption, ok in r:
                draw.text((x, y), caption, fill=(0, 110, 0) if ok else (190, 0, 0), font=font)
                block.paste(tile, (x, y + 30))
                draw.rectangle([x - 1, y + 29, x + tile.width, y + 30 + tile.height], outline=(180, 180, 180))
                x += tile.width + GAP
            y += max(t.height for t, _, _ in r) + 40 + GAP
        yield block


def write(chapter, entries):
    """Stack figure blocks into pages; returns the files written."""
    pages, page, used = [], [], 0
    for block in blocks(entries):
        if page and used + block.height > PAGE:
            pages.append(page)
            page, used = [], 0
        page.append(block)
        used += block.height
    if page:
        pages.append(page)
    folder = OUT / chapter
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("sheet-*.png"):
        old.unlink()
    written = []
    for n, page in enumerate(pages, 1):
        sheet = Image.new("RGB", (WIDTH, sum(b.height for b in page)), "white")
        y = 0
        for b in page:
            sheet.paste(b, (0, y))
            y += b.height
        path = folder / f"sheet-{n}.png"
        sheet.save(path)
        written.append(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return written
