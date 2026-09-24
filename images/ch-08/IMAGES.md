# Images for ch-08

Figures in `ch-08-dynamic-pages.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `javascript-off-on.png` | capture | 2026-09-22 | https://quotes.toscrape.com/js/ | hand-run script, before tools/shots: two captures of the same page, JavaScript disabled and enabled, joined side by side and labeled |
| `network-tab-json.png` | capture | 2026-09-24 | https://quotes.toscrape.com/scroll | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1000 at 2× |
| `playwright-codegen.png` | capture | 2026-09-22 | https://quotes.toscrape.com/ | hand-run script, before tools/shots: playwright codegen --target python (Playwright 1.63, its bundled Chrome for Testing 153), headed on Xvfb, grabbed with ImageMagick import |
| `selenium-chrome-for-testing.png` | capture | 2026-09-22 | https://xkcd.com/ | hand-run script, before tools/shots: webdriver.Chrome() with Selenium 4.49 on a machine with no Chrome; Selenium Manager downloaded Chrome for Testing 154; headed on Xvfb, grabbed with ImageMagick import |
| `view-source-js.png` | capture | 2026-09-22 | view-source:https://quotes.toscrape.com/js/ | hand-run script, before tools/shots: Chrome for Testing 154 driven by Selenium 4.49, headed on a virtual display (Xvfb), View Source grabbed with ImageMagick import; the top of the source through line 43 |
| `xkcd-inspect.png` | capture | 2026-09-24 | https://xkcd.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1000 at 2× |
<!-- shots:end -->

## Notes

- Each figure shows browser UI or joins two captures. `view-source-js`,
  `network-tab-json`, and `xkcd-inspect` are headed captures (tools/shots
  milestone M2). `javascript-off-on` is a composite (M3): two headless captures
  of the same page, JavaScript off and on, joined and labeled; a take on
  2026-09-24 scored 2/64 against the approved image.
  `selenium-chrome-for-testing` and `playwright-codegen` show the tool itself,
  so they need that tool as the engine (M4); until then their recipes record
  how they were made.
- **`network-tab-json` and `xkcd-inspect`, retaken 2026-09-24.**
  - Why: the first versions, made by scripts before the toolkit, showed the
    whole 1680-pixel window, so DevTools' text came to about 5 pixels in the
    book's column. They also carried Chrome for Testing's "only for automated
    testing" notice under the address bar.
  - Now: each shows DevTools alone, taken in an 800×1000 window with DevTools
    docked at the bottom, 600 pixels tall and zoomed to 125%. Its text comes to
    13.4 pixels in the book. Headed captures run with `--disable-infobars`, so
    there is no notice.
  - `xkcd-inspect` stops at the breadcrumb bar, above the Styles pane that
    DevTools won't hide. It shows the comic current on 2026-09-24 (#3302,
    "Voyager Instruments"); a retake will show another, and its caption and
    alt text will need the new name and hover text.
- `selenium-chrome-for-testing.png` keeps Chrome for Testing's "only for
  automated testing" bar, because the bar is the lesson: the caption and alt
  text point at it, and its recipe says `expect: {infobar: true}`. It is the
  only figure that may show an infobar. It still shows the comic current on
  2026-09-22 (Stargazing 5).
- quotes.toscrape.com is a practice sandbox with no robots.txt.
- The week 8 slides use crops of the same captures; see the course repo,
  `slides/week-08/img/IMAGES.md`.
