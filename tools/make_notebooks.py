#!/usr/bin/env python3
"""Generate companion Jupyter notebooks from the book's chapter sources.

Each ch-*.qmd file is converted to notebooks/<same-stem>.ipynb:
prose becomes Markdown cells, ```{python} blocks become (unexecuted)
code cells. Quarto-specific syntax that Jupyter cannot render —
callout fences and heading anchors — is stripped or simplified so the
notebooks read cleanly on their own.

Run from the repository root after editing any chapter's code:

    python tools/make_notebooks.py

The script is deterministic: regenerating without chapter changes
produces byte-identical notebooks, so `git status` shows drift.
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


def make_notebook(qmd_path: Path) -> dict:
    text = qmd_path.read_text(encoding="utf-8")
    # The chapters' "Companion Notebook" download callout is navigation
    # for the rendered book; inside the notebook itself it is noise.
    text = re.sub(
        r"^::: \{\.callout-tip\}\n## Companion Notebook\n.*?\n:::\n",
        "",
        text,
        flags=re.M | re.S,
    )
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
    for qmd in chapters:
        nb = make_notebook(qmd)
        out = OUT_DIR / (qmd.stem + ".ipynb")
        out.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
        print(f"{out.relative_to(ROOT)}: {len(nb['cells'])} cells ({n_code} code)")


if __name__ == "__main__":
    main()
