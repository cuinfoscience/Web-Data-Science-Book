# Web Data Science — Quarto Book

Instructions for AI coding agents (Claude Code, Codex, and any other) and for people extending the book. This is the one instructions file: `CLAUDE.md` only imports it, and an agent that looks for its own file (`GEMINI.md`, `.cursorrules`, and so on) should read this one.

## Project Memory: `docs/`

Before starting work, read `docs/handoff.md` (where work stands, what is paused, what is next) and `docs/decisions.md` (standing decisions and the reasons for them). After-action reports are in `docs/aar/`, plans and roadmaps in `docs/plans/`; `docs/README.md` says how each is kept. When work pauses or a decision is made, update those files in the same pull request.

## Git and Pull Requests

Merge with merge commits. Don't squash, rebase, or force-push a branch someone may have seen. A merge commit keeps the branch inside `main`, so a session that has to reuse one branch starts its next pull request with a fast-forward, and the review history stays readable. Open a new branch for each pull request, and don't base one pull request on another's unmerged branch. Merge only when the maintainer asks, and never merge a student's pull request. If the environment can't delete merged branches, list them in `docs/handoff.md`. The reasons are in `docs/decisions.md`.

## Project Overview

This is a Quarto book for an upper-division undergraduate and master's-level course on web data science taught at the University of Colorado Boulder's Department of Information Science. It covers retrieving, parsing, and analyzing data from the web using Python.

## Build Instructions

```bash
# Preview the book locally
quarto preview

# Render the book (HTML is the only configured format)
quarto render

# Regenerate the companion notebooks after editing chapter code
python tools/make_notebooks.py
```

PDF output is not currently configured; adding it would require TinyTeX and a `pdf` entry under `format:` in `_quarto.yml`.

### Dependencies

- Quarto 1.4+
- Python 3.10+ via Anaconda
- Jupyter (for rendering .qmd files with Python code)
- Key Python libraries: requests, beautifulsoup4, lxml, pandas, numpy, scipy, matplotlib, seaborn, selenium, pypdf, praw, spotipy, atproto, Mastodon.py, openai, anthropic, gensim, nltk, scapy, dnspython

## Editorial Voice and Style

- **Person**: Second person ("you"). Address the reader directly as a student learning these skills.
- **Tone**: Formal but approachable, engaging, and supportive. Think "experienced mentor explaining things clearly" rather than "textbook lecturing." Occasional humor is welcome, but keep it dry and relevant.
- **Audience**: Advanced undergraduates and early-career master's students with some Python experience. They know loops, functions, lists, and dictionaries, but may not have experience with web protocols, APIs, or HTML parsing.
- **Code style**: Narrative code blocks with comments. Code is set to `eval: false` globally — students run code themselves. Include expected output as comments where it helps comprehension. Use meaningful variable names and include docstrings in functions. **Each comment lives on one line — never hard-wrap a comment sentence across lines**; let the editor soft-wrap. This applies to the Recommended Exercises scaffold cells and every other code block.
- **Chapter structure**: Each chapter follows a consistent pattern:
  1. Learning objectives (bulleted list in a callout)
  2. Conceptual introduction with motivation
  3. Library/framework introduction
  4. Guided tutorial with narrative code blocks
  5. Recommended Exercises (one guided build, 5–7 steps) followed by Additional Exercises (open-ended, "Graduate extension (INFO 5617)" last)
  6. Social history / public interest data science sidebar
  7. Common debugging issues
  8. Key takeaways
  9. Further reading links
- **Cross-references**: Use Quarto's `@sec-` syntax for chapter cross-references. Reference the *Missing Manual for Information Scientists* by chapter number and title where relevant using callout blocks.
- **Missing Manual references**: Use `::: {.callout-tip}` blocks formatted as: "For a deeper introduction to [topic], see *Missing Manual* Chapter N: [Title]."
- **Callout types**:
  - `.callout-tip` — Missing Manual cross-references, practical tips
  - `.callout-warning` — Ethical considerations, legal cautions, "Warning!" blocks about ToS violations
  - `.callout-note` — Connections to the post-API age framework (openness, oversight, ownership)
  - `.callout-important` — Critical debugging or setup steps
