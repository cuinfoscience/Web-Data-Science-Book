# Wikipedia lead sections, 2004–2026

The lead sections (the text before the first heading) of five English Wikipedia articles, as they stood at 00:00 UTC on January 1 of each year from 2004 to 2026, plus each article's current revision. The articles are Barack Obama, Hillary Clinton, Donald Trump, Joe Biden and Kamala Harris. Collected on 2026-11-09 for chapter 13 of *Web Data Science* and week 13's lab.

| File | What it holds |
|---|---|
| `revisions.csv` | One row per article and year, `current` included. Each row gives the revision in place at that moment: `revid`, `timestamp`, `size` in bytes, and the saved `html_file`. `revid` is empty where the title had no revision yet. |
| `html/` | Each revision's lead as HTML, from `action=parse&oldid=REVID&prop=text&section=0`. |
| `leads.csv` | Each lead's text, with its length in `words`: the HTML's `<p>` paragraphs, read with BeautifulSoup by the chapter's `lead_text()`. Tables, reference marks and hatnotes are left out. So are two kinds of leftover from rendering one section of an old revision today: links to templates that no longer exist, such as `Template:Active editnotice`, and error messages (`class="error"`), such as a "Cite error" for footnotes whose list is further down the article, or `[invalid input: 'ɵ']` in a pronunciation. |
| `lead-vectors.npy` | One embedding per row of `leads.csv` (116 × 2,048, float32), from `nvidia/nemotron-3-embed-1b:free` through OpenRouter on 2026-11-09, in six requests of 20 leads or fewer. Each row is scaled to length 1. |
| `lead-vectors-rows.csv` | The title and year of each row of `lead-vectors.npy`. |

**How it was collected:**
- For each title and year, `action=query&prop=revisions&rvstart=YYYY-01-01T00:00:00Z&rvdir=older&rvlimit=1` found the revision; then `action=parse` returned its lead.
- The requests were paced at one a second, with a User-Agent. Wikipedia still answered 429 (Too Many Requests) many times, asking for waits of up to about 40 seconds, so collecting all 116 snapshots took about 30 minutes.

**What's missing:**
- No revision existed yet under the title for Barack Obama on 2004-01-01, Donald Trump on 2004-01-01, or Kamala Harris on 2004-01-01 and 2005-01-01.
- For Donald Trump, this follows the page history of the current title. Wikipedia's history of a title doesn't always reach back to the article's first version, for example when pages were moved or merged.

**License:** Wikipedia's text is © its contributors, under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Each revision's authors are listed in its history, at `https://en.wikipedia.org/w/index.php?oldid=REVID&action=history`. These copies keep that license.
