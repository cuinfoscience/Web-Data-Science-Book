# Decision log

Standing decisions for the book and its tools, newest first. Each entry gives the decision, the reason, and where the decision is written or enforced. Entries are never deleted. When a decision is replaced, it is marked *superseded*, with a link to the entry that replaces it. Proposals that nobody has decided yet are listed in [`handoff.md`](handoff.md), not here.

## 2026-09-24 · A screenshot may relax to 1024×768 when that is clearer and still legible

**Decision.**
- 800×600 CSS pixels stays the default for what a screenshot shows.
- A screenshot may show up to 1024×768 when both of these hold:
  - the extra room removes clutter: rows that wrap, columns cut short with "…", panels squeezed together;
  - its text still passes `tools/shots/run check` everywhere it is shown: 11 pixels in the book, 16 on a 1920-pixel slide, 6 points in print.
- The recipe says what the room removes, in `oversize:`. The tools warn about a figure in that range that has no reason, has text too small at any target, or has text that was never measured.
- Beyond 1024×768, a recipe still needs a reason, such as DevTools zoomed to 175% for print.

**Why.** The 800×600 cap fixed tiny text, but under the cap alone some figures came out crammed (see "Figures are readable at both ends", below). The maintainer asked to allow 1024×768 when it keeps text legible and reduces clutter. At 1024 pixels wide, the book's column shows text at 76% of its size on screen, against 97% at 800. So the legibility check, not the size, stays the test: on-screen text needs about 14.5 CSS pixels, which for DevTools means zooming to about 150%.

**Where.** `tools/shots/lib/legibility.py` (`SOFT_LIMIT`, `RELAXED_LIMIT`, and `size_verdict`), `tools/shots/run check`, `tools/shots/README.md` ("The rules" and "Legibility"), `AGENTS.md`, and the course's `slides/common/AUTHORING.md`. *Amends* "A screenshot shows at most 800×600 CSS pixels of the screen", below.

## 2026-09-24 · No browser banners in figures

**Decision.**
- Figures don't show Chrome for Testing's "only for automated testing" notice, or any other infobar.
- Headed captures launch Chrome with `--disable-infobars`. `tools/shots` fails a headed take whose bars above the page are taller than the tab strip and address bar.
- The one exception is a figure whose subject is the bar: ch-08's window opened by Selenium, whose caption points at it. Its recipe says `expect: {infobar: true}`.

**Why.**
- The notice is 55 pixels of browser chrome that says nothing about the page, and it repeats in every capture that has it.
- It was in figures made by scripts before the toolkit, which ran Chrome without the switch: ch-08's `network-tab-json` and `xkcd-inspect`, and week 08's `network_json.png`.
- The toolkit's own captures had it off only because Playwright passes the switch by default.

**Where.** `tools/shots/lib/headed.py` (the switch and the guard), `tools/shots/README.md` ("No infobars"), `AGENTS.md` ("Figures and screenshots"), and the course's `slides/common/AUTHORING.md`.

## 2026-09-24 · Chapter work resumes

**Decision.** The maintainer lifted the pause set after the chapter 5 pilot. The order of work:
- The screenshot back-fill of chapters 1–4 comes first, in the plan's order: ch-04, ch-01, ch-02, ch-03. Each chapter gets one textbook PR and one course PR.
- Two gates come before it: the pilot's resolution note, and effect tests for the DevTools preferences (AAR P0-3).
- The chapter 7–8 and slide retakes (AAR P2-1) follow the back-fill.
- Computed outputs wait on their plan's §9 decisions, not on the pause.