- **Data sources**: Use the specific sources from the course notebooks (leg.colorado.gov, the-numbers.com, Wikipedia, Boulder City Council PDFs, etc.). These may change; document the specific URLs and dates accessed.
- **Exercises**: two sections per chapter. **Recommended Exercises** is the take-home assignment: one guided build of 5–7 numbered steps (`**Step N — Title.**` prose followed by a ```{python} block containing only comment prompts like `# Your code here` — never solution code), ending with an interpretation step answered in comments or Markdown. Steps may use only concepts from that chapter or earlier ones, never later chapters, and should cite earlier chapters with `@sec-` references. The empty cells flow into the companion notebook, which students complete and submit. **Additional Exercises** are open-ended items, no scaffold, with one **Graduate extension (INFO 5617)** exercise as the final numbered item — a scholarly reading paired with an open-ended, rigorous task for the 5000-level section. At least one exercise per chapter should involve a data source not used in the tutorial.
- **Companion notebooks**: every chapter has a generated Jupyter notebook in `notebooks/` (regenerate with `python tools/make_notebooks.py` after editing chapter code; see the Companion Notebooks appendix).
- **Word count target**: ~3,000 words per chapter (soft target; tutorial-heavy chapters may run to 4,000–5,000 including code blocks).
- **Figures and screenshots**: images live in `images/ch-NN/`, each made from a recipe in `tools/shots/recipes/ch-NN.yml` and recorded in that folder's `provenance.json` (see `tools/shots/README.md`; run `tools/shots/run check` before a PR).
  - A screenshot is a real capture of a real page. Diagrams and renders are welcome, but never rebuild a real site's interface with invented content.
  - Every figure has `fig-alt` that transcribes the text and numbers a reader needs from it. The ch-07 and ch-08 figures, at 280–440 characters, set the bar.
  - A figure showing anything that changes (counts, versions, a live page) says in its caption when it was captured, as in "in September 2026."
  - A count, date, or total printed in a caption comes from a query whose limit and paging are recorded with the figure. If the query hit its limit, page until it doesn't, or don't print the number.
  - Numbered markers are drawn by `tools/shots` from the recipe's `annotate:` marks, each pointing at a page element or a DevTools row, so they follow the page on a retake. Don't place markers at hand-typed pixel positions or paint them into the image.
  - **Readable where it is shown, at both ends.** A reader can't use text that is too small, and can't use a figure too crammed to follow.
    - Scope each figure to what its paragraph discusses: crop to it, and hide the panels, columns, and sidebars the text doesn't mention.
    - Enlarge by zooming the application, not by widening the window. Three of the four chapter 5 figures zoom DevTools to 125%.
    - A figure shows 800×600 CSS pixels of the screen by default. It may relax to 1024×768 when the extra room removes clutter (rows that wrap, columns cut short with "…", panels squeezed together) and `check` still passes its text everywhere it is shown; the recipe says what the room removes in `oversize:`. At 1024 pixels wide the book's column shows text at 76% of its size on screen, so zoom DevTools to about 150%. Beyond 1024×768, a recipe needs a reason too.
    - `tools/shots/run check` is the one place that judges text size. It measures the text at each place the recipe's `targets:` names: the book's column, a slide at a stated share of the text width, or a printed handout. It fails text under 11 pixels in the book, 16 on a 1920-pixel slide, or 6 points in print.
    - Before a PR, look at every take in `tools/shots/run sheet ch-NN`. A wrapped row, or a column cut short with "…", means the figure shows too much for its size: scope it down, or relax to 1024×768 if its text still passes.
  - Keep the capture's own traces out of frame: the proxy's address in DevTools' General section, and response headers that echo the capture's IP address or location. Where the setup changes what a reader would see (HTTP/1.1 through a proxy, a first visit with nothing cached), the caption says so.
  - A change to `tools/shots` is done when two things are true: it has made one real figure that someone has looked at, and every setting it passes to Chrome or DevTools has a test in `tools/shots/selftest.py` that reads the effect back. An unknown key fails silently. In the chapter 5 pilot, two faults got past a passing selftest: a DevTools preference that the browser ignored, and a User-Agent option that also rewrote Client Hints.

## File Structure

```
web-data-science/
├── _quarto.yml          # Project configuration
├── AGENTS.md            # This file — project instructions for agents and people
├── CLAUDE.md            # Imports AGENTS.md, for Claude Code
├── docs/                # AARs, plans, the decision log, and the hand-off note
├── index.qmd            # Preface
├── ch-01-introduction.qmd through ch-15-research-design.qmd
├── appendix-ai-disclosure.qmd
├── appendix-further.qmd
├── images/ch-NN/        # Figures, with provenance.json and IMAGES.md
├── tools/shots/         # Screenshot recipes and the capture toolkit
└── references.bib       # BibTeX references
```

## Companion Resources

- **Missing Manual for Information Scientists**: https://cuinfoscience.github.io/INFO-Missing-Manual/
  - Referenced throughout for foundational computing skills (Jupyter, debugging, regex, scripting, version control, secrets management, etc.)
- **Course notebooks**: The original Jupyter notebooks from INFO 4871 (Fall 2024) are the primary source material for tutorial content.
- **JRC paper**: Keegan (2026), "Public interest data infrastructuring" — provides the theoretical framework for Chapter 3 and the public interest thread throughout.

## Prose safeguards — the significance-verdict family

The recurring failure in generated prose for this book is the **significance
verdict**: a sentence or clause whose entire content is that the adjacent
evidence means something. It appears under endlessly novel strings — "the
distinction matters," "the differences matter," "the variety is diagnostic,"
"that is the point," "the asymmetry is the tell," "the tagline is earned,"
"each of these earns its place," "That is X rather than Y" — so banning
strings only trains paraphrase. The rule targets the function:

- **Never write a sentence that asserts the significance of its neighbors.**
  Significance is carried by a consequence, not an adjective: "A gated service
  can be negotiated with; a deleted one cannot" needs no "the distinction
  matters, because" in front of it — the consequence *is* the mattering.
- **The delete test.** If a sentence can be removed with no information lost,
  it was a verdict, not a claim. Apply it to every paragraph-closing sentence
  in new prose.
- **End on the strongest fact, not a beat.** No quotable one-liner closers
  ("openness as a design property rather than a press release"), no counting
  verdicts ("three deaths, three causes"), no demonstrative applause ("That is
  the point.").
- **No verdict verbs on the book's own material**: earned, earns its place,
  deserves, is telling, is diagnostic, is the tell, is no accident.
- **Known banned figures** (tripwires for the function above, not the whole
  ban): the gap matters, load-bearing, seam to follow, arc, the distinction/
  difference(s) matter(s).

Run `python tools/trope_lint.py` before opening a PR. Its hits are flags for
the delete test, not automatic failures — "status codes matter because CDX
records every attempt" survives the test (the because-clause carries content);
"the differences matter" before a list of the differences does not. New prose
deserves the scan most: fresh composition is where this family regenerates.

## Extending the Book

When adding new chapters or updating existing ones:

1. Follow the chapter structure template above
2. Add the new .qmd file to the `chapters` list in `_quarto.yml`
3. Use narrative code blocks (`eval: false`) — do not assume API keys or live endpoints. (Showing computed charts and tables is proposed in `docs/plans/2026-09-24-computed-outputs.md`; until it is adopted, code stays unexecuted.)
4. Include at least one cross-reference to another chapter and one to the Missing Manual
5. Add any new references to `references.bib`
6. Test the build with `quarto preview` before committing
