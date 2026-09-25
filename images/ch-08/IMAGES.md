# Images for ch-08

Figures in `ch-08-dynamic-pages.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `javascript-off-on.png` | capture | 2026-09-24 | https://quotes.toscrape.com/js/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 370×520 at 2× |
| `network-tab-json.png` | capture | 2026-09-24 | https://quotes.toscrape.com/scroll | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1000 at 2× |
| `playwright-codegen.png` | capture | 2026-09-25 | https://quotes.toscrape.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×230 at 2×, playwright codegen's recorder (Playwright 1.63.0), its Inspector 800×595 below |
| `selenium-chrome-for-testing.png` | capture | 2026-09-25 | https://xkcd.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2×, webdriver.Chrome() under Selenium 4.49.0 (ChromeDriver 154.0.8037.57) |
| `view-source-js.png` | capture | 2026-09-24 | view-source:https://quotes.toscrape.com/js/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 816×720 at 2× |
| `xkcd-inspect.png` | capture | 2026-09-24 | https://xkcd.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1000 at 2× |
<!-- shots:end -->

## Notes

- Each figure shows browser UI or joins two captures. `view-source-js`,
  `network-tab-json`, and `xkcd-inspect` are headed captures (tools/shots
  milestone M2). `javascript-off-on` is a composite (M3): two headless captures
  of the same page, JavaScript off and on, joined and labeled.
  `selenium-chrome-for-testing` and `playwright-codegen` show the tool itself,
  so the tool is their engine (M4): `engine: selenium` and `engine: codegen`.
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
- **`view-source-js` and `javascript-off-on`, retaken 2026-09-24**, to fit
  800×600.
  - `view-source-js` was 1100×760: the whole source from its first line, 1100
    pixels wide because line 43, the first quote's text, runs about 140
    characters. Now it starts at `<body>` (line 11) and turns on View Source's
    "Line wrap", so line 43 wraps. The window is 816×720 so that lines 11–43
    fit below the browser's bars, and the 800-pixel crop leaves out the
    scrollbar. Text: 12.6 pixels in the book.
  - `javascript-off-on` was 1858×758, two 900-pixel pages. Now each page is
    370 pixels wide, in the site's narrow layout (Login under the title), and
    the pair with its labels and frame is 798×592. The words are legible (13.6
    pixels in the book), so the recipe no longer exempts it from the
    legibility check.
  - The week 8 slides keep their own versions (`view_source_js.png`,
    `requests_vs_browser.png`), which suit their frames and pass the slide
    threshold.
- **`selenium-chrome-for-testing` and `playwright-codegen`, retaken
  2026-09-25**, by the toolkit's first engines.
  - Why: the versions of 2026-09-22 showed a 1280×860 window and two windows
    1,630 pixels across, so the book's column showed their text at 61% and
    48% of its size on screen.
  - `selenium-chrome-for-testing` is the 800×600 window `webdriver.Chrome()`
    opens, driven by Selenium alone. Selenium Manager resolves Chrome for
    Testing 154 and its ChromeDriver, as the chapter describes. At this width
    the bar's sentence stops after "For regular browsing, use a…". The page's
    text comes to 19.4 pixels in the book.
  - `playwright-codegen` is codegen's recorder in Chrome for Testing 154, fed
    real clicks: the tag *change*, then the first *(about)* link. The browser
    (800×230) sits above the Inspector (800×595), cropped after line 15,
    `browser.close()`. The Inspector draws code at 14 pixels, which come to
    13.6 in the book.
  - quotes.toscrape.com redirects its author pages to plain http, which the
    session's proxy doesn't carry. The recipe turns Chrome's HTTPS-Upgrades
    back on, as in regular Chrome, so the page loads over https. Codegen on a
    student's machine shows it over http, with "Not secure".
- `selenium-chrome-for-testing.png` keeps Chrome for Testing's "only for
  automated testing" bar, because the bar is the lesson: the caption and alt
  text point at it, and its recipe says `expect: {infobar: true}`. It is the
  only figure that may show an infobar. It shows the comic current on
  2026-09-25 (#3302, "Voyager Instruments"); a retake will show another, and
  its alt text will need the new name.
- quotes.toscrape.com is a practice sandbox with no robots.txt.
- The week 8 slides use crops of the same captures; see the course repo,
  `slides/week-08/img/IMAGES.md`.
