# Web Data Science

A Quarto textbook for **INFO 4617 / 5617: Web Data Science** at the University of Colorado Boulder, Department of Information Science.

This book teaches advanced undergraduates and master's students how to retrieve, parse, and analyze data from the web using Python. It covers static and dynamic web scraping, structured data formats (XML, JSON), the protocol stack (TCP/IP, DNS, HTTP), document extraction (HTML, archived pages, PDFs), and authenticated APIs (Wikipedia, U.S. Census, FRED, FEC, Reddit, Spotify, Bluesky, Mastodon, OpenAI, Anthropic), along with automation via GitHub Actions and a capstone treatment of research design.

A theoretical thread on the **post-API age** — the structural pressures of *enclosure*, *exemption*, and *erosion* shaping access to web data, and the counter-values of *openness*, *oversight*, and *ownership* — runs throughout the book.

> **Help improve this book.** Found something broken, missing, or unclear? You don't need to know git or the fix. [File an issue](https://github.com/cuinfoscience/Web-Data-Science-Book/issues/new/choose) in a few minutes, or read **[CONTRIBUTING.md](CONTRIBUTING.md)** to make the change yourself.

## Book Contents

The book is organized into four parts plus appendices:

**Part I — Foundations**
1. Introduction to Web Data Science
2. Ethics, Law, and Responsible Data Collection
3. The Post-API Age
4. Data Formats: XML and JSON
5. Web Architecture and Protocols

**Part II — Documents**

6. Parsing Static Web Pages
7. Archived Web Pages and the Wayback Machine
8. Dynamic Web Pages with Selenium
9. Extracting Data from PDFs

**Part III — APIs**

10. Introduction to APIs: Wikipedia
11. Government Data APIs
12. Social and Media Platform APIs
13. AI and Language Model APIs

**Part IV — Practice**

14. Automating Data Collection
15. Research Design with Web Data

**Appendices**
- Companion Notebooks
- AI Coauthorship and Responsible Disclosure
- Where to Go from Here

## Building the Book

