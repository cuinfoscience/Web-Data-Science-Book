# Images for ch-07

Figures in `ch-07-archives.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `about-this-capture.png` | capture | 2026-09-22 | https://web.archive.org/web/20040212031928/http://www.thefacebook.com/ | hand-run script, before tools/shots: headless Playwright (Node), 1280×800 window at 1×, top 240 pixels, after hovering and clicking About this capture by position |
| `devtools-archived-page.png` | capture | 2026-09-22 | https://web.archive.org/web/20040212031928/http://www.thefacebook.com/ | hand-run script, before tools/shots: Chrome on a virtual display (Xvfb) with DevTools docked right, grabbed with ImageMagick import |
| `facebook-2004.png` | capture | 2026-09-22 | https://web.archive.org/web/20040121224607/http://facebook.com/ | hand-run script, before tools/shots: headless Playwright (Node), 1280×800 window at 1×, the whole window |
| `wayback-calendar.png` | capture | 2026-09-22 | https://web.archive.org/web/2005*/facebook.com | hand-run script, before tools/shots: headless Playwright (Node), 1280×800 window at 1×, the whole window |
| `x-com-1999.png` | capture | 2026-09-22 | https://web.archive.org/web/19991114081850/http://x.com/ | hand-run script, before tools/shots: headless Playwright (Node), 1280×800 window at 1×, top 610 pixels |
<!-- shots:end -->

## Notes

- Live numbers drift. The calendar's "Saved N times," its capture circles,
  and the toolbar's capture counts change daily; these figures show them as
  of 2026-09-22.
- `about-this-capture.png`: the panel's **Collected by** section loads on
  hover, a few seconds after **Timestamps**. The first take (course PR #43)
  missed it; the recipe hovers first and waits for it.
- `x-com-1999.png`: the images are broken because the archive never saved
  them: six of the seven the page references were captured only as 404s, in
  August and September 2000 (CDX API, full query). An early query capped at
  25 rows suggested otherwise; see course PR #44.
- `devtools-archived-page.png` is a headed capture (tools/shots milestone M2):
  its recipe inspects a word of the 2004 page, then climbs the Elements tree
  by keyboard to the page's own `<center>`, so the body shows the toolbar
  insert, the comment that ends it, and Thefacebook's markup.
- The week 7 slides use crops of the same captures; their notes are in the
  course repo, `slides/week-07/img/IMAGES.md`.
