# Images for ch-05

Figures in `ch-05-protocols.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `element-picker.png` and `element-picker_annotated.png`, `.pdf` | capture | 2026-09-24 | https://en.wikipedia.org/wiki/University_of_Colorado_Boulder | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2× |
| `inspector-heading.png` and `inspector-heading_annotated.png`, `.pdf` | capture | 2026-09-24 | https://en.wikipedia.org/wiki/University_of_Colorado_Boulder | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2× |
| `network-headers.png` and `network-headers_annotated.png`, `.pdf` | capture | 2026-09-24 | https://en.wikipedia.org/wiki/University_of_Colorado_Boulder | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×1000 at 2× |
| `network-requests.png` | capture | 2026-09-24 | https://en.wikipedia.org/wiki/University_of_Colorado_Boulder | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2× |
<!-- shots:end -->

## Notes

- **`inspector-heading` and `element-picker`:** the Elements tree has DevTools' whole width, so its rows don't wrap: the Styles pane sits under it at its smallest (`layout: stacked, sidebar: 1`), and the crop stops above the breadcrumb bar and Styles' tab bar. The text discusses neither.
- **`inspector-heading`:** the pointer rests on the selected `<h1>` row in the Elements tree, which is what makes Chrome shade the heading on the page and show its label. The scroll offset keeps Wikipedia's fundraising banner, when one runs, out of the way.
- **`element-picker`:** the label over the infobox is drawn by Chrome, not the page, so no marker can be anchored to it; the caption names it instead. The picker button is switched on and the pointer rests near the infobox's top-left corner.
- **`network-requests`:** a first visit (`first_visit: true`): cookies and cache are cleared before the reload, so every row has a real size and time. The Waterfall column is switched on and the timeline above the list is hidden; Chrome 154 does the opposite by default, and the chapter says how to add the column. Initiator is hidden too, so Name and Type aren't cut short.
- **`network-headers`:** DevTools alone, cropped from a 1000-pixel-tall window. In a 600-pixel window Chrome keeps DevTools under about 360 pixels, too short for the request headers. On any retake, keep **General** and **Response headers** folded. General's Remote Address is the capture's proxy (127.0.0.1). The response headers include `x-client-ip`, the address the capture ran from, and `set-cookie` lines with a GeoIP location. The connection is HTTP/1.1 because of the proxy; the caption says so.
