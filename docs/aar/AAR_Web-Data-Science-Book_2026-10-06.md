# After-Action Report: weeks 7 and 8, and the review pass on students' pull requests, 2026-09-25 → 2026-10-06

Written for the maintainer and for the agents who continue the book and the course. It follows up [the `tools/shots` sprint's AAR](AAR_Web-Data-Science-Book_2026-09-24.md). Each gap in §5 names the property of the instructions, tools, or settings that let it happen, so that §6 can change that property.

## 1. Summary

In twelve days, agents shipped course weeks 7 and 8 and their chapters. A second session ran a review pass that merged 16 students' pull requests. The merging itself went cleanly: 67 pull requests merged across the two repositories, every one with a merge commit, and no agent force-pushed. What cost the instructor most was **material pitched past its reader**. Of the instructor's 55 messages in the session, 16 corrected the depth of a section or the starting point it assumed:
- week 8's setup material was rebuilt twice in a day: from a PDF of code to copy, to a second notebook, to a page that leads to the chapter's own notebook;
- four sections of chapter 8 were stubs or skipped a step;
- week 7's Friday slides were "far too much and too complicated", and the instructor's own edits cut what the agent had added to two decks.

The next costs, in order:
- **code that was never run**, the earlier AAR's §5.7, never acted on: the instructor's error in week 7's first cell, seven students' pull requests that fixed examples that failed when run, and five errors that the review pass found on `main`;
- **generated notebooks that drift on `main`**: Notebook sync failed 20 of its 46 completed runs, and `main` drifted three times on one morning;
- **who can merge**: five students' changes reached `main` without review, and two had to be reverted.

The three highest-leverage revisions:
- **P0-1:** state in `AGENTS.md` the reader's starting point (Anaconda as installed, no terminal, the browser editor), and what a section owes that reader;
- **P0-2:** run every cell you add or change before the pull request, with a small tool that compares what it prints with its output comments;
- **P0-3:** regenerate the notebooks on `main` after each merge, and fail a pull request only when it edits `notebooks/` directly.

## 2. Scope reviewed

- **Window:** 2026-09-25 → 2026-10-06, three sprints:
  - **week 7** (09-25 → 10-02): chapter 7's retakes, week 7's slides, the first Friday code-review standup and its three handouts;
  - **week 8** (10-02 → 10-06): chapter 8's logged-in browsing, headless mode, Playwright, and setup; week 8's slides and setup page; follow-ups on chapters 5 and 8;
  - **the review pass** (10-06): another session reviewed every student's open pull request on chapters 1–7, merged 12 low-risk ones, and fixed what the reviews found. The maintainer merged four more.
- **Evidence:**
  - Textbook: 96 commits (46 non-merge, +3,060/−720 lines); 45 merged pull requests (24 by agents, 19 by students, 2 by the maintainer) and 11 closed without merging.
  - Course: 54 commits (30 non-merge, +4,700/−1,969); 22 merged pull requests, all by agents.
  - CI: 59 Notebook sync runs, 55 Render, 47 Publish, and 10 screenshot checks in the textbook; 51 slide builds and 28 handout builds in the course.
  - One Claude Code session in this container, compacted 44 times in the window: 55 messages from the instructor, 16 of them sent mid-turn; 1 interrupt; 59 tool errors.
  - The review pass ran in another session (`session_01RVz3AfLXeoPTBDSMMi29rP`), whose transcript is not on this machine. Its evidence is its five pull requests (#223–#227), their descriptions, and the hand-off it updated.
  - Not available: GitHub review comments, since review happens in the sessions and in pull request descriptions. PR and CI data came from GitHub's REST API.
- **Earlier AAR:** [`AAR_Web-Data-Science-Book_2026-09-24.md`](AAR_Web-Data-Science-Book_2026-09-24.md), with resolution notes through 2026-10-05.
- **Rigor level:** standard, as before. These are shared teaching materials, the instructor reviews every agent pull request, and about 40 students use the output.
- **Intent baseline:**
  - the textbook's `AGENTS.md`, `CONTRIBUTING.md`, and `docs/decisions.md`;
  - the course's `slides/common/AUTHORING.md` and `handouts/README.md`. The course has no `AGENTS.md`, so the collector found no instruction file there (§5.5);
  - the instructor's requests in the session.

## 2a. Follow-up on earlier revisions

| ID | Earlier action | Applied? | Recurred? | Verdict |
|---|---|---|---|---|
| P0-1 | Legibility at both ends; one threshold source | Yes | No. None of the 55 messages is about text size, and the window's new figures (week 8's handout, week 7's handouts) pass `check`. | Worked; keep |
| P0-2 | Merge commits, a new branch per pull request, no rewritten history | Text: yes. Automatic branch deletion: on in the textbook, off in the course. The force-push permission rule: no; the textbook has no `.claude/settings.json`. | Not by agents: 40 merge commits on the textbook's `main`, 0 squashes, 0 force-pushes (was 12 and about 6). But 59 merged branches wait to be deleted, and the course's `AUTHORING.md` still says to rebase. | Worked for agents; the rest carried into P1-1 and P1-2 |
| P0-3 | Read back each external setting; a real figure before "done" | Yes (68 effect tests) | One new class: outputs that change when their inputs don't (PDF dates, #220; `sync`'s record time, #221). The agent found both in its own output, before the instructor did. | Worked; close |
| P1-1 | CI re-checks image provenance on pull requests that change images | Yes, 09-25 | 10 runs; no image pull request merged without it | Worked |
| P1-2 | One instruction file; records beside the code | Yes | The collector found `AGENTS.md`, `CLAUDE.md`, and both earlier AARs | Worked in the textbook; the course has no instruction file (P1-2 below) |
| P1-3 | The session collector reads mid-turn messages | No; the skill is unchanged | Yes: it counted 2 of 55 instructor messages | Carry forward as P1-3 |
| P2-1 | Dated captions; retakes | Done, except three screenshots that need the maintainer | — | Carry forward (P2-3) |
| P2-2 | Computed outputs in the book build | Not decided | The pattern it was meant to fix recurred, at high cost (§5.2) | Superseded in part by P0-2, which needs no decision; the plan's own questions stay open |

## 3. What the agent was supposed to do (Q1)

- **The reader** (`AGENTS.md`): "Advanced undergraduates and early-career master's students with some Python experience. They know loops, functions, lists, and dictionaries, but may not have experience with web protocols, APIs, or HTML parsing."
- **Code** (`AGENTS.md`): narrative cells with `eval: false` ("students run code themselves"), and "expected output as comments where it helps comprehension". Every live request sends the reader's User-Agent. Chapter 1 builds `webdata` with every library the chapters import.
- **Earlier chapters** (added 10-05): when a later chapter adds an example that an earlier one would benefit from, the same pull request adds a pointer there.
- **Git** (`AGENTS.md`, `decisions.md`): merge commits only; merge only when the maintainer asks. Students' pull requests merge after the Friday standup or, since 10-06, in a review pass the maintainer asks for.
- **Notebooks** (`AGENTS.md`, `CONTRIBUTING.md`): edit the `.qmd`, then run `tools/make_notebooks.py`. CI checks the notebooks on pull requests.
- **The course** (`AUTHORING.md`): Overleaf pushes to `main` without warning, so "start from fresh `origin/main` … rebase rather than fight". A frame the instructor rewrote is a review comment. On 10-06, `handouts/README.md` gained "A setup page", which begins "Start where students are."
- **The sprints' goals:** week 7's archive chapter and its first Friday standup; week 8's logged-in and headless browsing, Selenium Manager, Playwright, and a setup handout; a review pass that merges low-risk student work and fixes what it finds.

## 4. What actually happened (Q2)

- **Week 7.**
  - Chapter 7's five figures were retaken within the size limit (#161), and week 7's slide screenshots were remade (course #62).
  - On 09-30 the instructor hit an error in week 7's first notebook cell. archive.org's Availability API answered 429 with an HTML page, and `response.json()` raised `JSONDecodeError`. Students' #192 and #203 later went after the same cell, and #191 and #198 after the chapter's other archive requests.
  - On 10-02 the instructor asked for more scaffolding in chapter 7's bag-of-words section. The stopword list became a text file, `webdata` gained every library the chapters import, and chapter 5 dropped scapy (`decisions.md`, 10-02).
  - The Friday standup got a review table (course #60), slides, and three handouts. The handouts were written as Markdown and converted to LaTeX PDFs at the instructor's request (course #73). The instructor called the slides "still far too much and too complicated" and asked for step-by-step guidance for students who edit in the browser. His Overleaf edit then cut 12 lines from the frames.
- **Week 8.**
  - Chapter 8 gained logged-in and headless browsing (#216). Its Playwright commands (#217) and its advice on Chrome's sandbox (#218) were corrected the same day.
  - The setup handout was a four-page PDF of screenshots and code (course #78, 10-05). On 10-06 the instructor wrote: "I don't understand the week 08 handout at all … why students are being asked to copy code from a PDF into a Jupyter Notebook." A pre-class notebook followed, then: "Revised notebook still not adequate … Restart from scratch. You are a 20-year-old information science student with a tenuous understanding of the technical stack of terminals, package management, etc." The final form is a page that leads to chapter 8's own notebook, which gained an install cell (#222, course #80).
  - The same afternoon the instructor found four thin spots in chapter 8: two stub sections (8.8, 8.9), a list of locator strategies with no definitions (8.4), and a Network-tab check with no bridge to a scraper (8.2.3). #222 and #229 fixed them, and #230 fixed a wrong claim in chapter 5 that #229 had exposed.
  - The instructor's Overleaf edit of week 8's Monday deck deleted 36 lines, including an environment-variable fix and a whole frame on why Playwright's sync API fails in a notebook.
- **The review pass (10-06).**
  - The session reviewed every student pull request on chapters 1–7. It merged 12 of them between 04:41 and 04:47 and closed 10 that had nothing to merge. The maintainer merged #80, #116, #131, and #179.
  - #223 regenerated the notebooks that those merges had left stale, and recorded the merge rule. #224 fixed five errors on `main`, and #225 the User-Agent of chapter 6's Oscars example. #226 made the reviews' notes on #80 and #131. #227 listed 59 merged branches the session could not delete.
- **Merges and settings.**
  - Students merged three of their own pull requests (#54 on 10-02, #214 and #215 on 10-05). Two other students' changes went straight to `main` through GitHub's editor on 09-25, and #193 reverted them on 10-02.
  - The textbook's ruleset on `main` requires a pull request, with 0 approvals, and allows squash and rebase merges.
  - Overleaf pushed to the course's `main` on 10-02 and 10-05. On 10-02 the instructor had to point out a race with the session's branch twice.
- **CI.** Notebook sync failed 20 of 46 completed runs (43%). Of the 20, 14 ran on branches in the repository, two of them agents' on 10-06, and 6 came from forks. Render failed 6 of 44, the screenshot check 1 of 10, and the course's slide builds 2 of 51.
- **The session.** It was compacted 44 times. Of its 59 tool errors, 27 were edits to a file not read since a compaction. On 10-06 `main` moved under two merges (#222, course #82). Both times the session merged `main` into the branch, waited for CI, and merged the new head.

## 5. Gap analysis (Q3)

### 5.1 The reader's starting point was assumed, not stated

**Observation.** 16 of the 55 messages, in three groups:
- **Where the reader starts.**
  - "Ensure there is a pathway in the handout to use selenium manager without activating the webdata environment" (10-05).
  - "Assume a student who has not configured or activated the class `webdata` environment. Proceed from a vanilla Anaconda install" (10-06).
  - "You are a 20-year-old information science student with a tenuous understanding of the technical stack of terminals, package management, etc." (10-06).
  - An audit of the libraries `webdata` needs, and dropping scapy because its `sudo` install "sets a bad example" (both 10-02).
- **Where code lives.**
  - Code copied from a PDF into a notebook (10-06).
  - A second notebook that repeated the chapter's: "a lot of this material is already in the ch08 notebook" (10-06).
  - Week 7's handouts converted from Markdown to annotated PDFs (10-02).
- **How deep a section goes.**
  - Chapter 7's bag-of-words section "needs more scaffolding" (10-02).
  - Week 7's Friday slides were "far too much and too complicated" (10-02).
  - In chapter 8 (all 10-06): two stubs (8.8, 8.9); strategies listed but not defined (8.4); a missing bridge from the Network tab to a scraper (8.2.3 → 8.3); code whose scope wasn't stated (8.9).

The instructor's own edits removed what the agent had added to slides: 48 lines cut and 10 added, across two decks. Week 8's setup material took three forms in 24 hours, and the first of them had already merged.

**Root cause: ambiguous, with a missing piece.**
- `AGENTS.md`'s audience line says what readers know. The agent filled the rest with what the course's environment provides: `webdata` activated, a terminal, a working Selenium. Nothing says that readers start from Anaconda as installed, rarely use a terminal or conda, edit the book in GitHub's browser editor, and run code only in Jupyter.
- Nothing says what a section owes its reader. No rule rejects a section that is a heading and one cell, and none asks example code to say what it fits. Chapter 6's Strategy 6 does that as a habit, not a rule.
- The guidance that worked, `handouts/README.md`'s "A setup page" ("Start where students are"), was written on 10-06 and only for the course. The book has no counterpart, and the slides' guide says nothing about how much a frame carries.

### 5.2 Code that was never run (the earlier §5.7, again)

**Observation.**
- The instructor's `JSONDecodeError` in week 7's first cell (09-30).
- Seven merged student pull requests that fixed examples that failed or misbehaved when run:
  - a 403 (#188);
  - a page parsed before it was fetched (#179);
  - a `NameError` (#210);
  - truncated text that skewed similarity scores (#202);
  - `Retry-After` ignored (#116);
  - no timeout, so a request could hang (#126);
  - an undefined `responsible_get` (#131).

  Two more students went after chapter 7's first cell (#192, #203).
- The review pass's five errors on `main` (#224): two requests without a User-Agent, both answered 403; stale expected output; a wrong description of the Oscars cards; and a stale selector that raised `AttributeError`. On top of these, the Oscars example sent the maintainer's own User-Agent (#225).
- Chapter 8:
  - a cell that called `driver.get()` on a driver the cell above had quit (#222);
  - Playwright commands that could run another environment's Python (#217);
  - advice that turned Chrome's sandbox off on readers' own computers (#218).

Where code was run before its pull request, nothing came back. Week 8's setup page and chapter 8's install cell were walked through in a stand-in Anaconda, as an ordinary user. #229's cells were run as written, and every printed line matched its comment.

**Root cause: missing.** `AGENTS.md` sets `eval: false` and asks for "expected output as comments", but no rule says the author runs the code first. No tool compares a cell's output with its comments. The earlier AAR proposed computed outputs (P2-2), a large change that waits on four decisions. The cheap part, running code before publishing it, needs none of them.

### 5.3 Generated notebooks drift on `main`

**Observation.** Notebook sync failed 20 of 46 completed runs. Students edit in the browser, which can't run `tools/make_notebooks.py`, so their pull requests fail by design. Whenever such a change merges, `main` itself drifts, and every open pull request fails a check that isn't its fault. That happened after #50, after the review pass's twelve merges, and after #80, #116, and #131; #222 had to wait. Agents spent two pull requests regenerating notebooks (#223, #226). On 09-25 the hand-off recommended a fix:
- regenerate the notebooks on `main`;
- make the pull request check informational;
- fail direct edits to `notebooks/`.

The fix waited on the maintainer while the problem recurred.

**Root cause: a missing mechanism.** The notebooks are generated but committed. The generator runs only when an agent remembers it, and the only check runs on pull requests. Prose can't fix this, because a browser edit can't run a script. It belongs in CI.

### 5.4 Students can merge their own work

**Observation.**
- Three students merged their own pull requests (#54, #214, #215).
- Two students' web-editor commits went straight to `main` on 09-25 (reverted in #193).
- The review pass then had to review changes that had already merged.

The ruleset on `main` requires a pull request with 0 approvals, and allows squash and rebase. The merge policy (merge commits; students' work merges after the standup) exists only as prose. On 09-25 the hand-off recommended a ruleset that requires one approval.

**Root cause: missing** (a repository setting).

### 5.5 The course's instructions are hard to find, and one contradicts the book's

**Observation.**
- The collector found no instruction file in the course repository. Its rules live in `slides/common/AUTHORING.md` and `handouts/README.md`.
- `AUTHORING.md` says to "rebase rather than fight" when Overleaf pushes, against the merge policy the textbook adopted on 09-24. No rebase happened this window, but the rule is still there for an agent to follow.
- Overleaf's pushes (10-02, 10-05) raced the session's branch, and the instructor raised the first one twice.
- Automatic branch deletion is off in the course repository.

**Root cause: buried and contradictory.**

### 5.6 A documentation edit rebuilds every deck

**Observation.** The instructor asked on 10-06: "Why is the CI rebuilding every slide deck?" `build-slides.yml` builds all 14 decks when anything under `slides/common/` changes, and `AUTHORING.md`, a guide that no deck includes, lives there.

**Root cause:** tool configuration.

### 5.7 A long session, compacted 44 times

**Observation.** 27 of 59 tool errors were edits to a file not read since a compaction; the last window had 11. The session's standing constraints survived its summaries, and git shows no rule broken after a compaction. The cost is time.

**Root cause: novel** to long sessions. A one-line note is enough.

### 5.8 The review tooling still misses most of the steering

**Observation.** The session collector counted 2 of the 55 instructor messages, as the earlier AAR's P1-3 predicted. 16 of the 55 came mid-turn, and most are observations ("I don't understand…", "Why is…") rather than corrections. This report's counts come from a hand-written extractor.

**Root cause:** the earlier P1-3 was not applied.

## 6. Recommended revisions (Q4)

### [P0-1] State the reader's starting point, and what a section owes them
- **Target:** `AGENTS.md` → "Editorial Voice and Style" (replace "Audience"; add "Depth"); course `slides/common/AUTHORING.md` (one line)
- **Root cause:** ambiguous + missing (§5.1)
- **Medium:** definition text, because each section needs judgment
- **Evidence:** 16 of 55 instructor messages; week 8's setup rebuilt twice in a day; 48 lines the instructor cut from two decks.
- **Change:** in `AGENTS.md`, replace the Audience bullet with:
  > - **Audience**: advanced undergraduates and early-career master's students in information science. They know Python's loops, functions, lists, and dictionaries, and they run code in Jupyter. Assume no more than that about their tools. They start from Anaconda as installed, with nothing activated; they rarely open a terminal or run conda; and they edit this book in GitHub's browser editor. When a step needs more (an install, an environment, a terminal command, a downloaded browser), show it in the notebook where it runs, and say what it prints when it works.

  Then add after it:
  > - **Depth**: a section that introduces a tool or a technique says what it is and why the task needs it, shows it working with real output, and connects to the next section. A section that is only a heading and a cell belongs inside its neighbor. Example code that fits one site says so, and says what carries over to others; Strategy 6 in chapter 6 is the model.

  In `AUTHORING.md`, after the rules on frames:
  > - **A frame carries what students need in the room.** Environment fixes, edge cases, and "why it fails" detours go to the chapter or a setup page, and the frame points there. The instructor's edits to weeks 7 and 8 cut exactly these.
- **Why it works:** the agent wrote for the reader the definition described, and that reader had a working environment. Naming the real starting point, in the instructor's words ("vanilla Anaconda", "a tenuous understanding of … terminals, package management"), and naming what a section owes, moves these corrections into the first draft.
- **Owner:** maintainer review · **Status:** Proposed

### [P0-2] Run every cell you add or change before the pull request
- **Target:** `AGENTS.md` → "Code style"; new `tools/check_cells.py`; one line in `.github/pull_request_template.md`
- **Root cause:** missing (§5.2)
- **Medium:** tool config for the comparison, which is mechanical; definition text for the rule, since which cells to run and which sites to call need judgment
- **Supersedes:** the urgent part of the earlier P2-2
- **Evidence:** 17 code errors found after merge (§5.2), and none in the cells that were run before their pull request.
- **Change:** add `tools/check_cells.py`. Given a chapter and a range of headings, it runs the `{python}` cells in order, in one fresh Python, and compares each printed line with the `# …` comment lines below the `print`. It reports mismatches and exceptions, and waits `--delay` seconds between cells that make requests. A prototype ran chapter 8's §8.4 on 2026-10-06: six cells, and every printed line matched. In `AGENTS.md`, add to "Code style":
  > Before a pull request that adds or changes code, run each changed cell as written, in a fresh environment built like chapter 1's `webdata`, with `tools/check_cells.py`. Make each output comment what the cell printed that day, and date it when it can change. Say in the pull request which cells ran, and where. If you couldn't run a cell, say why.
- **Why it works:** a comment that shows output is a claim, and nothing checked these claims. Every error in §5.2 was in a cell that no one ran before it merged.
- **Owner:** auto-applyable (tool); maintainer review (text) · **Status:** Proposed

### [P0-3] Regenerate the notebooks on `main`; fail only direct edits
- **Target:** new `.github/workflows/regenerate-notebooks.yml`; `.github/workflows/notebook-sync.yml`; the ruleset on `main`
- **Root cause:** a missing mechanism (§5.3)
- **Medium:** CI, because the rule is mechanical and has no exceptions
- **Evidence:** Notebook sync failed 20 of 46 runs; `main` drifted three times on 10-06; two agent pull requests did nothing but regenerate notebooks.
- **Change** (untested; test it before you enable it):
  ```yaml
  name: Regenerate notebooks on main
  on:
    push:
      branches: [main]
      paths: ["ch-*.qmd", "appendix-*.qmd", "tools/make_notebooks.py"]
  permissions:
    contents: write
  jobs:
    regenerate:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: {python-version: "3.11"}
        - run: python tools/make_notebooks.py
        - run: |
            git diff --quiet -- notebooks/ && exit 0
            git config user.name "github-actions[bot]"
            git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
            git add notebooks/
            git commit -m "Regenerate notebooks after ${GITHUB_SHA::7}"
            git push
  ```
  The ruleset on `main` must let GitHub Actions bypass it, or the push is refused. Then change `notebook-sync.yml` so that a pull request fails only when it edits `notebooks/` directly, as #117 did, and other drift shows as a notice.
- **Why it works:** the generator runs where every change lands, whoever made the change, so a browser edit no longer turns every other pull request's check red.
- **Owner:** maintainer review (ruleset and workflow) · **Status:** Proposed

### [P1-1] Require a review on `main`, and merge commits only
- **Target:** the ruleset "protect main"; a new `.github/CODEOWNERS`; both repositories' merge settings
- **Root cause:** missing (§5.4)
- **Medium:** repository settings
- **Evidence:** 5 unreviewed changes reached `main` (3 self-merges, 2 web-editor commits), and 2 were reverted.
- **Change:**
  - In "protect main", set `required_approving_review_count: 1`, `require_code_owner_review: true`, and `allowed_merge_methods: ["merge"]`. Keep the maintainer's bypass.
  - Add `.github/CODEOWNERS` with `* @brianckeegan`.
  - In both repositories, turn off squash and rebase merging (Settings → General).
  - In the course repository, turn on "Automatically delete head branches".
- **Why it works:** GitHub enforces the policy, so the standup becomes the merge point for students. The maintainer, and agents merging through the maintainer's bypass, are unaffected.
- **Owner:** maintainer · **Status:** Proposed. The hand-off has recommended it since 09-25.

### [P1-2] Give the course an instruction file, and reconcile its merge rule
- **Target:** new course `AGENTS.md` and `CLAUDE.md`; `slides/common/AUTHORING.md` → "Working alongside the instructor"
- **Root cause:** buried + contradictory (§5.5)
- **Medium:** definition text
- **Change:** a short course `AGENTS.md` that points to `slides/common/AUTHORING.md`, `handouts/README.md`, and the textbook's "Git and Pull Requests"; and a `CLAUDE.md` that imports it. In `AUTHORING.md`, replace "rebase rather than fight" with:
  > … assume more edits may land mid-branch. Before you open or merge a pull request, fetch `main` and merge it into your branch. Never rebase or force-push: the instructor's Overleaf may already hold the old commits.
- **Owner:** auto-applyable · **Status:** Proposed

### [P1-3] The session collector reads mid-turn messages (carried forward)
- **Target:** the `agent-after-action-review` skill's `scripts/collect_session_evidence.py`
- **Root cause:** not applied (§5.8)
- **Medium:** tool config
- **Change:** as the earlier P1-3 proposed. Treat a record with `type: "attachment"` whose `attachment.type` is `"queued_command"` as a human turn, with the text in `attachment.prompt`. Count messages that ask a question or report a problem, not only corrections.
- **Owner:** skill maintainer · **Status:** Proposed

### [P1-4] Check a response before parsing it
- **Target:** `AGENTS.md` → "Requests in code"
- **Root cause:** missing (§5.2)
- **Medium:** definition text
- **Evidence:** the instructor's `JSONDecodeError` (09-30); students' #192 and #203 on the same cell; #116.
- **Change:** append:
  > Check a response before you parse it: call `response.raise_for_status()`, or print the status when it isn't 200. A rate-limited API often answers 429 with an HTML page, and `.json()` on that page fails with a `JSONDecodeError` that hides the cause.
- **Owner:** maintainer review · **Status:** Proposed

### [P2-1] Build only the decks a change affects
- **Target:** the course's `.github/workflows/build-slides.yml` (§5.6)
- **Change:**
  ```diff
  - if [ -n "$BASE" ] && git diff --name-only "$BASE" HEAD -- 'slides/common/' | grep -q .; then
  + if [ -n "$BASE" ] && git diff --name-only "$BASE" HEAD -- 'slides/common/' ':!slides/common/*.md' | grep -q .; then
  ```
- **Owner:** auto-applyable · **Status:** Proposed

### [P2-2] After a compaction, read before you edit
- **Target:** `docs/handoff.md` → "Notes for cloud sessions" (§5.7)
- **Change:** "After a context compaction, the session no longer knows which files it has read. Read a file before you edit it."
- **Owner:** auto-applyable · **Status:** Applied in the pull request that adds this report

### [P2-3] Carry forward: three hand screenshots, and the computed-outputs decision
- The earlier P2-1's three screenshots wait for the maintainer, as the hand-off says. The computed-outputs plan's four questions are still open; P0-2 no longer depends on them.
- **Owner:** maintainer · **Status:** Deferred

### [P2-4] Write down the merge check that worked
- **Target:** `AGENTS.md` → "Git and Pull Requests"
- **Medium:** definition text
- **Evidence:** every merge in the window used a merge commit, and two races with `main` were caught on 10-06 (#222, course #82).
- **Change:** add:
  > Before a merge, pass the head that CI checked as the expected head, and check that `main` hasn't moved since the branch last merged it. If it has, merge `main` into the branch, and wait for CI again. After the merge, check that `main`'s tree is the tree of the head you merged.
- **Owner:** auto-applyable · **Status:** Proposed

## 7. Strengths to sustain

- **The merge procedure.** It merges `main` into a branch (never rebasing), passes the expected head, scans for closing keywords, and checks the tree after the merge. Every merge in the window used a merge commit, and no agent squashed, force-pushed, or closed an issue by mistake. Twice on 10-06, `main` moved between CI and the merge; both times the session merged `main` in and merged the new head. P2-4 writes the procedure down.
- **Walking it as a student.** The week 8 setup was tested in a stand-in Anaconda, as an ordinary user, with nothing activated. That found what the readers would have hit: Selenium couldn't find Selenium Manager, and conda-forge's two `playwright` commands clashed. #229's cells were run as written and compared line by line. P0-2 makes this the book's rule.
- **Facts from their sources.** Claims were checked against the W3C WebDriver standard, Selenium's own source (its locator converter), Chrome DevTools' source (its Copy menu), PyPI's release dates, and live APIs, always with the course's User-Agent and 8 seconds or more between requests.
- **Instructions became standing rules the same day.** "Always update earlier chapters" became item 7 of `AGENTS.md`'s "Extending the Book" (10-05). Nine decisions were logged in the window. "Start where students are" became a section of `handouts/README.md` (10-06).
- **The review pass.** Each fix was checked live. Overlaps with students' open pull requests were tested with `git merge-tree`. Risky pull requests were held for the maintainer, and the new merge rule was recorded before it was used. The pass found §5.2's errors on `main`, which is what a review pass is for.
- **Reproducible outputs.** Drawing with `SOURCE_DATE_EPOCH` ended the binary diffs that said nothing. Byte churn from redrawn figures went from 4 of 4 to 0.
- **The earlier P0-1.** Legibility held: no message about text size in the window.

## 8. Revision actions — tracking table

| ID | Pri | Target | Medium | Change | Owner | Status | Check next time |
|---|---|---|---|---|---|---|---|
| P0-1 | P0 | `AGENTS.md`, course `AUTHORING.md` | definition | Reader's starting point; what a section owes; frame density | maintainer | Proposed | Instructor messages correcting depth or starting point: 16 of 55 → ≤ 4; setup material rebuilt after merge: 2 → 0 |
| P0-2 | P0 | `AGENTS.md`, `tools/check_cells.py`, PR template | tool + definition | Run changed cells; compare output with comments | auto + maintainer | Proposed | Code errors found after merge (instructor, students' fixes, review passes): 17 → ≤ 3; agent PRs that change code and report a run: 1 → all |
| P0-3 | P0 | two workflows, ruleset | CI | Regenerate notebooks on `main`; fail only direct edits | maintainer | Proposed | `main` drifting from its notebooks: 3 times in a day → 0; Notebook sync failures: 20 of 46 → only direct edits |
| P1-1 | P1 | ruleset, `CODEOWNERS`, settings | repo setting | One approval; merge commits only; course deletes merged branches | maintainer | Proposed | Unreviewed changes on `main`: 5 → 0; merged branches left: 59 → 0 |
| P1-2 | P1 | course `AGENTS.md`, `CLAUDE.md`, `AUTHORING.md` | definition | Instruction file; merge `main` in, never rebase | auto | Proposed | Instruction files the collector finds in the course: 0 → 1; "rebase" advice in course docs: 1 → 0 |
| P1-3 | P1 | skill collector | tool | Read mid-turn messages | skill maintainer | Proposed | Instructor messages counted: 2 of 55 → all |
| P1-4 | P1 | `AGENTS.md` | definition | Check a response before parsing it | maintainer | Proposed | Student fixes for an unchecked response: 3 → 0 |
| P2-1 | P2 | course `build-slides.yml` | CI | Markdown in `slides/common/` builds no deck | auto | Proposed | Decks built for a docs-only change: 14 → 0 |
| P2-2 | P2 | `docs/handoff.md` | note | Read before editing after a compaction | auto | Applied 2026-10-06 | Edits refused for an unread file: 27 → ≤ 5 |
| P2-3 | P2 | course decks; computed-outputs plan | content, decision | Three screenshots; four questions | maintainer | Deferred | Screenshots taken: 0 of 3 → 3; plan decided: no → yes |
| P2-4 | P2 | `AGENTS.md` | definition | Write down the merge check | auto | Proposed | Merges that land a head CI didn't check: 0 → 0 |
