"""Chapter 9's renders: pages of the City of Boulder's revenue reports, drawn by pdfplumber,
and one picture of a table with the words Tesseract read on it.

    python tools/shots/renders/ch-09.py OUTDIR

    python tools/shots/renders/ch-09.py OUTDIR sales-use-tax   # only this one

Reads the saved copies in data/ch-09/ and writes five PNGs to OUTDIR, each 1600
pixels wide: 2 pixels per CSS pixel of an 800-pixel frame, as the recipes in
tools/shots/recipes/ch-09.yml say. The last is a chart that matplotlib draws
from what the chapter's revenue-report case study reads. Run it in the webdata environment, which has
pdfplumber, pypdf, pytesseract, and Tesseract, then import each one
(tools/shots/README.md, "Hand captures"), naming the program that drew it:

    tools/shots/run import ch-09 pdf-objects --file OUTDIR/pdf-objects.png \\
        --by "Brian C. Keegan" --date YYYY-MM-DD --tool "pdfplumber X.Y.Z"
"""
import re
import sys
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image, ImageDraw
from pypdf import PdfReader

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


def missing_totals_row(out):
    """pdfplumber's table finder on December 2024's summary table: the cells it found,
    shaded, and the totals row below them, which it left out."""
    with pdfplumber.open(DATA / "revenue-report-2024-12.pdf") as pdf:
        crop, im = page_image(pdf.pages[1], (48, 148, 594, 396))  # 396: below the totals row, above the footnote
        tables = crop.find_tables()
        im.debug_tablefinder()
        im.save(out / "missing-totals-row.png")
        return f"missing-totals-row.png: {len(tables)} tables, the first ending at {tables[0].bbox[3]:.1f} points"


def ocr_confidence(out):
    """The retail sales tax rows of December 2024's Exhibit 3, a picture of a table, with a box
    around each word Tesseract read: blue for a confidence of 80 or more, red below."""
    image = PdfReader(DATA / "revenue-report-2024-12.pdf").pages[14].images[0].image.convert("L")
    words = pytesseract.image_to_data(image, config="--psm 6", output_type=pytesseract.Output.DICT)
    box = (340, 36, 1130, 266)  # image pixels: the YEAR column through MAY, the header through 2024
    scale = WIDTH / (box[2] - box[0])
    crop = image.crop(box).convert("RGB")
    crop = crop.resize((WIDTH, round(crop.height * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(crop)
    low = boxed = 0
    for i, text in enumerate(words["text"]):
        x, y, w, h, conf = (words[k][i] for k in ("left", "top", "width", "height", "conf"))
        if not text.strip() or float(conf) < 0 or x < box[0] or x + w > box[2] or y < box[1] or y + h > box[3]:
            continue
        rect = [(x - box[0] - 3) * scale, (y - box[1] - 3) * scale,
                (x + w - box[0] + 3) * scale, (y + h - box[1] + 3) * scale]
        draw.rectangle(rect, outline=BLUE if float(conf) >= 80 else RED, width=4)
        boxed += 1
        low += float(conf) < 80
    crop.save(out / "ocr-confidence.png")
    return f"ocr-confidence.png: {boxed} words boxed, {low} below 80"


def chart_axes():
    """A figure 1600 by 800 pixels, with text that comes to 16 CSS pixels and more in an 800-pixel frame."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(8, 4), dpi=200)
    ax.spines[["top", "right"]].set_visible(False)
    return fig, ax


def sales_use_tax(out):
    """Total sales and use tax by year, each year's latest printing, with its change from the year before."""
    reports = ["revenue-report-2018.pdf", "revenue-report-2019.pdf", "revenue-report-2020.pdf",
               "revenue-report-2021-12.pdf", "revenue-report-2022-12.pdf",
               "revenue-report-2023-12.pdf", "revenue-report-2024-12.pdf"]
    latest = {}
    for name in reports:
        with pdfplumber.open(DATA / name) as pdf:
            page = next(p for p in pdf.pages[:4] if "This report provides" in (p.extract_text() or ""))
            years = [int(y) for y in page.search(r"(20\d\d) +(20\d\d)")[0]["groups"]]
            found = page.search("Total Sales and Use Tax")[0]
            line = page.crop((0, found["top"] - 1, page.width, found["bottom"] + 1))
            words = [w["text"] for w in line.extract_words() if w["x0"] > found["x1"]][:2]
            for year, word in zip(years, words):
                latest[year] = int(re.sub(r"[^\d]", "", word))  # reports run oldest to newest
    years = sorted(latest)
    totals = [latest[y] / 1e6 for y in years]
    fig, ax = chart_axes()
    ax.bar(years, totals, color="#1f4e79")
    for i, year in enumerate(years[1:], start=1):
        change = (latest[year] / latest[years[i - 1]] - 1) * 100
        ax.text(year, totals[i] + 2, f"{change:+.1f}%", ha="center", fontsize=12)
    ax.set_xticks(years)
    ax.set_ylim(0, 200)
    ax.set_ylabel("Sales and use tax ($ millions)")
    fig.tight_layout()
    fig.savefig(out / "sales-use-tax.png")
    return f"sales-use-tax.png: {[round(t, 1) for t in totals]}"


FIGURES = {"pdf-objects": pdf_objects, "two-exhibit-3s": two_exhibit_3s,
           "missing-totals-row": missing_totals_row, "ocr-confidence": ocr_confidence,
           "sales-use-tax": sales_use_tax}

if __name__ == "__main__":
    if len(sys.argv) < 2 or any(name not in FIGURES for name in sys.argv[2:]):
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    folder.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[2:] or FIGURES:
        print(FIGURES[name](folder))
