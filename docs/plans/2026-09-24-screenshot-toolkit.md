# Plan: a screenshot toolkit for the textbook (`tools/shots/`)

> Moved here on 2026-09-24 from the course repo (`cuinfoscience/INFO4617-Fall2026`, `docs/plans/2026-09-24-screenshot-toolkit.md`), so the toolkit's records sit beside its code. It was written there: "this repo" means the course repo, and paths under `slides/`, `handouts/`, and `syllabus/` are the course repo's.

**Status:** M1–M3 merged (#135–#137). After the chapter 5 pilot, #142 added a read-back of every
DevTools setting, the no-infobar guard, and a `brief:` for every figure, and #144 added the relaxed
1024×768 size limit. M4 (§8) is next. Proposed 2026-09-24. Implements [P0-2] of
[`../aar/2026-09-24-screenshots.md`](../aar/2026-09-24-screenshots.md), and
carries the checks behind [P1-2] and [P1-3]. The back-fill of chapters 1–5 that
uses it is planned separately in
[`2026-09-24-screenshot-backfill-ch01-05.md`](2026-09-24-screenshot-backfill-ch01-05.md).

## 1. What it is
The toolkit is committed code in `cuinfoscience/Web-Data-Science-Book`. It
lets an AI agent in a Claude Code cloud session capture, annotate, check, and
record every screenshot in the book, for any chapter. It then copies each one,
with its notes, into this repo's slides and handouts. Each figure gets a short
recipe, and running a recipe again reproduces the figure, or fails with a
reason.

## 2. Decisions already made
These come from the scoping questions answered on 2026-09-24:

- **Who runs it:** an AI agent in a cloud session. So the toolkit sets itself
  up from a bare container and reports problems in words an agent can act on.
  When the network policy says no, it stops instead of routing around the
  block.
- **Where it lives:** `tools/shots/` in the textbook repo, next to
  `make_notebooks.py` and `trope_lint.py`. The book is the source; slides and
  handouts copy from it.
- **Annotation:** chosen per figure. Each figure is plain, has boxes and
  arrows, or has numbered markers.
- **Slides and handouts:** copies, with notes. Nothing links back to the book's
  image URLs.
- **Staleness:** dated snapshots. Captions say when a figure was captured, and
  nothing re-captures on a schedule.

## 3. Requirements, and the finding each one answers

| # | The toolkit must… | AAR finding |
|---|---|---|
| R1 | set up its own environment in a fresh container, safely re-runnable | §5.1 capture code had no home |
| R2 | say within a minute whether capture works in this session, and why not | §5.8 access changes between sessions |
| R3 | re-capture any figure from a committed recipe with one command | §5.1 |
| R4 | fail loudly on error pages, block pages, and missing elements, and never overwrite an approved image | §5.6 a 502 page overwrote a good capture |
| R5 | drive DevTools the way that worked: real input, the keyboard in the Elements tree, offsets measured before DevTools opens | §5.6 |
| R6 | capture at 2× and crop separately for each target (book, slide, handout) | §5.7 1× in the book, 2× in the handout, by accident |
| R7 | check that text is legible at each target size before anyone reviews the figure | §5.7 one figure dropped, one rebuilt |
| R8 | place markers from element boxes recorded at capture time, not typed coordinates | §5.7 |
| R9 | record each image's kind, source, date, browser, User-Agent, and recipe | §5.3 no line between capture, render, and look-alike; §5.5 no book provenance |
| R10 | refuse to print a number from a query that hit its limit | §5.4 the 25-row CDX query |
| R11 | check that every figure has alt text, and a date in its caption when it drifts | P1-3 |
| R12 | copy figures into slides and handouts, with notes, without erasing anything | §5.2 `make` erases notes |
| R13 | give hand captures of pages behind a login the same record | §5.8 |

## 4. Layout

```
tools/shots/
  README.md            add a figure, capture, review, promote, sync
  bootstrap.sh         install and configure the capture environment (safe to re-run)
  shots.py             the command line (section 6)
  lib/
    env.py             virtual display, proxy, certificate trust, browser discovery
    browser.py         launch Chrome for Testing: headless or headed; window, scale, UA
    devtools.py        open, dock, zoom; Inspect by right-click; tree by keyboard; Network
    steps.py           wait, click, hover, scroll, type, key, reload, JavaScript off
    guards.py          status codes, block and error pages, expected text, blank images
    crop.py            element boxes, padding, per-target crops
    annotate.py        TikZ overlay from recorded anchors, built to PDF and PNG
    legibility.py      smallest text in the crop, at each target size
    evidence.py        recorded queries with limits and paging
    provenance.py      provenance.json and the generated part of IMAGES.md
    sync.py            copy into the course repo, with notes
  styles/
    shotmarkers.sty    marker styles, copied from handouts/common/handoutmarkers.sty
  recipes/
    ch-07.yml ch-08.yml        the 11 existing figures (the regression suite)
    ch-01.yml … ch-05.yml      the back-fill
    course.yml                 course-only figures, such as a PR's "Files changed" view
  out/                 git-ignored: raw takes, logs, contact sheets
images/ch-NN/
  <figure>.png                 approved images, named as today
  <figure>_annotated.png       when a figure has markers
  provenance.json              written by the tool
  IMAGES.md                    a generated table plus notes the tool never touches
```

## 5. A recipe
One YAML file per chapter. This is how ch-05's Network-tab figure would look:

```yaml
chapter: ch-05
defaults:
  user_agent: "Web Data Science/v1 brian.keegan@colorado.edu"   # the one the handouts teach
  window: [800, 600]       # CSS pixels: at most what a figure shows (P1-5, a soft limit)
  scale: 2                 # device pixels per CSS pixel
  pause: [8, 30]           # seconds between page loads on one host

figures:
  - id: network-tab-wikipedia
    kind: capture                       # capture | render | diagram | illustration
    section: "The Network Tab"
    url: https://en.wikipedia.org/wiki/University_of_Colorado_Boulder
    mode: headed                        # DevTools needs a real window
    devtools: {panel: network, dock: bottom, zoom: 1.25, size: 340}   # zoom, not a wider window
    steps:
      - reload: {}                      # the panel records only while it is open
      - wait: {network_idle: true}
      - select_request: {name: University_of_Colorado_Boulder}
      - devtools_tab: headers
    expect:
      status: 200
      text: ["University of Colorado Boulder"]
    crop: {region: window}
    annotate:
      style: markers                    # none | boxes | markers
      marks:
        - {n: 1, at: {devtools: filter-bar}}
        - {n: 2, at: {devtools: request-row, name: University_of_Colorado_Boulder}}
        - {n: 3, at: {devtools: header, name: user-agent}}
    targets:
      book:   {width_px: 760}
      slides: {week: "05", width_in: 3.9}
    drifts: true                        # counts and sizes change; caption needs a date
    caption: >-
      Chrome's Network tab after reloading the University of Colorado Boulder
      article, September 2026.
    alt: >-
      Screenshot of Chrome with the Wikipedia article above and DevTools below. …
```

This sketch predates the toolkit, and the built syntax differs in places;
the textbook's `tools/shots/README.md` is the reference.

A page-only figure is shorter. It needs no `mode`, `devtools`, or `steps`
beyond a `wait`, and its markers anchor to CSS selectors, for example
`at: {selector: "#firstHeading"}`.

## 6. Commands

| Command | What it does |
|---|---|
| `shots doctor [ch-NN]` | Checks the session; see §7.2. With a chapter, also makes one polite request to each host its recipes use. |
| `shots capture ch-NN [--only id]` | Runs recipes. Each take goes to `out/ch-NN/<id>/<UTC time>.png` with a log. Never writes to `images/`. |
| `shots check ch-NN [--sheet]` | Checks guards, legibility, alt text, caption dates, and that every figure is referenced in the `.qmd`. `--sheet` renders each take at its target sizes on one page, for the agent's own review before the PR. |
| `shots promote ch-NN id [--take T]` | Copies a reviewed take into `images/ch-NN/`, builds its annotated version, and writes provenance. The only command that writes there. |
| `shots sync ch-NN id --course PATH --to slides/week-NN/img [--as name.png]` | Copies into the course repo, with notes; see §7.9. |
| `shots import ch-NN id --file raw.png --by NAME --url URL --date D` | Registers a hand capture of a page behind a login, then crops, redacts, annotates, and records it like any other figure. |
| `shots status` | Every figure's age, kind, and whether its recipe changed since its last take. Reports; never re-captures on its own. |
| `shots clean [ch-NN]` | Deletes old takes in `out/`, keeping the newest take of each figure. |

## 7. How each part works

### 7.1 Environment (`bootstrap.sh`, `lib/env.py`)
The bootstrap installs only what is missing, and says what it installed:

- **Packages:** `xvfb`, `xdotool`, `imagemagick`, `libnss3-tools`, and Noto fonts, so non-Latin pages render as text rather than empty boxes. It adds `texlive-pictures`, `latexmk`, and `poppler-utils` only when a recipe asks for markers.
- **Python:** a virtual environment with pinned `playwright`, `selenium` (used only for Selenium Manager's browser download), `pyyaml`, `pillow`, and `websockets`.
- **The browser:** Chrome for Testing at a pinned major version, downloaded by Selenium Manager (`selenium-manager --browser chrome --browser-version N --output json`) and launched by Playwright with `executable_path`. The bootstrap never runs `playwright install`, which this environment forbids.
- **Stray drivers:** it sets `SE_SKIP_DRIVER_IN_PATH=true`, so a stray chromedriver on `PATH` cannot break a session again.
- **The proxy:** Chrome gets `--proxy-server` from `HTTPS_PROXY`. The bootstrap checks that Chrome's certificate store trusts the proxy's certificate authority, and adds it with `certutil` only if it is missing.
- **TLS:** it never disables certificate checks, and never unsets the proxy.

It runs on demand, because `shots doctor` says when it is needed. The
alternative is to put it in the cloud environment's setup script (environment
menu → Edit → Setup script), so every session starts ready. That costs a few
minutes in sessions that take no screenshots, so it is your call.

### 7.2 Preflight (`shots doctor`)
Each check prints PASS or FAIL and, on failure, the next step:

1. Is the proxy set, and does its status endpoint answer?
2. Is the pinned browser present, and at what version?
3. Does a headless capture of `https://example.com/` return 200 with "Example Domain"? A certificate error here means trust is not set up.
4. Do the virtual display, `xdotool`, and `import` work? A headed capture of the same page must not come back blank.
5. With a chapter: one request, with the User-Agent, to each host in its recipes. A 403 or 407 from the proxy is reported as a policy block, with no retry. An answer from the site itself is reported as the site's.
6. Is TeX available, if any recipe needs markers?

This is the check that was missing on 2026-09-09. Run it at the start of
every capture task, and do not reuse an earlier session's answer.

### 7.3 Capture (`lib/browser.py`, `lib/steps.py`)
- **One engine.** Playwright drives Chrome for Testing: headless for page-only figures, headed on the virtual display for anything that shows browser UI. That covers DevTools, View Source, and menus. Headed screenshots are grabbed with ImageMagick `import`. Selenium drives only the figures whose subject is Selenium (ch-08).
- **Scale.** Every capture is at scale 2, and the virtual screen is sized from the window and scale plus a margin. Book, slide, and handout crops come from the same take.
- **Size.** A figure shows at most 800×600 CSS pixels of the screen (P1-5, added 2026-09-24 after the instructor found text too small). That is a small window, or a crop to what the text discusses; DevTools is zoomed, not given a wider window. It is a soft limit: going over is a warning, and the recipe says why. (Relaxed 2026-09-24: up to 1024×768 when the extra room removes clutter and the text still passes; see `docs/decisions.md`.)
- **Politeness.** Each request uses one User-Agent: the one the handouts teach, set once in the recipe defaults. Page loads on one host are 8–30 seconds apart. A 5xx or dropped connection is retried three times, backing off 30, 60, then 120 seconds. Cookie banners get "necessary only." The toolkit never logs in or types credentials.
- **Steps.** Each step waits for its condition; none sleeps a fixed time. A step that reveals content on hover waits for that content to appear. On 2026-09-22 the Wayback toolbar's **Collected by** section was missed this way.

### 7.4 DevTools (`lib/devtools.py`)
This module turns what the handout and ch-07 and ch-08 captures learned into
code.

- **Settings.** The dock position, panel split, and zoom go into the profile's `Preferences` before launch. The keys are `currentDockState`, `inspector-view.split-view-state`, and the per-host zoom level for `devtools`.
- **The browser's toolbar height** is measured before DevTools opens, as outer minus inner window height. Screen positions of page elements come from that measurement. The fixed 144-pixel constant goes away.
- **Inspect.** It opens by a real right-click on the element's center, then the menu entry. Within the Elements tree, the tool moves by keyboard: Right expands, Left collapses, Up and Down move. It does not click disclosure triangles.
- **Locating DevTools controls,** such as a request row or a header name. Milestone 2 chooses between two ways, and keeps whichever proves reliable:
  - read the DevTools front end's own page over the browser's debugging port, which gives exact boxes;
  - use fixed positions measured once for each pinned Chrome version.

  Input always stays real (`xdotool`).

### 7.5 Guards (`lib/guards.py`)
A take fails, and nothing is promoted, when:

- the main document's status is not the one the recipe expects;
- the page title or text matches a block or error pattern, such as "Just a moment," "Access denied," "You've been blocked," "Too Many Requests," "Bad Gateway," or "upstream request failed";
- an expected text or element is missing;
- the image is nearly blank.

A figure whose subject is a refusal says so in its recipe (`expect: {block: true}`, or `expect: {error: ERR_NAME_NOT_RESOLVED}`), and then the guard requires the refusal. Failed takes stay in `out/` with their logs.

### 7.6 Annotation (`lib/annotate.py`)
- **Anchors.** At capture time, each marker's anchor is recorded as a box in image pixels, from a CSS selector for page elements or a DevTools locator (§7.4). A plain `{xy: [x, y]}` is allowed as a fallback, and gets flagged for review.
- **Output.** The tool writes a TikZ overlay like the handout's `*_annotated.tex`, with styles copied from `handoutmarkers.sty`. It builds a vector PDF (for slides and handouts) and a 2× PNG (for the book).
- **Styles.**
  - `markers`: numbered circles with leader lines.
  - `boxes`: rounded rectangles and arrows.
  - `none`.
- **Fit.** Markers that would cover text move outward along their leader. A label that would overflow is anchored to its side.
- **Retakes.** Anchors come from the new take, so markers follow the page.

### 7.7 Legibility (`lib/legibility.py`)
The first check is a soft limit on size (P1-5): a figure that shows more than 800×600 CSS pixels gets a warning saying how small the book's column will make its text, unless its recipe says why it needs more.

At capture time the tool records the computed font size of the visible text inside the crop. For DevTools, the size follows from the DevTools zoom. It then works out how tall that text will be at each target size:

- the book's column;
- the slide column the figure will fill;
- the handout column.

A figure under the threshold fails `check`, before anyone reviews it. Starting thresholds are 11 px in the book and 16 px on a 1920-pixel-wide slide. The pilot calibrates them against known cases: the week-07 and week-08 figures that read well, and the `infinite_scroll.png` that did not.

### 7.8 Provenance (`lib/provenance.py`)
`images/ch-NN/provenance.json` records the following for each image:

- `kind`: `capture`, `render`, `diagram`, or `illustration`, as P0-3 settles;
- the recipe id, and a hash of the recipe;
- the URL requested, and the final URL;
- the status code;
- the capture time in UTC;
- the browser and version;
- the User-Agent, window, and scale;
- the crop;
- who captured it: the tool, or a named person for imports;
- the evidence queries behind any number in its caption;
- the image's SHA-256.

`IMAGES.md` is generated from that record between `<!-- shots:begin -->` and
`<!-- shots:end -->`. Everything outside the markers belongs to people, and
the tool never touches it.

### 7.9 Evidence (`lib/evidence.py`)
A recipe that prints a number lists the queries behind it. For example:

```yaml
evidence:
  - id: xcom-image-captures
    url: https://web.archive.org/cdx/search/cdx
    params: {url: "x.com/images/*", output: json, limit: 1000, showResumeKey: "true"}
    page: resume_key          # follow resumeKey until the API stops returning one
    claim: "six of the seven images were only ever captured as 404s"
```

The tool pages until the query is exhausted, then records each request, the
row counts, the total, and the date. It saves the responses in `out/` and a
summary in `provenance.json`. A page that returns exactly its limit, with no
paging configured, fails. That is the check that would have caught week-07's
first account of the broken x.com images.

### 7.10 Alt text and captions
`check` requires the following for each figure:

- a `fig-alt` that transcribes the text and numbers a reader needs;
- a date in the caption when the recipe says `drifts: true`;
- a figure block in the chapter's `.qmd`, `![…](images/ch-NN/<id>.png){#fig-<id> .lightbox fig-alt="…"}`, matching the recipe.

The ch-07 and ch-08 figures, at 280–440 characters of alt text, set the bar.

### 7.11 Sync to the course repo (`lib/sync.py`)
- **What it copies:** the PNG, and the vector PDF when there are markers, into a week's `img/` folder.
- **Notes:** it writes the figure's notes into that folder's `IMAGES.md`, between `<!-- shots:begin -->` and `<!-- shots:end -->`: kind, source file and textbook commit, URL, capture date, browser, and User-Agent.
- **Placeholders:** when `--as` names a placeholder listed in `stubs.tsv`, the file replaces the placeholder under the same name, and the row is removed.
- **Prerequisite:** P0-1 (`make_stubs.py` keeps notes) must land first, or the next `make` erases what sync wrote.
- **Handouts:** the same command, with `--to handouts/week-NN/img`.

### 7.12 Rules the toolkit enforces or reminds
- Identify yourself, and pace requests (§7.3). `doctor` warns when a recipe URL is disallowed by the site's `robots.txt`.
- No logins, no credentials, and no cookies beyond "necessary only."
- No student names, avatars, or work without consent. A pull-request screenshot uses a PR by the instructor or a TA, or crops those details out.
- `redact:` boxes (by selector, or by rectangle for imports) are blacked out before an image is written anywhere in the repo. A scan flags email addresses in the crop; the course User-Agent's contact address is allowed.
- No look-alikes of real sites (pending P0-3).
- Crop to what the text discusses. No bulk captures of third-party pages.

## 8. Milestones
Each milestone is one PR in the textbook repo, except M0. Each is tested
against figures that already exist, so "working" means reproducing what was
done by hand.

| | Scope | Test |
|---|---|---|
| **M0** | P0-1 in this repo: `make_stubs.py` keeps notes | `make week-07` leaves week-07's 100-line `IMAGES.md` intact, and still updates its placeholder table |
| **M1** | bootstrap, doctor, headless capture, guards, `out/` and promote, provenance, generated `IMAGES.md`; recipes for all 11 ch-07 and ch-08 figures (closes P1-1) | Re-capture `wayback-calendar`, `facebook-2004`, and `x-com-1999`; takes match the committed crops, allowing for drift; a forced 502 fails the guard and leaves the approved image untouched |
| **M2** | headed mode, virtual-display sizing, DevTools (Elements by right-click and keyboard, Network panel), View Source | Re-capture `xkcd-inspect`, `network-tab-json`, `devtools-archived-page`, and the Oscars DevTools shot |
| **M3** | annotation from anchors, legibility, contact sheet | Rebuild both Oscars annotated figures from recipes, with markers within a few pixels of the hand-placed ones; `infinite_scroll`-style text fails legibility |
| **M4** | evidence queries, alt-text and caption checks, sync, import, and an offline CI job (`shots check --offline` on PRs touching `images/**` or `tools/shots/**`) | Re-run the x.com CDX evidence and get "complete"; syncing ch-08 into week-08 reproduces its files and notes |

The chapter-5 pilot needs M1–M3. M4 can land alongside it.

## 9. Risks
- **DevTools changes between Chrome versions.** The major version is pinned, DevTools locators live in one table, and M2's tests catch breakage when the pin moves.
- **Access differs by session.** `doctor` reports it, and a proxy 403 or 407 stops the run without a retry.
- **Sites change or block cloud addresses.** Guards fail the take, and the author picks another page or marks the figure as a refusal on purpose.
- **Disk.** The session's disk allowance is fixed. Chrome for Testing, and TeX when markers are needed, take several hundred megabytes. `shots clean` prunes old takes in `out/`.
- **Scope creep.** The toolkit makes screenshots, not diagrams. Diagrams stay with Graphviz and the existing `generate_images.py` scripts, recorded with `kind: diagram`.
