# Images for ch-09

Figures in `ch-09-pdfs.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `missing-totals-row.png` | render | 2026-10-06 | https://documents.bouldercolorado.gov/WebLink/ElectronicFile.aspx?docid=194397&dbid=0&repo=LF8PROD2 | Claude Code: rendered with pdfplumber 0.11.10; imported by tools/shots |
| `ocr-confidence.png` | render | 2026-10-06 | https://documents.bouldercolorado.gov/WebLink/ElectronicFile.aspx?docid=194397&dbid=0&repo=LF8PROD2 | Claude Code: rendered with pytesseract 0.3.13 with Tesseract 5.5.3; imported by tools/shots |
| `pdf-objects.png` | render | 2026-10-06 | https://documents.bouldercolorado.gov/WebLink/ElectronicFile.aspx?docid=194397&dbid=0&repo=LF8PROD2 | Claude Code: rendered with pdfplumber 0.11.10; imported by tools/shots |
| `two-exhibit-3s.png` | render | 2026-10-06 | https://documents.bouldercolorado.gov/WebLink/ElectronicFile.aspx?docid=194397&dbid=0&repo=LF8PROD2 | Claude Code: rendered with pdfplumber 0.11.10; imported by tools/shots, 1 area blacked out |
<!-- shots:end -->

## Notes

All four figures are renders, not screenshots: pdfplumber draws pages of the
book's saved copies of the city's revenue reports (`data/ch-09/`), or, for
`ocr-confidence`, boxes Tesseract's words on one of the report's images, and
`tools/shots/renders/ch-09.py` is the script. Recipes:
`tools/shots/recipes/ch-09.yml`. They were the first renders imported with
`--tool` (2026-10-06), so their records say "rendered with pdfplumber" or
"rendered with pytesseract".

- **Little here drifts.** The saved copies are fixed files, checked by hash
  in `data/ch-09/manifest.csv`, so a retake only changes if pdfplumber draws
  differently, or, for `ocr-confidence`, if Tesseract reads differently. The source address is the portal's download link for the
  December 2024 report (docid 194397); `two-exhibit-3s` also draws the 2018
  report (docid 194398), which its recipe's steps name.
- `pdf-objects.png`: page 2 of the December 2024 report, cropped to the
  summary table (PDF points 48–594 across, 148–394 down). Every one of the
  290 rectangles in the crop is outlined, which shades the header cells
  darker than the page does. Characters are boxed only in the title and the
  Sales Tax row, 73 of them, so the other rows stay readable. The chapter's
  code counts 549 rectangles on the whole page.
- `two-exhibit-3s.png`: page 15 of both reports, each cropped to 720 points
  across from 76 down, so both titles sit at the same height. The 2018
  table's numbers are too small to read at this size, and don't need to be:
  the figure shows the format. The 2024 note's phone number and email
  address are blacked out (the recipe's `redact:`); the chapter quotes the
  note with "…" in their place.
- `missing-totals-row.png`: page 2 of the December 2024 report, cropped to
  PDF points 48–594 across and 148–396 down: the table in `pdf-objects`,
  with 2 more points at the bottom, so the totals row's double rule is in
  and the footnote (from 397.7 down) is out. pdfplumber's
  `debug_tablefinder()` with its default settings fills the cells it found,
  draws their edges in red, and circles the rules' crossings. The table it
  finds ends at 375 points, and the totals row runs from 380 to 391.
- `ocr-confidence.png`: the one image on page 15 of the December 2024
  report (2,545 by 1,331 pixels), cropped to image pixels 340–1130 across
  and 36–266 down, which is the YEAR column through MAY for the retail
  sales tax rows, 2019–2024, enlarged from 790 to 1,600 pixels. The boxes
  come from `pytesseract.image_to_data()` on the whole image in grayscale
  with `--psm 6`, as in the chapter: 42 words, 13 of them below 80 (red).
  The caption names Tesseract's three misreads in the crop, which the image
  can't show, since it shows the page. On a retake with another Tesseract,
  check them again, and the counts in the chapter's text.
