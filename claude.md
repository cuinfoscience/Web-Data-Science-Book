# Web Data Science — Quarto Book

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

## File Structure

```
web-data-science/
├── _quarto.yml          # Project configuration
├── claude.md            # This file — project instructions
├── index.qmd            # Preface
├── ch-01-introduction.qmd through ch-15-research-design.qmd
├── appendix-ai-disclosure.qmd
├── appendix-further.qmd
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
3. Use narrative code blocks (`eval: false`) — do not assume API keys or live endpoints
4. Include at least one cross-reference to another chapter and one to the Missing Manual
5. Add any new references to `references.bib`
6. Test the build with `quarto preview` before committing
