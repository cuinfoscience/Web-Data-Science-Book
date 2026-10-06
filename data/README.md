# Data files

Files that the chapters' code reads over the web, so a reader needs no extra
package or download step to get them.

| File | Read by | What it is |
|---|---|---|
| `stopwords-en.txt` | Chapter 7, "Document Similarity with Bag-of-Words" | 198 English stopwords, one per line: NLTK's English list (the `stopwords` corpus in [nltk_data](https://github.com/nltk/nltk_data)), copied unchanged on 2026-10-02. NLTK took it from the Snowball project's stopword lists, by way of PostgreSQL, and has added to it since. |
| `ch-09/*.pdf` | Chapter 9, from "This Chapter's Files" on | Copies of the City of Boulder's PDFs from its records portal, [documents.bouldercolorado.gov](https://documents.bouldercolorado.gov/WebLink/Browse.aspx?id=194345&dbid=0&repo=LF8PROD2), downloaded on 2026-10-06 and saved unchanged under readable names: the Finance Department's seven year-end revenue reports, 2018 to December 2024 (`revenue-report-YYYY[-12].pdf`), and the City Council's signed minutes of 13 meetings (`council-minutes-YYYY-MM-DD.pdf`). For the minutes: one December meeting each from 2018 and 2019, whose scanned minutes run to 5 MB apiece; every December meeting from 2020 to 2024 (one in 2021, two in each other year); and December 5 and 19, 2000, which the portal holds as page images and turned into PDFs on request. Public records; the chapter keeps copies so that a class doesn't send its requests to the city's server. |
| `ch-09/manifest.csv` | Chapter 9, "Getting the Files" | One row per PDF: the portal's document number (`docid`), its name and folder there, its size, its SHA-256 hash, the address it was downloaded from, when, and a `note` where a file needs one. A reader can download any of them again and compare hashes, except the two minutes from 2000: the portal builds a new PDF for every download, so their hashes never match, and their `source_url` is the record's page in the portal's viewer. |
| `ch-09/boulder-ca-bundle.pem` | Chapter 9, "Getting the Files" | Certificates for `verify=` in `requests`: certifi's root certificates plus the intermediate certificate (DigiCert Global G2 TLS RSA SHA256 2020 CA1) that the portal's server leaves out of its handshake. `ch-09/make_ca_bundle.py` builds it; run it again when certifi updates or the city changes its certificate. |

The chapters fetch these files from
`https://raw.githubusercontent.com/cuinfoscience/Web-Data-Science-Book/main/data/`.
That host serves no robots.txt (checked 2026-10-02), so a script may read
from it. Renaming or moving a file here breaks the chapters that read it, so
change the chapters in the same pull request.
