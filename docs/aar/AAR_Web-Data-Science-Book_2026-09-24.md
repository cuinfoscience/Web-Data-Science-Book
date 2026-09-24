# After-Action Report: the screenshot sprint (`tools/shots`), chapters 5, 7, and 8, 2026-09-21 → 2026-09-24

Written for agents on other books, who may copy `tools/shots` and cannot read this
project's history. Each gap in §5 is stated as a principle, then one real case,
then its cause. Appendix A sketches the design and why each part exists;
Appendix B lists the settings that are specific to this book.

## 1. Summary

In four days one Claude Code session made 41 real screenshots for a Quarto
textbook (chapters 5, 7, and 8), its slide decks, and a handout. It also turned
throwaway capture scripts into a toolkit, `tools/shots`: recipes, guarded capture,
provenance, measured markers, and legibility checks. The images are real and can
be made again. What cost the instructor most was **legibility, at both ends**:
- whole-window captures shrank text to 42–71% of its on-screen size;
- once an 800×600 cap fixed that, figures became **crammed**, with narrow panels,
  wrapped rows, and truncated columns.

The next costs, in order, were:
- **toolkit bugs found late**, only when a real chapter used the toolkit;
- **hand-checking** that each image was a real, unedited capture;
- **git churn** from squash merges and force-pushes.

The three highest-leverage revisions:
- **P0-1:** state legibility as an outcome measured where the figure is shown, and
  scope each figure to one idea;
- **P0-2:** merge with merge commits, a new branch per PR, and no rewritten
  history;
- **P0-3:** read back the effect of every setting sent to an external program, and
  make one real figure before a toolkit change counts as done.

## 2. Scope reviewed

