#!/usr/bin/env python3
"""Generate companion Jupyter notebooks from the book's chapter sources.

Each ch-*.qmd file is converted to notebooks/<same-stem>.ipynb:
prose becomes Markdown cells, ```{python} blocks become (unexecuted)
code cells. Quarto-specific syntax that Jupyter cannot render —
callout fences, heading anchors, and figure attributes and
cross-references — is stripped or simplified so the notebooks read
cleanly on their own. A chapter cross-reference, `@sec-ethics`, becomes
a link to that chapter in the published book (in a code comment, the
chapter's name alone, "Chapter 2"), and a citation from
`references.bib`, `[@key]` or `@key`, becomes author and year, as the
book prints them.

Run from the repository root after editing any chapter's code:

    python tools/make_notebooks.py

The script is deterministic: regenerating without chapter changes
produces byte-identical notebooks, so `git status` shows drift. It exits
with an error when a figure or an @fig- reference is left unconverted,
which would show as a broken image in the notebook.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "notebooks"

BOOK_URL = "https://cuinfoscience.github.io/Web-Data-Science-Book/"

HEADER_TEMPLATE = (
    "*Companion notebook for* **{title}**, *from* [Web Data Science]({book_url}) "
    "*by Brian C. Keegan (INFO 4617/5617, University of Colorado Boulder).*\n\n"
    "*Generated from `{source}` — the book chapter is the authoritative version. "
    "Code cells are provided unexecuted: run them yourself, and expect to install "
    "the chapter's libraries and supply your own API keys where noted. "
    "Licensed CC BY-NC-SA 4.0.*"
)


def strip_quarto_syntax(markdown: str) -> str:
    """Remove Quarto-only syntax that renders as noise in Jupyter."""
    lines = []
    for line in markdown.split("\n"):
        # Drop callout/div fences (::: {.callout-tip} ... :::) but keep
        # their inner content, which is ordinary markdown.
        if re.match(r"^\s*:::+\s*(\{.*\})?\s*$", line):
            continue
        # Strip heading anchors/attributes: "# Title {#sec-x}" -> "# Title"
        line = re.sub(r"^(#+ .*?)\s*\{[^}]*\}\s*$", r"\1", line)
        lines.append(line)
    text = "\n".join(lines)
    # Collapse the blank runs left behind by removed fences.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Quarto figures: ![caption](images/...){#fig-label .lightbox fig-alt="..."}
# A caption may hold code spans and balanced brackets, as Pandoc allows:
# `<![CDATA[ … ]]>` inside backticks does not end the caption.
CAPTION = r"(?:`[^`]*`|\[[^\[\]`]*\]|[^\[\]`])*"
FIGURE_RE = re.compile(r"!\[(" + CAPTION + r")\]\((images/[^)\s]+)\)(?:\{([^}]*)\})?")


def figure_numbers(text: str, chapter: int) -> dict:
    """{label: "Figure N.M"} for the chapter's figures, numbered as Quarto numbers them."""
    numbers = {}
    for match in FIGURE_RE.finditer(text):
        label = re.search(r"#(fig-[\w-]+)", match.group(3) or "")
        if label:
            numbers[label.group(1)] = f"Figure {chapter}.{len(numbers) + 1}"
    return numbers


def convert_figures(text: str, chapter: int, numbers: dict = None) -> str:
    """Rewrite Quarto figures and @fig- references for a standalone notebook.

    A downloaded notebook has no images/ folder beside it, so figure
    paths point at the published book instead. Quarto's attribute block
    would show as literal text in Jupyter, so it becomes plain alt text
    plus a visible caption, and each @fig- reference becomes the number
    Quarto gives that figure in the book ("Figure 7.2"). `numbers` maps
    every chapter's labels, so a reference to another chapter's figure
    converts too.
    """
    numbers = dict(numbers or {}, **figure_numbers(text, chapter))

    def replace(match):
        caption, path, attrs = match.group(1), match.group(2), match.group(3) or ""
        alt = re.search(r'fig-alt="([^"]*)"', attrs)
        label = re.search(r"#(fig-[\w-]+)", attrs)
        image = f"![{alt.group(1) if alt else caption}]({BOOK_URL}{path})"
        if not label:
            return image
        return f"{image}\n\n*{numbers[label.group(1)]}: {caption}*"

    text = FIGURE_RE.sub(replace, text)
    return re.sub(r"@(fig-[\w-]+)", lambda m: numbers.get(m.group(1), m.group(0)), text)


LATEX_ACCENTS = {"\\'": "\u0301", '\\"': "\u0308", "\\`": "\u0300", "\\^": "\u0302", "\\~": "\u0303"}
LATEX_LETTERS = {"\\ss": "ß", "\\AA": "Å", "\\aa": "å", "\\o": "ø", "\\O": "Ø"}


