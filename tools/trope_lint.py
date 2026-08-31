#!/usr/bin/env python3
"""Flag significance-verdict prose in the book's chapters.

The significance verdict is a sentence or clause whose entire content is
that the adjacent evidence means something: "the distinction matters,"
"the variety is diagnostic," "that is the point," "the tagline is earned."
It regenerates under endlessly novel strings, so this scanner catches the
common stems while claude.md's prose-safeguards section states the rule
that actually governs: never assert significance the consequence should
carry, and delete-test every paragraph-closing sentence.

Hits are flags for the delete test, not failures. "Status codes matter
because CDX records every capture attempt" survives the test — the
because-clause carries content. "The differences matter" directly before
a list of the differences does not. The scanner always exits 0; it
informs judgment rather than replacing it.

Run from the repository root:

    python tools/trope_lint.py              # scan every chapter
    python tools/trope_lint.py ch-03*.qmd   # scan specific files
"""
import glob
import re
import sys
from pathlib import Path

FAMILIES = {
    "significance verdict (X matters)":
        r"\b(distinction|difference|differences|gap|detail|point|choice|order"
        r"|framing|naming|timing|asymmetry|contrast) matters?\b"
        r"|\bmatters?,? because\b",
    "demonstrative applause (That is the point / That is X rather than Y)":
        r"\bThat is the point\b"
        r"|\bThat is [a-z]+ as a [a-z]+ (property|practice|habit)\b"
        r"|\bwhich is,? for this (chapter|book),? the lesson\b",
    "verdict predicates (is diagnostic / is telling / is the tell)":
        r"\bis diagnostic\b|\bis telling\b|\bis the tell\b",
    "verdict verbs on own material (earned / earns its place)":
        r"\bearn(s|ed)? (its|their) place\b|\b(tagline|name|title) is earned\b",
    "counting verdict (Three X, three Y)":
        r"\b(Two|Three|Four|Five) [a-z]+, (two|three|four|five) [a-z]+,"
        r" and the [a-z]+ matter",
    "banned figures (course list)":
        r"\bthe arc remains\b|\bload-bearing\b|\bseam to follow\b"
        r"|\bthe gap matters\b",
    "aphoristic antithesis close (rather than a press release)":
        r"rather than a (press release|policy statement|slogan|talking point)\b",
    "filler significance (it is worth noting / pausing)":
        r"\b[Ii]t is worth (noting|pausing|remembering|emphasi[sz]ing)\b",
}

# Prose only: strip fenced code blocks so comments and code never match.
FENCE = re.compile(r"^```.*?^```\s*$", re.M | re.S)


def scan(path):
    raw = Path(path).read_text()
    # Blank out fenced blocks but keep line numbers aligned.
    def blank(m):
        return "\n" * m.group(0).count("\n")
    prose = FENCE.sub(blank, raw)
    hits = []
    for family, pattern in FAMILIES.items():
        for m in re.finditer(pattern, prose):
            line = prose[:m.start()].count("\n") + 1
            start = max(0, m.start() - 45)
            snippet = " ".join(prose[start:m.end() + 45].split())
            hits.append((line, family, snippet))
    return sorted(hits)


def main():
    targets = sys.argv[1:] or sorted(glob.glob("ch-*.qmd"))
    total = 0
    for path in targets:
        hits = scan(path)
        if not hits:
            continue
        print(f"== {path}: {len(hits)} flag(s)")
        for line, family, snippet in hits:
            print(f"   L{line} [{family}]")
            print(f"        ...{snippet}...")
        total += len(hits)
    if total:
        print(f"\n{total} flag(s). Each is a candidate for the delete test "
              "(claude.md, 'Prose safeguards'), not an automatic failure.")
    else:
        print("No significance-verdict flags found.")


if __name__ == "__main__":
    main()
