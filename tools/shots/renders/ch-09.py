"""Chapter 9's renders: pages of the City of Boulder's revenue reports, drawn by pdfplumber.

    python tools/shots/renders/ch-09.py OUTDIR

Reads the saved copies in data/ch-09/ and writes two PNGs to OUTDIR, each 1600
pixels wide: 2 pixels per CSS pixel of an 800-pixel frame, as the recipes in
tools/shots/recipes/ch-09.yml say. Run it in the webdata environment, which has
pdfplumber, then import each one (tools/shots/README.md, "Hand captures"):

    tools/shots/run import ch-09 pdf-objects --file OUTDIR/pdf-objects.png \\
        --by NAME --date YYYY-MM-DD --tool "pdfplumber X.Y.Z"
"""
import sys
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw

DATA = Path(__file__).resolve().parents[3] / "data" / "ch-09"
WIDTH = 1600                      # image pixels: an 800-pixel frame at scale 2
RED, BLUE = (220, 50, 47), (38, 139, 210)


def page_image(page, bbox):
    """The part of `page` inside `bbox` (PDF points), drawn WIDTH pixels wide."""
    crop = page.crop(bbox)
    return crop, crop.to_image(resolution=WIDTH / crop.width * 72)


def pdf_objects(out):
    """December 2024's summary table: every rectangle the page draws, in red, and the
    characters of the title and the first row, each in its own blue box."""
    with pdfplumber.open(DATA / "revenue-report-2024-12.pdf") as pdf:
        page = pdf.pages[1]
        crop, im = page_image(page, (48, 148, 594, 394))
        bands = [page.search("Sales and Use Tax Summary")[0], page.search("Sales Tax")[0]]
        chars = [c for c in crop.chars if c["text"].strip()
                 and any(b["top"] - 1 <= c["top"] <= b["bottom"] + 1 for b in bands)]
        im.draw_rects(crop.rects, stroke=RED, stroke_width=2, fill=RED + (40,))
        im.draw_rects(chars, stroke=BLUE, stroke_width=2, fill=None)
        im.save(out / "pdf-objects.png")
        return f"pdf-objects.png: {len(crop.rects)} rectangles, {len(chars)} characters boxed"


def two_exhibit_3s(out):
    """Exhibit 3 in 2018, a table of text, above Exhibit 3 in December 2024, a picture of
    a table under a note, with a gray rule between them."""
    parts = []
    for name, bbox in (("revenue-report-2018.pdf", (36, 76, 756, 205)),
                       ("revenue-report-2024-12.pdf", (36, 76, 756, 245))):
        with pdfplumber.open(DATA / name) as pdf:
            parts.append(page_image(pdf.pages[14], bbox)[1].original.convert("RGB"))
    top, bottom = parts
    gap = 32
    image = Image.new("RGB", (WIDTH, top.height + gap + bottom.height), "white")
    image.paste(top, (0, 0))
    ImageDraw.Draw(image).line([(0, top.height + gap // 2), (WIDTH, top.height + gap // 2)],
                               fill=(150, 150, 150), width=4)
    image.paste(bottom, (0, top.height + gap))
    image.save(out / "two-exhibit-3s.png")
    return f"two-exhibit-3s.png: {image.size[0]}x{image.size[1]}, 2018's part {top.height} tall"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    folder.mkdir(parents=True, exist_ok=True)
    print(pdf_objects(folder))
    print(two_exhibit_3s(folder))
