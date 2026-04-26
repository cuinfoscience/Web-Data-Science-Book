# Web Data Science

A Quarto textbook for **INFO 4613 / 5613: Web Data Science** at the University of Colorado Boulder, Department of Information Science.

This book teaches advanced undergraduates and master's students how to retrieve, parse, and analyze data from the web using Python. It covers static and dynamic web scraping, structured data formats (XML, JSON), the protocol stack (TCP/IP, DNS, HTTP), document extraction (HTML, archived pages, PDFs), and authenticated APIs (Wikipedia, U.S. Census, FRED, FEC, Reddit, Spotify, Bluesky, Mastodon, OpenAI, Anthropic), along with automation via GitHub Actions and a capstone treatment of research design.

A theoretical thread on the **post-API age** — the structural pressures of *enclosure*, *exemption*, and *erosion* shaping access to web data, and the counter-values of *openness*, *oversight*, and *ownership* — runs throughout the book.

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
- AI Coauthorship and Responsible Disclosure
- Where to Go from Here

## Building the Book

This book is written in [Quarto](https://quarto.org/). To build it locally:

### Prerequisites

- [Quarto 1.4+](https://quarto.org/docs/get-started/)
- Python 3.10+ (the [Anaconda](https://www.anaconda.com/download) distribution is recommended)
- LaTeX (for PDF output) — install via [TinyTeX](https://yihui.org/tinytex/) with `quarto install tinytex`

### Python dependencies

The code blocks in the book reference these libraries. Most students will not need all of them at once; install as you work through each chapter:

```bash
pip install requests beautifulsoup4 pandas matplotlib seaborn \
            selenium webdriver-manager pypdf gensim nltk \
            scapy dnspython praw spotipy atproto Mastodon.py \
            openai anthropic
```

### Build commands

```bash
# Preview the book locally (live reload)
quarto preview

# Render all configured formats
quarto render

# Render HTML only
quarto render --to html

# Render PDF only
quarto render --to pdf
```

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
├── appendix-ai-disclosure.qmd
├── appendix-further.qmd
├── references.bib               # BibTeX bibliography
├── book/                        # Rendered book output
├── claude.md                    # Editorial guidelines for AI-assisted authoring
├── CLAUDE_CODE_EXPANSION_PROMPT.md  # Chapter expansion instructions
├── LICENSE                      # MIT
└── README.md
```

## Companion Resource: The Missing Manual

The book references the *[Missing Manual for Information Scientists](https://www.brianckeegan.com/ParatechnicalComputingHandbook/book/)* throughout for foundational computing skills (Jupyter, debugging, regex, scripting, version control, secrets management, and more). The two books are designed to complement each other: this book focuses on web-data-specific techniques while delegating general computing skills to the *Missing Manual*.

## Pedagogical Approach

Each chapter follows a consistent structure:

1. **Learning objectives** in a callout block
2. **Conceptual motivation** — why this matters
3. **Library/framework introduction** — what tools you will use
4. **Guided tutorial** with narrative code blocks
5. **Exercises** (4–5 per chapter, graduated from guided to open-ended)
6. **Social history and public interest** sidebar
7. **Common debugging issues**
8. **Key takeaways**
9. **Further reading**

The book uses second person ("you") and addresses the reader as a student learning these skills. Code blocks include comments explaining each line and expected outputs. Cross-references to other chapters use Quarto's `@sec-` syntax; cross-references to the *Missing Manual* appear in `::: {.callout-tip}` blocks.

## Contributing

Contributions are welcome. If you find an error, have a suggestion, or want to propose an exercise:

- **Errata and small fixes**: open an [issue](https://github.com/cuinfoscience/Web-Data-Science-Book/issues) or a pull request
- **Larger contributions**: open a [discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions) first to coordinate

The `claude.md` file documents editorial voice, formatting conventions, and chapter structure for anyone — human or AI — extending the book.

## AI Disclosure

Portions of this book were drafted with the assistance of large language model tools, including Claude. All content has been reviewed, edited, and verified by the author. See the [AI Coauthorship and Responsible Disclosure appendix](appendix-ai-disclosure.qmd) for the full disclosure statement and a discussion of responsible AI use in academic writing.

## Citation

If you use this book in teaching or research, please cite:

> Keegan, B. C. (2026). *Web Data Science: Retrieving, Parsing, and Analyzing Data from the Web with Python*. Department of Information Science, University of Colorado Boulder. <https://github.com/cuinfoscience/Web-Data-Science-Book>

## License

This book is released under the [MIT License](LICENSE). You are free to use, modify, and distribute the materials, including for teaching at other institutions, with appropriate attribution.

## Acknowledgements

This book grew out of the INFO 4871/4613 Web Data Science course at the University of Colorado Boulder. It has benefited from the questions, frustrations, and insights of many cohorts of students. The author also gratefully acknowledges the journalists, researchers, and civic technologists whose work demonstrates why web data fluency matters for the public interest.
