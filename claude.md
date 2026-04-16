# Web Data Science — Quarto Book

## Project Overview

This is a Quarto book for an upper-division undergraduate and master's-level course on web data science taught at the University of Colorado Boulder's Department of Information Science. It covers retrieving, parsing, and analyzing data from the web using Python.

## Build Instructions

```bash
# Preview the book locally
quarto preview

# Render all formats
quarto render

# Render HTML only
quarto render --to html

# Render PDF only (requires LaTeX)
quarto render --to pdf
```

### Dependencies

- Quarto 1.4+
- Python 3.10+ via Anaconda
- Jupyter (for rendering .qmd files with Python code)
- Key Python libraries: requests, beautifulsoup4, pandas, matplotlib, seaborn, selenium, pypdf, praw, spotipy, atproto, Mastodon.py, openai, anthropic, gensim, nltk, scapy, dnspython

## Editorial Voice and Style

- **Person**: Second person ("you"). Address the reader directly as a student learning these skills.
- **Tone**: Formal but approachable, engaging, and supportive. Think "experienced mentor explaining things clearly" rather than "textbook lecturing." Occasional humor is welcome, but keep it dry and relevant.
- **Audience**: Advanced undergraduates and early-career master's students with some Python experience. They know loops, functions, lists, and dictionaries, but may not have experience with web protocols, APIs, or HTML parsing.
- **Code style**: Narrative code blocks with comments. Code is set to `eval: false` globally — students run code themselves. Include expected output as comments where it helps comprehension. Use meaningful variable names and include docstrings in functions.
- **Chapter structure**: Each chapter follows a consistent pattern:
  1. Learning objectives (bulleted list in a callout)
  2. Conceptual introduction with motivation
  3. Library/framework introduction
  4. Guided tutorial with narrative code blocks
  5. Exercises (3–5 per chapter, graduated difficulty)
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
- **Exercises**: 3–5 per chapter. Graduate from guided application to open-ended exploration. At least one exercise per chapter should involve a data source not used in the tutorial.
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

- **Missing Manual for Information Scientists**: https://www.brianckeegan.com/ParatechnicalComputingHandbook/book/
  - Referenced throughout for foundational computing skills (Jupyter, debugging, regex, scripting, version control, secrets management, etc.)
- **Course notebooks**: The original Jupyter notebooks from INFO 4871 (Fall 2024) are the primary source material for tutorial content.
- **JRC paper**: Keegan (2026), "Public interest data infrastructuring" — provides the theoretical framework for Chapter 3 and the public interest thread throughout.

## Extending the Book

When adding new chapters or updating existing ones:

1. Follow the chapter structure template above
2. Add the new .qmd file to the `chapters` list in `_quarto.yml`
3. Use narrative code blocks (`eval: false`) — do not assume API keys or live endpoints
4. Include at least one cross-reference to another chapter and one to the Missing Manual
5. Add any new references to `references.bib`
6. Test the build with `quarto preview` before committing
