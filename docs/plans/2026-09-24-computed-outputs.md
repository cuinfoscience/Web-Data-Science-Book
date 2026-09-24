# Computed figures and tables in the book: roadmap

**Status:** Proposed 2026-09-24. Not implemented. Two things have to happen before work starts: the maintainer's decisions in §9, and the end of the pause on chapter work (`docs/decisions.md`).

**In one paragraph.** The chapters show code but never its results, because `_quarto.yml` sets `execute: eval: false` for the whole book. This plan puts computed charts and DataFrame tables on the website and keeps the student notebooks free of outputs. Code re-runs only when code changes. Each chapter gets a small compute file for any code that runs. The compute file reads a dated snapshot of the data, never the network. Quarto freezes each compute file's results, keyed to that file's own text. The chapter embeds those results and runs nothing itself. A prose edit therefore runs nothing, and CI never runs book code. Ten tests of Quarto 1.10.18 shaped this design (§3). Two of them showed that freezing a chapter directly cannot meet the requirement.

## 1. The gap

- `_quarto.yml` sets `execute: eval: false`. `index.qmd` gives the reason: "Code blocks in this book are narrative … set to not execute automatically. You should run the code yourself." `appendix-notebooks.qmd` repeats it.
- A scan of the book's 284 code blocks found 22 that draw a chart, in 11 of the 15 chapters. Another 24 end by printing something from a DataFrame, such as `print(df.head())`. A reader sees `plt.show()` and no chart.
- Quarto can run code cells and put their figures and tables in the page, with captions, alt text, and cross-references ([Quarto: figures](https://quarto.org/docs/authoring/figures.html)).

## 2. Requirements

1. The website shows selected computed figures and HTML tables of DataFrames. They are numbered and cross-referenced like the book's other figures.
2. The notebooks in `notebooks/` stay free of outputs. Students run the code themselves.
3. Code re-runs only when code, or the data it reads, changes. A prose change never re-runs code.
4. Building the book never touches the network, and CI never runs book code.
5. Computed figures follow the book's figure rules: readable where shown, alt text, a dated caption, and recorded provenance for their data.

## 3. What Quarto does, tested

Tested on 2026-09-24 with a scratch two-chapter book: Quarto 1.10.18, Python 3.11, pandas 3.0.6, matplotlib 3.11.2. Each code cell appended a line to a log file when it ran. So "re-ran" in the table below was observed, not inferred.

| # | Setup | Change | Observed |
|---|---|---|---|
| 1 | The chapter runs its own code; `freeze: auto` | Prose only | Every cell in the chapter re-ran. Freeze keys on the whole file. |
| 2 | The chapter runs its own code; `freeze: true` | Prose only | Nothing re-ran, and the site kept showing the **old prose**. The frozen result stores the chapter's whole text. |
| 3 | The chapter runs its own code; `cache: true` (Jupyter Cache) | Prose, then code | After prose: nothing re-ran ("Notebook read from cache"). After code: it re-ran. The cache lives in `.jupyter_cache/`, which a fresh checkout does not have. |
| 4 | Code in a compute file (`computed/ch-01.qmd`); `freeze: auto` set for `computed/` only; the chapter embeds the results | Chapter prose, with a full render and with a single-file render | Nothing re-ran. |
| 5 | Same as 4 | The compute file's code | That file re-ran on the next full render. Nothing else did. |
| 6 | Same as 4, in a fresh copy that has `_freeze/`, with a Python that has Jupyter but not pandas or matplotlib | None | The figure and the table rendered from `_freeze/`. Nothing ran. |
| 7 | Same as 6, after an edit to the compute file without refreshing `_freeze/` | None | The render started running the code, then failed on the missing pandas import. An MD5 check run before the render caught the edit. |
| 8 | Tables through `embed` | — | Pandas' default HTML output came through as an **empty** table. A `Styler` came through empty too, and `Markdown(df.to_markdown())` stopped the render. Two forms worked: `HTML(df.to_html())`, and a plain `df.head()` after registering an HTML formatter. Both came through as a styled, numbered table. |
| 9 | Alt text | Set on the chapter's figure div, or in the compute cell (`fig-alt`) | On the div, it landed on the `<div>`, and the `<img>` had no alt. In the compute cell, it landed on the `<img>`. |
| 10 | `quarto render computed/ch-01.qmd` on its own | — | The file ran and left `computed/ch-01.ipynb` in the source tree, **with outputs**. |

More observations:
- The `hash` in a freeze file is the MD5 of the compute file. Checking that a freeze is current takes a few lines of code.
- Compute files were not published as pages. No notebook links or notebook previews appeared.
- The HTML of each embedded block carries a `data-notebook` attribute: the compute file's absolute path on the machine that built the book.
- Embedded figures came out at 1× resolution (569×411 pixels, with no `width` attribute). Figures run inside a chapter came out at 2×, with `width` and `height` set.

Rows 1 and 2 are why code that runs cannot stay in the chapters. A frozen chapter either re-runs all its code on every prose edit or publishes stale prose. Row 3 meets the requirement on one machine, but not in CI and not for a co-author. Rows 4 to 7 meet it everywhere.

## 4. Design: fetch, compute, show

```
fetch    rare · uses the network · run by hand       tools/compute fetch ch-05
           → data/ch-05/pageviews.json  + provenance: URL, time, User-Agent, status, sha256
compute  offline · seconds · re-runs only when its own text changes
           computed/ch-05.qmd    code cells only; freeze: auto; results in _freeze/ (committed)
show     every render · free
           ch-05-protocols.qmd   ::: {#fig-pageviews} {{< embed computed/ch-05.qmd#pageviews echo=true >}} caption :::
```

### 4.1 Fetch: a dated snapshot with provenance

A render that calls an API is slow, depends on rate limits and keys, and draws a different figure each time. The book instead shows a figure made from a dated snapshot of the data.

- The fetch sends the same request as the code the chapter shows, with the same URL and parameters. It identifies itself with the book's one User-Agent and follows its pacing. It should reuse `tools/shots` for identity, pacing, and provenance, not add a second HTTP client.
- It writes `data/ch-NN/<name>.json` (or `.csv`) and a provenance record like the screenshots' records: URL, time, User-Agent, HTTP status, and sha256.
- A fetch that needs an API key runs on the maintainer's machine. The key goes in neither the snapshot nor the provenance.
- This carries the earlier AAR's P1-2 ("counts in captions come from a recorded query") over to figures.

### 4.2 Compute: code-only files, frozen

- Each chapter gets one file, `computed/ch-NN.qmd`, that holds only code cells: a hidden setup cell, then one cell per figure or table.
- `computed/_metadata.yml` sets `execute: {eval: true, freeze: auto}` for that directory alone. Chapters keep `eval: false` and are never frozen, so their prose always renders fresh (row 2).
- The hidden setup cell (`#| include: false`) does four things:
  - It loads each snapshot by path and sha256: `data = load("data/ch-05/pageviews.json", sha256="…")`. Freeze sees only the compute file's text. With the hash written in that text, new data is a code change, and freeze notices it.
  - It blocks network access for the rest of the run, so compute cannot fetch.
  - It applies the book's matplotlib style (§6) and registers the DataFrame HTML formatter that row 8 needs.
  - It binds the names that the chapter's fetch code produces, `data` in ch-05. The plotting code then reads the same in the book and in the notebook.
- Figure and table cells get labels without a `fig-` or `tbl-` prefix, because the chapter's div numbers them. Alt text goes in the cell, as `fig-alt` (row 9).
- Commit `_freeze/computed/`. Quarto's documentation recommends committing frozen output. In the test, one compute file with one small figure froze to 68 KB.
- To refresh, run a full `quarto render`. It re-runs only the compute files whose text changed. Don't render a compute file on its own (row 10). Add `computed/*.ipynb` to `.gitignore`.

### 4.3 Show: the chapter embeds the results

```markdown
::: {#fig-pageviews}
{{< embed computed/ch-05.qmd#pageviews echo=true >}}

Daily views of the English Wikipedia article "University of Colorado Boulder",
January 2026, from the Wikimedia pageviews API (retrieved 2026-09-24).
:::
```

- The chapter owns the caption and the label, so editing either one runs nothing (row 4).
- `echo=true` shows the code that actually ran. The fetch code before it stays a narrative block (`eval: false`), because the compute file reads the snapshot instead.
- Tables work the same way, inside `::: {#tbl-…}`.
- Set `notebook-links: false` and `notebook-view: false` in `_quarto.yml`. The test produced no notebook links or previews anyway. Setting both keeps a later Quarto release from publishing a notebook that has outputs.

### 4.4 The notebooks stay free of outputs

- `tools/make_notebooks.py` builds notebooks from chapter text, never from executed notebooks. Every code cell it writes has `outputs: []`, and that stays true.
- New: the script resolves each `{{< embed computed/ch-NN.qmd#label … >}}` into a code cell holding that cell's source, minus its `#|` lines. Without this step, a notebook would show the shortcode as text and lose the plotting code. Hidden setup cells stay out of the notebooks.
- New check, `notebooks-clean`: it fails if any `.ipynb` in the repository, or in `book/` after a render, has outputs or execution counts.

## 5. Guardrails

| Guardrail | Stops | How | Where |
|---|---|---|---|
| Code runs only in compute files, and only they are frozen | Prose edits re-running code (rows 1 and 4) | Directory layout; `computed/_metadata.yml` | The repository's structure |
| Snapshots pinned by sha256 | Stale figures after new data, and data that changes unnoticed | `load(path, sha256=…)` in the setup cell | Compute files |
| No network during compute | A render that fetches; data with no record | A socket guard in the setup cell | Compute files |
| `freeze-current` check before the render | CI running book code (row 7) | The MD5 of each compute file must equal its `_freeze` hash | First step of `render.yml` and `publish.yml` |
| No plotting libraries in CI | A skipped check that turns into a fetch | Workflows install only Jupyter, as they do now | Workflows |
| `notebooks-clean` check | Outputs in student notebooks or in a published `.ipynb` | A scan for outputs and execution counts | `notebook-sync.yml`, and after the render |
| Figure checks | Figures that can't be read, have no date, or lack alt text | The `tools/shots` rules: legibility, alt text of 280–440 characters, captions dated against provenance | `tools/compute check` |
| Path filters | Checks running on pull requests that change none of their inputs | Run on `computed/**`, `data/**`, `_freeze/**`, and `ch-*.qmd` | Workflows |
| A pinned Quarto version | An update that changes how `embed` behaves (row 8) | `quarto-actions/setup` with `version:`; re-run the pilot's effect tests after an upgrade | Workflows |

Each guardrail gets a test that shows it firing:
- a stale compute file fails CI;
- a notebook with an output fails `notebooks-clean`;
- a network call during compute fails the render.

That is the done-rule from the AAR's P0-3.

### 5a. Alternatives considered

- **Freeze the chapters** (`freeze: auto` or `true`). This either fails requirement 3 or publishes stale prose (rows 1 and 2).
- **Jupyter Cache in the chapters.** It meets requirement 3 on one machine. A fresh checkout, in CI or on a co-author's machine, has no cache and re-runs every cell, network calls included. Committing `.jupyter_cache/` would add a SQLite database and executed notebooks to the repository: notebooks with outputs, and diffs no one can read.
- **Embed from executed `.ipynb` files.** Tables come through intact. But the repository then holds notebooks with outputs, diffs become unreadable, and freeze does not apply, so staleness needs its own check.
- **Images made by `tools/shots`.** A `render` recipe kind would run a script to make a PNG, then treat it like a screenshot: recipe, provenance, and legibility check. This route gives no HTML tables, and the code shown can drift from the code that ran. It is the fallback if `embed` proves brittle across Quarto releases.

## 6. Readable figures

The two-sided legibility rule in the AAR (P0-1) applies to computed figures too.
- **Too small.** In the book's 778-pixel column, a figure's text comes out at about `font_pt × 96/72 × min(1, 778 / css_width)` CSS pixels. Here `css_width` is the figure's rendered width, a little under `width_in × 96` because matplotlib trims the margins.
  - ch-05's plot as written (`figsize=(10, 4)` with matplotlib's 10-point default) rendered 953 CSS pixels wide in a test, so the column shrinks it and its text comes to 10.9 pixels. That is under the book's 11-pixel floor.
  - The book's style should set 11-point text on a figure 7 inches wide, which comes to about 14.7 pixels. The check computes this size from the rendered figure and fails anything under 11 pixels.
  - Embedded figures came out at 1× with no width attribute (§3). The pilot has to confirm the displayed width and set the resolution explicitly.
- **Too crammed.** Give each figure one idea. Label axes with units, and keep series few enough to tell apart. Keep tables to the rows and columns the text discusses: `df.head()`, not `df`.
- **Alt text** of 280–440 characters says what the figure shows, such as the trend and the peak, as for screenshots. It sits in the compute cell (row 9), so an edit to it re-runs that one file, offline and in seconds.
- **Dated captions** say "retrieved YYYY-MM-DD", and the check compares that date with the snapshot's provenance.

## 7. Teaching stance

Showing results changes a promise the preface makes. Proposed wording for the preface:

> Code blocks in this book are narrative: they are not run when the book is built. The exception is a block that draws a chart or builds a table. There the book shows the result that code produced from a dated snapshot of the data, so you know what to expect. Your own run will differ, because the data will have changed since. The companion notebooks come without outputs: running the code, seeing it fail, and debugging it is still where the learning happens.

- Show results only for figures and tables the text discusses. Other printed output, and the exercises, stay unexecuted.
- Where the book shows a table, `print(df.head())` becomes `df.head()`. That gives Jupyter's rich table, the same one students see in the notebooks. In a plain `.py` script a bare expression prints nothing, so say that at the chapter's first table.

## 8. Roadmap

Paused until the maintainer decides §9 and lifts the pause on chapter work.

- **M0: pilot on chapter 5.** One figure: daily pageviews, the block after "Now convert the response to a DataFrame and plot it". One table: `df.head()` of the same data.
  - Fetch the snapshot, write `computed/ch-05.qmd`, and embed its results. Teach `make_notebooks.py` to resolve embeds, add the checks, and render.
  - M0 is done when the maintainer has looked at the real figure and table in the rendered book, and each guardrail in §5 has a test that shows it firing.
- **M1: tools.** Build `tools/compute/`: fetch, pinned loading, the offline guard, the style, the formatter, and `check`. Wire it into CI, and add the pilot's lessons to this plan.
- **M2: chapters with figures,** one pull request per chapter. Start with the figures that need no key and no paid API. By the scan:
  - ch-07, ch-10, and ch-12 have 3 figures each;
  - ch-09 has 2;
  - ch-01, ch-04, ch-14, and ch-15 have 1 each.

  ch-11 and ch-13 come last. ch-11's four figures fetch from the Census and FRED APIs, some with an API key. ch-13's two figures call an embeddings API that charges for each call.
- **M3: tables** that the text discusses, chapter by chapter.
- **Git:** merge commits, a new branch per pull request, and no rewritten history (`docs/decisions.md`).

## 9. Decisions needed

1. Should the book show computed outputs at all, given the preface's stance? If yes, approve or edit the wording in §7.
2. Which design: compute files with `embed` (§4, recommended), or the `tools/shots` fallback (§5a)?
3. Scope: figures first, or figures and tables together?
4. Where do snapshots live: in the repository under `data/` (recommended while they stay small), or somewhere else?
