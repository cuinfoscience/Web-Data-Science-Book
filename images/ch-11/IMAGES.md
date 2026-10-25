# Images for ch-11

Figures in `ch-11-government.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `census-table.png` and `census-table_annotated.png`, `.pdf` | capture | 2026-10-25 | https://data.census.gov/table/ACSDT5Y2024.B19013?g=050XX00US08013 | tools/shots: Google Chrome for Testing 154.0.8037.92, 640×520 at 2.5× |
| `co-generation-mix.png` | render | 2026-10-25 | https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=annual&data[]=generation&facets[location][]=CO&facets[sectorid][]=99&start=2001&end=2025 | Claude Code: rendered with matplotlib 3.11.2 with requests 2.34.2; imported by tools/shots |
| `congress-bill.png` and `congress-bill_annotated.png`, `.pdf` | capture | 2026-10-25 | https://www.congress.gov/bill/119th-congress/house-bill/7730 | Brian C. Keegan: screenshot by hand in a browser on macOS (not recorded); imported by tools/shots |
| `cpi-denver-national.png` | render | 2026-10-25 | https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCNS&frequency=a&aggregation_method=avg&units=pc1&observation_start=2015-01-01&observation_end=2025-12-31 | Claude Code: rendered with matplotlib 3.11.2 with requests 2.34.2; imported by tools/shots |
| `eia-browser.png` and `eia-browser_annotated.png`, `.pdf` | capture | 2026-10-25 | https://www.eia.gov/opendata/browser/electricity/retail-sales?frequency=annual&data=price;&facets=stateid;sectorid;&stateid=CO;&sectorid=RES;&sortColumn=period;&sortDirection=desc; | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×840 at 2× |
| `fred-series.png` and `fred-series_annotated.png`, `.pdf` | capture | 2026-10-25 | https://fred.stlouisfed.org/series/MHICO08013A052NCEN | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `housing-boulder-longmont.png` | render | 2026-10-25 | https://api.census.gov/data/2024/acs/acs5?get=NAME,B25034_002E,B25034_003E,B25034_004E,B25034_005E,B25034_006E,B25034_007E,B25034_008E,B25034_009E,B25034_010E,B25034_011E&for=place:07850,45970&in=state:08 | Claude Code: rendered with matplotlib 3.11.2 with requests 2.34.2; imported by tools/shots |
<!-- shots:end -->

## Notes

- **census-table** is a 640-pixel window at scale 2.5: the same pixels as an 800-pixel window zoomed to 125%, which the caption says. At 100% the site's labels and chips are 10 and 11 pixels, which measured 9.7 pixels in the book, under its 11. At this width data.census.gov folds its filter and results panels into a **View Filters** button at the window's foot, so the table needs no clicks. Two elements carry the chip text "2024: ACS 5-Year Estimates Detailed Tables"; the first sits unseen under the Universe chip, so marker 2 takes the second (`nth: 1`). The estimate and margin, 103,994 and ±2,268, are the ones the chapter's Census request returns.
- **fred-series**: at 800 pixels FRED puts the latest value, units, and frequency on one line under Observations, so one marker covers them. The crop ends above the chart.
- **eia-browser**: the dashboard keeps laying itself out after its text appears, and a scroll made before that is undone; the recipe waits for the network to go idle, then scrolls Data Type to 60 pixels down, below the sticky header. It is 800×757, over 800×600, so the form's choices and the URL they build are in one picture.
- **congress-bill** is a hand capture (`mode: hand`). www.congress.gov answered the toolkit with a Cloudflare challenge (403) twice on 2026-10-25, 33 minutes apart, and the toolkit doesn't get past a challenge, so the maintainer took the screenshot in his own browser: H.R. 7730's page, about 720 CSS pixels wide at scale 2, from the title through the overview box. Its markers are placed by `xy` and need checking after any retake. At about 1,000 pixels and up the page also shows tabs for the bill's text, actions, and cosponsors, but its 13-pixel text then measures 9 pixels in the book, so the chapter names them instead.
- The three renders come from `tools/shots/renders/ch-11.py`, which runs the chapter's cells with the four keys from the environment; its output, with keys scrubbed, is what the chapter's comments show.
