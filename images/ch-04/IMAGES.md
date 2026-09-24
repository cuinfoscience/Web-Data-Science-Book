# Images for ch-04

Figures in `ch-04-data-formats.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `house-xml-tree.png` and `house-xml-tree_annotated.png`, `.pdf` | capture | 2026-09-24 | https://clerk.house.gov/xml/lists/MemberData.xml | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×680 at 2× |
| `rss-feed-xml.png` and `rss-feed-xml_annotated.png`, `.pdf` | capture | 2026-09-24 | https://feeds.bbci.co.uk/news/science_and_environment/rss.xml | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×700 at 2× |
| `view-source-rss-link.png` and `view-source-rss-link_annotated.png`, `.pdf` | capture | 2026-09-24 | view-source:https://www.pbs.org/newshour/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 816×600 at 2× |
<!-- shots:end -->

## Notes

- **Why these hosts.** Chrome draws an XML file as a tree only when it is served as `text/xml` or `application/xml`. PBS NewsHour's feed (`application/rss+xml`) and Data Skeptic's (`text/plain`) show as plain text, so neither can show the tree; the chapter's Step 2 says so. The Guardian's and www.bbc.co.uk's robots.txt files disallow Claude's agents, so no figure comes from either. The BBC's feeds are served from feeds.bbci.co.uk, whose robots.txt allows them. The science and environment feed was picked over the front-page feed in the starter list for headlines that aren't political.
- **Figure 4-2 is not made.** The back-fill plan's Open-Meteo figure (the forecast in Chrome's JSON view) is left out: api.open-meteo.com's robots.txt disallows every path.
- **`house-xml-tree`:** two blocks are folded with Chrome's own triangles, `<title-info>` and the first member's `<committee-assignments>`, and the caption says so. The crop starts below Chrome's note that the file has no style information. The fold buttons are found by their tags' text and XPath: CSS `:has()` with `:text-is()` took more than a minute on the roster's 18,000-line tree. The first member is Alaska's at-large seat (AK00); if the roster's order or that member changes, update the alt text, which names the member.
- **`rss-feed-xml`:** the headlines change through the day, so a retake needs the alt text's first headline and date updated. Folding `<image>` saves the two lines that let the second `<item>` fit in 600 pixels; folding `<copyright>` hides a line of CDATA that would run past the right edge. Chrome doesn't wrap CDATA, so the first item's description still runs past it; the caption says so. The second `<item>`'s marker hangs 3 pixels past the bottom edge, so the annotated image is 3 pixels taller than the capture.
- **`view-source-rss-link`:** a headed capture. The find bar is browser UI, so the search is typed with real keys (`key`, `type`). Chrome centers the match, so the recipe scrolls after searching, to put line 32 just below the find bar with four whole rows of line 31's script beside it. The crop is a fixed band of the window, from the toolbar to the end of line 33. The source changes with the site: before a retake, check that the `<link rel="alternate">` is still on line 33 (`curl -s https://www.pbs.org/newshour/ | grep -n application/rss+xml`), and move the recipe's line numbers if not.
- The course copies: `slides/week-04/img/` in the course repository has `house-xml-tree`, and `handouts/week-04/img/` has `rss-feed-xml` and `view-source-rss-link` for `rss-feeds.md`.
