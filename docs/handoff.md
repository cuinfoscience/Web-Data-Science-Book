# Hand-off note

**Updated 2026-09-24**, after textbook #141–#146 and course #54 merged. This note describes the present state. Rewrite it when a session stops or the state changes, and don't let it grow into a history. History lives in git, in [`decisions.md`](decisions.md), and in the AARs.

## Where things stand

- **Screenshot toolkit, `tools/shots`.** Milestones M1–M3 are merged (#135–#137). Since the chapter 5 pilot (#142, #144):
  - every setting the toolkit sends to Chrome or DevTools is read back and tested (AAR P0-3, done);
  - headed captures run without Chrome for Testing's infobar, and a guard fails any take that shows one;
  - every recipe figure has a `brief:`, and `tools/shots/README.md` ("Making a figure, start to finish") goes from the brief to a merged pull request;
  - the size limit has two tiers: 800×600 by default, and up to 1024×768 when the extra room removes clutter and the text still passes.

  The selftest passes 73 of 73. `check` reports 0 errors and 11 warnings: 9 chapter 7–8 figures over the size limit, and 2 captions without a capture date.
- **Chapters.**
  - ch-05 has four DevTools figures from the pilot (#138).
  - ch-08: two DevTools figures were retaken within 800×600 (#142). §8.3 now checks Selenium Manager before the first browser, and covers Firefox, Edge, and Safari (#143).
- **Contributors.** `CONTRIBUTING.md`, a pull request template, and issue forms that point to it (#146). The README acknowledges the AI tools used to write the book (#145).
- **Project records.** `AGENTS.md` and `docs/` (#139–#141): the AARs, the plans, the decision log, and this note.
- **Course repository.** Course #54 is merged: week 8's Network screenshot without the banner, and `AUTHORING.md`'s no-banner rule and relaxed size limit. It pairs with textbook #142 and #144.

## Next

In this order:

1. **Back-fill chapters 1–4** in the [plan](plans/2026-09-24-screenshot-backfill-ch01-05.md)'s order (§4): ch-04, ch-01, ch-02, ch-03.
   - Each chapter is a textbook and course pair of pull requests.
   - Each figure starts from its brief, within 800×600, or within 1024×768 when that is clearer and still legible.
   - Chapter 1 needs a Jupyter server in the container.
   - `shots import`, for hand captures such as week 1's issue form, isn't built (M4). `adopt` records provenance, but it won't crop or redact.
2. **Retake the chapter 7–8 figures** (AAR P2-1), one chapter per pull request.
   - 9 figures are over the size limit, and 2 captions (`x-com-1999`, `selenium-chrome-for-testing`) lack a capture date.
   - The relaxed limit may fit `view-source-js`, which shows 1100×760 now.
   - `selenium-chrome-for-testing` and `playwright-codegen` need M4's Selenium and codegen engines.
   - 18 slide screenshots are over the limit too.
3. **Toolkit M4** ([plan](plans/2026-09-24-screenshot-toolkit.md), §8). It covers:
   - evidence queries for counts in captions (AAR P1-2);
   - `sync` to the course repository, and `import`;
   - the Selenium and codegen engines;
   - the `shots-check` CI job (AAR P1-1).
4. **The course side of the contributor docs.**
   - `handouts/common/revision-framework.md` and week 1's deck still name `claude.md`, now `AGENTS.md`.
   - The handouts say pull requests have no form. The textbook has a template now.
5. **Computed outputs.** If they are adopted, run the [plan](plans/2026-09-24-computed-outputs.md)'s M0 pilot on chapter 5.

## Waiting on the maintainer

| Item | What to decide |
|---|---|
| Who merges students' pull requests | `CONTRIBUTING.md` says the maintainer, matching the revision framework and `decisions.md`. Week 4's deck says students with write access can. Pick one, and the other document follows. |
| Notebook sync on browser edits | A pull request edited in GitHub's browser editor can't regenerate its notebook, so the Notebook sync check fails. Either let CI regenerate the notebooks on pull requests (a workflow change), or keep the check and have the maintainer regenerate before merging. `CONTRIBUTING.md` describes the second. |
| robots.txt rules for AI agents | The chapter 4 back-fill read a robots.txt group addressed to Claude's agents (`ClaudeBot`, `Claude-User`, and others) as applying to captures, though the browser sends the course's User-Agent. So chapter 4 has no Guardian or www.bbc.co.uk figure, and `doctor` now warns about such groups. Confirm the practice and it goes into `decisions.md`, or say otherwise. |
| AAR P0-2 | Enable the permission rule that denies force-pushes (untested; test it first). Turn on "Automatically delete head branches" in both repositories. |
| AAR P1-1 | The `shots-check` CI workflow, part of M4. |
| AAR P1-3 | Fix the review skill's session collector. This belongs to whoever maintains the skill, not this repository. |
| Computed outputs | The four questions in the plan's §9. |
| Chapters 1–4 back-fill | <ul><li>Week 01's look-alikes (`issue_form.png`, `pr_review.png`): use a real public issue and pull request that aren't a student's, or capture them by hand.</li><li>The unused placeholders (week 02's four, week 03's `ad_observatory`, week 05's `dev_tools_network`): delete or keep.</li><li>Figure 1-1: should it replace `anaconda_jupyter.png` in `setup.md`?</li></ul> |

## Known issues

- **Merged branches that the session could not delete.** The cloud session's git proxy refuses branch deletion with HTTP 403, so these remain. Delete them by hand, or turn on automatic deletion so they stop piling up.
  - **This repository, merged into `main`:**
    - earlier work: `add-ci`, `ch06-strategy-framework`, `fix-notebook-drift`, `fix-oscars-403-headers`, and the head branch of #53, a student's pull request merged on 2026-09-04;
    - chapters 4, 5, 7, and 8: `claude/ch04-refresh-live-data`, `claude/ch04-rss-directory-links`, `claude/ch04-rss-starter-feeds`, `claude/ch04-swap-rss-links`, `claude/ch05-protocols-expansion`, `claude/ch05-protocols-terminal-tools`, `claude/ch07-wayback-background`, `claude/ch08-selenium-manager-playwright`, `claude/ch08-selenium-preflight`;
    - the toolkit: `claude/pilot-ch05`, `claude/shots-toolkit-m1`, `claude/shots-toolkit-m2`, `claude/shots-toolkit-m3`, `claude/shots-devtools-effect-tests`, `claude/shots-relaxed-limit`;
    - docs: `claude/docs-agents-md`, `claude/aar-p0-edits`, `claude/lift-pause-pilot-gate`, `claude/readme-ai-acknowledgement`, `claude/contributing-guide`, and this note's own branch, `claude/handoff-after-merges`, once it merges.
  - **The course repository, merged into `main`:** `add-slides-ci`, `claude/detrope-week02-images`, `claude/week-01-screenshots-2aiqhh`, `claude/week-02-expansion`, `claude/week-04-rss-feeds-handout`, `claude/wk02-fixes`, `fix-oscars-403-headers-slides`, `overleaf-2026-08-24-0430`, and `overleaf-2026-08-24-0500`.
  - **The course repository, closed without merging:** `claude/swartz-ca-frames` (#23). Delete it only if #23 won't be revived. GitHub can restore it from the closed pull request.
  - **Keep:** `main`, `gh-pages`, every branch with an open pull request (students' included), and the course session's branch, `claude/info-4617-fall-2026-syllabus-07ahb8`.
- **Students' pull requests.** About 40 are open.
  - Most were made in the browser, so they fail Notebook sync (see the table above).
  - Six come from a fork's `main` branch. There, every later commit joins the open pull request, and two of them share one set of changes. `CONTRIBUTING.md` now asks for one branch per pull request.
- **Contributor docs that still disagree.** Found by #146's audit and left for later:
  - **Python version:** 3.10 or later in the README and `AGENTS.md`; 3.12 or later in the preface and syllabus; 3.11 in the setup handout and CI.
  - **User-Agent:** the chapters use six User-Agent strings, while `decisions.md` names one for the book's request examples.
  - **Exercises:** the revision framework invites starter cells, rubrics, and expected output; `AGENTS.md` rules out solutions and scaffolds.
  - **Common Issues:** ch-15 has no Common Issues section, though the "common issue" revision type assumes one.
  - **Length:** five chapters run past 7,000 words, against a target of about 3,000.
- **Course CI.** On course #51, the week-7 and week-8 deck builds sat in "Install TeX Live" (apt) for more than 30 minutes. That pull request changed neither deck, and it merged at the maintainer's instruction. The build on `main` after the merge passed. If the stall recurs, cache the TeX install, or build inside a TeX Live container.

## Hands off

- Chapter 6 and course week 6: leave them untouched (maintainer's instruction).
- Students' branches and pull requests: never merge, edit, or rebase them.
- Issues a student's open pull request already fixes: leave the fix to it. On 2026-09-24 a chapter 4 fix for #90 had to be withdrawn because #92, the reporter's own pull request, already fixed it. Check the issue's linked pull requests and the open ones on that chapter first.

## Notes for cloud sessions

- Don't retry the branch-deletion refusal (HTTP 403). List the branches here instead.
- Don't run `playwright install`. The toolkit uses Chrome for Testing through `tools/shots/bootstrap.sh`, and the container already has Chromium.
- Before a capture, read the "Field notes" in `tools/shots/README.md`, and add to them what the capture teaches.
- HTTPS goes through the session's proxy. Never turn off TLS verification. Captures through the proxy use HTTP/1.1, and captions that show protocol details say so.
- Quarto isn't installed system-wide. Download a release into the session's scratch directory. The computed-outputs tests used 1.10.18.
- **Merging several pull requests that touch the same files.**
  - Rehearse the merges first in a scratch worktree (`git worktree add --detach … origin/main`). Then merge `main` into each branch in turn, never rebasing.
  - A merge's "ours" and "theirs" swap between a rehearsal (`main` checked out) and the real merge (the branch checked out). Take the resolved files from the rehearsal's commit; don't rerun a script that picks sides.
- A clone may track only `main`. Fetch other branches by full refspec: `git fetch origin "+refs/heads/<branch>:refs/remotes/origin/<branch>"`.
