# After-Action Report: screenshots for chapters 7–8, weeks 07–08, and the week-06 handout (2026-08-21 → 2026-09-24)

> Moved here on 2026-09-24 from the course repo (`cuinfoscience/INFO4617-Fall2026`, `docs/aar/2026-09-24-screenshots.md`), so the toolkit's records sit beside its code. It was written there: "this repo" means the course repo, and paths under `slides/`, `handouts/`, and `syllabus/` are the course repo's.

## 1. Summary
Between 2026-09-22 and 2026-09-24, one Claude Code cloud session made 37 real screenshots: 5 for textbook ch-07, 6 for ch-08, 15 for the week-07 deck, 9 for week-08, and 2 for the week-06 Oscars handout. They shipped in seven PRs (textbook #128 and #129; this repo #43, #44, #45, #46, #47). Before 2026-09-22 the project could not capture a real page from a cloud session. Week-01's images (2026-08-21) were rendered from a local mirror or rebuilt as look-alikes. Week-02's were drawn from live text. The first attempt at the week-04 pull-request handout (2026-09-09) was blocked, and the instructor captured those four images by hand.

The images themselves are sound. Every capture identified itself with a named User-Agent and paused between requests. DevTools was operated with real clicks. Captions were checked against a second source, notes carry dates, and every book figure has long, specific alt text. What the work left behind is weak, and three findings matter most:

1. **None of the capture code was kept.** The 37 capture and query scripts and 205 intermediate images sit in a scratchpad that disappears with the container. So do the steps that made capture possible at all: six packages installed by hand, a stray chromedriver on `PATH`, the DevTools preference keys, and a measured 144-pixel offset. They survive only in the session transcript and, as prose, in three `IMAGES.md` files. The next chapter would start from nothing. Root cause: **missing** (§5.1) → [P0-2], the toolkit plan.
2. **Building a deck erases its image notes.** `slides/Makefile` runs `make_stubs.py` before every build, and `make_stubs.py` rewrites `img/IMAGES.md` from `stubs.tsv` every time. On copies of the four weeks that have hand-written notes, one run cut week-04's file from 75 lines to 7, week-05's from 100 to 13, week-07's from 100 to 27, and week-08's from 87 to 20. Two of those files end by asking the reader to restore them from git history. Root cause: **contradictory** (§5.2) → [P0-1], auto-applyable.
3. **Nothing defines a "screenshot."** Three kinds of image share the name in these folders: real captures, renders drawn from live text, and look-alikes of GitHub filled with invented content. Week-01's `issue_form.png` and `pr_review.png` are look-alikes; the second shows a made-up PR #42 from "student-reviewer." Only a commit message says so, and week-01's `IMAGES.md` still calls all eight of its images gray placeholders. Week-05's notes, meanwhile, decline to fabricate the same kind of image. Root cause: **ambiguous** (§5.3) → [P0-3], needs your decision.

The smaller findings:

- One caption claim rested on a query capped at 25 results. It shipped wrong and was corrected the same day.
- The book's 11 figures have no record of where they came from.
- Several capture problems were each solved by trial and error: DevTools clicks, a panel that loads only on hover, server errors, marker placement, and legibility. None of those fixes was written down where a tool could use it.

## 2. Scope reviewed
- **Window:** 2026-08-21 (commit `9007506`, the first browser-captured images in either repo) through 2026-09-24 (PR #47). The review concentrates on 2026-09-22 → 24, when real capture first worked; the earlier weeks are the baseline it replaced.
- **Artifacts:**
  - Textbook `images/ch-07/` (PR #128, 5 figures) and `images/ch-08/` (PR #129, 6 figures).
  - Slides: `slides/week-07/img/` (PR #43, corrected by #44) and `slides/week-08/img/` (PR #45).
  - Handout: `handouts/week-06/img/` (PRs #46 and #47).
  - For comparison, every image in `slides/week-01` to `week-05`.
- **Evidence:**
  - Git history of both repos, and every `IMAGES.md` and `stubs.tsv` in weeks 01–08.
  - The container's `apt` history.
  - The session scratchpad: 23 top-level capture and query scripts plus 14 for the handout, and 205 intermediate captures in seven folders.
  - The session transcript (about 7,800 lines), searched for failure signals.
  - A pixel audit of every image in weeks 01–05.
  - A test run of `make_stubs.py` on copies of weeks 04, 05, 07, and 08; the working tree was not touched.
- **Human review:** none of the seven PRs has a review comment. The only human edit to images in the window is the instructor's Overleaf commit `adb1ce4`, which swapped week-07's four meme placeholders for real memes, the handoff the notes asked for. As the 2026-09-21 AAR found, this repo has no reviewer besides its author, so this report relies on git, the transcript, and direct tests.
- **Intent baseline:** no written contract for screenshots exists. The nearest sources:
  - `slides/common/AUTHORING.md`, sections "Images" and "Images almost everywhere, memes welcome."
  - The textbook's `claude.md`, which says nothing about figures, provenance, or alt text.
  - The requests that started each piece of work.

## 3. What the process was supposed to do (Q1)
Written down:

- `AUTHORING.md` §Images: list every image in `img/stubs.tsv` with a "one-line description of the real asset," then run `make_stubs.py`, which "renders labeled gray placeholders and writes `IMAGES.md`." It names "dev-tools screenshots" and "a GitHub PR screenshot for the Friday section" as typical images.
- `AUTHORING.md`, voice section: "Keep placeholder stubs for anything you cannot source."
- Every generated `IMAGES.md`: "Replace each with the real asset described below (keep the same filename), then rebuild."

The book teaches rules that apply equally to any tool that fetches pages for the book:

- Name yourself in the User-Agent with a contact address (ch-02).
- Pace requests and back off on errors (ch-02, ch-07).
- Check a page by hand before automating it (ch-08).
- Record the date of anything that drifts. Ch-03 puts it this way: "your table is a snapshot, not a fact."

Requested:

- On 2026-09-09: "Add screenshots using playwright and a 640x480 or similar resolution" (the week-04 pull-request handout).
- Later: real screenshots for ch-07, ch-08, weeks 07 and 08, and the Oscars handout.

Not written anywhere:

- where capture code lives;
- what counts as a screenshot;
- how the book records where a figure came from;
- how images travel from the book to slides and handouts;
- how large text must be to read on a slide;
- what alt text must contain.

## 4. What actually happened (Q2)

| Date | Work | Method | Result |
|---|---|---|---|
| 2026-08-21 | week-01, 8 images | Headless Playwright. The book site and repo page were rendered from a local mirror, because the proxy passed page loads but not their CDN assets. The new-issue form and the PR view were rebuilt as look-alikes and filled with the deck's worked example. | Shipped. The method is recorded only in the message of commit `9007506`. `IMAGES.md` still describes all eight images as gray placeholders. |
| 2026-08-24 | week-02, 2 figures | `slides/common/make_figures.py` draws the live text of Wikipedia's `robots.txt` and an httpbin response into a browser-like frame. | Shipped. The script's docstring says "Not mock screenshots." |
| 2026-09-09 | week-04 pull-request handout (PR #35) | Playwright | Blocked. Connections to example.com and Wikipedia were reset, and GitHub's web pages answered 403 from the session gateway. The session judged the block a fixed policy boundary. The next day the instructor captured the four images by hand (`handout_*.png`). The first batch was pasted into the chat, where it reached the session as pictures only, with no file to crop. The instructor then pushed the files. The session blacked out an email address in one, downscaled all four, and documented both. |
| 2026-09-22 | ch-07 (5), week-07 (15) | Headless Playwright through the proxy, after adding the proxy's certificate authority to Chrome's store; one DevTools shot from headed Chrome on a virtual display (Xvfb). | Shipped in #128 and #43. #44 corrected a caption claim and retook one image the same day. |
| 2026-09-22 → 23 | ch-08 (6), week-08 (9 + a diagram) | Selenium 4.49 driving Chrome for Testing 154, headed on Xvfb; real clicks with xdotool; screen grabs with ImageMagick. Playwright 1.63 for Playwright's own screenshots. | Shipped in #129 and #45. |
| 2026-09-23 → 24 | week-06 handout (2 screenshots, 2 annotated) | The same stack at device scale 2, with DevTools settings written into the browser profile and TikZ markers drawn over the untouched screenshots. | Shipped in #46 and #47. |

What went wrong along the way:

- **Environment.**
  - The `apt` history shows packages installed by hand mid-task: `libnss3-tools` (2026-09-22 20:23), then `xvfb`, `imagemagick`, and `x11-apps` (20:47), then `xdotool` and `graphviz` (2026-09-23 01:03).
  - A chromedriver 147 at `/opt/node22/bin` shadowed the driver Selenium Manager would have matched to Chrome 154. It caused three `SessionNotCreated` failures before `SE_SKIP_DRIVER_IN_PATH=true` fixed them.
  - A device-scale-2 window larger than the virtual screen cut off the page heading. Restarting Xvfb at 3400×4200 fixed it.
- **Interaction.**
  - A CSS selector that did not match led to clicking by coordinates.
  - Page coordinates computed as outer minus inner window height were wrong once DevTools was docked at the bottom. The fix was a measured constant, 144 px.
  - The DevTools console's `inspect()` did not select the element it was given.
  - Clicking a disclosure triangle in the Elements tree both expanded the node and selected it. Running Inspect again on the target restored the selection.
  - The Wayback toolbar loads **Collected by** only on hover. The first `about_capture.png` missed it, and #44 retook it.
- **Identification.** Every capture sent a named User-Agent with a contact address. It was never the string the course teaches: the captures used `INFO4617-course-slides …` and `INFO4617-course-materials/1.0 …`. The Oscars handout teaches `Web Data Science/v1 brian.keegan@colorado.edu`, which the instructor chose on 2026-09-24.
- **Server errors.** The Wayback Machine answered 502 or dropped the connection on about half of first attempts. One 502 page overwrote a good calendar capture, because captures were written straight to their final file names.
- **Evidence.** Week-07's first account of the broken x.com images rested on a CDX query capped at 25 rows. The full query showed that six of the seven images were only ever captured as 404s, and #44 corrected the slide and its notes.
- **GitHub pages.**
  - On 2026-09-23, a signed-out capture of a public PR worked: week-08's `pr_review.png` shows textbook PR #129. So the 2026-09-09 verdict no longer held, and no record says what changed.
  - For signed-out viewers, GitHub collapses a large `.qmd` diff behind "Load diff."
  - Pages behind a login, such as the new-issue form, cannot be captured from a session.
- **Legibility.**
  - Week-08's `infinite_scroll.png` was dropped because it could not be read at slide size.
  - The zero-bytes comparison had to be rebuilt larger.
  - The book's 11 figures are 1× captures, 1100–1858 px wide; the handout's are 2×. Nothing set which scale to use.
- **Annotation.** The handout's markers are TikZ placed in the screenshot's pixel coordinates, placed by hand. Fitting them took several rebuilds:
  - markers covered text at small scale and were shrunk and given leader lines;
  - a label overflowed its column and became an overlay anchored east;
  - the unit length had to be recomputed to follow `\linewidth`.
- **Provenance.**
  - Slides and the handout got `IMAGES.md` notes with URL, date, method, and User-Agent. The book's `images/ch-07/` and `images/ch-08/` got none; what is known about them sits in captions, alt text, and two PR descriptions.
  - Week-05's notes say the four `handout_*.png` files live in `handouts/common/img/`. That folder does not exist; the files are in `slides/week-04/img/`.
- **The weeks 01–05 audit.**
  - Weeks 02, 03, and 05 still hold 11 gray placeholders. Only one is on a slide: week-05's `pr_review.png`, on "A revision menu for Chapter 5."
  - The other ten sit unused in their `img/` folders.
  - Week-01's deck shows the two look-alikes and the two mirror renders.

## 5. Gap analysis (Q3)

### 5.1 — Capture code and its environment had no home
**Root cause: missing.** No repo had a place for capture code, so each figure got a throwaway script in the scratchpad. The session wrote 37 of them, and none was committed. The knowledge that made capture work was just as temporary: which packages to install, how to trust the proxy, the chromedriver conflict, DevTools settings, and window sizes. When the container is reclaimed, all of it is gone. The `IMAGES.md` notes say what was done ("Chrome for Testing 154 driven by Selenium 4.49 on a virtual display"). They do not say enough to do it again: a note cannot be run, and it says nothing about the conflicts the setup has to avoid. The 2026-09-09 attempt ended at connection resets and a gateway 403. The 2026-09-22 attempt succeeded after the browser was routed through the proxy and trusted its certificate authority. Nobody can now say whether that configuration, or a change in the session's network policy, made the difference.

### 5.2 — `IMAGES.md` is both a generated file and a hand-kept record
**Root cause: contradictory.** `AUTHORING.md` says `make_stubs.py` "writes `IMAGES.md`." That makes it a build output. Practice since week-04 has made the same file the one place a week records where each image came from, how it was made, and what to redo when it goes stale. The build follows the contract and erases the practice. Tested on copies:

| Week | `IMAGES.md` before | after one `make` |
|---|---|---|
| week-04 | 75 lines | 7 |
| week-05 | 100 | 13 |
| week-07 | 100 | 27 |
| week-08 | 87 | 20 |

The script already refuses to overwrite a real image ("Never clobber a real asset"); it gives the notes no such protection. The week-07 and week-08 notes each end with a workaround ("restore these notes from git history"). That is a warning in place of a fix, and it is invisible to anyone who runs `make`, because the Makefile sends the script's output to `/dev/null`. CI has not tripped it only because `build-slides.yml` calls `latexmk` directly.

### 5.3 — "Screenshot" means three different things
**Root cause: ambiguous.** The folders hold:

- **real captures:** weeks 07–08, ch-07–08, the handout, and the instructor's four `handout_*.png`;
- **renders from live data:** week-02, where the text is real and the browser frame is drawn;
- **look-alikes:** week-01's issue form and PR view, GitHub's interface rebuilt and filled with invented content (PR "#42," "student-reviewer," "course-instructor").

The look-alikes were disclosed, but only in the message of commit `9007506`. Nothing on the slide or in `IMAGES.md` tells a student or a later author that the PR never existed. The rules point both ways. `AUTHORING.md` says to keep a stub "for anything you cannot source," which argues against rebuilding what cannot be captured. Week-05's notes refuse to "post a comment solely to manufacture a screenshot" and leave `pr_review.png` gray, the stricter reading. Nothing records which kind each image is, so a reader cannot tell. This is a judgment call about what students are shown, so it is surfaced as a decision (P0-3) rather than settled here.

### 5.4 — A number in a caption came from a capped query
**Root cause: novel.** Week-07 was the first time a caption made a claim about how many captures exist or succeeded. The first explanation of x.com's broken images came from a CDX query with a 25-row limit, read as if it were complete. The fix was a full query, and the claim changed, which is the lesson ch-07 itself teaches about the archive. No step asks, before a number goes into a caption, whether the query that produced it was complete. Anything that counts or dates things will make the same mistake: the CDX API, pageview totals, "Saved N times" figures, rate-limit headers.

### 5.5 — The book does not record where its figures came from
**Root cause: missing.** Slides and handouts inherited `IMAGES.md` from `make_stubs.py`, and the book has no equivalent. The 11 figures in `images/ch-07/` and `images/ch-08/` carry good captions and alt text. Nothing records the URL each was captured from, the date, the browser, the User-Agent, or what a retake would need. That is the information a revising student or a future edition needs, and the book is the source that slides and handouts copy from.

### 5.6 — Interaction and server failures were fixed on the spot, not in code
**Root cause: novel**, and becoming **buried**. These were the project's first real browser captures, so each failure was new. Every fix is now known:

- set the window size to fit the virtual screen;
- measure the browser's toolbar height before DevTools opens;
- move through the Elements tree by keyboard instead of clicking triangles;
- wait for panels that load on hover;
- treat a 502 page as a failure, not a capture;
- write retakes to a new file and replace the old one only after review.

All of these live in the transcript, so the next session would have to find them again.

### 5.7 — Scale, legibility, and markers were fitted by hand
**Root cause: missing.** Nothing says what scale to capture at, how large text must be at its final size, or how a marker finds its target. The book's figures are 1× and the handout's are 2×. Legibility was judged by looking at a compiled slide, after the fact; one image was dropped and one rebuilt. The handout's markers are positioned in hand-typed pixel coordinates. A retake at a new scroll position or window size means placing every marker again, even though the browser knew each element's box at the moment of capture.

### 5.8 — Access changes between sessions, and nothing checks it
**Root cause: novel.** The 2026-09-09 session judged the block a fixed policy boundary. The instructor then spent a session capturing four images by hand. Thirteen days later the same kind of capture, including a public GitHub page, worked. The earlier verdict was never re-tested; a new request simply happened to succeed. The access problems split into two kinds:

- **Permanent:** pages behind a login (the new-issue form, anything that needs write access) can never be captured by the agent. They need the instructor, or a different subject. Week-08's `pr_review.png` shows a subject that works: a public PR's "Files changed" view, captured while signed out, with no student work in it. When the instructor does capture, the images have to arrive as files; on 2026-09-10, images pasted into the chat reached the session as pictures it could see but not crop, resize, or redact.
- **Per session:** whether the proxy passes a browser at all. A one-minute check at the start of each capture task would have answered that on 2026-09-09 and every day since.

## 6. Recommended revisions (Q4)

### [P0-1] Stop `make_stubs.py` from overwriting hand-written notes
- **Target:** `slides/common/make_stubs.py`; `slides/common/AUTHORING.md` §Images; the closing warnings in `slides/week-07/img/IMAGES.md` and `slides/week-08/img/IMAGES.md`
- **Root cause:** contradictory (§5.2)
- **Evidence:** four weeks lose 68–87 lines of notes on one `make` (table in §5.2)
- **Change:**
  > Before (`make_stubs.py`): `with open(os.path.join(img_dir, "IMAGES.md"), "w") as md:` — the whole file, every run.
  >
  > After: the generated placeholder table goes between `<!-- stubs:begin -->` and `<!-- stubs:end -->`. The script replaces only what is between the markers, keeps everything outside them, and creates the file with markers when none exists. When an existing `IMAGES.md` has no markers, the script leaves it alone and prints `IMAGES.md has hand-written notes; not touching it`, and the Makefile stops sending that output to `/dev/null`.
  >
  > Before (`AUTHORING.md`): "This renders labeled gray placeholders and writes `IMAGES.md`."
  >
  > After: "This renders labeled gray placeholders and keeps a table of them in `IMAGES.md`. Everything else in `IMAGES.md` is yours: when you replace a placeholder, say where the real image came from, how it was made, and the date."
- **Why it works:** it gives the notes the same protection the script already gives real images, and it stops the failure from happening in silence.
- **Owner:** auto-applyable
- **Status:** Proposed

### [P0-2] Build a screenshot toolkit in the textbook repo
- **Target:** new `tools/shots/` in `cuinfoscience/Web-Data-Science-Book`; plan in [`../plans/2026-09-24-screenshot-toolkit.md`](../plans/2026-09-24-screenshot-toolkit.md)
- **Root cause:** missing (§5.1); it also closes §5.4, §5.6, §5.7, and §5.8
- **Evidence:** 37 uncommitted capture and query scripts; six packages installed by hand; three driver failures from a stray chromedriver; the fixes in §4, none of them in code
- **Change:** a committed tool that an agent in a cloud session can run from nothing:
  - a setup script and a one-minute preflight check;
  - one recipe file per chapter describing each figure;
  - capture with guards that fail loudly on error and block pages;
  - retakes that never overwrite an approved image;
  - markers anchored to page elements;
  - a legibility check at each target size;
  - a provenance record per figure;
  - a command that copies figures into slides and handouts with their notes.
  The plan phases the work and gives each phase a test: re-capture figures that already exist.
- **Why it works:** the knowledge that is now in a transcript becomes code that runs the same way next time. Its first test cases are figures that have already been captured once by hand.
- **Owner:** maintainer review of the plan
- **Status:** Proposed

### [P0-3] Decide what counts as a screenshot, and label every image
- **Target:** decision first; then `AUTHORING.md` §Images, the toolkit's rules, and week-01's `issue_form.png` and `pr_review.png`
- **Root cause:** ambiguous (§5.3)
- **Evidence:** two look-alikes on the week-01 deck, disclosed only in a commit message; week-05's notes refuse the same practice
- **Change:** not proposing text until you choose. Options:
  - **(a) Real or labeled.** Only real captures and labeled illustrations (diagrams, renders from live data). No look-alikes of a real site. Replace week-01's two images with real captures: a real filed issue on the textbook repo in place of the empty form, and a public PR's "Files changed" view in place of PR #42.
  - **(b) Look-alikes allowed when labeled.** They stay, but the slide says "illustration" and `IMAGES.md` says what they are.
  - **(c) Per case.** Look-alikes only where the real page is behind a login, and always labeled.

  I recommend (a), because the book and course teach students to check what a page really says. Whatever you choose, every provenance entry records its kind: `capture`, `render`, `diagram`, or `illustration`.
- **Why it works:** a later author, or a student, can then tell from the file's own record what an image shows.
- **Owner:** maintainer decision
- **Status:** Proposed — awaiting your call

### [P1-1] Record where the book's existing figures came from
- **Target:** new `images/ch-07/IMAGES.md` and `images/ch-08/IMAGES.md` in the textbook repo
- **Root cause:** missing (§5.5)
- **Evidence:** 11 figures and no provenance. The facts already exist in `slides/week-07/img/IMAGES.md` and `slides/week-08/img/IMAGES.md`, which describe the same captures.
- **Change:** for each figure, record the source URL, capture date, browser and version, User-Agent, crop, and what a retake needs. Once P0-2 lands, the toolkit's recipes for these 11 figures replace the hand-written files.
- **Why it works:** the book is the source the slides copy from, so it should hold the record the copies point back to.
- **Owner:** auto-applyable
- **Status:** Proposed

### [P1-2] A number in a caption needs a complete query behind it
- **Target:** `AUTHORING.md` §Images and the textbook's `claude.md` (one rule each); the toolkit's `evidence` step
- **Root cause:** novel (§5.4)
- **Evidence:** the 25-row CDX query behind week-07's first broken-capture claim; corrected in #44
- **Change:** add "Any count, date, or total printed in a caption or on a slide comes from a query whose limit and paging are recorded next to the figure. If the query hit its limit, page until it doesn't, or don't print the number." In the toolkit, an evidence query that returns exactly its limit fails.
- **Why it works:** it turns ch-07's own lesson ("the archive is incomplete, and your query may be too") into a check that runs before the claim ships.
- **Owner:** auto-applyable (the rule); P0-2 (the check)
- **Status:** Proposed

### [P1-3] Write down the alt-text and as-of habits that worked
- **Target:** textbook `claude.md`; toolkit `check`
- **Root cause:** missing. The practice is strong (§7), but nothing written requires it.
- **Change:** "Every figure has `fig-alt` that transcribes the text and numbers a reader needs from it (the ch-07 and ch-08 figures run 280–440 characters). A figure showing anything that changes (counts, versions, live pages) says when in its caption."
- **Owner:** auto-applyable
- **Status:** Proposed

### [P1-4] Back-fill chapters 1–5
- **Target:** textbook ch-01 to ch-05, slides weeks 01–05, and their handouts; plan in [`../plans/2026-09-24-screenshot-backfill-ch01-05.md`](../plans/2026-09-24-screenshot-backfill-ch01-05.md)
- **Root cause:** not a gap. It is the work that the new ability makes possible, and it should wait on P0-1 to P0-3.
- **Owner:** maintainer review, one pilot chapter first
- **Status:** Proposed

### [P1-5] Keep a screenshot within 800×600 of the screen
- **Target:** textbook `tools/shots/` and `claude.md`; `slides/common/AUTHORING.md`; both plans
- **Root cause:** missing, and found after this report: the instructor's review on 2026-09-24 ("font sizes on some of these images are too small to be accessible"). §5.7 found no rule for scale or text size; the captures used whole 1280- and 1680-pixel windows, and the slides and the book show them far smaller.
- **Change:** a first, soft limit. A screenshot shows at most 800×600 CSS pixels of the screen (1600×1200 image pixels at 2×): a small window, a crop to what the text discusses, and DevTools zoomed rather than a wider window. Going over is allowed with a stated reason. The measured legibility check (§7.7 of the toolkit plan) stays the finer test.
- **Owner:** maintainer decision (made); the toolkit enforces it as a warning
- **Status:** Applied in the toolkit (textbook PR #137) and in `AUTHORING.md`; existing figures flagged for retakes (§9)

### [P2-1] Fix the two stale `IMAGES.md` files
- **Target:** `slides/week-01/img/IMAGES.md` (calls eight real or look-alike images "placeholders"); `slides/week-05/img/IMAGES.md` (points at a `handouts/common/img/` that does not exist)
- **Root cause:** drift, caused by §5.2
- **Change:** rewrite week-01's notes from commit `9007506`'s message, following whatever P0-3 decides; in week-05's notes, point at `slides/week-04/img/`.
- **Owner:** auto-applyable, after P0-1 (otherwise the next `make` undoes it)
- **Status:** Proposed

## 7. Strengths to sustain
- **Honest and polite on every request.** Each capture sent a named User-Agent with a contact address. Pauses ran 8–30 seconds between Wayback page loads, and errors were retried with backoff. The book teaches the same behavior in ch-02 and ch-07, so the figures were made the way the book says to work.
- **Real tools, operated for real.** DevTools was driven with real right-clicks and keyboard input, not mocked up. Ch-08's Chrome for Testing window keeps its own "only for automated testing" bar, because that bar is part of the lesson.
- **Claims checked against a second source.** Before the x.com and facebook.com captions shipped, they were checked against the CDX API and the raw `id_` captures. When one explanation proved wrong, #44 corrected it in public the same day and wrote the reason into the notes.
- **Dates on everything that drifts.** The captions name the month ("in September 2026"), and the notes say "correct as of 2026-09-22."
- **Alt text that transcribes.** All 11 book figures carry `fig-alt` of 282–441 characters. Each transcribes the text and numbers on screen, not just "screenshot of X."
- **A pull-request screenshot with no student work.** Week-08 used the public "Files changed" view of the textbook's own PR #129, and the notes say so.
- **Annotation kept as source.** The handout's markers are TikZ drawn over an untouched screenshot. `make figures` builds each figure twice: vector PDF for print, 250-dpi PNG for the notebook. A retake means moving coordinates, not repainting pixels.
- **Redaction done and documented.** One of the instructor's week-04 handout captures showed a real email address. It was blacked out before commit, and the notes include the code that did it.

## 8. Revision actions — tracking table

| ID | Priority | Target | Change | Owner | Status |
|----|----------|--------|--------|-------|--------|
| P0-1 | P0 | `slides/common/make_stubs.py`, `AUTHORING.md` | Generated table between markers; never overwrite notes; stop hiding the output | auto-applyable | **Applied** (2026-09-24) — see §9 |
| P0-2 | P0 | textbook `tools/shots/` | Build the screenshot toolkit per the plan | maintainer review | Plan approved (merged, #48); M1–M3 **merged** (textbook #135–#137) |
| P0-3 | P0 | `AUTHORING.md`, week-01 images | Decide what counts as a screenshot; label every image's kind | maintainer decision | **Resolved: option (a)**, real or labeled — rule in `AUTHORING.md`; week-01's look-alikes replaced in the ch-01 back-fill |
| P1-1 | P1 | textbook `images/ch-07`, `images/ch-08` | Provenance notes for the 11 existing figures | auto-applyable | **Applied** (merged with M1, textbook #135): `provenance.json` and `IMAGES.md` for all 11 |
| P1-2 | P1 | `AUTHORING.md`, textbook `claude.md`, toolkit | Numbers in captions need a complete, recorded query | auto-applyable + P0-2 | Rules **applied** in `AUTHORING.md` and the textbook's `claude.md` (#135); the toolkit's query check is M4 |
| P1-3 | P1 | textbook `claude.md`, toolkit | Alt-text and as-of rules | auto-applyable | **Applied** (#135): the `claude.md` rule and `check`, which flags 3 ch-07/08 captions that don't say when they were captured |
| P1-4 | P1 | ch-01–05, weeks 01–05, handouts | Back-fill per the plan, pilot first | maintainer review | Plan approved (#48); pilot **done** (textbook #138, course #51); gate closed 2026-09-24 (§9); chapters 1–4 next |
| P1-5 | P1 | toolkit, `AUTHORING.md`, textbook `claude.md`, plans | A screenshot shows at most 800×600 CSS pixels (a soft limit) | maintainer decision | Rule **applied** in `AUTHORING.md`; toolkit warning **merged** (textbook #137); restated as the two-sided rule (P0-1 of [the toolkit-sprint AAR](AAR_Web-Data-Science-Book_2026-09-24.md)); retakes listed in §9 |
| P2-1 | P2 | week-01 and week-05 `IMAGES.md` | Fix stale notes | auto-applyable, after P0-1 | **Applied** (2026-09-24) |

## 9. Resolution (2026-09-24)

The maintainer merged this report and both plans (#48), then chose option
(a) for P0-3: real captures, plus diagrams and renders labeled as such, and
no look-alikes. `slides/common/AUTHORING.md` §Images now states the rule under
"What counts as a screenshot," together with the P1-2 rule for numbers in
captions. Week-01's `issue_form.png` and `pr_review.png` stay on the (already
taught) deck until the chapter 1 back-fill replaces them with real captures.
Week-01's `IMAGES.md` now says what they are. Week-02's two renders are the
one place the new caption rule is not yet met; the chapter 2 back-fill offers
a real-browser capture (2-1) for the instructor to choose between.

P0-1 landed as planned, with one change to the design: an `IMAGES.md` with
no markers that consists only of lines the old script wrote (weeks 01–03 and
09–14 before this fix) is still regenerated in its old format, since it holds
no notes. Those files therefore don't churn. A file with notes and no markers
is left alone, and the script says so on every build. `make_stubs.py --check`
reports what a build would change without changing anything.

Applying it turned up three things this report had missed:

- **Week-06's notes were at risk too.** Its `IMAGES.md` has 63 hand-written
  lines that the old script would have erased. The fix protects them without
  any edit to week-06, which stays untouched while students work on it; the
  build prints a reminder that its table is not being maintained.
- **Week-07's `stubs.tsv` still listed the four meme placeholders** the
  instructor had replaced in Overleaf (`adb1ce4`) under new file names. The next
  build would have drawn four unused gray `meme_*.png` files back into the
  folder. The rows are gone, and week-07's notes now describe the
  instructor's picks.
- **Week-05's notes duplicated week-04's section on the handout screenshots**
  and pointed at a folder that doesn't exist. The section is now a two-line
  pointer to `slides/week-04/img/`.

Tested on a copy of `slides/`: `make week-07` (exit 0, 34 pages) added a new
`stubs.tsv` row to the table, drew its placeholder, and kept every line of
the notes. A pure old-format file (week-09) picked up a new row in its old
format. A missing `IMAGES.md` (week-10) was created with markers. Week-06's
file was byte-identical afterward. On the real tree, `make_stubs.py --check
week-*` reports nothing to change.

### Later the same day: text too small to read (P1-5)

The instructor found the text in some images too small to be accessible and
set a first, soft limit: a screenshot shows at most about 800×600 of the
screen. Measured against it:

- **Textbook:** all 11 ch-07 and ch-08 figures show 1100–1858 CSS pixels
  across. The book's 778-pixel column shows their text at 42–71% of its size on
  screen, and DevTools' text in the full-window captures at about 5 pixels.
  The toolkit's `check` now flags each one.
- **Slides:** 18 screenshots in weeks 01, 07, and 08 appear on their slides
  smaller than they were on screen:
  - week 01: all five, at about half;
  - week 07: six, at 45–63%;
  - week 08: seven, at 45–80%.

  The thin strips (the Wayback toolbar, the address bar) are wider than 800
  but are shown larger than life at full slide width, so they read fine.
- **Week-06 handout:** within the limit or zoomed. The card shows 560×595 CSS
  pixels; the DevTools figure is zoomed to 175%.

A capture within the limit is possible even for DevTools. An 800×600 window
with DevTools docked at the bottom, zoomed to 125%, and its Styles pane beside
the tree puts xkcd's `<img>` and its `title` and `alt` at 13.4 pixels in the
book's column. The same figure today is at 5.1.

The retakes follow the back-fill's order, with ch-07 and ch-08 (and weeks 07
and 08) after the chapter-5 pilot. Week 06 stays untouched this week.

### Later the same day: the chapter 5 pilot, and its gate (P1-4)

The pilot merged as textbook #138 and course #51. The back-fill plan asks for
a note on what review changed, in four parts, before chapter 4 starts.

- **Figures.** Four of the eight candidates were made:
  - 5-1 `inspector-heading`;
  - 5-2 `element-picker`;
  - 5-4 `network-requests`;
  - 5-5 `network-headers`.

  5-3 and 5-6 show native context menus (Copy selector or XPath, and Copy as
  cURL). Chrome draws those outside the page and DevTools, where the
  toolkit's steps and anchors can't reach, so they were not attempted. The
  optional 5-7 and 5-8 were left out. On the week-05 deck, 5-1 fills the
  Inspector frame. `pr_review.png` stays a placeholder, because every
  chapter 5 pull request with a review comment is a student's.
- **Legibility.** The thresholds held: the four figures measure 12.8–14.6
  pixels in the book, against a floor of 11.

  The pilot found a failure at the other end. Squeezed under the 800×600
  cap, the first takes were crammed: the Styles pane took 40% of the width,
  rows wrapped, and names were cut to "…". Three of the four were retaken
  with a narrower scope:
  - a stacked Styles pane at its smallest;
  - hidden columns and timeline;
  - a taller window cropped to DevTools.

  On slides, DevTools text needs 0.56–0.58 of the text width, more than the
  0.48 that W/1680 gives. Both findings are now rules in the textbook's
  `AGENTS.md` and the course's `AUTHORING.md` (P0-1 of
  [the toolkit-sprint AAR](AAR_Web-Data-Science-Book_2026-09-24.md)).
- **Markers.** Markers are numbered and placed on measured anchors:
  - a brace marks a block of rows (the Client Hints);
  - a box marks a control (the picker button).

  An overlay that Chrome draws itself, such as the picker's size label, takes
  no marker; the caption names it. Markers are drawn once, at the book's
  scale, so on a slide at 0.75 of the text width they come out about half
  size. That needs fixing before slide copies need markers.
- **Captions.** Captions are dated ("September 2026"). They say what the
  capture setup changes that a reader would see: a first visit with nothing
  cached, and HTTP/1.1 through the proxy. They never claim a route the
  capture didn't take. The alt text runs 400–433 characters. The capture's
  own traces stay out of frame: the proxy's address, the egress IP, and a
  GeoIP cookie.

The pilot also found five toolkit bugs that the selftest missed (§5.2 of
[the toolkit-sprint AAR](AAR_Web-Data-Science-Book_2026-09-24.md)), all
handled in #138. The last gate before chapter 4 is an effect test for each
DevTools preference the toolkit writes (that AAR's P0-3).