**Why.** The pause existed to review the toolkit and the process before scaling them. That review is done: the AAR, its P0 text (#140, course #53), and the pilot gate, closed on 2026-09-24.

**Where.** [`handoff.md`](handoff.md), and [`plans/2026-09-24-screenshot-backfill-ch01-05.md`](plans/2026-09-24-screenshot-backfill-ch01-05.md). *Supersedes* "Pause chapter work after the chapter 5 pilot", below.

## 2026-09-24 · Figures are readable at both ends

**Decision.**
- A figure is scoped to what its paragraph discusses, then enlarged. Text too small and a figure too crammed both fail the reader.
- Crop to the subject, and hide the panels, columns, and sidebars the text doesn't mention.
- Enlarge by zooming the application, not by widening the window.
- `tools/shots/run check` is the one place that judges text size: 11 pixels in the book's column, 16 on a 1920-pixel slide, 6 points in print.
- The 800×600 cap stays, as a soft limit inside this rule.

**Why.** The 800×600 cap fixed the tiny text of whole-window captures. The chapter 5 pilot then squeezed DevTools into the cap, and the figures came out crammed: the Styles pane took 40% of the width, rows wrapped, and columns were cut short. Separately, the slide rule in `AUTHORING.md` (W/1680 of the text width) was too small for DevTools text by the toolkit's slide threshold. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.1, P0-1.)

**Where.** `AGENTS.md` ("Figures and screenshots"), the course's `slides/common/AUTHORING.md` ("How much a screenshot shows"), and `tools/shots/lib/legibility.py`. *The cap was relaxed the same day: a figure may show up to 1024×768 when its text still passes (entry above).*

## 2026-09-24 · Pull requests merge with merge commits; history is never rewritten

**Decision.**
- Merge pull requests with merge commits. Do not squash or rebase.
- Never force-push a branch someone may have seen.
- Open a new branch for each pull request, and don't base one pull request on another's unmerged branch.
- A session given one fixed branch restarts it from `main` after each merge. With merge commits, that is a fast-forward, not a force-push.
- Agents merge only when the maintainer asks, and never merge a student's pull request.

**Why.** Squash merges left the session's branch behind `main` after every merge. It had to be reset and force-pushed, about six times in one day, and one stacked pull request had to be rebased. The review history became hard to follow, and the maintainer asked why. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.3.)

**Where.** This log, and `AGENTS.md` ("Git and Pull Requests"). A permission rule that denies force-pushes is proposed and untested (P0-2). *Supersedes* the squash merges used up to #138.

## 2026-09-24 · Pause chapter work after the chapter 5 pilot

*Superseded the same day by "Chapter work resumes", above.*

**Decision.** After the chapter 5 screenshot pilot merged (#138 here, #51 in the course repo), stop implementation on other chapters until the maintainer resumes it. That covers the back-fill of chapters 1–4, the retakes for chapters 7–8 and the slides, and computed outputs.

**Why.** Review the toolkit and the process before scaling them. The pilot found five toolkit bugs, plus figures that were too crammed to read.

**Where.** [`handoff.md`](handoff.md) lists what is paused.

## 2026-09-24 · One instructions file, `AGENTS.md`; records in `docs/`

**Decision.**
- The agent instructions live in `AGENTS.md`, renamed from `claude.md`. `CLAUDE.md` only imports it. An agent that looks for another file (`GEMINI.md`, `.cursorrules`) is pointed at `AGENTS.md` by the README.
- Project records live in this repository's `docs/`: AARs, plans, this log, and the hand-off note. The screenshot AAR and plans moved here from the course repository, which keeps pointers.

**Why.** Agents and their tools look for these names. The lowercase `claude.md` was not found by the AAR's own collector. Records sit beside the code they govern: `tools/shots` is here. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.5.)

**Where.** `AGENTS.md`, `README.md` ("For AI Agents"), [`README.md`](README.md) in this folder.

## 2026-09-24 · A screenshot shows at most 800×600 CSS pixels of the screen

**Decision.** A screenshot figure shows at most 800×600 CSS pixels of the screen. A recipe that needs more says why in `oversize:`.

**Why.** Whole-window captures shrank text to 42–71% of its on-screen size in the book's 778-pixel column. DevTools' text came out near 5 pixels.

**Status.** Standing, as the soft limit inside the entry above, "Figures are readable at both ends". The cap is a heuristic that serves that aim. Under the cap alone, the chapter 5 pilot produced crammed figures. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.1.) *Amended the same day: 800×600 is the default, and a figure may relax to 1024×768 when the room removes clutter and its text still passes. See "A screenshot may relax to 1024×768 when that is clearer and still legible", at the top.*

**Where.** `tools/shots/lib/legibility.py` (`SOFT_LIMIT`), `tools/shots/run check`, the course's `slides/common/AUTHORING.md`, and `AGENTS.md`.

## 2026-09-24 · Screenshots come from a toolkit, and one chapter goes first

**Decision.** Screenshots are made with `tools/shots`. Each figure has a recipe, guarded capture, provenance, measured markers, and a check, so it can be made again. A new use of the toolkit is piloted on one chapter before it rolls out.

**Why.** Scripts in a scratchpad made figures that no one could remake or trace. ([Screenshot AAR](aar/2026-09-24-screenshots.md), P0-2 and P1-4.)

**Status.** Milestones M1–M3 done (#135–#137). The chapter 5 pilot is done (#138).

**Where.** [`plans/2026-09-24-screenshot-toolkit.md`](plans/2026-09-24-screenshot-toolkit.md), `tools/shots/README.md`.

## 2026-09-24 · Real captures, or diagrams labeled as diagrams

**Decision.**
- A screenshot is a real capture of a real page, with its URL, date, and method recorded.
- Diagrams, charts, and renders drawn from live data are welcome, labeled as what they are. A render drawn to look like a browser window says so in its caption.
- Never rebuild a real site's interface by hand and fill it with invented content. If a page can't be captured, keep the placeholder, or show a real page that makes the same point.
- A count or date printed in a caption comes from a recorded query.

**Why.** Look-alikes of GitHub pages, filled with invented content such as a made-up pull request, sat among real screenshots. Only a commit message disclosed them. ([Screenshot AAR](aar/2026-09-24-screenshots.md), P0-3.)

**Where.** The course's `slides/common/AUTHORING.md` ("What counts as a screenshot"), and the toolkit's provenance and `check`. `check` matches each image against its recorded capture.

## 2026-09-23 · One honest identity for captures and examples

**Decision.**
- Captures and the book's request examples identify themselves with one User-Agent: `Web Data Science/v1 brian.keegan@colorado.edu`.
- They wait 8–30 seconds between page loads on a host.
- No logins, and no student names or student work in any image.
- Traces of the capture setup stay out of frame: the proxy's address, the egress IP, and location cookies.

**Why.** Sites can see who is asking and can refuse. The book teaches identifying yourself, so its own tools do too.

**Where.**
- The identity and pacing are set in one place, `tools/shots/lib/recipes.py` (`DEFAULTS`). The toolkit's selftest reads the identity back from a local server, Client Hints included.
- The rule on capture traces is in `AGENTS.md`, under "Figures and screenshots".

## Before 2026-09 · Code in the book is narrative

**Decision.** Code blocks do not run when the book is built (`execute: eval: false` in `_quarto.yml`), and the companion notebooks ship without outputs.

**Why.** "Running code, seeing it fail, and debugging it is where the learning happens" (`index.qmd`).

**Status.** Standing. Showing computed figures and tables is proposed in [`plans/2026-09-24-computed-outputs.md`](plans/2026-09-24-computed-outputs.md). That plan keeps the notebooks free of outputs.
