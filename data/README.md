# Data files

Plain-text files that the chapters' code reads over the web, so a reader needs
no extra package or download step to get them.

| File | Read by | What it is |
|---|---|---|
| `stopwords-en.txt` | Chapter 7, "Document Similarity with Bag-of-Words" | 198 English stopwords, one per line: NLTK's English list (the `stopwords` corpus in [nltk_data](https://github.com/nltk/nltk_data)), copied unchanged on 2026-10-02. NLTK took it from the Snowball project's stopword lists, by way of PostgreSQL, and has added to it since. |

The chapters fetch these files from
`https://raw.githubusercontent.com/cuinfoscience/Web-Data-Science-Book/main/data/`.
That host serves no robots.txt (checked 2026-10-02), so a script may read
from it. Renaming or moving a file here breaks the chapters that read it, so
change the chapters in the same pull request.
