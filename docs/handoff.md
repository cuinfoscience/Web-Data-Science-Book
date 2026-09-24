# Hand-off note

**Updated 2026-09-24**, after textbook #148–#152 and courses #55 and #56 merged, and after the maintainer's decisions on the User-Agent, the Python version, and students' pull requests. This note describes the present state. Rewrite it when a session stops or the state changes, and don't let it grow into a history. History lives in git, in [`decisions.md`](decisions.md), and in the AARs.

## Where things stand

- **Screenshot toolkit, `tools/shots`.** Milestones M1–M3 are merged (#135–#137). Since the chapter 5 pilot:
  - every setting the toolkit sends to Chrome or DevTools is read back and tested (AAR P0-3);
  - headed captures run without Chrome for Testing's infobar, and a guard fails any take that shows one;
  - every recipe figure has a `brief:`, and `tools/shots/README.md` ("Making a figure, start to finish") goes from the brief to a merged pull request;
  - the size limit has two tiers: 800×600 by default, and up to 1024×768 when the extra room removes clutter and the text still passes;
  - the README's "Field notes" record what the captures taught (#150), and `doctor` reads each host's robots.txt for the course's User-Agent, listing groups for Claude's agents as a note;
  - `tools/make_notebooks.py` reads brackets inside code spans in captions, and fails when a figure or `@fig-` reference is left unconverted (#151).

  The selftest passes 73 of 73. `check` reports 0 errors and 8 warnings: six in chapter 7 (five figures over the size limit, one undated caption), and two in chapter 8 (the Selenium and codegen windows, which need M4).
- **Chapters.**
  - ch-01: the setup works as written (#152). Jupyter installs into `webdata`, terminal commands are shell blocks, and the first request sends a User-Agent.
  - ch-04 has three figures from the back-fill and fixes for #84, #87, and #132 (#149). Figure 4-2 (Open-Meteo's JSON) is left out; see the table below.
  - ch-05 has four DevTools figures from the pilot (#138).
  - ch-08: its View Source and JavaScript off/on figures are within the size limit, and the Selenium caption is dated (#142, #148). §8.3 checks Selenium Manager before the first browser (#143).
- **Decisions on 2026-09-24** ([`decisions.md`](decisions.md)): robots.txt is read for the course's User-Agent, and examples send one; the book recommends Python 3.14; students' pull requests merge after a code-review standup in class on a Friday.
- **Contributors.** `CONTRIBUTING.md`, a pull request template, and issue forms that point to it (#146). The README acknowledges the AI tools used to write the book (#145).
- **Project records.** `AGENTS.md` and `docs/`: the AARs, the plans, the decision log, and this note.
- **Course repository.**
  - Course #55 is merged: week 4's figures for the RSS handout and slides, Jupyter in week 1's setup, and `AUTHORING.md`'s notes on copies and the field notes.
  - Course #56 merged alongside this note's pull request. It adds the roadmap for the Friday code review (`docs/plans/2026-09-24-friday-code-review.md`) and the merge rule in the revision framework, the pull request walkthrough, and week 4's FAQ. It also puts Python 3.14 in week 1's setup and gensim from conda-forge in week 7's deck.

## Next

In this order:

1. **The first Friday code-review standup** for students' pull requests, on the course's roadmap ([plan](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/docs/plans/2026-09-24-friday-code-review.md)). Before it, prepare the plan's review table: every open student pull request with its chapter, the issue it fixes, its checks, and any conflict or duplicate.
2. **Back-fill chapters 1–3** in the [plan](plans/2026-09-24-screenshot-backfill-ch01-05.md)'s order (§4): ch-01, ch-02, ch-03.
   - ch-01: 1-1 and 1-2 can be made now that Jupyter installs into `webdata`. 1-3 pairs the article with View Source, as a composite. 1-4 (the pageviews API in Chrome's JSON view) got 429 from Wikimedia on the session's first request: the shared cloud address was over Wikimedia's limit. Try once later, or capture it from another network.
   - Each chapter is a textbook and course pair of pull requests, and each figure starts from its brief.
   - `shots import`, for hand captures such as week 1's issue form, isn't built (M4).
3. **Retake the chapter 7 figures** (AAR P2-1): five are over the size limit, and `x-com-1999`'s caption lacks a date. On 2026-09-24 web.archive.org reset every connection after about 11 seconds; retry. Chapter 8's two tool windows wait for M4.
4. **Toolkit M4** ([plan](plans/2026-09-24-screenshot-toolkit.md), §8): evidence queries for counts in captions (AAR P1-2), `sync` and `import`, the Selenium and codegen engines, and the `shots-check` CI job (AAR P1-1).
5. **Align the chapters' User-Agent strings** with `WebDataScience/1.0 (your-email@colorado.edu)`, after the Friday review.
   - Students' #88 and #93 add one to chapter 4's requests.
   - Chapter 7's three top-level requests (Availability, the raw capture, CDX) send none, and week 7's deck copies them. Change the chapter and the deck together, so the slides match the notebook.
   - The course's week 11 deck calls keyed APIs (Census, FRED, FEC) without one. Week 1's setup handout and week 10's deck already send one (course #56 fixed week 1).
6. **The course side of the contributor docs.** `handouts/common/revision-framework.md` and week 1's deck still name `claude.md`, now `AGENTS.md`, and the handouts say pull requests have no form.
7. **Computed outputs.** If they are adopted, run the [plan](plans/2026-09-24-computed-outputs.md)'s M0 pilot on chapter 5.

## Waiting on the maintainer

| Item | What to decide |
|---|---|
| Notebook sync on browser edits | A pull request edited in GitHub's browser editor can't regenerate its notebook, so the Notebook sync check fails. Either let CI regenerate the notebooks on pull requests (a workflow change), or keep the check and have the maintainer regenerate before merging, for example after the Friday review. `CONTRIBUTING.md` describes the second. |
| Figure 4-2 and Open-Meteo | api.open-meteo.com's robots.txt disallows every path, the course's User-Agent included, so the back-fill left out figure 4-2, the forecast in Chrome's JSON view. Chapter 2 says robots.txt addresses crawlers, and that deliberate API clients follow the API's own terms. Capture 4-2 as an API client, or leave it out. Either way, Step 5 of chapter 4's exercise sends students to the same API after Step 1 taught them to check robots.txt, so it could point back to chapter 2's distinction. |
| AAR P0-2 | Enable the permission rule that denies force-pushes (untested; test it first). Turn on "Automatically delete head branches" in both repositories. |
| AAR P1-1 | The `shots-check` CI workflow, part of M4. |
| AAR P1-3 | Fix the review skill's session collector. This belongs to whoever maintains the skill, not this repository. |
| Computed outputs | The four questions in the plan's §9. |
| Chapters 1–3 back-fill | <ul><li>Week 01's look-alikes (`issue_form.png`, `pr_review.png`): use a real public issue and pull request that aren't a student's, or capture them by hand.</li><li>The unused placeholders (week 02's four, week 03's `ad_observatory`, week 05's `dev_tools_network`): delete or keep.</li><li>Figure 1-1: should it replace `anaconda_jupyter.png` in `setup.md`?</li></ul> |

## Known issues

- **Students' pull requests.** About 40 are open; they merge after the Friday code review.
  - Four conflict with `main` since #149 and #152 merged: #52 (chapter 1), and #88, #89, and #93 (chapter 4). #88 and #93 make the same change. Resolving a conflict is a good demonstration for the review.
  - Most were made in the browser, so they fail Notebook sync (see the table above).
  - Six come from a fork's `main` branch. There, every later commit joins the open pull request, and two of them share one set of changes. `CONTRIBUTING.md` now asks for one branch per pull request.
  - #92 is the fix for issue #90, which a commit message in #149 closed by mistake; it was reopened.
- **Merged branches that the session could not delete.** The cloud session's git proxy refuses branch deletion with HTTP 403, so these remain. Delete them by hand, or turn on automatic deletion so they stop piling up.
  - **This repository, merged into `main`:**
    - earlier work: `add-ci`, `ch06-strategy-framework`, `fix-notebook-drift`, `fix-oscars-403-headers`, and the head branch of #53, a student's pull request merged on 2026-09-04;
    - chapters: `claude/ch01-setup-fixes`, `claude/ch04-figures`, `claude/ch04-refresh-live-data`, `claude/ch04-rss-directory-links`, `claude/ch04-rss-starter-feeds`, `claude/ch04-swap-rss-links`, `claude/ch05-protocols-expansion`, `claude/ch05-protocols-terminal-tools`, `claude/ch07-wayback-background`, `claude/ch08-retakes`, `claude/ch08-selenium-manager-playwright`, `claude/ch08-selenium-preflight`;
    - the toolkit: `claude/pilot-ch05`, `claude/shots-toolkit-m1`, `claude/shots-toolkit-m2`, `claude/shots-toolkit-m3`, `claude/shots-devtools-effect-tests`, `claude/shots-relaxed-limit`, `claude/shots-field-notes`, `claude/notebook-figure-brackets`;
    - docs: `claude/docs-agents-md`, `claude/aar-p0-edits`, `claude/lift-pause-pilot-gate`, `claude/readme-ai-acknowledgement`, `claude/contributing-guide`, `claude/handoff-after-merges`, and this note's own branch, `claude/decisions-ua-python`, once it merges.
  - **This repository, closed without merging:** `claude/decisions-ua-python-review` (#153). This note's pull request replaced it with the same changes, because the message of #153's first commit quoted a closing keyword with #90's number: merged, it would have closed #90 again.
  - **The course repository, merged into `main`:** `add-slides-ci`, `claude/detrope-week02-images`, `claude/week-01-screenshots-2aiqhh`, `claude/week-02-expansion`, `claude/week-04-rss-feeds-handout`, `claude/wk02-fixes`, `fix-oscars-403-headers-slides`, `overleaf-2026-08-24-0430`, and `overleaf-2026-08-24-0500`.
  - **The course repository, closed without merging:** `claude/swartz-ca-frames` (#23). Delete it only if #23 won't be revived. GitHub can restore it from the closed pull request.
  - **Keep:** `main`, `gh-pages`, every branch with an open pull request (students' included), and the course session's branch, `claude/info-4617-fall-2026-syllabus-07ahb8`.
- **Contributor docs that still disagree.** Found by #146's audit and left for later:
  - **User-Agent:** the chapters use six User-Agent strings; `decisions.md` now names the pattern for examples, and aligning them is item 5 of "Next".
  - **Exercises:** the revision framework invites starter cells, rubrics, and expected output; `AGENTS.md` rules out solutions and scaffolds.
  - **Common Issues:** ch-15 has no Common Issues section, though the "common issue" revision type assumes one.
  - **Length:** five chapters run past 7,000 words, against a target of about 3,000.
- **Course CI.** On course #51, the week-7 and week-8 deck builds sat in "Install TeX Live" (apt) for more than 30 minutes. That pull request changed neither deck, and it merged at the maintainer's instruction. The build on `main` after the merge passed. If the stall recurs, cache the TeX install, or build inside a TeX Live container.

## Hands off

- Chapter 6 and course week 6: leave them untouched (maintainer's instruction).
- Students' branches and pull requests: never merge, edit, or rebase them. The maintainer merges them after the Friday code review.
- Issues a student's open pull request already fixes: leave the fix to it. On 2026-09-24 a chapter 4 fix for #90 had to be withdrawn because #92, the reporter's own pull request, already fixed it. Check the issue's linked pull requests and the open ones on that chapter first.
- Closing keywords: write "fixes #N", "closes #N", or "resolves #N" only where the change fixes #N. GitHub reads them anywhere in a commit message that reaches `main`; "already fixes #90", in a sentence about #92, closed #90. A quotation counts too, so search a branch's commit messages before merging it.

## Notes for cloud sessions

- Don't retry the branch-deletion refusal (HTTP 403). List the branches here instead.
- Don't run `playwright install`. The toolkit uses Chrome for Testing through `tools/shots/bootstrap.sh`, and the container already has Chromium.
- Before a capture, read the "Field notes" in `tools/shots/README.md`, and add to them what the capture teaches.
- HTTPS goes through the session's proxy. Never turn off TLS verification. Captures through the proxy use HTTP/1.1, and captions that show protocol details say so.
- Quarto isn't installed system-wide. Download a release into the session's scratch directory. The computed-outputs tests used 1.10.18.
- The clone may be shallow. Before auditing what changed and when, run `git fetch --unshallow origin`: a shallow clone shows its oldest commit as the whole repository arriving at once.
- **Merging several pull requests that touch the same files.**
  - Rehearse the merges first in a scratch worktree (`git worktree add --detach … origin/main`). Then merge `main` into each branch in turn, never rebasing.
  - A merge's "ours" and "theirs" swap between a rehearsal (`main` checked out) and the real merge (the branch checked out). Take the resolved files from the rehearsal's commit; don't rerun a script that picks sides.
- A clone may track only `main`. Fetch other branches by full refspec: `git fetch origin "+refs/heads/<branch>:refs/remotes/origin/<branch>"`.
