# Images for ch-07

Figures in `ch-07-archives.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `about-this-capture.png` | capture | 2026-09-25 | https://web.archive.org/web/20040212031928/http://www.thefacebook.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2×, closed shadow roots opened |
| `devtools-archived-page.png` | capture | 2026-09-25 | https://web.archive.org/web/20040212031928/http://www.thefacebook.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×680 at 2× |
| `facebook-2004.png` | capture | 2026-09-25 | https://web.archive.org/web/20040121224607/http://facebook.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 778×600 at 2×, closed shadow roots opened |
| `wayback-calendar.png` | capture | 2026-09-25 | https://web.archive.org/web/2005*/facebook.com | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1100 at 2× |
| `x-com-1999.png` | capture | 2026-09-25 | https://web.archive.org/web/19991114081850/http://x.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 700×600 at 2×, closed shadow roots opened |
<!-- shots:end -->

## Notes

All five were retaken with `tools/shots` on 2026-09-25 (AAR P2-1), within
the size limit: four within 800×600, and the calendar at 740×830, which its
recipe's `oversize:` explains. Recipes: `tools/shots/recipes/ch-07.yml`.

- **Live numbers drift.** The calendar's "Saved N times," its circles, and
  the toolbar's capture counts change daily. These figures show them as of
  2026-09-25, and the chapter quotes the same numbers. The counts come from
  the archive's `/__wb/sparkline` API: on 2026-09-25 its sums matched the
  calendar for facebook.com (8,516,745) and the toolbar for x.com (94,893),
  and gave google.com's 20,394,311.
- **The toolbar is narrow here.** Below 1,100 pixels wide, the Wayback
  toolbar drops its logo and its strip chart of captures by year. Every
  figure here is narrower, so the chapter's paragraph on the toolbar says
  what a wider window adds. The toolbar keeps its parts in a closed shadow
  root, which the recipes open (`open_shadow: true`) so they can wait for
  its capture count. The count arrives from a second request, which failed
  on some loads on 2026-09-25; two takes showed the toolbar without it.
- `wayback-calendar.png`: at 800 pixels wide the calendar sets three months
  to a row, so reaching August's blue circles takes three rows. The
  histogram shows 2004 to 2019, the years around the one selected. The CDX
  API gives the colors' boundaries: 200 until April 8, 2005 (still
  AboutFace's page, by the raw capture's title), 403 from April 10, and 200
  again from August 6.
- `facebook-2004.png`: the page is 823 pixels wide and most of its text is
  11 pixels, so the window is 778 pixels wide, the book's column, and its
  edge cuts the last of the banner's four photos. The archive answered 502
  for some of the page's images on some loads, and one take lost the banner
  with the tagline; the toolkit now fails and retries a take whose own
  images get a 5xx answer.
- `about-this-capture.png`: the panel's **Collected by** section loads on
  hover, a few seconds after **Timestamps**. The first take (course PR #43)
  missed it; the recipe hovers the About button (`#wm-expand`), opens the
  panel, and waits for "alexa_dv". The panel is translucent, so the 2004
  page shows faintly behind it.
- `x-com-1999.png`: the images are broken because the archive never saved
  them: six of the seven the page references were captured only as 404s, in
  August and September 2000 (CDX API, full query). An early query capped at
  25 rows suggested otherwise; see course PR #44. The page's fine print is 10
  pixels, so the window is 700 pixels wide.
- `devtools-archived-page.png` is a headed capture, with DevTools docked at
  the bottom and zoomed to 125%. The recipe picks the page's own `<center>`
  in its empty left margin, a third of the way down, because its top is
  under the pinned toolbar. Picking scrolls the page, so the recipe scrolls
  it back to the top. The crop stops above DevTools' breadcrumb bar.
- The week 7 slides use crops of the 2026-09-22 captures; their notes are
  in the course repo, `slides/week-07/img/IMAGES.md`.
