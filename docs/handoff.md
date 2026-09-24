# Hand-off note

**Updated 2026-09-24**, at the end of the session that ran the screenshot sprint. This note describes the present state. Rewrite it when a session stops or the state changes, and don't let it grow into a history. History lives in git, in [`decisions.md`](decisions.md), and in the AARs.

## Where things stand

- **Screenshot toolkit, `tools/shots`.** Milestones M1–M3 are merged (#135–#137). The selftest passes 56 of 56 checks.
- **Chapter 5 pilot.** Merged. Four DevTools figures are in `ch-05-protocols.qmd` (#138). The course deck for week 5 uses one of them, and the course repository keeps copies of all four with notes (course #51).
- **The pull request that adds this note** (branch `claude/docs-agents-md`) does four things:
  - renames `claude.md` to `AGENTS.md`, with `CLAUDE.md` importing it;
  - adds `docs/`, and moves the screenshot AAR and plans here from the course repository;
  - adds the sprint's AAR ([`aar/AAR_Web-Data-Science-Book_2026-09-24.md`](aar/AAR_Web-Data-Science-Book_2026-09-24.md));
  - adds the computed-outputs plan ([`plans/2026-09-24-computed-outputs.md`](plans/2026-09-24-computed-outputs.md)).

## Paused

The maintainer paused this work on 2026-09-24. Don't start any of it until they resume it:
- the back-fill of chapters 1–4 ([plan](plans/2026-09-24-screenshot-backfill-ch01-05.md));
- retakes of the 11 chapter 7–8 figures and 18 slide screenshots that fail the 800×600 limit, and dates for 3 chapter 7–8 captions (AAR P2-1);
- computed figures and tables ([plan](plans/2026-09-24-computed-outputs.md)).

## Waiting on the maintainer

| Item | What to decide |
|---|---|
| AAR P0-1 | Apply the two-sided legibility wording to `AGENTS.md` and the course's `AUTHORING.md`? |
| AAR P0-2 | The policy is decided ([`decisions.md`](decisions.md)). Still open: add its text to `AGENTS.md`; enable the permission rule that denies force-pushes (untested); turn on GitHub's "Automatically delete head branches" in both repositories. |
| AAR P0-3 | Add effect tests for the DevTools preferences (mechanical), and the "done" rule for toolkit changes (text). |
| AAR P1-1 | Add the `shots-check` CI workflow, which runs only on pull requests that change images. |
| AAR P1-3 | Fix the review skill's session collector. This belongs to whoever maintains the skill, not this repository. |
| Computed outputs | The four questions in the plan's §9. |

## Known issues

- **Merged branches that the session could not delete.** The cloud session's git proxy refuses branch deletion with HTTP 403, so these remain. Delete them by hand, or turn on automatic deletion so they stop piling up.
  - This repository, merged into `main`: `add-ci`, `ch06-strategy-framework`, `claude/ch04-refresh-live-data`, `claude/ch04-rss-directory-links`, `claude/ch04-rss-starter-feeds`, `claude/ch04-swap-rss-links`, `claude/ch05-protocols-expansion`, `claude/ch05-protocols-terminal-tools`, `claude/ch07-wayback-background`, `claude/ch08-selenium-manager-playwright`, `claude/pilot-ch05`, `claude/shots-toolkit-m1`, `claude/shots-toolkit-m2`, `claude/shots-toolkit-m3`, `fix-notebook-drift`, and `fix-oscars-403-headers`. Also merged: the head branch of #53, a student's pull request merged on 2026-09-04.
  - The course repository, merged into `main`: `add-slides-ci`, `claude/detrope-week02-images`, `claude/week-01-screenshots-2aiqhh`, `claude/week-02-expansion`, `claude/week-04-rss-feeds-handout`, `claude/wk02-fixes`, `fix-oscars-403-headers-slides`, `overleaf-2026-08-24-0430`, and `overleaf-2026-08-24-0500`.
  - The course repository, closed without merging: `claude/swartz-ca-frames` (#23). Delete it only if #23 won't be revived. GitHub can restore it from the closed pull request.
  - Keep `main`, `gh-pages`, every branch with an open pull request (students' included), and the course session's branch, `claude/info-4617-fall-2026-syllabus-07ahb8`.
- **Course CI.** On course #51, the week-7 and week-8 deck builds sat in "Install TeX Live" (apt) for more than 30 minutes. That pull request changed neither deck, and it merged at the maintainer's instruction. The build on `main` after the merge passed. If the stall recurs, cache the TeX install or build inside a TeX Live container.
- **Toolkit.** Three of the eight settings the toolkit sends to Chrome or DevTools have tests that read the effect back. The DevTools layout preferences have none (AAR P0-3). M4, counts in captions checked against recorded queries, is still planned.

## Hands off

- Chapter 6 and course week 6: leave them untouched (maintainer's instruction).
- Students' branches and pull requests: never merge, edit, or rebase them.

## Notes for cloud sessions

- Don't retry the branch-deletion refusal (HTTP 403). List the branches here instead.
- Don't run `playwright install`. The toolkit uses Chrome for Testing through `tools/shots/bootstrap.sh`, and the container already has Chromium.
- HTTPS goes through the session's proxy. Never turn off TLS verification. Captures through the proxy use HTTP/1.1, and captions that show protocol details say so.
- Quarto isn't installed system-wide. Download a release into the session's scratch directory. The computed-outputs tests used 1.10.18.

## Next, when work resumes

1. Decide the AAR's P0 actions, and apply the agreed text to `AGENTS.md` and the course's `AUTHORING.md`.
2. Add the missing effect tests (P0-3) before changing the toolkit again.
3. Retake the chapter 7–8 figures and the slide screenshots under P0-1, one chapter per pull request.
4. Back-fill chapters 1–4 by the plan.
5. If computed outputs are adopted, run the plan's M0 pilot on chapter 5.
