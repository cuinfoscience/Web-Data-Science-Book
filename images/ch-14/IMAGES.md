# Images for ch-14

Figures in `ch-14-automation.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `afternoon-forecasts.png` | render | 2026-11-13 | https://raw.githubusercontent.com/cuinfoscience/Web-Data-Science-Book/main/data/ch-14/forecasts.csv | Claude Code, for Brian C. Keegan: rendered with matplotlib 3.11.2 with pandas 3.1.1 and requests 2.34.2; imported by tools/shots |
| `nws-forecast-page.png` | capture | 2026-11-13 | https://forecast.weather.gov/MapClick.php?lat=40.015&lon=-105.2705 | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `nws-points-json.png` and `nws-points-json_annotated.png`, `.pdf` | capture | 2026-11-13 | https://api.weather.gov/points/40.015,-105.2705 | tools/shots: Google Chrome for Testing 154.0.8037.92, 760×600 at 2× |
<!-- shots:end -->

## Notes

- **nws-forecast-page** is a composite of two parts of one page, each loaded on its own: `#seven-day-forecast` (the extended forecast) and `#about_forecast` (the box at the page's foot). Each part scrolls its element into view before the crop. The map, the current conditions, and the detailed text forecast between them are left out. The caption and the chapter's tour quote the Last Update the take shows (11:46 am MST Nov 12, 2026, captured at 02:53 UTC on Nov 13, 7:53 pm MST on the 12th); a retake changes both, and the chapter's text must change with them. The site serves no robots.txt (404 on 2026-11-13).
- **nws-points-json** is the API's answer as Chrome's JSON viewer shows it, captured as an API client (`api_client: true`): api.weather.gov's robots.txt is `User-agent: *`, `Disallow: /`. The NWS indents its JSON itself, so Pretty-print is left as it is; the crop starts at `"properties"` and ends at `"state": "CO"`.
- **afternoon-forecasts** comes from `tools/shots/renders/ch-14.py`, which runs every cell from "One Request by Hand" to "Failures and Monitoring" (requests to api.weather.gov, with the course's User-Agent) and draws the chart from `data/ch-14/forecasts.csv`. Its lines depend on the span of that copy; a refreeze of the data means a new chart, new outputs (`--fill "## Reading What It Collected"`), and new numbers in the text around them.
