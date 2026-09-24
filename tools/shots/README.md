# tools/shots

Capture, check, and record the book's screenshots, so that every figure can
be made again the same way and says where it came from. The plan and the
after-action report behind it are in the course repo:
`docs/plans/2026-09-24-screenshot-toolkit.md` and
`docs/aar/2026-09-24-screenshots.md`.

Done so far:

- **M1:** headless captures, guards, retries, provenance, and `check`.
- **M2:** headed captures of browser UI (DevTools, View Source), with real input on a virtual display.

Still to come:

- **M3:** annotation, legibility checks, and composites.
- **M4:** evidence queries, copying figures into the course repo, CI, and the two ch-08 figures whose subject is a tool itself (the window Selenium opens, Playwright's recorder).

## Quick start

```bash
bash tools/shots/bootstrap.sh --headed            # once per container; safe to re-run
tools/shots/run doctor ch-07                      # every time, first: can this session capture?
tools/shots/run capture ch-07                     # takes go to tools/shots/out/ch-07/<figure>/
tools/shots/run compare ch-07 wayback-calendar    # same picture as the approved image?
tools/shots/run promote ch-07 wayback-calendar    # copy the take into images/ch-07/, record it
tools/shots/run check                             # before a PR
```

- **`bootstrap.sh`** does five things:
  - installs what is missing;
  - creates `tools/shots/.venv` with the pinned packages in `requirements.txt`;
  - fetches Chrome for Testing at a pinned major version (154) through Selenium Manager;
  - makes sure Chrome trusts the session proxy's certificate;
  - with `--headed`, adds the virtual display (Xvfb), real input (xdotool), and screen grabs (ImageMagick) that headed figures need.

  It never runs `playwright install` and never turns off certificate checks.
- **`doctor`** answers whether capture works in this session. Do not reuse an earlier session's answer:
  - it checks the proxy, the browser, a real headless capture of example.com, and a real headed one with DevTools open;
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
- **Steps:** `wait` (for `text`, `selector`, or `network_idle`), `hover`, `click` (by `selector`, `text`, or, as a last resort, `position`), `scroll`, `press`, and `settle` (seconds, for animation with no end signal).
- **Other modes:** `mode: headed` is below. `mode: composite` (M3) and an `engine:` other than Playwright (M4) mark figures that `capture` skips with a note.
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
- `tree: {keys: [Left], until: '^<center', max: 24}` clicks the selected row, so the Elements tree has keyboard focus, then presses keys until the selected node matches.
- `devtools_click: {text: '^Fetch/XHR$'}` and `devtools_wait: {text: 'quotes\?page=4'}` click or wait for something in DevTools, found by its text (a pattern) or `css:`. DevTools may break a row into pieces ("quotes", ":", a value), so match with `\s*` between them.
- `key: 'ctrl+f'`, `type: 'var data'`, and `pointer: {selector: …}` are real keys, real typing, and the real pointer resting on an element, for tooltips.

Crops for headed figures are in window coordinates:

- `{window: true}`: the whole window;
- `{content: true, height: 760}`: below the browser's own bars;
- `{top: 0, height: 680}`: a band of the window;
- `{between: ['body', 'td.line-number[value="43"]']}`: from the top of one element to the bottom of another, which is how View Source is cut at a line;
- `{selector: …, pad: 8}`: one element.

## Provenance

- **`images/<chapter>/provenance.json`** records, for each image:
  - its kind and source URL;
  - when it was captured, and by whom (the tool, or a hand-run script before it);
  - the browser, User-Agent, window, scale, and crop;
  - a hash of the recipe and of the image.
- **Existing images:** `adopt` records ones made before the toolkit, from their recipe's `legacy:` block.
- **`images/<chapter>/IMAGES.md`** gets a table generated from `provenance.json`, between `<!-- shots:begin -->` and `<!-- shots:end -->`. Everything outside the markers is for people, and the tool never touches it: what a figure shows that is easy to miss, and what a retake needs.

## Checks

`check` reports **errors**, which exit 1:

- a recipe that does not validate;
- an image without provenance;
- an image changed after its provenance was recorded (replaced by hand);
- a kind that disagrees with the recipe;
- a figure block with no `fig-alt`;
- an out-of-date `IMAGES.md` table.

It reports **warnings** for:

- a figure not used in its chapter;
- short alt text;
- a drifting figure whose caption does not give the capture year.

`selftest` runs 24 offline checks against a local web server. It needs the browser but no network. It covers:

- the guards, retries, `promote`, and `check`;
- headed capture: Inspect through the element picker, the tree walked by keyboard, a request found and clicked in the Network panel, and View Source cut at a line.

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
| `lib/guards.py` | error and block pages, retries, and policy blocks |
| `lib/capture.py` | one figure, start to finish, and the take log |
| `lib/compare.py` | take against approved image |
| `lib/provenance.py` | `provenance.json` and the `IMAGES.md` table |
| `selftest.py` | the offline test |
| `recipes/` | one YAML file per chapter |
| `out/`, `.venv/` | takes and the virtual environment (git-ignored) |