This book is written in [Quarto](https://quarto.org/). To build it locally:

### Prerequisites

- [Quarto 1.4+](https://quarto.org/docs/get-started/)
- Python 3.14; 3.13 also works (the [Anaconda](https://www.anaconda.com/download) distribution is recommended)
- Jupyter (`pip install jupyter`) — Quarto uses it to process the book's executable code cells

### Python dependencies

The code blocks in the book reference these libraries. Most students will not need all of them at once; install as you work through each chapter:

```bash
pip install requests beautifulsoup4 lxml pandas numpy scipy \
            matplotlib seaborn selenium pypdf nltk \
            scapy dnspython praw spotipy atproto Mastodon.py \
            openai anthropic
conda install -c conda-forge gensim   # chapter 7; PyPI has no Python 3.14 build of gensim yet
```

### Build commands

```bash
# Preview the book locally (live reload)
quarto preview

# Render the book (HTML)
quarto render
```

The book is currently configured for HTML output plus downloadable
companion notebooks. PDF output via LaTeX is a possible future addition;
it would require `quarto install tinytex` and a `pdf` entry under
`format:` in `_quarto.yml`.

By default, code blocks are not executed (`eval: false` in `_quarto.yml`). Students are expected to run code themselves in Jupyter Notebooks. This design choice reflects a pedagogical commitment: running code, encountering errors, and debugging them is where the learning happens.

## Repository Structure

```
Web-Data-Science-Book/
├── _quarto.yml                  # Quarto project configuration
├── index.qmd                    # Preface
├── ch-01-introduction.qmd       # Chapter source files
├── ch-02-ethics.qmd
├── ...
├── ch-15-research-design.qmd
├── appendix-notebooks.qmd       # Index of companion notebooks
├── appendix-ai-disclosure.qmd
├── appendix-further.qmd
├── notebooks/                   # Companion Jupyter notebooks (generated from the chapters; don't edit)
├── images/                      # Figures, one folder per chapter, each with provenance.json
├── tools/                       # Maintenance scripts (notebooks, prose lint, the screenshot toolkit)
├── references.bib               # BibTeX bibliography
├── docs/                        # Project records: AARs, plans, decision log, hand-off note
├── .github/                     # Issue forms, the pull request template, and CI checks
├── CONTRIBUTING.md              # How to report a problem or change the book
├── AGENTS.md                    # Style guide and instructions for AI agents and contributors
├── CLAUDE.md                    # Imports AGENTS.md, for Claude Code
├── LICENSE                      # CC BY-NC-SA 4.0
└── README.md
```

`quarto render` writes the rendered book to `book/`, which is not kept in the repository.

## Companion Resource: The Missing Manual

The book references the *[Missing Manual for Information Scientists](https://cuinfoscience.github.io/INFO-Missing-Manual/)* throughout for foundational computing skills (Jupyter, debugging, regex, scripting, version control, secrets management, and more). The two books are designed to complement each other: this book focuses on web-data-specific techniques while delegating general computing skills to the *Missing Manual*.

## Pedagogical Approach

Each chapter follows a consistent structure:

1. **Learning objectives** in a callout block
2. **Conceptual motivation** — why this matters
3. **Library/framework introduction** — what tools you will use
4. **Guided tutorial** with narrative code blocks
5. **Exercises**: Recommended Exercises (one guided build of 5–7 steps, whose code cells hold only prompts) and Additional Exercises (open-ended, ending with a graduate extension for INFO 5617 students)
6. **Social history and public interest** sidebar
7. **Common debugging issues**
8. **Key takeaways**
9. **Further reading**

The book uses second person ("you") and addresses the reader as a student learning these skills. Code blocks include comments explaining each line and expected outputs. Cross-references to other chapters use Quarto's `@sec-` syntax; cross-references to the *Missing Manual* appear in `::: {.callout-tip}` blocks.

## Contributing

Contributions are welcome, and first-time contributors are the reason this section exists. **Start with [CONTRIBUTING.md](CONTRIBUTING.md)**: it walks through each step, in the browser or on your computer.

- **Report a problem or an idea**: [choose an issue form](https://github.com/cuinfoscience/Web-Data-Science-Book/issues/new/choose). *Something is wrong* is for errors, dead links, and outdated screenshots; a *Gap report* is for anything missing or unclear that stopped you; a *Suggestion* is for anything that would make the book better. Every chapter page links to the forms (**Report an issue**).
- **Fix it yourself**: open a pull request that changes the chapter's `.qmd` file, not the generated notebooks. **Edit this page** on any chapter page opens the file in GitHub's editor. The pull request template asks for the location, the problem, why it matters, and your change.
- **Larger contributions**: open a [discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions) first to coordinate.

Students in INFO 4617/5617 contribute as part of the course; its [revision framework](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/handouts/common/revision-framework.md) explains how. [`AGENTS.md`](AGENTS.md) is the full style guide, for anyone, human or AI, extending the book.

## For AI Agents

Instructions for AI coding agents — Claude Code, Codex, and others — are in [`AGENTS.md`](AGENTS.md). If your agent looks for its own instructions file (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, and so on), point it at `AGENTS.md`: the repository keeps one set of instructions, and `CLAUDE.md` only imports it.

Project records are in [`docs/`](docs/): after-action reports, plans and roadmaps, the decision log ([`docs/decisions.md`](docs/decisions.md)), and the hand-off note ([`docs/handoff.md`](docs/handoff.md)) that says where work stands. Read the hand-off note before starting, and update it when you stop.

## AI Disclosure

Portions of this book were drafted with the assistance of large language model tools, including Claude. All content has been reviewed, edited, and verified by the author. See the [AI Coauthorship and Responsible Disclosure appendix](appendix-ai-disclosure.qmd) for the full disclosure statement and a discussion of responsible AI use in academic writing.

## Citation

If you use this book in teaching or research, please cite:

> Keegan, B. C. (2026). *Web Data Science: Retrieving, Parsing, and Analyzing Data from the Web with Python*. Department of Information Science, University of Colorado Boulder. <https://github.com/cuinfoscience/Web-Data-Science-Book>

## License

This book is released under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE) (CC BY-NC-SA 4.0). You are free to share and adapt the materials — including for teaching at other institutions — with attribution, for noncommercial purposes, under the same license terms.

## Acknowledgements

This book grew out of the INFO 4871/5871 Web Data Science course at the University of Colorado Boulder. It has benefited from the questions, frustrations, and insights of many cohorts of students. The author also gratefully acknowledges the journalists, researchers, and civic technologists whose work demonstrates why web data fluency matters for the public interest.

AI tools, chiefly Anthropic's Claude, helped draft and revise the book's text, code, and tooling, under the author's direction and review; the [AI Coauthorship and Responsible Disclosure appendix](https://cuinfoscience.github.io/Web-Data-Science-Book/appendix-ai-disclosure.html) describes how.