def bib_text(value: str) -> str:
    """A BibTeX field as plain text: accents resolved, braces dropped."""
    import unicodedata
    for macro, letter in LATEX_LETTERS.items():
        value = re.sub(r"\{" + re.escape(macro) + r"\}", letter, value)
    for macro, mark in LATEX_ACCENTS.items():
        value = re.sub(r"\{" + re.escape(macro) + r"(\w)\}", lambda m: m.group(1) + mark, value)
    value = value.replace("\\&", "&").replace("{", "").replace("}", "")
    return unicodedata.normalize("NFC", value)


def read_bib(path: Path) -> dict:
    """{key: "Lazer et al." , ...} and years, from references.bib: (names, year) per key."""
    entries = {}
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"^@\w+\{([^,\s]+),", text, re.M):
        key, start = match.group(1), match.end()
        end = text.find("\n@", start)
        body = text[start:end if end != -1 else len(text)]
        author = re.search(r"^\s*author\s*=\s*\{(.*)\},?\s*$", body, re.M)
        year = re.search(r"^\s*year\s*=\s*\{?(\d{4})", body, re.M)
        if not (author and year):
            continue
        raw = author.group(1)
        if raw.startswith("{") and raw.endswith("}"):   # an organization, kept whole
            names = [bib_text(raw)]
        else:
            names = [bib_text(n.split(",")[0].strip()) for n in raw.split(" and ")]
        if len(names) == 1:
            who = names[0]
        elif len(names) == 2:
            who = f"{names[0]} and {names[1]}"
        else:
            who = f"{names[0]} et al."
        entries[key] = (who, year.group(1))
    return entries


def section_links(root: Path) -> dict:
    """{"sec-ethics": "[Chapter 2](…ch-02-ethics.html)", …}, as Quarto numbers chapters and appendices."""
    links = {}
    config = (root / "_quarto.yml").read_text(encoding="utf-8")
    appendices = re.findall(r"^\s+- (appendix-[\w-]+\.qmd)", config.split("appendices:", 1)[-1], re.M)
    files = [("Chapter " + str(int(re.match(r"ch-(\d+)", q.name).group(1))), q)
             for q in sorted(root.glob("ch-*.qmd"))]
    files += [(f"Appendix {chr(ord('A') + i)}", root / name) for i, name in enumerate(appendices)]
    for label_text, qmd in files:
        if not qmd.exists():
            continue
        label = re.search(r"^# .*\{#(sec-[\w-]+)\}", qmd.read_text(encoding="utf-8"), re.M)
        if label:
            links[label.group(1)] = f"[{label_text}]({BOOK_URL}{qmd.stem}.html)"
    return links


CODE_SPAN = re.compile(r"(`+)(?:.(?!\1))*?.?\1", re.S)
BRACKET_CITE = re.compile(r"\[([^\[\]]*?-?@[^\[\]]*)\]")
NARRATIVE_CITE = re.compile(r"(?<![\w@.\-/])@([A-Za-z][\w-]*\d{4}[\w]*)")


def convert_references(prose: str, links: dict, bib: dict) -> str:
    """Chapter references and citations in Markdown prose, outside code spans."""

    def bracket(match):
        parts = []
        for part in match.group(1).split(";"):
            cite = re.fullmatch(r"\s*(.*?)(-?)@([\w-]+)(.*?)\s*", part, re.S)
            if not cite or cite.group(3) not in bib:
                return match.group(0)
            prefix, suppress, key, locator = cite.groups()
            who, year = bib[key]
            parts.append(f"{prefix}{'' if suppress else who + ' '}{year}{locator}")
        return "(" + "; ".join(parts) + ")"

    def narrative(match):
        key = match.group(1)
        if key not in bib:
            return match.group(0)
        who, year = bib[key]
        return f"{who} ({year})"

    def outside_code(text):
        text = re.sub(r"@(sec-[\w-]+)", lambda m: links.get(m.group(1), m.group(0)), text)
        text = BRACKET_CITE.sub(bracket, text)
        return NARRATIVE_CITE.sub(narrative, text)

    pieces, pos = [], 0
    for span in CODE_SPAN.finditer(prose):
        pieces.append(outside_code(prose[pos:span.start()]))
        pieces.append(span.group(0))
        pos = span.end()
    pieces.append(outside_code(prose[pos:]))
    return "".join(pieces)


def name_sections(code: str, links: dict) -> str:
    """Chapter references in a code cell's comments, as the chapter's name alone ("Chapter 2"), with no link."""
    def name(match):
        link = links.get(match.group(1))
        return re.match(r"\[(.*?)\]", link).group(1) if link else match.group(0)
    return re.sub(r"@(sec-[\w-]+)", name, code)


