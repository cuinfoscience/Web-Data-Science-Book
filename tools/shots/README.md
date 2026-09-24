# tools/shots

Capture, check, and record the book's screenshots, so that every figure can
be made again the same way and says where it came from. The plan and the
after-action report behind it are in the course repo:
`docs/plans/2026-09-24-screenshot-toolkit.md` and
`docs/aar/2026-09-24-screenshots.md`.

Done so far:

- **M1:** headless captures, guards, retries, provenance, and `check`.
- **M2:** headed captures of browser UI (DevTools, View Source), with real input on a virtual display.
- **M3:** numbered markers placed from what the browser measured, a legibility check at each size a figure is shown, side-by-side composites, and contact sheets.

Still to come:

- **M4:** evidence queries, copying figures into the course repo, CI, and the two ch-08 figures whose subject is a tool itself (the window Selenium opens, Playwright's recorder).

## Quick start

```bash
bash tools/shots/bootstrap.sh --headed --tex      # once per container; safe to re-run
tools/shots/run doctor ch-07                      # every time, first: can this session capture?
tools/shots/run capture ch-07                     # takes go to tools/shots/out/ch-07/<figure>/
tools/shots/run sheet ch-07                       # look at every take at the size it will be shown
tools/shots/run compare ch-07 wayback-calendar    # same picture as the approved image?
tools/shots/run promote ch-07 wayback-calendar    # copy the take into images/ch-07/, record it
tools/shots/run check                             # before a PR
```

- **`bootstrap.sh`** does five things, plus two optional ones:
  - installs what is missing;
  - creates `tools/shots/.venv` with the pinned packages in `requirements.txt`;
  - fetches Chrome for Testing at a pinned major version (154) through Selenium Manager;
  - makes sure Chrome trusts the session proxy's certificate;
  - installs fonts, so pages in other scripts render as text and labels have a face;
  - with `--headed`, it adds the virtual display (Xvfb), real input (xdotool), and screen grabs (ImageMagick) that headed figures need;
  - with `--tex`, it adds pdflatex with TikZ and pdftocairo, which draw markers.

  It never runs `playwright install` and never turns off certificate checks.
- **`doctor`** answers whether capture works in this session. Do not reuse an earlier session's answer:
  - it checks the proxy, the browser, a real headless capture of example.com, and a real headed one with DevTools open;
  - it checks for TeX, and fails if a recipe has markers and TeX is missing;
  - with a chapter, it makes one request to each host that chapter's recipes use;
  - it reports a proxy refusal as a policy block, which you report rather than route around.

## The rules

These come from `slides/common/AUTHORING.md` in the course repo and from the AAR:

- **Real or labeled.** A screenshot is a real capture of a real page. Diagrams and renders are welcome, marked with their `kind`. Never rebuild a real site's interface with invented content.
- **One honest User-Agent** for every request (`Web Data Science/v1 brian.keegan@colorado.edu`, the one the handouts teach). Page loads on one host are 8–30 seconds apart.
- **Retries:** a 5xx or a dropped connection is retried three times, 30, 60, then 120 seconds apart. A block page, a 403, or a proxy refusal is not retried.
- **No logins, no credentials, no student names or work.** A page behind a login is captured by the instructor by hand (M4 adds `import`).
- **Dated captions.** A figure that shows things that change (counts, versions, live pages) says in its caption when it was captured.

## How a capture works

`capture` runs each figure's recipe in a fresh browser context:

1. It paces the request.
2. It loads the page.
3. It runs the steps.
4. It checks the page and the image against the guards.
5. It crops.
6. It writes the take to `tools/shots/out/<chapter>/<figure>/<UTC time>.png`, with a `.json` log beside it.

A take fails its guards when:

- the status is unexpected;
- the page reads like an error or block page (a Cloudflare challenge, "Access denied," the Wayback Machine's "Fail with status");
- expected text is missing;
- the image is nearly blank.

A failed take is named `<UTC time>.FAILED.png` and kept for inspection. `promote` refuses it. Nothing but `promote` writes to `images/`.

`compare` scores a take against the approved image with a difference hash: near 0 of 64 for the same region of the same page, about 32 for a different page. The score ignores scale, so a 2× take compares fairly with a 1× image, and live numbers that drift barely move it.

## Recipes

One YAML file per chapter in `recipes/`. A figure:

```yaml
- id: x-com-1999                 # the image is images/ch-07/x-com-1999.png
  kind: capture                  # capture | render | diagram | illustration
  section: "Broken and Missing Captures"
  url: https://web.archive.org/web/19991114081850/http://x.com/
  steps:                         # each step waits for a condition; none sleeps blindly
    - wait: {selector: '#wm-ipp-base'}
    - wait: {text: 'X\.com Corporation'}   # a regular expression; reaches into shadow DOM
  expect:                        # guards beyond the defaults
    text: ['X\.com Corporation']
  crop: {top: 0, height: 610}    # CSS pixels; or {window: true}, {selector: ..., pad: 8}
  drifts: true                   # shows things that change: the caption must say when
  legacy:                        # how an image made before tools/shots was made
    captured: 2026-09-22
    method: headless Playwright (Node), 1280×800 window at 1×, top 610 pixels
```

- **Defaults:** a 1280×800 window at scale 2, 8–30 second pauses, a 60-second limit on each wait, three retries, and JavaScript on. A chapter can change them under `defaults:`, and a figure can override any of them.
- **Steps:** `wait` (for `text`, `selector`, or `network_idle`), `hover`, `click` (by `selector`, `text`, or, as a last resort, `position`), `scroll`, `press`, and `settle` (seconds, for animation with no end signal). `scroll: {selector: …, offset: 175}` puts an element's top 175 pixels below the window's top.
- **Crops around an element** take `pad` as one number or four (top, right, bottom, left, as in CSS), and `width` and `height` to fix the size: `{selector: '.card', pad: [13, 0, 0, 18.5], width: 560, height: 595}`.
- **Other modes:** `mode: headed` and `mode: composite` are below. An `engine:` other than Playwright (M4) marks a figure that `capture` skips with a note.
- **Patterns** are regular expressions. A leading `(?i)` ignores case; the tool turns it into JavaScript's `i` flag, because Playwright and DevTools evaluate patterns in JavaScript, which has no inline flags.
- **Quoting:** quote any YAML value that contains ` #`, or everything after it becomes a comment. In single quotes, a backslash is literal: write `'quotes\?page=2'`.

## Headed figures

A figure that shows browser UI (DevTools, View Source, a menu) sets `mode: headed`:

```yaml
- id: xkcd-inspect
  kind: capture
  url: https://xkcd.com/
  mode: headed
  window: [1680, 1000]              # the whole browser window, in CSS pixels
  devtools: {dock: right, panel: elements}
  steps:
    - wait: {selector: '#comic img'}
    - inspect: {selector: '#comic img', selects: '^<img'}
  crop: {window: true}
```

How a headed capture runs:

- **The window:** Chrome for Testing opens on a virtual display sized for the window at its scale. It gets a fresh profile, a debugging port, and no "controlled by automated test software" bar.
- **DevTools settings:** `devtools:` opens DevTools with the page, from settings written into the profile before launch:
  - `dock` (`right`, `bottom`, `left`);
  - `zoom` (1.75 makes its text large enough for print);
  - `size`: the pane's width, or its height when docked at the bottom;
  - `sidebar`: the Styles sidebar's width.

  DevTools 154 ignores the stored `panel`, so the toolkit clicks that panel's tab. For `network`, it then reloads the page so the log is complete.
- **Finding DevTools controls:** docked DevTools is itself a web page. The toolkit reads that page over the debugging port to find where a tab, button, request row, or header name is drawn, then clicks it for real with xdotool. No pixel positions are typed into recipes.
- **Before any step:** it waits for the page's `load` event and for DevTools to draw its Elements tree. DevTools undoes a selection made before then.
- **The screen grab:** the pointer is parked in the page's bottom-left corner, so hover styles and DevTools' node highlight clear. Then the screen is grabbed.

Headed steps, in addition to the ones above:

- `inspect: {selector: …}` (or `text:`) selects the element in DevTools. By default it clicks DevTools' "Select an element" button, checks the button switched on, then clicks the element. `via: menu` right-clicks and chooses Inspect instead, which can't confirm the menu opened. `selects:` is a pattern the selected node must match; one retry is made if it doesn't.
- `tree: {keys: [Left], until: '^<center', max: 24}` clicks the empty right-hand end of the selected row, so the Elements tree has keyboard focus, and checks that it does. Clicking the node's own text could start editing its tag, which would swallow the keys. Then it presses keys until the selected node matches.
- `devtools_click: {text: '^Fetch/XHR$'}` and `devtools_wait: {text: 'quotes\?page=4'}` click or wait for something in DevTools, found by its text (a pattern) or `css:`. DevTools may break a row into pieces ("quotes", ":", a value), so match with `\s*` between them.
- `key: 'ctrl+f'`, `type: 'var data'`, and `pointer: {selector: …}` are real keys, real typing, and the real pointer resting on an element, for tooltips.

Crops for headed figures are in window coordinates:

- `{window: true}`: the whole window;
- `{content: true, height: 760}`: below the browser's own bars;
- `{top: 0, height: 680}`: a band of the window;
- `{between: ['body', 'td.line-number[value="43"]']}`: from the top of one element to the bottom of another, which is how View Source is cut at a line;
- `{selector: …, pad: 8}`: one element.

`devtools: {sidebar: hidden}` shows the Elements tree alone, without the Styles pane.

## Markers

A figure with numbered markers lists them under `annotate:`. Each mark points
`at` something, and the browser measures where that is at the moment of
capture, so a retake moves the markers with the page. Nothing is placed by
typing in pixel positions.

```yaml
annotate:
  width_in: 2.625        # the whole figure's printed width; sets the markers' scale
  size: small            # 11-point markers, or small ones (8.5 points)
  marks:
    - {n: 3, at: {selector: '.field--name-field-award-category-oscars', box: text}}
    - {n: 5, at: {selector: '.field--name-field-honoree-type', box: text}, column: honoree}
    - {n: 4, shape: brace, at: {selector: '.paragraph--type--award-honoree'}, x: 202.5}
    - {n: 1, shape: bracket, at: {selector: '.field--name-field-award-categories'}, x: -1}
    - {n: 2, at: {devtools: {row: 'paragraph--type--award-category'}}, side: left, x: 30, gap: 7}
    - {label: '← you clicked', at: {devtools: {selected: true}}, x: -4}
```

What a mark can point `at`:

- a page element: `selector:` or `text:` (a pattern). `box: element` (the default for a selector) is the element's box; `box: text` (the default for text) is the box of its words, and `box: first-line` of their first line;
- something in DevTools: `devtools: {row: …}` is an Elements-tree row, from its disclosure triangle to the end of its first line; `{selected: true}` is the selected row; `{text: …}` or `{css: …}` is anything else DevTools draws;
- `nth: 2` picks a match (from 0), `nth: [0, 3]` joins a run of matches into one box, and `all: true` joins them all;
- `xy: [x, y]` in image pixels, as a last resort. The tool flags it, because it will not follow the page.

A mark's `shape`:

- `marker` (the default with a number `n`): a numbered circle on the thing's `side` (right, left, above, or below), `gap` CSS pixels away (4 by default). A dotted leader line joins the circle to its thing whenever they end up apart.
- `brace`: a curly brace along the thing's side, spanning it. Its number, or its `label`, sits just past the brace's tip.
- `bracket`: an open bracket. When the thing runs past the picture's edge, the bracket runs past it too and ends in an arrow.
- `box`: a rounded box around the thing, with its number beside it.
- `label` (the default without a number): text beside the thing. With a number as well, the marker follows the text: "4 more honorees ④".

Placement:

- `x` and `y` pin a mark to a place in the crop, in CSS pixels, counted from the right or bottom edge when negative. Pins are for choices about the figure's own empty space, such as a column of markers in DevTools' margin. They are not a way to reach the thing.
- Markers with the same `column` share one line, just past the widest of their things.
- Markers on one line that would overlap spread apart evenly, keep their order, and get leader lines.
- A marker that would touch another mark's brace or bracket moves back toward its own thing.
- A label over the picture gets a white backing.

`capture` draws the markers on every passing take, beside it:
`<UTC time>.annotated.pdf` for slides and handouts (vector), and `.png` for the
book, at one pixel per pixel of the screenshot. `annotate` redraws them from
an existing take after you change the marks, with no new capture; changing
what a mark points at does need a new capture. `promote` draws them once more,
from the recipe as it is then, and copies both files into `images/` as
`<figure>_annotated.png` and `.pdf`. The styles are the course handouts'
(`styles/shotmarkers.sty` copies `handoutmarkers.sty` from the course repo),
so a marker drawn here looks like one in a handout.

## Legibility

Every take records the size of the text inside its crop, counted by
character, from the page and from DevTools. The legibility check works out
how tall that text will be where the figure is shown:

| Target | Recipe | Shown at | Threshold |
|---|---|---|---|
| book | on for every chapter figure; `targets: {book: false}` turns it off | the HTML book's column, 778 pixels in a 1280-pixel-wide window, or the image's own width if narrower | 11 px |
| slides | `targets: {slides: {width: 0.8}}`, the share of a course slide's text width | a slide 1920 pixels wide | 16 px |
| handout | `targets: {handout: {width_in: 5.04}}` | print | 6 pt |

The size judged is the one that four in five characters reach or exceed, so a
footer does not fail a figure but small main text does. `capture` reports it
for every take. `check` fails a promoted image under a threshold, unless its
recipe says why the words don't matter: `legibility: {skip: "the lesson is
the empty page"}`. The thresholds are the plan's starting values; the chapter 5
pilot calibrates them.

Known cases, measured or computed from the images:

- Week 08's `infinite_scroll.png`, dropped because it could not be read on its slide: DevTools text at 11 pixels, in a 555-pixel crop, on 35% of the slide's text width. That is 11.7 pixels on a 1920-pixel slide, under 16. The selftest checks this case.
- Week 08's `xkcd_inspect.png` read well: the same text on half the text width comes to 16.7 pixels.
- The week-06 handout's DevTools figure measures 6.7 points in print. Its card figure measures 5.2 points, which is readable at the edge; at 3 inches wide it would pass.
- Full-window DevTools captures in the book's column (`network-tab-json`, `xkcd-inspect`) come to about 5 pixels. The book's lightbox lets a reader enlarge them. Whether that counts is the pilot's question.

## Composites

`mode: composite` captures each of its `parts` as a figure of its own, then
joins them side by side on white, each labeled below, inside a thin frame:

```yaml
- id: javascript-off-on
  url: https://quotes.toscrape.com/js/
  mode: composite
  window: [900, 695]
  parts:
    - {label: JavaScript off, javascript: false, steps: [{wait: {text: 'Quotes to Scrape'}}]}
    - {label: JavaScript on, steps: [{wait: {text: 'Albert Einstein'}}]}
  layout: {gap: 28, pad: 15, label_px: 28}     # CSS pixels
```

A part can set its own `url`, `steps`, `expect`, `crop`, `javascript`,
`window`, `scale`, `mode` (headless or headed), and `devtools`. Each part is
paced, guarded, and retried like any take, and the joined take lists its parts.

## Contact sheets

`sheet ch-NN` draws each figure's newest take, with its markers if it has
any, at the size each of its targets shows it: the book's column, its share
of a 1920-pixel slide, a handout at 96 pixels per inch. The measured text size
and the verdict are written above each one. Look at the sheet before a pull
request, and attach it to the pull request, so a reviewer sees what readers
will see.

## Course-only figures

`recipes/course.yml` holds figures made for the course repo rather than a
chapter. `capture`, `annotate`, and `sheet` work on them. `promote` refuses
them, because their images live in the course repo (`sync`, in M4, will copy
them there), and `check` only validates their recipes. The two figures there
rebuild the week-06 Oscars handout's annotated screenshots and are the
regression test for markers. Every mark lands within 10 image pixels (5 CSS
pixels) of where it was placed by hand. In the DevTools figure, markers, the
label, and the brace are within 2.5 pixels, and leader lines within 6: the hand
version stopped leaders closer to a triangle than to text. On the 2× card
figure the largest difference, 9.6 pixels, is where the hand version bent its
column of markers.

## Provenance

- **`images/<chapter>/provenance.json`** records, for each image:
  - its kind and source URL;
  - when it was captured, and by whom (the tool, or a hand-run script before it);
  - the browser, User-Agent, window, scale, and crop;
  - a hash of the recipe and of the image;
  - the sizes of its text, which `check` judges;
  - for a composite, its parts;
  - for an image with markers, hashes of the annotated PNG and PDF, the printed width they were drawn for, and a hash of the marks.
- **The recipe's hash** covers what decides the capture. Marks, targets, and legibility settings are left out, so changing them needs no new take.
- **Existing images:** `adopt` records ones made before the toolkit, from their recipe's `legacy:` block.
- **`images/<chapter>/IMAGES.md`** gets a table generated from `provenance.json`, between `<!-- shots:begin -->` and `<!-- shots:end -->`. Everything outside the markers is for people, and the tool never touches it: what a figure shows that is easy to miss, and what a retake needs.

## Checks

`check` reports **errors**, which exit 1:

- a recipe that does not validate;
- an image without provenance;
- an image changed after its provenance was recorded (replaced by hand);
- a kind that disagrees with the recipe;
- an annotated PNG or PDF that is missing, or changed after it was drawn;
- text too small to read at one of the figure's targets (see Legibility);
- a figure block with no `fig-alt`;
- an out-of-date `IMAGES.md` table.

It reports **warnings** for:

- a figure not used in its chapter (a figure may use either `<figure>.png` or `<figure>_annotated.png`);
- short alt text;
- a drifting figure whose caption does not give the capture year;
- marks changed in the recipe since the annotated image was drawn (promote again).

`selftest` runs 46 offline checks against a local web server. It needs the browser but no network. It covers:

- the guards, retries, `promote`, and `check`;
- anchors measured at capture, at scale 1 and 2; markers, braces, brackets, and hand-placed marks drawn to PDF and PNG; `annotate` without a new capture;
- legibility, with week 08's `infinite_scroll.png` as the failing case; a composite; `sheet`;
- headed capture: Inspect through the element picker, the tree walked by keyboard, a request found and clicked in the Network panel, View Source cut at a line, and anchors in DevTools and on the page in one take.

It skips the marker checks if TeX is missing and the headed checks if the virtual display is.

## Files

| Path | What it is |
|---|---|
| `bootstrap.sh`, `requirements.txt`, `run` | setup, pinned packages, and a wrapper that uses the toolkit's own Python |
| `shots.py` | the commands |
| `lib/env.py` | paths, the proxy, and the pinned browser |
| `lib/recipes.py` | loading and validating recipes |
| `lib/browser.py`, `lib/steps.py`, `lib/crop.py` | launching Chrome for Testing, running steps, and cropping |
| `lib/display.py` | the virtual display, real input, and screen grabs |
| `lib/devtools.py` | DevTools settings, and reading the DevTools page to find things on screen |
| `lib/headed.py` | one headed attempt: window, DevTools, headed steps, and the crop |
| `lib/measure.py` | at capture: anchors' boxes and the text's sizes, in the take's pixels |
| `lib/annotate.py`, `styles/shotmarkers.sty` | markers laid out from anchors, drawn with TikZ to PDF and PNG |
| `lib/legibility.py` | text size at each target, against the thresholds |
| `lib/sheet.py` | contact sheets |
| `lib/guards.py` | error and block pages, retries, and policy blocks |
| `lib/capture.py` | one figure, start to finish, composites, and the take log |
| `lib/compare.py` | take against approved image |
| `lib/provenance.py` | `provenance.json` and the `IMAGES.md` table |
| `selftest.py` | the offline test |
| `recipes/` | one YAML file per chapter, and `course.yml` for course-only figures |
| `out/`, `.venv/` | takes, markers, contact sheets, and the virtual environment (git-ignored) |
