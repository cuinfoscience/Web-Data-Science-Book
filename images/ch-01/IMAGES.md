# Images for ch-01

Figures in `ch-01-introduction.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `article-view-source.png` | capture | 2026-09-24 | https://en.wikipedia.org/wiki/University_of_Colorado_Boulder | tools/shots: Google Chrome for Testing 154.0.8037.57, 370×520 at 2× |
| `jupyter-cells.png` and `jupyter-cells_annotated.png`, `.pdf` | capture | 2026-09-24 | http://localhost:8888/notebooks/ch-01-introduction.ipynb | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2× |
| `jupyter-new-menu.png` and `jupyter-new-menu_annotated.png`, `.pdf` | capture | 2026-09-24 | http://localhost:8888/tree | tools/shots: Google Chrome for Testing 154.0.8037.57, 824×600 at 2× |
| `pageviews-json.png` and `pageviews-json_annotated.png`, `.pdf` | capture | 2026-09-25 | https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/University_of_Colorado_Boulder/daily/20260101/20260131 | tools/shots: Google Chrome for Testing 154.0.8037.57, 600×520 at 2× |
<!-- shots:end -->

## Notes

- **The Jupyter server.** `jupyter-new-menu` and `jupyter-cells` are captures of a real Jupyter Notebook 7.6.3 (JupyterLab 4.6.4, Python 3.14.7) on this machine, installed with the chapter's own commands. Miniforge supplied `conda`; Anaconda's installer isn't needed for what the figures show. To set it up again:

  ```bash
  conda create -n webdata python=3.14 && conda activate webdata
  pip install notebook requests beautifulsoup4 pandas matplotlib seaborn
  python tools/make_notebooks.py                    # the companion notebook, current with the chapter
  mkdir -p ~/webdata-notebooks && cp notebooks/ch-01-introduction.ipynb ~/webdata-notebooks/
  cd ~/webdata-notebooks && jupyter notebook --no-browser --ip=127.0.0.1 --port=8888 \
      --IdentityProvider.token='' --ServerApp.password=''
  ```

  Add `--allow-root` if the session runs as root. The server has no token, so the recipes' addresses carry no secret, and it listens only on this machine. Before the first take, a settings override answers Jupyter's first-run prompts about news and updates, which neither figure is about: `$CONDA_PREFIX/share/jupyter/lab/settings/overrides.json` holds `{"@jupyterlab/apputils-extension:notification": {"fetchNews": "false", "checkForUpdates": false}}`.
- **`jupyter-new-menu`:** Notebook 7's **New** menu lists the kernel, **Python 3 (ipykernel)**, where older Jupyter listed **Notebook**; the chapter's wording follows the menu. At 800 pixels wide the menu runs 15 pixels past the window's edge, so the window is 824 wide. The file's age in **Last Modified** is under the menu.
- **`jupyter-cells`:** the Markdown cell is the companion notebook's own text, so regenerate the notebook and copy it to the server's folder before a retake; text edited in that section of the chapter shows up here. Close the notebook's kernel session first, so the prompt reads `[1]:`: Jupyter's API wants its `_xsrf` cookie echoed in an `X-XSRFToken` header for the `DELETE /api/sessions/<id>`. The cell runs with Ctrl+Enter, which leaves it selected, framed in blue. **Not Trusted** is real: Jupyter hasn't signed a notebook it didn't write, and the caption says what it means. Jupyter scrolls a panel, not the window, so the recipe's `scroll` step names the panel with `within:`. Marker 1 is anchored to the rendered paragraph by selector, because a text pattern also matches the Markdown cell's hidden source editor; marker 3 to the output's `<pre>`, because a range over its wrapper includes the `<pre>`'s full-width box.
- **`article-view-source`:** a composite. The article is a headless take at 370 pixels, where Wikipedia's layout wraps the title and doesn't overflow. View Source is a headed take, because it is browser UI; Chrome won't draw a normal window much under 500 pixels wide, so its window is 520 wide and the crop takes 370 pixels of the page, to the end of line 29. Line wrap is off, so long lines run past the edge, as they do in Chrome by default. Wikipedia's markup changes: before a retake, check that the `<title>` is still on line 5.
- **`pageviews-json`:** figure 1-4, the chapter's pageviews URL in Chrome's JSON viewer.
  - **User-Agent.** It needs the User-Agent in the form Wikimedia's API accepts: a name and version, then contact information in parentheses. On 2026-09-24 the toolkit's old `Web Data Science/v1 brian.keegan@colorado.edu` got 429 ("You are making too many requests to the API") on the first request, four times, and the figure was put down to the session's shared address. It wasn't the address: Wikimedia rate-limits a client it can't identify to 10 requests a minute across its address. With `WebDataScience/1.0 (brian.keegan@colorado.edu)`, the same session got 200 on 2026-09-25 (`docs/decisions.md`).
  - **Pretty-print.** The recipe ticks **Pretty-print** by its position, because the checkbox is in a closed shadow root, as in chapter 4's `forecast-json`.
  - **Crop.** It ends under the third day's opening brace, so the list visibly goes on.
  - **Data.** The counts are January 2026's (657 views on the 1st, 761 on the 2nd) and shouldn't change. Chrome's viewer can, so the caption is dated. wikimedia.org has no robots.txt (404).
