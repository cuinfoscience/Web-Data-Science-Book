# Plan: back-fill screenshots for chapters 1–5

> Moved here on 2026-09-24 from the course repo (`cuinfoscience/INFO4617-Fall2026`, `docs/plans/2026-09-24-screenshot-backfill-ch01-05.md`), so the toolkit's records sit beside its code. It was written there: "this repo" means the course repo, and paths under `slides/`, `handouts/`, and `syllabus/` are the course repo's.

**Status:** In progress. The plan was proposed on 2026-09-24. The chapter 5 pilot
is done (textbook #138, course #51), and its gate closed the same day. The gate
note is in §9 of the screenshot AAR and in `tools/shots/README.md` ("What the
chapter 5 pilot settled"). Chapter 4 is done. Chapters 1 and 2 are done, except figures 1-4 and
2-2 (§4). Chapter 3 is done, except 3-2 and 3-3, which wait for web.archive.org (§4). Implements [P1-4] of
[`../aar/2026-09-24-screenshots.md`](../aar/2026-09-24-screenshots.md). Depends
on P0-1 (`make_stubs.py` keeps notes), on P0-3 (what counts as a screenshot),
and on toolkit milestones M1–M3 in
[`2026-09-24-screenshot-toolkit.md`](2026-09-24-screenshot-toolkit.md). M4 can
land with the pilot.

## 1. Ground rules
These come from the scoping questions answered on 2026-09-24:

- **Scope:**
  - textbook ch-01 to ch-05;
  - slides weeks 01–05;
  - the handouts those weeks use: `week-01/setup.md`, `week-04/rss-feeds.md`, and `common/pull-request-walkthrough.md`.
- **Hands off ch-06 and week-06 this week.** Students are working in them. Nothing in this plan touches `ch-06-static-pages.qmd`, `slides/week-06/`, or `handouts/week-06/`.
- **Pilot first:** one chapter goes end to end, and its review shapes the other four.
- **Fewer than 10 figures per chapter.** Add a figure only where the prose asks the reader to find something on screen. The candidates below run 4–8 per chapter.
- **No approved shot list in advance.** The candidates are a starting point. The PR is where each figure is accepted, cut, or swapped.
- **Real captures only** (pending P0-3). Pages behind a login go to the instructor with a capture checklist. Hand captures arrive as files on a branch, because pasted images reach the session as pictures it can see but not crop or redact.
- **At most 800×600 of the screen** (P1-5, added 2026-09-24): each capture shows at most 800×600 CSS pixels, at 2×, so its text reads at book and slide size. That means a small window, a crop to what the text discusses, and DevTools zoomed rather than widened. A figure that needs more says why in its recipe. (Relaxed 2026-09-24: up to 1024×768 when the extra room removes clutter and the text still passes at every target; see `docs/decisions.md`.) The same rule sizes the slide copies: an 800-pixel capture takes at least `0.48\textwidth`.
- **Slides and handouts get copies, with notes.** A figure replaces a placeholder under the same file name, or fills a frame that has no image and describes exactly what the figure shows. Otherwise it goes into `img/` with notes, for the instructor to place. Memes stay: "never ship a diagram where a meme lands better" (`AUTHORING.md`).

## 2. Where things stand (audit, 2026-09-24)
**The book:** ch-01 to ch-05 (and ch-06) contain no figures at all.

**Slides:**

| Week | On the slides now | Placeholders not on any slide | Other notes |
|---|---|---|---|
| 01 | `book_website.png` and `github_repo.png` (rendered from a local mirror, 2026-08-21); `issue_form.png` and `pr_review.png` (look-alikes); `book_pipeline.png` (diagram); `teambuilding.png` | none | `IMAGES.md` still calls all eight images placeholders; `anaconda_jupyter.png` (a real Jupyter capture) is used by the setup handout, not the deck |
| 02 | `robots_txt_browser.png` and `user_agent_devtools.png` (renders from live text); photos and memes | `github_issue`, `pr_review`, `legal_timeline`, `ethics_framework` | the frame `github_issue` was drawn for is commented out |
| 03 | photos, memes, news clippings | `ad_observatory`, `api_timeline`, `link_rot`, `three_pressures`, `pr_review` | three of the five are diagrams, outside the toolkit's job |
| 04 | `weather_forecast_plot.png` (live chart); memes | none | `handout_*.png`, the instructor's four captures, serve the pull-request handout |
| 05 | **`pr_review.png` is a gray placeholder on "A revision menu for Chapter 5"**; `network-requests-inspector.png` (the instructor's capture); generated diagrams | `dev_tools_network` | "Inspecting a page: the Inspector tab" has no image |

## 3. Pilot: chapter 5 and week 05

**Why ch-05:**

- **The most prose with no picture.** "Browser Developer Tools" spends about 1,100 words on things only a picture shows: "the small arrow-and-box icon," "the Waterfall column," "Copy as cURL." There is not one figure.
- **The hardest parts of the toolkit.** The pilot needs headed DevTools and markers on DevTools rows. If it passes, chapters 1–4 are mostly plain page captures.
- **The week's own gaps.** The week-05 deck has the only placeholder still on a slide, plus a text-only Inspector frame.
- **No disruption.** Chapter 5 has already been taught, so changes help re-readers and the next offering without disturbing this week's lab.

**Candidates.** The running example throughout is the chapter's own page, `en.wikipedia.org/wiki/University_of_Colorado_Boulder`.

| # | Section | What it shows | Annotation |
|---|---|---|---|
| 5-1 | The Inspector Tab | Elements panel after right-click → Inspect on the article title: the selected `h1#firstHeading`, its `id` and `class`, the page highlight | markers |
| 5-2 | The Inspector Tab | The element picker hovering the infobox: the highlight box and its size tooltip | box on the picker icon |
| 5-3 | The Inspector Tab | A node's context menu open at Copy → Copy selector / Copy XPath | none |
| 5-4 | The Network Tab | The request list after a reload: filter bar, Status, Type, Size, Time, Waterfall | markers |
| 5-5 | The Network Tab | The Headers pane for the article's own request: request `User-Agent`; response `content-type`, `server`, caching | markers |
| 5-6 | The Network Tab | Right-click a request → Copy → Copy as cURL | none |
| 5-7 | Diagnosing HTTP Errors | A 404 on Wikipedia with the Network tab showing its status (optional) | box |
| 5-8 | User-Agent Spoofing | `httpbin.org/headers` in the browser: what a real browser sends, beside the chapter's `requests` output (optional) | box |

**Week 05:**

- **`pr_review.png`:** replace it with a real capture: the signed-out "Files changed" view of a public textbook PR that revises chapter 5 and has an inline review comment. Use a PR by the instructor or a TA, or crop out names and avatars; GitHub hides large diffs from signed-out viewers, so pick a small one. If no suitable PR exists, capture one after a Friday review produces a real comment, rather than posting a comment to make the picture.
- **The Inspector frame:** 5-1 fills "Inspecting a page: the Inspector tab," which has no image and describes exactly what 5-1 shows.
- **The rest:** copies of 5-2 to 5-8 go into `img/` with notes. The Network frame keeps the instructor's own capture.
- **The unused placeholder:** `dev_tools_network.png` gets deleted, since 5-4 covers its description. It is the instructor's call.

**Pilot gate.** Once the pilot PRs are reviewed, record what review changed as a dated resolution note in the AAR and in the toolkit README:

- figures cut or swapped;
- legibility thresholds;
- the marker style;
- caption conventions.

Only then start chapter 4.

## 4. Chapters 1–4, after the pilot
Order: **ch-04, ch-01, ch-02, ch-03.**

- **ch-04** first: its figures are plain browser views of XML and JSON, the lowest risk, and they share work with the RSS handout.
- **ch-01** next: it needs one new piece, a real Jupyter server in the container.
- **ch-02** then: its figures are primary-source pages, each to be checked for loading signed out.
- **ch-03** last: its best figures show refusals and retired services. They need `expect: block`-style recipes and the most judgment about what to show.

### Chapter 4 — Data Formats

| # | Section | What it shows | Annotation |
|---|---|---|---|
| 4-1 | Working with Real XML | `clerk.house.gov/xml/lists/MemberData.xml` in Chrome's XML tree view: `<MemberData publish-date>` → `<members>` → `<member>` → `<member-info>` | markers |
| 4-2 | Handling Deeply Nested JSON | The chapter's Open-Meteo request in Chrome's JSON view, pretty-printed: `daily` → `time`, `temperature_2m_max` | markers |
| 4-3 | Recommended Exercises | One starter feed from `rss-feeds.md` in the browser: `<rss>` → `<channel>` → `<item>` | markers |
| 4-4 | Recommended Exercises | View Source searched for `application/rss+xml`, with the `<link rel="alternate">` that names a site's feed | box |

- **Slides:** copies of 4-1 and 4-2 go to week-04 for "XML → DataFrame: the real House roster" and "JSON: peel the onion on a live API," for the instructor to place.
- **Handout:** 4-3 and 4-4 go into `handouts/week-04/img/` for `rss-feeds.md`. The step "View the page source … search for `type="application/rss+xml"`" gets 4-4.
- **Done 2026-09-24:** 4-1, 4-3, and 4-4, with the course copies. 4-3 shows BBC News's science and environment feed: Chrome draws a feed as a tree only when it is served as `text/xml` or `application/xml`, and the Guardian's robots.txt disallows Claude's agents. 4-4 marks the feed's address with a numbered marker, because a box around line 33 covered its line number. **4-2 followed the same day,** once the maintainer decided that a figure of an API's response, the request a chapter's own code makes, is captured as an API client, although api.open-meteo.com's robots.txt disallows every path (`docs/decisions.md`). It is `forecast-json`: the chapter's request in Chrome's JSON view with Pretty-print ticked, marking `daily_units`, `daily`, `time`, and `temperature_2m_max`. `images/ch-04/IMAGES.md` has the details.

### Chapter 1 — Introduction

| # | Section | What it shows | Annotation |
|---|---|---|---|
| 1-1 | Jupyter Notebooks | Jupyter in the browser with the `webdata` kernel named at the top right, one code cell run, its output below | markers |
| 1-2 | Common Issues to Debug | The kernel picker listing `webdata` beside the base kernel: where a notebook's environment is chosen. The `ModuleNotFoundError` fix here and in `setup.md`'s Troubleshooting depends on it | box |
| 1-3 | Your First Request | The University of Colorado Boulder article beside View Source of the same page: what you see, and what `requests` gets | labels |
| 1-4 | Calling Your First API | The chapter's pageviews API URL in Chrome's JSON view: `items` → `timestamp`, `views` | markers |
| 1-5 | Calling Your First API | The same article and month in the Wikimedia Pageviews tool, the same numbers for people (optional) | none |

- **Jupyter:** 1-1 and 1-2 are captures of a real Jupyter server run in the container on `localhost`, with a kernel named `webdata`.
- **Handout:** 1-1 is offered to `setup.md` in place of `anaconda_jupyter.png`, because it shows the kernel name the Troubleshooting section depends on.
- **Slides, after P0-3:**
  - week-01's `issue_form.png` becomes a real, public, filed issue that follows the template, captured signed out, or the instructor captures the empty form by hand through `shots import`;
  - `pr_review.png` becomes a real public PR's "Files changed" view;
  - `github_repo.png` and `book_website.png` are re-captured live, since the mirror is no longer needed;
  - week-01's `IMAGES.md` is rewritten to match (P2-1).
- **Done 2026-09-24:** three figures, and a prose fix the capture found.
  - **1-1 became two figures** from a real Jupyter Notebook 7.6 server set up with the chapter's own commands: `jupyter-new-menu` (the file list with **New** open) and `jupyter-cells` (the companion notebook's Markdown cell above its first code cell, run, with the kernel's name). Notebook 7's **New** menu lists the kernel, **Python 3 (ipykernel)**, not **Notebook**, so the chapter's instruction changed to match.
  - **1-2 is dropped.** Since #152 the chapter says to start Jupyter from `webdata` and pick the Python 3 kernel; a picker listing `webdata` beside `base` would need an extra package the chapter doesn't install.
  - **1-3 is `article-view-source`**, a labeled composite at 370 pixels a side: the article, and View Source of the same address.
  - **1-4 is left out:** Wikimedia's REST API answered this cloud session's address with 429 twice on 2026-09-24. `images/ch-01/IMAGES.md` keeps a draft recipe, for a capture from another network.
  - **1-5 is skipped** (optional).
  - **Course:** copies of the two Jupyter figures go into `handouts/week-01/img/`, offered to `setup.md`; replacing `anaconda_jupyter.png` is the instructor's call. `book_website.png` and `github_repo.png` stay: in the deck's 0.35-wide column, a live capture's text is legible only when cropped to about 480 CSS pixels, which cuts the page's text short, so the column width is the instructor's call first. `issue_form.png` and `pr_review.png` wait on the maintainer's choice of a public issue and pull request that aren't a student's.

### Chapter 2 — Ethics, Law, and Responsible Data Collection

| # | Section | What it shows | Annotation |
|---|---|---|---|
| 2-1 | Technical Norms: `robots.txt` | `en.wikipedia.org/robots.txt` in the browser: the generic `User-agent: *` block | box |
| 2-2 | Comparing robots.txt Across Platforms | Reddit's whole `robots.txt`, the eight lines the chapter counts, if it loads for a cloud address (optional) | none |
| 2-3 | Responsible Request Headers | Wikimedia's User-Agent policy: the sentence asking clients to identify themselves and give contact information | box |
| 2-4 | Responsible Request Headers | The Network tab's Headers pane for a browser request: the `User-Agent` a real browser sends, for contrast with `requests`' default | marker |
| 2-5 | Terms of Service as Quasi-Law | A platform's terms, the clause on automated collection, only if it loads signed out | box |

- **Slides:** week-02's two renders stay, recorded as `kind: render`. 2-1 is offered as their real-browser counterpart, and the instructor chooses.
- **Placeholders:** the four unused placeholders are the instructor's call to delete or keep.
- **Done 2026-09-24:** two figures.
  - **2-1 is `robots-txt-wikipedia`:** the file in Chrome, from the comment welcoming "friendly, low-speed bots" through the generic block's `Disallow` rules. The toolkit gained `match:` anchors and scrolling for it, because a plain-text file is one text node.
  - **2-3 is `wikimedia-ua-policy`:** the policy's request for a User-Agent with contact information, its example, and its generic format. It moved to foundation.wikimedia.org.
  - **2-2 waits for the Friday review:** students' #50, #63, and #79 revise the paragraphs it would sit beside.
  - **2-4 is dropped:** chapter 5's `network-headers` shows the Headers pane, and captures send the course's User-Agent, not a browser's.
  - **2-5 is skipped** (optional).
  - **Course:** copies of both go to `slides/week-02/img/`, offered beside the deck's two renders.

### Chapter 3 — The Post-API Age

| # | Section | What it shows | Annotation |
|---|---|---|---|
| 3-1 | Dead-Endpoint Forensics | Three failures side by side, as a browser shows them. Pushshift's `{"detail":"Not authenticated"}` (403); Twitter v1.1's error 215, "Bad Authentication data" (400); and the browser's own error page for `api.crowdtangle.com`, which does not answer | labels |
| 3-2 | Enclosure | CrowdTangle's home page in the Wayback Machine before the August 2024 shutdown (ch-07's method, cross-referenced) | none |
| 3-3 | Enclosure | Reddit's 2023 announcement of API pricing, live or from the Wayback Machine if Reddit blocks the capture | box on the price |
| 3-4 | Exemption | Article 40 of the Digital Services Act on EUR-Lex: data access for vetted researchers | box |
| 3-5 | An Access Matrix | OpenAlex's response headers in the Network tab, if it sends the rate-limit headers the exercise prints (optional) | markers |

- **3-1:** a figure about refusals, so its recipe expects the refusals (toolkit §7.5). The chapter's table of status codes stays, and the figure shows what a reader meets.
- **Slides:** week-03's Friday frames ("Step 4 — attach the issue," "Step 5 — review basics") are offered real signed-out captures of a public issue and PR.
- **Placeholders:** the unused `ad_observatory.png` is left to the instructor, whose `meta-research-privacy.png` already covers that case.
- **Done 2026-09-24:** two figures, and a toolkit that can show a host that doesn't answer.
  - **3-1 is `dead-endpoints`** (figure 3.2), the three endpoints stacked: Pushshift's 403 in JSON, Chrome's own error page for CrowdTangle, whose names no longer resolve, and Twitter v1.1's 400 in JSON. Behind the session's proxy, a dead host fails as a refused one does, so the toolkit gained `expect: {error: ...}` with a public-DNS check before a take is kept.
  - **Twitter's part of 3-1 followed the maintainer's API-client decision** (`docs/decisions.md`); api.twitter.com's robots.txt disallows every path. The first version, merged in #158, showed two endpoints.
  - **3-4 is `dsa-article-40`** (figure 3.1): Article 40 from its heading through paragraph 4, boxed, on EUR-Lex, whose robots.txt asks for 10 seconds between requests.
  - **3-2 and 3-3 wait for web.archive.org,** which reset every connection from the session. reddit.com's robots.txt now disallows every path, so 3-3 can only come from the archive; confirm first that Reddit itself stated $0.24 per 1,000 calls. Both draft recipes are in `images/ch-03/IMAGES.md`.
  - **3-5 is skipped:** optional, and the chapter's take-home exercise asks students to find OpenAlex's rate-limit headers themselves.
  - **Course:** copies of both figures go to `slides/week-03/img/` with notes, for the instructor to place. The Friday frames' issue and pull request wait on the maintainer's choice, as week 1's do.

## 5. The pull-request handout
`handouts/common/pull-request-walkthrough.md` shows GitHub's web editor, which
needs write access, so the agent cannot capture it. The instructor's four
captures stay as they are. P2-1 fixes the note that points to a
`handouts/common/img/` folder that does not exist. If GitHub's editor changes
enough to make them wrong, the instructor re-captures them, and `shots import`
records, crops, and redacts them like any other figure.

## 6. How each chapter ships
- **Two linked PRs, opened together:**
  - a **textbook PR** with recipes, images, `provenance.json`, `IMAGES.md`, the figure blocks in the `.qmd`, and regenerated notebooks (`tools/make_notebooks.py`);
  - a **course PR** with the copies and notes in `slides/week-NN/img/` (and `handouts/…/img/`), and deck edits only where §1 allows.
- **The review table.** Each PR description lists every figure: section, what it shows, kind, annotation, alt text, capture date, and the legibility result. This is where figures are accepted or cut.
- **Done means:**
  - every figure has a recipe, a provenance entry with its kind, alt text, and a caption that dates anything that drifts;
  - legibility passes at book width, and at slide width for copies;
  - `quarto render` succeeds, the notebooks are regenerated, and `tools/trope_lint.py` passes on changed prose;
  - there are no student names or work, no logins, no look-alikes, and no personal data;
  - in the course PR, replaced placeholders keep their file names, their `stubs.tsv` rows are removed, `IMAGES.md` notes are updated, and the slide build passes;
  - ch-06 and week-06 are untouched.

## 7. Sequence
1. P0-1 in this repo; your decision on P0-3.
2. Toolkit M1–M3 in the textbook repo.
3. Pilot: ch-05 and week-05 (M4 alongside). Review. Resolution note.
4. ch-04, ch-01, ch-02, ch-03: one pair of PRs each, in that order.