def split_at_sections(prose: str) -> list:
    """Split a prose run into one markdown cell per ## section.

    Keeps notebooks navigable: each chapter section gets its own cell
    instead of long prose runs collapsing into one giant cell.
    """
    parts = re.split(r"(?=^## )", prose, flags=re.M)
    return [p.strip() for p in parts if p.strip()]


def qmd_to_cells(text: str, links: dict = None, bib: dict = None) -> list:
    """Split chapter text into alternating markdown and code cells."""
    cells = []
    pattern = re.compile(r"^```\{python\}\s*$(.*?)^```\s*$", re.M | re.S)
    pos = 0
    for match in pattern.finditer(text):
        prose = convert_references(strip_quarto_syntax(text[pos:match.start()]), links or {}, bib or {})
        for part in split_at_sections(prose):
            cells.append(("markdown", part))
        code = match.group(1).strip("\n")
        if code.strip():
            cells.append(("code", code))
        pos = match.end()
    tail = convert_references(strip_quarto_syntax(text[pos:]), links or {}, bib or {})
    for part in split_at_sections(tail):
        cells.append(("markdown", part))
    return cells


def leftovers(nb: dict) -> list:
    """What a conversion missed: @fig- and @sec- references and images/ paths left in the Markdown.

    A figure the pattern above did not match would show as a broken image
    and an unresolved reference; a chapter reference to a label no chapter
    defines would show as raw text. References inside code spans are left
    as written on purpose.
    """
    found = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        source = "".join(cell["source"])
        found += [f"unconverted reference {m}" for m in re.findall(r"@fig-[\w-]+", source)]
        prose = CODE_SPAN.sub("", source)
        found += [f"unconverted reference {m}" for m in re.findall(r"@sec-[\w-]+", prose)]
        found += [f"unconverted image path {m}" for m in re.findall(r"\]\((images/[^)\s]*)", source)]
    return found


def make_notebook(qmd_path: Path, numbers: dict = None, links: dict = None, bib: dict = None) -> dict:
    text = qmd_path.read_text(encoding="utf-8")
    # The chapters' "Companion Notebook" download callout is navigation
    # for the rendered book; inside the notebook itself it is noise.
    text = re.sub(
        r"^::: \{\.callout-tip\}\n## Companion Notebook\n.*?\n:::\n",
        "",
        text,
        flags=re.M | re.S,
    )
    chapter = int(re.match(r"ch-(\d+)", qmd_path.stem).group(1))
    text = convert_figures(text, chapter, numbers)
    title_match = re.search(r"^# (.+?)(?:\s*\{[^}]*\})?\s*$", text, re.M)
    title = title_match.group(1).strip() if title_match else qmd_path.stem

    header = HEADER_TEMPLATE.format(
        title=title, book_url=BOOK_URL, source=qmd_path.name
    )
    cells = [("markdown", header)] + qmd_to_cells(text, links, bib)

    nb_cells = []
    for kind, source in cells:
        # nbformat stores sources as lists of lines with trailing newlines.
        source_lines = source.splitlines(keepends=True)
        if kind == "markdown":
            nb_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": source_lines,
            })
        else:
            source_lines = name_sections(source, links or {}).splitlines(keepends=True)
            nb_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": source_lines,
            })

    return {
        "cells": nb_cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    chapters = sorted(ROOT.glob("ch-*.qmd"))
    if not chapters:
        raise SystemExit("No ch-*.qmd files found; run from the repository root.")
    # Every chapter's figure numbers first, so a reference to another
    # chapter's figure converts as well as one to the chapter's own.
    numbers = {}
    for qmd in chapters:
        chapter = int(re.match(r"ch-(\d+)", qmd.stem).group(1))
        numbers.update(figure_numbers(qmd.read_text(encoding="utf-8"), chapter))
    links = section_links(ROOT)
    bib = read_bib(ROOT / "references.bib")
    problems = []
    for qmd in chapters:
        nb = make_notebook(qmd, numbers, links, bib)
        out = OUT_DIR / (qmd.stem + ".ipynb")
        out.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
        print(f"{out.relative_to(ROOT)}: {len(nb['cells'])} cells ({n_code} code)")
        problems += [f"{qmd.name}: {p}" for p in leftovers(nb)]
    if problems:
        print("\nFigures the notebooks could not convert:", *problems, sep="\n  ")
        raise SystemExit(
            "Check each figure's caption and label in its chapter: an unbalanced "
            "bracket, or a reference to a label no chapter defines."
        )


if __name__ == "__main__":
    main()
