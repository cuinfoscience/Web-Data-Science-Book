# Images for ch-08

Figures in `ch-08-dynamic-pages.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `javascript-off-on.png` | capture | 2026-09-22 | https://quotes.toscrape.com/js/ | hand-run script, before tools/shots: two captures of the same page, JavaScript disabled and enabled, joined side by side and labeled |
| `network-tab-json.png` | capture | 2026-09-22 | https://quotes.toscrape.com/scroll | hand-run script, before tools/shots: Chrome for Testing 154 driven by Selenium 4.49, headed on Xvfb, DevTools docked right and operated with real clicks (xdotool), grabbed with ImageMagick import |
| `playwright-codegen.png` | capture | 2026-09-22 | https://quotes.toscrape.com/ | hand-run script, before tools/shots: playwright codegen --target python (Playwright 1.63, its bundled Chrome for Testing 153), headed on Xvfb, grabbed with ImageMagick import |
| `selenium-chrome-for-testing.png` | capture | 2026-09-22 | https://xkcd.com/ | hand-run script, before tools/shots: webdriver.Chrome() with Selenium 4.49 on a machine with no Chrome; Selenium Manager downloaded Chrome for Testing 154; headed on Xvfb, grabbed with ImageMagick import |
| `view-source-js.png` | capture | 2026-09-22 | view-source:https://quotes.toscrape.com/js/ | hand-run script, before tools/shots: Chrome for Testing 154 driven by Selenium 4.49, headed on a virtual display (Xvfb), View Source grabbed with ImageMagick import; the top of the source through line 43 |
| `xkcd-inspect.png` | capture | 2026-09-22 | https://xkcd.com/ | hand-run script, before tools/shots: Chrome for Testing 154, headed on Xvfb, right-click > Inspect on the comic with real clicks (xdotool), DevTools docked right, grabbed with ImageMagick import |
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
- The DevTools figures show the whole 1680-pixel window, so their DevTools
  text comes to about 5 pixels in the book's 778-pixel column (the lightbox
  enlarges it). A retake is judged by the legibility check (tools/shots
  README, "Legibility").
- Chrome for Testing labels its own window "only for automated testing";
  `selenium-chrome-for-testing.png` keeps that bar because it is the lesson.
- `xkcd-inspect.png` and `selenium-chrome-for-testing.png` show the comic
  that was current on 2026-09-22 (Stargazing 5). A retake will show another.
- quotes.toscrape.com is a practice sandbox with no robots.txt.
- The week 8 slides use crops of the same captures; see the course repo,
  `slides/week-08/img/IMAGES.md`.
