# Hand-off note

**Updated 2026-09-25**, after textbook #148–#152 and #154–#164 and courses #55–#64 merged, with the second part of toolkit M4 that this note's pull request adds: evidence queries, the recorded queries behind the claims in captions (AAR P1-2). This note describes the present state. Rewrite it when a session stops or the state changes, and don't let it grow into a history. History lives in git, in [`decisions.md`](decisions.md), and in the AARs.

## Where things stand

- **Screenshot toolkit, `tools/shots`.** Milestones M1–M3 are merged (#135–#137). Since the chapter 5 pilot:
  - every setting the toolkit sends to Chrome or DevTools is read back and tested (AAR P0-3);
  - headed captures run without Chrome for Testing's infobar, and a guard fails any take that shows one;
  - every recipe figure has a `brief:`, and `tools/shots/README.md` ("Making a figure, start to finish") goes from the brief to a merged pull request;
  - the size limit has two tiers: 800×600 by default, and up to 1024×768 when the extra room removes clutter and the text still passes;
  - the README's "Field notes" record what the captures taught (#150), and `doctor` reads each host's robots.txt for the course's User-Agent, listing groups for Claude's agents as a note;
  - `tools/make_notebooks.py` reads brackets inside code spans in captions, and fails when a figure or `@fig-` reference is left unconverted (#151).

  - `scroll` steps can scroll a panel (`within:`), as Jupyter needs, and `doctor` asks a local server (`localhost`) at its own address.
  - A figure can show a host that doesn't answer: the take is Chrome's own error page, kept only after public DNS confirms the host is gone rather than refused by the session's proxy. Composites can stack their parts, and `doctor` checks each part's host and robots.txt's `Crawl-delay`.
  - A figure of an API's response is marked `api_client: true` and captured as an API client where robots.txt disallows it; `doctor` reports that as a note, and still warns about any other disallowed page.
  - A take fails when a file from the page's own host (a stylesheet, image, font, or script) fails before any answer, or gets a server error (5xx), and is retried. On 2026-09-25 web.archive.org aborted some stylesheets on each load, and answered 502 for AboutFace's banner on one load and drew it on the next; those takes passed every text check.
  - `open_shadow: true` opens a closed shadow root, as the Wayback toolbar's is, so steps can wait for its capture count and hover its buttons, and the text measure counts it. A crop whose element is missing fails its take instead of ending the run.
  - M4's engines make a figure whose subject is a tool with that tool. `engine: selenium` drives the window `webdriver.Chrome()` opens through Selenium alone. `engine: codegen` runs codegen's recorder in Chrome for Testing and feeds it real clicks; `playwright codegen` itself can't run, because it wants Playwright's own Chromium build, which the toolkit never installs. The README's "Engines" says what the codegen engine had to work around: the Inspector's scale, its unreachable text, the script written only at close, and Playwright turning off HTTPS-Upgrades (#164).
  - `tools/shots/run evidence` runs the queries a recipe lists under `evidence:`, the ones behind a number or claim in a caption or its paragraph. It pages each to its end, fails a page that returns exactly its limit and can't page, and records the requests, rows, date, and a summary in `provenance.json` and `IMAGES.md`. `check` warns about evidence never run, or whose query or claim changed since.

  The selftest passes 119 of 119. `check` reports 0 errors and 0 warnings.
- **Chapters.**
  - ch-01: the setup works as written (#152). Jupyter installs into `webdata`, terminal commands are shell blocks, and the first request sends a User-Agent. #155 adds three figures: Jupyter's **New** menu, the companion notebook's cells, and the article beside View Source. It also corrects the instruction to choose **New** and then **Notebook**: Notebook 7's menu lists **Python 3 (ipykernel)**. Figure 1-4 (the pageviews JSON) is left out; see "Next".
  - ch-02: #156 adds Wikipedia's robots.txt at its generic block and Wikimedia's User-Agent policy, and `tools/shots` gains `match:` anchors for lines of plain text. Reddit's robots.txt (2-2) waits for the Friday review, since students' #50, #63, and #79 revise its paragraphs.
  - ch-03 has all four of the back-fill's figures. #158 added Article 40 of the Digital Services Act on EUR-Lex and the retired endpoints, and #159 added Twitter v1.1's part to the endpoints. #160 added two from the Wayback Machine: u/spez's post of 9 June 2023 announcing Reddit's $0.24 per 1,000 calls (3-3), from old.reddit.com's archived copy, since reddit.com's robots.txt disallows every path; and CrowdTangle's last capture, 14 August 2024, whose banner announced the shutdown (3-2). The archive's later captures of CrowdTangle's address are redirects, and the chapter now says so.
  - ch-04 has all four of the back-fill's figures: three in #149, with fixes for #84, #87, and #132, and the Open-Meteo forecast in Chrome's JSON view (4-2) in #159.
  - ch-05 has four DevTools figures from the pilot (#138).
  - ch-07: #161 retook its five Wayback figures within the size limit and dated every caption. Its counts and the calendar's colors follow the new takes, checked against the archive's APIs on 2026-09-25: 20,394,311 captures of google.com, 8,516,745 of facebook.com, and 94,893 of x.com; facebook.com's captures were 200s until April 8, 2005, not through March. Below 1,100 pixels wide the toolbar has no strip chart, so the toolbar paragraph now says what a wider window adds. This note's pull request adds evidence for two of its claims: the calendar's dates (200s until April 8, 2005, 403s from April 10 to August 4, 200s from August 6) and x.com's images (none of six ever a 200). The second corrected the paragraph: the spacer image was saved in April and May 2000, not only April.
  - ch-08: its View Source and JavaScript off/on figures are within the size limit, and the Selenium caption is dated (#142, #148). §8.3 checks Selenium Manager before the first browser (#143). This note's pull request retakes its two tool windows with the engines: the Selenium window, 800×600, and codegen's browser above its Inspector, 800×534, with captions and alt text to match. Every chapter 7 and 8 figure is now within the size limit.
- **Decisions on 2026-09-24** ([`decisions.md`](decisions.md)): robots.txt is read for the course's User-Agent, and examples send one; a figure of an API's response is captured as an API client; the book recommends Python 3.14; students' pull requests merge after a code-review standup in class on a Friday.
- **Contributors.** `CONTRIBUTING.md`, a pull request template, and issue forms that point to it (#146). The README acknowledges the AI tools used to write the book (#145).
- **Project records.** `AGENTS.md` and `docs/`: the AARs, the plans, the decision log, and this note.
- **Course repository.**
  - Course #55 is merged: week 4's figures for the RSS handout and slides, Jupyter in week 1's setup, and `AUTHORING.md`'s notes on copies and the field notes.
  - Course #57 is merged: copies of chapters 1 and 2's figures, offered to week 1's setup handout and week 2's deck; neither changed.
  - Course #58 is merged: copies of chapter 3's figures, offered to week 3's deck, which didn't change, and `make_stubs.py`'s markers in weeks 2 and 3's `IMAGES.md`.
  - Course #59 is merged: figure 4.2 in week 4's `img/`, and the three-part retired endpoints in week 3's.
  - Course #60 is merged: the Friday review table in `docs/plans/2026-09-24-friday-code-review-table.md`, and the Friday plan scheduled for week 7's Friday, October 2, with what that day's frames need from the table.
  - Course #61 is merged: week 3's copies of chapter 3's two archive figures, offered to its frames on Reddit's pricing and CrowdTangle.
  - Course #62 is merged: week 7's slide screenshots, remade from the `week07-*` recipes in `tools/shots/recipes/course.yml` (#162), with a copy of chapter 7's figure 7.3. Their text now reaches 16 pixels on a 1,920-pixel slide; the old crops showed it at 6 to 15. Four frames were resized to fit, and three frames' facts changed with the new takes.
  - Course #63 is merged: three of week 8's slide screenshots, remade from the `week08-*` recipes in 480-pixel windows (#163). Their text went from about 7–11 pixels to 18–19.6 on a 1,920-pixel slide.
  - Course #64 is merged: week 8's two tool windows (#164), `selenium_browser.png`, a crop to the bar's first sentence for its 35% column (18.5 pixels), and `codegen.png`, figure 8.6 (16.2 pixels in its 55% column).
  - Course #56 is merged. It adds the roadmap for the Friday code review (`docs/plans/2026-09-24-friday-code-review.md`) and the merge rule in the revision framework, the pull request walkthrough, and week 4's FAQ. It also puts Python 3.14 in week 1's setup and gensim from conda-forge in week 7's deck.

## Next

In this order:

1. **The first Friday code-review standup**, week 7's Friday, October 2 ([plan](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/docs/plans/2026-09-24-friday-code-review.md)). Its review table, built on 2026-09-24, is in the course's `docs/plans/` (course #60). Rebuild it on Thursday, October 1: its "How it was built" lists the steps, and GitHub hasn't run the checks on pull requests from forks. Then build week 7's Friday frames from it (the plan's §4, "Slides").
2. **Finish the back-fill** ([plan](plans/2026-09-24-screenshot-backfill-ch01-05.md), §4). Every chapter has had its pass; what is left waits on a host, the Friday review, or the maintainer.
   - Figure 1-4 (the pageviews JSON) waits for another network: Wikimedia's REST API answered this session's address with 429 twice on 2026-09-24 and once on 2026-09-25 (`images/ch-01/IMAGES.md` has a draft recipe). Figure 2-2 (Reddit's robots.txt) waits for the Friday review.
   - `shots import`, for hand captures such as week 1's issue form, isn't built (M4).
3. **The rest of AAR P2-1** is blocked; each item needs a course recipe cropped for its frame's column, as weeks 7 and 8's have (`tools/shots/README.md`, "Course-only figures").
   - Week 1's screenshots wait for the maintainer (see the table below).
   - Week 8's `pr_review.png` waits for a session that can read github.com's robots.txt for the course's User-Agent. A cloud session reaches github.com only for its own repositories, so the request is refused (403).
4. **The rest of toolkit M4** ([plan](plans/2026-09-24-screenshot-toolkit.md), §8): `sync` and `import`, and the `shots-check` CI job (AAR P1-1). The engines and evidence queries are done. A figure whose caption or paragraph rests on a count should gain `evidence:` as it is next retaken; chapter 7's two are the pattern.
5. **Align the chapters' User-Agent strings** with `WebDataScience/1.0 (your-email@colorado.edu)`, after the Friday review.
   - Students' #88 and #93 add one to chapter 4's requests.
   - Chapter 7's three top-level requests (Availability, the raw capture, CDX) send none, and week 7's deck copies them. Change the chapter and the deck together, so the slides match the notebook.
   - The course's week 11 deck calls keyed APIs (Census, FRED, FEC) without one. Week 1's setup handout and week 10's deck already send one (course #56 fixed week 1).
6. **Chapter 4's Step 5**, after the Friday review. It sends students to Open-Meteo after Step 1 taught them to check robots.txt, whose file there disallows every path; a sentence could point back to chapter 2's distinction between crawlers and API clients. Students' #86 revises Step 5, so wait for it.
7. **The course side of the contributor docs.** `handouts/common/revision-framework.md` and week 1's deck still name `claude.md`, now `AGENTS.md`, and the handouts say pull requests have no form.
8. **Computed outputs.** If they are adopted, run the [plan](plans/2026-09-24-computed-outputs.md)'s M0 pilot on chapter 5.

## Waiting on the maintainer

| Item | What to decide |
|---|---|
| Notebook sync on browser edits | A pull request edited in GitHub's browser editor can't regenerate its notebook, so the Notebook sync check fails. Either let CI regenerate the notebooks on pull requests (a workflow change), or keep the check and have the maintainer regenerate before merging, for example after the Friday review. `CONTRIBUTING.md` describes the second. On 2026-09-24 #117, which edited `notebooks/ch-05-protocols.ipynb` directly, merged with bare quotes that made the notebook invalid JSON: Jupyter couldn't open it, and every pull request's Notebook sync failed until #157 moved its note into the chapter. Merging only after Notebook sync passes would have caught it. |
| Merges before the standup | Students who can push branches to this repository can also merge, and a student merged #117 on 2026-09-24, before any review. A branch-protection rule on `main` that requires the maintainer's review would make the Friday standup the merge point (the course plan's §7). |
| AAR P0-2 | Enable the permission rule that denies force-pushes (untested; test it first). Turn on "Automatically delete head branches" in both repositories. |
| AAR P1-1 | The `shots-check` CI workflow, part of M4. |
| AAR P1-3 | Fix the review skill's session collector. This belongs to whoever maintains the skill, not this repository. |
| Computed outputs | The four questions in the plan's §9. |
| Chapters 1–3 back-fill | <ul><li>Week 01's look-alikes (`issue_form.png`, `pr_review.png`): use a real public issue and pull request that aren't a student's, or capture them by hand.</li><li>The unused placeholders (week 02's four, week 03's `ad_observatory`, week 05's `dev_tools_network`): delete or keep.</li><li>Week 1's setup handout: should `jupyter-new-menu_annotated.png` or `jupyter-cells_annotated.png` (copies of figures 1.1 and 1.2 in the course's `handouts/week-01/img/`) replace `anaconda_jupyter.png`? The handout's "Make a new notebook" is the step figure 1.1 shows.</li><li>Week 1's `book_website.png` and `github_repo.png` sit in a 0.35-wide column, where a live capture's text is legible only when cropped to about 480 CSS pixels. Widen the column, or accept a tight crop, before they are retaken live.</li></ul> |

## Known issues

- **Students' pull requests.** 39 are open; they merge after the Friday code review. The course's review table (#60) lists each one's checks, conflicts, and overlaps.
  - Four conflict with `main` since #149 and #152 merged: #52 (chapter 1), and #88, #89, and #93 (chapter 4). #88 and #93 make the same change. Resolving a conflict is a good demonstration for the review.
  - Most were made in the browser, so they fail Notebook sync (see the table above).
  - Six come from a fork's `main` branch. There, every later commit joins the open pull request, and two of them share one set of changes. `CONTRIBUTING.md` now asks for one branch per pull request.
  - #92 is the fix for issue #90, which a commit message in #149 closed by mistake; it was reopened.
- **Merged branches that the session could not delete.** The cloud session's git proxy refuses branch deletion with HTTP 403, so these remain. Delete them by hand, or turn on automatic deletion so they stop piling up.
  - **This repository, merged into `main`:**
    - earlier work: `add-ci`, `ch06-strategy-framework`, `fix-notebook-drift`, `fix-oscars-403-headers`, and the head branch of #53, a student's pull request merged on 2026-09-04;
    - chapters: `claude/ch01-setup-fixes`, `claude/ch04-figures`, `claude/ch04-refresh-live-data`, `claude/ch04-rss-directory-links`, `claude/ch04-rss-starter-feeds`, `claude/ch04-swap-rss-links`, `claude/ch05-protocols-expansion`, `claude/ch05-protocols-terminal-tools`, `claude/ch07-wayback-background`, `claude/ch08-retakes`, `claude/ch08-selenium-manager-playwright`, `claude/ch08-selenium-preflight`;
    - the toolkit: `claude/pilot-ch05`, `claude/shots-toolkit-m1`, `claude/shots-toolkit-m2`, `claude/shots-toolkit-m3`, `claude/shots-devtools-effect-tests`, `claude/shots-relaxed-limit`, `claude/shots-field-notes`, `claude/notebook-figure-brackets`;
    - docs: `claude/docs-agents-md`, `claude/aar-p0-edits`, `claude/lift-pause-pilot-gate`, `claude/readme-ai-acknowledgement`, `claude/contributing-guide`, `claude/handoff-after-merges`, and `claude/decisions-ua-python`;
    - the back-fill: `claude/ch01-figures`, `claude/ch02-figures`, `claude/ch03-figures`, `claude/ch05-a-record-note`, `claude/api-client-figures`, `claude/wayback-figures`, `claude/ch07-retakes`, `claude/week07-slide-shots`, `claude/week08-slide-shots`, `claude/m4-tool-engines`, and this note's own branch, `claude/m4-evidence`, once it merges.
  - **This repository, closed without merging:** `claude/decisions-ua-python-review` (#153). #154 replaced it with the same changes, because the message of #153's first commit quoted a closing keyword with #90's number: merged, it would have closed #90 again.
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
