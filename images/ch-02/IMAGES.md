# Images for ch-02

Figures in `ch-02-ethics.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `robots-txt-wikipedia.png` and `robots-txt-wikipedia_annotated.png`, `.pdf` | capture | 2026-09-24 | https://en.wikipedia.org/robots.txt | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×600 at 2× |
| `wikimedia-ua-policy.png` and `wikimedia-ua-policy_annotated.png`, `.pdf` | capture | 2026-09-24 | https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×700 at 2× |
<!-- shots:end -->

## Notes

- **`robots-txt-wikipedia`:** Chrome shows a plain-text file as one `<pre>` holding one text node, so no element stands for a line. The recipe finds lines with `match:` (a pattern searched in an element's text, with `^` and `$` at each line), both to scroll and to anchor the markers. The figure starts at the comment block before `User-agent: *` (line 132 of the file on 2026-09-24) and ends at the last `/wiki/Spesial%3A` rule. The figure block shows it at 78% of the column, about its size on screen. Wikipedia edits the file: before a retake, check that the comment "Friendly, low-speed bots..." still leads into the generic block (`curl -s https://en.wikipedia.org/robots.txt | grep -n -A3 'Friendly'`); the markers follow the text, not the line numbers.
- **`wikimedia-ua-policy`:** the policy is on foundation.wikimedia.org. At 800 pixels its text runs in a 430-pixel column beside a navigation box, so the crop is that column: from "This change is most likely to affect scripts" to the end of the paragraph on the generic format. Scrolling past the page's header turns on the skin's sticky header, and the page's own header leaves the flow, lifting the content about 40 pixels. The `match` scroll measures again and corrects. The markers sit at the left of each block; aimed at the sentence itself, which starts mid-line, a marker needs a leader line across the text. The window is 700 tall so the crop starts below the page's floating contents button. The figure block shows it at 60% of the column.
- **Left out:** 2-2, Reddit's robots.txt, waits for the Friday review: students' pull requests #50, #63, and #79 revise the paragraphs it would sit beside. 2-4, a browser's own request headers, is covered by chapter 5's `network-headers`; captures send the course's User-Agent, not Chrome's own. 2-5, a platform's terms of service, is optional, and the chapter quotes no one platform's clause.
