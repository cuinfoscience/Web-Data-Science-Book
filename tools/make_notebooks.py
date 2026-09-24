#!/usr/bin/env python3
"""Generate companion Jupyter notebooks from the book's chapter sources.

Each ch-*.qmd file is converted to notebooks/<same-stem>.ipynb:
prose becomes Markdown cells, ```{python} blocks become (unexecuted)
code cells. Quarto-specific syntax that Jupyter cannot render —
callout fences, heading anchors, and figure attributes and
cross-references — is stripped or simplified so the notebooks read
cleanly on their own.

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


def split_at_sections(prose: str) -> list:
    """Split a prose run into one markdown cell per ## section.

    Keeps notebooks navigable: each chapter section gets its own cell
    instead of long prose runs collapsing into one giant cell.
    """
    parts = re.split(r"(?=^## )", prose, flags=re.M)
    return [p.strip() for p in parts if p.strip()]


def qmd_to_cells(text: str) -> list:
    """Split chapter text into alternating markdown and code cells."""
    cells = []
    pattern = re.compile(r"^```\{python\}\s*$(.*?)^```\s*$", re.M | re.S)
    pos = 0
    for match in pattern.finditer(text):
        prose = strip_quarto_syntax(text[pos:match.start()])
        for part in split_at_sections(prose):
            cells.append(("markdown", part))
        code = match.group(1).strip("\n")
        if code.strip():
            cells.append(("code", code))
        pos = match.end()
    tail = strip_quarto_syntax(text[pos:])
    for part in split_at_sections(tail):
        cells.append(("markdown", part))
    return cells


def leftovers(nb: dict) -> list:
    """What a figure conversion missed: @fig- references and images/ paths left in the Markdown.

    Either one means a figure the pattern above did not match, so the
    notebook would show a broken image and an unresolved reference.
    """
    found = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        source = "".join(cell["source"])
        found += [f"unconverted reference {m}" for m in re.findall(r"@fig-[\w-]+", source)]
        found += [f"unconverted image path {m}" for m in re.findall(r"\]\((images/[^)\s]*)", source)]
    return found


def make_notebook(qmd_path: Path, numbers: dict = None) -> dict:
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
    cells = [("markdown", header)] + qmd_to_cells(text)

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
    problems = []
    for qmd in chapters:
        nb = make_notebook(qmd, numbers)
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