- **Window:** 2026-09-21 → 2026-09-24.
- **Evidence:**
  - Textbook repo: 16 commits (12 non-merge, +7,225/−718 lines), 10 merged PRs (#119, #123–#125, #128, #129, #135–#138).
  - Course repo: 22 commits (16 non-merge, +6,077/−1,138), 12 PRs (#40–#51).
  - One Claude Code session with 14 compactions in the window:
    - 8 steering messages from the instructor, read by hand; the transcript collector found 0 (§5.6);
    - 2 stop-hook warnings about unpushed commits;
    - 61 tool errors in 6 repeated patterns.
  - Not available: the `gh` CLI. PR and CI data came from the GitHub connector. There are no GitHub review comments; review happens in the session.
- **Earlier AAR:** `docs/aar/2026-09-24-screenshots.md` (same date; it covers the captures before the toolkit).
- **Rigor level:** standard. These are shared teaching materials, the instructor reviews every PR, and students use the output.
- **Intent baseline:**
  - the textbook's `claude.md` (now `AGENTS.md`);
  - the course's `slides/common/AUTHORING.md`;
  - `tools/shots/README.md`;
  - the toolkit and back-fill plans in `docs/plans/`;
  - the instructor's requests in the session.

## 2a. Follow-up on earlier revisions

| ID | Earlier action | Applied? | Recurred? | Verdict |
|---|---|---|---|---|
| P0-1 | Deck builds stop erasing hand-written image notes | Yes (course #49) | No: notes edited this sprint survived every build | Worked |
| P0-2 | Build a screenshot toolkit | Yes (#135–#137; pilot #138) | No: every new figure has a recipe, takes, and provenance | Worked |
| P0-3 | Real captures or labeled diagrams, no look-alikes | Yes (rule in `AUTHORING.md`) | No look-alikes made since | Worked for making images; checking them is still by hand → §5.4 |
| P1-1 | Provenance for chapters 7–8 | Yes (#135) | — | Worked |
| P1-2 | Counts in captions come from a recorded query | Rule yes; toolkit check no (planned M4) | No new counts from queries | Carry forward |
| P1-3 | Alt text and dated captions | Yes | 3 chapter 7–8 captions still lack a date | Carry forward (P2-1) |
| P1-4 | Back-fill chapters 1–5, pilot first | Pilot done (#138, #51) | — | Worked: the pilot found 5 toolkit bugs before any wider rollout |
| P1-5 | A figure shows at most 800×600 CSS pixels | Yes | **Yes, in a new form:** crammed figures, and a slide rule that disagrees with the toolkit | Failed: re-diagnosed as P0-1 |
| P2-1 | Fix stale notes | Yes | No | Close |

## 3. What the agent was supposed to do (Q1)

Each figure is:
- a real capture, or a diagram labeled as one;
- made again from a recipe, with provenance;
- given alt text of 280–440 characters and a caption dated when it shows things that change.

Captures identify themselves with one honest User-Agent and wait 8–30 seconds between
page loads on a host. No logins, no student names or work. Chapters are piloted
before a wider rollout, and nothing merges until the instructor asks.

Rules for how readable a figure must be came mid-sprint, in two documents:
- `AUTHORING.md`: "a screenshot shows at most 800×600 CSS pixels of the screen … a capture W CSS pixels wide needs at least W/1680 of the text width";
- the textbook's `claude.md`: "Text must be readable where the figure is shown."

No document stated how pull requests merge.

## 4. What actually happened (Q2)

- **Before the toolkit (09-22 → 09-24):**
  - 11 chapter 7–8 figures and 24 slide screenshots, made by scripts in a scratchpad at 1280–1680-pixel windows;
  - two handout figures (DevTools zoomed to 175%, markers in TikZ).
  - Course #44 corrected an explanation that #43 had shipped wrong.
- **Toolkit (09-24):**
  - The earlier AAR, then the plan, then milestones M1–M3, all merged the same day (#135–#137).
  - At 14:46 the instructor found text too small to read and set an 800×600 soft limit, which went into M3 and `AUTHORING.md`.
- **Chapter 5 pilot (09-24):**
  - 4 figures, 19 takes (#138 textbook, #51 course).
  - The pilot turned up five toolkit bugs (§5.2).
  - After the instructor's answer, the pilot turned up a sixth problem: crammed figures, redone with narrower scope.
  - Pending rework: 11 chapter 7–8 figures and 18 slide screenshots fail the limit. Their retakes are paused.
- **Git:**
  - 12 agent PRs squash-merged.
  - The course repo's one session branch was reset after each squash: about 5 force-pushes, and the stop hook flagged unpushed commits twice.
  - M3, stacked on M2, had to be rebased after M2's squash.
  - The instructor asked why (15:02).
  - The session cannot delete branches (HTTP 403), so 27 merged branches remain.
- **Friction:** Edit calls on files not yet read (11) or changed since read (5); two merge calls with a short commit SHA.

## 5. Gap analysis (Q3)

### 5.1 Legibility has two ends, and it is an outcome, not a window size

**Principle.** A reader fails the same way on text that is too small and on a
figure that is too crammed.
- Measure text size where the figure is shown (a book column, a projected slide, a page).
- Scope each figure to the one thing its paragraph discusses: crop to it, hide what the text doesn't mention, and enlarge by zooming the application.
- A cap on the capture region is a heuristic that serves this outcome. It is not the outcome.

**Case.** The chapter 7–8 figures were whole browser windows:
- in the book's 778-pixel column, their text showed at 42–71% of its on-screen size;
- DevTools' text came out near 5 pixels.

The 800×600 cap fixed new captures, and the chapter 5 pilot then squeezed DevTools
into 800 pixels:
- the Styles pane took 40% of the width;
- rows of the Elements tree wrapped onto two lines;
- the Network list cut names to "University_of_C…" and types to "docu…".

Every letter was readable, and the figure as a whole was not. Separately, the slide
rule (W/1680 of the text width, 0.48 for an 800-pixel capture) disagreed with the
toolkit's 16-pixel slide threshold. DevTools text needs 0.56.

**Root cause.** At first *missing*: no rule existed until the instructor complained.
Then *ambiguous*: the rule limited a proxy (region size) instead of the outcome
(text size and density at each place the figure is shown). And *contradictory*: two
documents gave different slide thresholds.

### 5.2 A setting you cannot observe is a setting you have not set

**Principle.** Every setting passed to an external program needs a test that reads
the effect back from that program: a browser flag, an app preference, a header. An
unknown key fails silently. A self-test that runs a tool against its own fixtures
cannot see this. Only a real use can.

**Case.** Five bugs surfaced only when the chapter 5 pilot made real figures, after
three milestones had merged:
1. Playwright's `user_agent` option also rewrote the User-Agent Client Hints, and claimed Windows for a string naming no system. Every capture since M1 said so.
2. The DevTools preference meant to hide the Styles pane used a key DevTools ignores.
3. The Network panel's reload was a second visit: cookies and cache from the first load showed up as "(memory cache)" rows and a GeoIP cookie.
4. Chrome caps docked DevTools at about 70% of the window height.
5. Chrome 154 hides the Waterfall column by default.

The 52-check selftest passed throughout, and none of these raises an error.

**Root cause.** *Missing:* no practice of reading effects back. The plan also merged
toolkit milestones before any real figure used them. The earlier AAR said "pilot
first" for the back-fill of chapters, not for the toolkit itself.

### 5.3 Rewriting history costs the reviewer

**Principle.** Choose a merge policy that never rewrites a branch a reviewer has seen:
- with merge commits, a branch stays inside `main`, and reusing it is a fast-forward;
- with squash merges, every PR needs a fresh branch;
- stacked PRs plus squash always means a rebase.

Write the policy where the agent reads it.

**Case.** The session's instructions give it one fixed branch per repo, and say to
reset that branch after a merge. The agent chose squash merges, and no repo rule said
otherwise. Together these forced a force-push after every merge: about 5 in the
course repo, plus one rebase of a stacked PR. The instructor asked why, and the
answer was the agent's own preference. Branch deletion is blocked in the session, so
merged branches pile up (27).

**Root cause.** *Missing* merge policy, and a *contradiction* between the session's
fixed-branch reset and squash merging. The instructor decided on 2026-09-24: merge
commits, no rewritten history, a new branch per PR.

### 5.4 "Real and unedited" should be checkable where review happens

**Principle.** Evidence that an image is authentic must reach the reviewer where they
decide. Otherwise they check it by hand every time. Put the check in CI, on the PRs
that change images and only those, so the look a person gives goes to content.

**Case.** Each image carries its provenance:
- source URL, capture time, browser, User-Agent;
- a hash of its recipe and a hash of the image.

`tools/shots/run check` verifies all of it, but only on the agent's machine. The
instructor sees a PNG in a diff, and still checked by hand that images were real
captures. Traces of the capture setup were caught only by looking:
- the proxy's address (127.0.0.1) in DevTools;
- the egress IP echoed in an `x-client-ip` header;
- a GeoIP cookie naming a location.

**Root cause.** *Buried:* the evidence exists, but not where the decision is made.

### 5.5 Instructions belong where agents look

**Principle.** Keep one instruction file per repo, under the name agents look for
(`AGENTS.md`, with `CLAUDE.md` importing it). Keep a project's plans and reviews
beside the code they govern.

**Case.**
- The textbook's instructions were in a lowercase `claude.md`, and this AAR's own evidence collector found no instruction file.
- The screenshot AAR and the toolkit's plans lived in the course repo, invisible from the textbook.
- Mid-sprint rules landed in two rulebooks (4 edits to `AUTHORING.md`, 3 to `claude.md`), which then disagreed (§5.1).
- 14 compactions meant the rules often survived only in summaries.

**Root cause.** *Buried*, and rules spread across two repos. The fix is applied in the
PR that adds this report.

### 5.6 The review tooling missed most of the steering

The session collector counts corrections from user turns. Six of the sprint's eight
steering messages arrived mid-turn, stored as `queued_command` attachments, which the
collector skips. Its correction pattern also misses observations phrased as requests
("Font sizes … are too small", "I'm seeing lots of force-pushing … explain why"). It
reported 0 corrections. *Novel*; a fix to the skill's script is in §6.

### 5.7 The book's code never ran

The chapters show code with no charts or tables: `eval: false`, a teaching choice
stated in the preface. That now conflicts with the aim of showing computed figures.
*Contradictory*, planned in `docs/plans/2026-09-24-computed-outputs.md`.

## 6. Recommended revisions (Q4)

### [P0-1] State legibility as a two-sided outcome; one threshold source
- **Target:** `AGENTS.md` → "Figures and screenshots"; course `slides/common/AUTHORING.md` → "How much a screenshot shows"
- **Root cause:** ambiguous + contradictory (§5.1)
- **Medium:** definition text for scoping (it needs judgment). The toolkit's `check` stays the one place that computes thresholds and slide widths.
- **Evidence:** 11/11 chapter 7–8 figures and 18 slide screenshots below their on-screen size. 3 of 4 pilot figures redone for cramming. Slide rule 0.48 vs. the 0.56 needed.
- **Change:** in `AGENTS.md`, replace the "Text must be readable" bullet with:
  > - **Readable where it is shown, at both ends.** Text too small and a figure too crammed fail the same reader. Scope each figure to what its paragraph discusses: crop to it, and hide panels, columns, and sidebars the text doesn't mention. Enlarge by zooming the application (DevTools at 125%), not by widening the window. A figure shows at most 800×600 CSS pixels unless its recipe says why (`oversize:`). `tools/shots/run check` measures text at each place the figure appears (book column, slide, print) and gives the slide width to use. Before a PR, look at `tools/shots/run sheet ch-NN`: a wrapped row or a column cut to "…" means the figure shows too much.

  In `AUTHORING.md`, replace "needs at least W/1680 of the text width" with:
  > "at least the width `tools/shots` reports for it: W/1680 of the text width for a page's own text, more for DevTools".
- **Why it works:** the agent optimized the one number it was given, region size, and moved the failure to the other end. Naming both failures, and the method (scope, then zoom), gives it the outcome to aim at. One threshold source removes the disagreement.
- **Owner:** maintainer review · **Status:** Proposed

### [P0-2] Merge commits, a new branch per PR, no rewritten history
- **Target:** `AGENTS.md` → new "Git and pull requests"; `docs/decisions.md`; `.claude/settings.json`
- **Root cause:** missing + contradictory (§5.3)
- **Medium:**
  - definition text for the policy;
  - a permission `deny` for force-pushes, because it is mechanical and has no exceptions;
  - a repo setting for deleting merged branches.
- **Evidence:** 12 squash merges, about 6 force-pushes, 2 stop-hook warnings, the instructor's question at 15:02, 27 leftover branches.
- **Change:** add to `AGENTS.md`:
  > ## Git and pull requests
  > Merge with merge commits. Don't squash, rebase, or force-push a branch someone may have seen: a merge commit keeps the branch inside `main`, so a reused branch fast-forwards and the review history stays readable. Open a new branch for each pull request, and don't base one pull request on another's unmerged branch. If the environment can't delete merged branches, list them in `docs/handoff.md`.

  And in `.claude/settings.json` (untested; test it before enabling):
  ```json
  {"permissions": {"deny": ["Bash(git push --force:*)", "Bash(git push -f:*)", "Bash(git push --force-with-lease:*)"]}}
  ```
  Also turn on GitHub's "Automatically delete head branches".
- **Why it works:** with merge commits, the session's fixed branch no longer needs a reset. The deny rule stops a force-push even after a compaction has buried the prose.
- **Owner:** policy decided by the maintainer 2026-09-24; the text is auto-applyable; the permission and repo setting need maintainer review · **Status:** Decided; text Proposed

### [P0-3] Read back every external setting; a real figure before "done"
- **Target:** `tools/shots/selftest.py`; `tools/shots/README.md`; `AGENTS.md` → "Figures and screenshots"
- **Root cause:** missing (§5.2)
- **Medium:** tool config for the effect tests, which are mechanical; definition text for "done", which needs judgment.
- **Evidence:** 5 bugs found after M1–M3 merged. The selftest was green throughout. One of the bugs misreported the platform on every request.
- **Change:** the selftest gains one effect test per external setting. Each reads back:
  - the headers a local server received (added in #138 for Client Hints);
  - the DevTools layout drawn after each preference: the Styles split, the timeline, and the columns (still to add);
  - the page state after a first-visit reload (added in #138).

  In `AGENTS.md`, add:
  > A change to `tools/shots` is done when it has made one real figure that someone has looked at, and when every setting it passes to Chrome or DevTools has a test that reads the effect back — an unknown key fails silently.
- **Why it works:** it moves discovery from a chapter pilot, where it causes retakes, into the change itself.
- **Owner:** auto-applyable (tests); maintainer review (text) · **Status:** Proposed

### [P1-1] CI re-checks image provenance, only on PRs that change images
- **Target:** new `.github/workflows/shots-check.yml`
- **Root cause:** buried (§5.4)
- **Medium:** tool config (CI)
- **Evidence:** the instructor checks "real and unedited" by hand.
- **Change:**
  ```yaml
  on:
    pull_request:
      paths: ["images/**", "tools/shots/recipes/**", "tools/shots/lib/**"]
  jobs:
    check:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: {python-version: "3.11"}
        - run: pip install -r tools/shots/requirements.txt
        - run: python tools/shots/shots.py check
  ```
  `check` needs no browser and no network. Add a line to `AGENTS.md`: a PR that adds images lists them in a review table and states that `check` passes.
- **Why it works:** the reviewer gets a green check that the file is the recorded capture, and spends their look on content.
- **Owner:** maintainer review · **Status:** Proposed

### [P1-2] One instruction file, and records beside the code
- **Target:** `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`
- **Root cause:** buried (§5.5)
- **Medium:** definition text and file layout
- **Evidence:** the collector found 0 instruction files and 0 earlier AARs from the textbook.
- **Change:**
  - `claude.md` becomes `AGENTS.md`, and `CLAUDE.md` imports it.
  - `docs/` holds AARs, plans, `decisions.md`, and `handoff.md`.
  - The screenshot AAR and plans move here.
- **Owner:** auto-applyable · **Status:** Applied in the PR that adds this report

### [P1-3] The session collector reads mid-turn messages and observation-style steering
- **Target:** the `agent-after-action-review` skill's `scripts/collect_session_evidence.py`
- **Root cause:** novel (§5.6)
- **Medium:** tool config
- **Change:** before `if rtype != "user": continue`, treat `r["type"] == "attachment"` with `r["attachment"]["type"] == "queued_command"` as a human turn, whose text is `attachment["prompt"]`. Add to `CORRECTION_RE`:
  `\btoo (small|large|big|long|many|much)\b|\bI'?m seeing\b|\bexplain why\b|\b(major )?gap\b|\bnot (readable|legible|accessible)\b`
- **Owner:** skill maintainer · **Status:** Proposed

### [P2-1] Carry forward: dated captions and the 800×600 retakes
- **Target:** `images/ch-07`, `images/ch-08`; weeks 01, 07, and 08
- **Change:** date the 3 flagged captions; retake the 11 figures and 18 slide screenshots under P0-1.
- **Owner:** maintainer (paused 2026-09-24) · **Status:** Deferred

### [P2-2] Computed figures and tables in the book build
- **Target:** `docs/plans/2026-09-24-computed-outputs.md` (§5.7)
- **Owner:** maintainer decision · **Status:** Proposed

## 7. Strengths to sustain

- **Recipes and provenance** made retakes cheap. The pilot's 19 takes were each one command, and every promoted image can be made again.
- **Markers from measured anchors.** The browser measures where a marked thing is at capture time, so markers follow the page. No marker was placed by typed pixel positions.
- **Real input, confirmed.** Clicks in DevTools went through a real pointer and were checked by reading DevTools' own page, with no pixel offsets.
- **One honest identity and pacing.** Every page load returned 200, and no site blocked a capture.
- **Pilot first** (earlier P1-4). One chapter surfaced five bugs before three more chapters and 29 retakes depended on the toolkit.
- **Finding a setting by changing it by hand.** Dragging DevTools' splitter and reading back what it stored found the real preference key in one try. This emerged during the sprint and is worth keeping as a method.
- **Privacy caution.** The capture's own traces were kept out of frame, and a placeholder was kept rather than show a student's PR.
- **Questions before big tasks.** Structured questions settled real-or-labeled images, the soft limit, and the merge policy before work began.

## 8. Revision actions — tracking table

| ID | Pri | Target | Medium | Change | Owner | Status | Check next time |
|---|---|---|---|---|---|---|---|
| P0-1 | P0 | `AGENTS.md`, `AUTHORING.md` | definition | Two-sided legibility; scope, then zoom; `check` is the one threshold | maintainer | Applied 2026-09-24 (see note) | Figures failing `check` at any target: 29 → 0 new; figures redone for cramming: 3 → 0 |
| P0-2 | P0 | `AGENTS.md`, `docs/decisions.md`, `.claude/settings.json`, repo setting | definition + permission | Merge commits, new branch per PR, no force-push | maintainer | Decided; text applied 2026-09-24; permission and repo setting open | Force-pushes: ~6 → 0; squash merges by the agent: 12 → 0; stop-hook unpushed warnings: 2 → 0 |
| P0-3 | P0 | `selftest.py`, `AGENTS.md` | tool config + definition | Effect test per external setting; a real figure before "done" | auto + maintainer | Applied 2026-09-24: text, then a read-back of every setting (see note) | Toolkit bugs found after merge: 5 → ≤1; settings with an effect test: 3 of 8 → 8 of 8 |
| P1-1 | P1 | `.github/workflows/shots-check.yml` | CI | `check` on PRs that change images | maintainer | Proposed | Image PRs merged without `check` in CI: all → 0 |
| P1-2 | P1 | `AGENTS.md`, `CLAUDE.md`, `docs/` | layout | One instruction file; records beside the code | auto | Applied | Instruction files found by the collector: 0 → 1; earlier AARs found: 0 → 2 |
| P1-3 | P1 | skill collector | tool config | Read `queued_command`; wider correction pattern | skill maintainer | Proposed | Steering messages counted: 0 of 8 → 8 of 8 |
| P2-1 | P2 | chapters 7–8, weeks 01/07/08 | content | Dated captions; retakes | maintainer | In progress: 2 of 11 ch-07/08 figures retaken, 1 of 3 captions dated (see note) | Captions flagged: 3 → 0; figures over the limit: 29 → 0 |
| P2-2 | P2 | `docs/plans/` | plan | Computed outputs | maintainer | Proposed | Plan decided, yes or no |

### Resolution notes

**2026-09-24: P0 text applied at the maintainer's request.**
- **P0-1.** Applied to `AGENTS.md` ("Figures and screenshots") and to the course repository's `slides/common/AUTHORING.md` ("How much a screenshot shows"), in a changed form. The proposal said `check` "gives the slide width to use", but `check` has no such output. It measures text size at each target the recipe names, and fails text under 11 pixels in the book, 16 on a 1920-pixel slide, or 6 points in print. The applied text describes that. `AUTHORING.md` keeps W/1680 as a starting point for a page's own text, notes that DevTools needs more, and names `check` as the judge.
- **P0-2.** `AGENTS.md` gained "Git and Pull Requests". It adds one rule from `docs/decisions.md` that the proposal lacked: merge only when the maintainer asks, and never merge a student's pull request. Still open: the permission rule that denies force-pushes (untested), and GitHub's automatic deletion of merged branches.
- **P0-3.** `AGENTS.md` gained the "done" rule for `tools/shots` changes. Still open: effect tests for the DevTools layout preferences (Styles split, overview, columns).

**2026-09-24, later: P0-3's effect tests, and the Chrome for Testing notice.**
- **Every setting is read back.** Each headed take now reads DevTools' own page for what it drew, records it, and `capture` reports any difference from the recipe. The selftest checks each setting, 68 of 68 in all. The metric was "settings with an effect test: 3 of 8 → 8 of 8". Every setting the toolkit sends to Chrome or DevTools now has one, listed in the table under "Headed figures" in `tools/shots/README.md`.
- **The read-back found a bug on its first run,** the kind §5.2 predicts. `sidebar: hidden` set the Styles pane's size for only one layout, so in a narrow pane that DevTools stacked, the pane took 325 pixels and squeezed the tree. DevTools 154 can't hide the pane at all. `hidden` now means "at its smallest" in both layouts, and the README says so.
- **The maintainer found a banner the checks had missed.** Chrome for Testing's "only for automated testing" notice appeared in three chapter 8 figures and one week-8 slide, all made by scripts before the toolkit. The toolkit had it off only because Playwright passes `--disable-infobars` by default. The switch is now explicit, and a guard fails any headed take with an infobar. `network-tab-json` and `xkcd-inspect` were retaken within 800×600, with text at 13.4 pixels in the book. That counts toward P2-1. The Selenium figure keeps the notice, because the notice is its subject.

## Appendix A — Design sketch: why each part exists

```
recipe (YAML per chapter)
  → capture: headless page, or a headed browser on a virtual display, driven with real input
  → guards: HTTP status, block and challenge pages, expected text, a blank image
  → take: PNG + JSON log (URL, time, browser, User-Agent, crop, anchors, text sizes)
  → annotate: numbered markers from measured anchors (vector PDF; a PNG laid over the untouched pixels)
  → legibility: text size where shown (book, slide, print); a soft cap on the region
  → promote: copy into images/ch-NN/, with provenance.json and an IMAGES.md table
  → check: hashes, recipe drift, markers, legibility, alt text, dated captions
  → sheet: every take drawn at the size it will be shown
```

- **The recipe is the source, and the image is a build product.** Without that, nothing can be made again, which was the earlier AAR's first finding.
- **Measure, don't type pixels.** Anchors and text sizes come from the live page at capture time, so a retake re-places everything.
- **Guard before keeping a take.** An error page that looks like a page is the most common silent failure in web captures.
- **Provenance travels with the image.** It is what lets a reviewer, or CI, trust a file they didn't make.
- **Each rule has a check.** A rule with no check was broken in this sprint as soon as it was written.
- **One honest identity**, set in one place, and read back to confirm it (§5.2).

## Appendix B — Porting checklist: settings specific to this book

| Setting | Where | This book's value |
|---|---|---|
| User-Agent and contact | `tools/shots/lib/recipes.py` `DEFAULTS["user_agent"]` | `Web Data Science/v1 brian.keegan@colorado.edu`; replace with your own |
| Pacing and retries | `recipes.py` `DEFAULTS["pause"]`, `["retries"]`; `lib/capture.py` `BACKOFF` (`SHOTS_BACKOFF`) | 8–30 s; 30/60/120 s |
| Window, scale, soft cap | `recipes.py` `DEFAULTS["window"]`, `["scale"]`; `lib/legibility.py` `SOFT_LIMIT` | 800×600 at 2× |
| Display targets | `lib/legibility.py` `BOOK_PX`, `SLIDE_PX`, `SLIDE_TEXT`, `THRESHOLDS`; `lib/annotate.py` `BOOK_WIDTH_IN` | 778-px column; 1920-px slides, 16:9 beamer text width; 11 px / 16 px / 6 pt |
| Marker style | `tools/shots/styles/shotmarkers.sty`; `annotate.py` `MARKER_PT` | the course handouts' 11-pt markers |
| Paths | `lib/env.py` `ROOT`, `RECIPES`, `OUT`, `IMAGES` (`SHOTS_*` variables) | `images/ch-NN/`, `recipes/ch-NN.yml` |
| Figure markup | `shots.py` `figure_block` | Quarto `![caption](images/ch-NN/f.png){#fig-… fig-alt="…"}` |
| Browser and DevTools | `lib/env.py` `chrome_path()`, `CHROME_VERSION`; `lib/devtools.py` preference keys | Chrome for Testing 154. The keys change between versions: re-verify them (§5.2) |
| Proxy | `lib/env.py` `proxy()`, loopback bypass | the session's egress proxy |
| Block-page guards | `lib/guards.py` `BLOCK_PATTERNS` | Cloudflare, "Access denied", Wayback errors |
| Course copies and notebook links | `recipes/course.yml`; `tools/make_notebooks.py` `BOOK_URL` | the course repo; the published book URL |
| Setup | `tools/shots/bootstrap.sh` | Python venv, Chrome for Testing, Xvfb, xdotool, ImageMagick, fonts, TeX for markers |
