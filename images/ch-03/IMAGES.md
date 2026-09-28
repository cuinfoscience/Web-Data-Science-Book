# Images for ch-03

Figures in `ch-03-post-api.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `crowdtangle-last-capture.png` | capture | 2026-09-25 | https://web.archive.org/web/20240814023608/https://www.crowdtangle.com/; https://web.archive.org/web/20240814023608if_/https://www.crowdtangle.com/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 776×600 at 2× |
| `dead-endpoints.png` | capture | 2026-09-24 | https://api.pushshift.io/reddit/search/submission/?q=test&size=1; https://api.crowdtangle.com/posts; https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=nasa | tools/shots: Google Chrome for Testing 154.0.8037.57, 560×400 at 2× |
| `dsa-article-40.png` and `dsa-article-40_annotated.png`, `.pdf` | capture | 2026-09-24 | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065 | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×700 at 2× |
| `reddit-api-pricing.png` | capture | 2026-09-25 | https://web.archive.org/web/20230609174525/https://old.reddit.com/r/reddit/comments/145bram/addressing_the_community_about_changes_to_our_api/ | tools/shots: Google Chrome for Testing 154.0.8037.57, 776×600 at 2× |
<!-- shots:end -->

## Notes

The chapter 3 part of the screenshot back-fill
([plan](../../docs/plans/2026-09-24-screenshot-backfill-ch01-05.md), §4),
captured on 2026-09-24 and 2026-09-25. Recipes: `tools/shots/recipes/ch-03.yml`.

### `dead-endpoints` (figure 3.3, "Dead-Endpoint Forensics")

Plan item 3-1: the section's three retired endpoints, stacked in the
chapter's order.

- **Pushshift answers.** Its 403 is one line of JSON, `{"detail":"Not
  authenticated"}`, under Chrome's Pretty-print bar. The server header is
  Cloudflare's. If the service is ever retired outright, this part changes
  kind, and the caption with it.
- **CrowdTangle doesn't.** The page is Chrome's own. On 2026-09-24 public DNS
  answered SERVFAIL for api.crowdtangle.com, www.crowdtangle.com, and
  crowdtangle.com, and the session's proxy answered 502 to the tunnel. Chrome
  reports that as `ERR_TUNNEL_CONNECTION_FAILED`, the name the caption gives.
  `capture` asked public DNS before keeping the take, because a host the
  proxy refuses by policy fails the same way (see the toolkit README's
  "Refusals and dead hosts"); the answer is in `provenance.json`. A retake on
  a direct connection shows Chrome's message that it couldn't find the host's
  address, and the caption's last sentence changes to match.
- **The crop** runs from Chrome's icon to the error's name
  (`.icon` to `.error-code`), from the page's 24-pixel indent, so the error
  page lines up with the JSON above it.
- **Twitter API v1.1 answers too:** a 400 with one line of JSON, error 215,
  "Bad Authentication data." api.twitter.com's robots.txt disallows every
  path for every agent but Googlebot and Bingbot, and the part is an API's
  response, captured as an API client (`api_client: true`; the maintainer's
  decision of 2026-09-24 in `docs/decisions.md`). It joined the figure after
  that decision, so the first version, merged in #158, showed two endpoints.
  Before the decision, the reconnaissance script had sent one request to the
  same URL before reading the host's robots.txt.

### `dsa-article-40` (figure 3.2, "Exemption")

Plan item 3-4: Article 40 of the Digital Services Act, from its heading
through paragraph 4, boxed. The text is the Official Journal's (CELEX
32022R2065), which doesn't change, so the caption carries no date.

- **EUR-Lex's robots.txt asks for 10 seconds between requests,** so the
  recipe's pause starts at 12.
- **Some first visits get a script check:** EUR-Lex answered 202, ran a
  script, and reloaded the page with 200. The take was made on a visit
  without one (200).
- **A contents box floats over the bottom quarter of the window**
  (`#TOCSidebarSA`); the recipe closes it with `#tocHideBtnStandalone`.
- **Paragraph ids start with a digit,** so the crop and the box select
  `[id="040.004"]`, not `#040.004`.

### `crowdtangle-last-capture` (figure 3.4, "Dead-Endpoint Forensics")

Plan item 3-2, captured on 2026-09-25 when web.archive.org answered again: the
capture that the chapter's `last_snapshot()` finds, stacked in two views.

- **It is the last capture of the site, not of the address.** The
  availability API still answered `20240814023608` on 2026-09-25, as the
  chapter prints. The CDX API lists the address's captures after it, until
  December 2024 (the toolbar's "16 Feb 2012 - 12 Dec 2024"), and every one is
  a 301 redirect. The chapter's sentence says so.
- **The page announced its own end.** Its banner, "CrowdTangle will no longer
  be available after August 14, 2024", is in Bootstrap's `navbar-fixed-top`,
  pinned to the top of the window, where the Wayback toolbar is pinned too,
  so the toolbar covers it and it shows faintly through. The second part is
  the archive's `if_` view of the same capture, which leaves the toolbar
  out.
- **Pages here come back half drawn.** On 2026-09-25 the archive aborted some
  of the page's stylesheets, a different few on each load; the text checks
  passed on takes that showed the page unstyled. `capture` now fails a take
  when a file from the page's host fails before any answer, and retries it:
  both parts here took several attempts. Look at the take before promoting
  it.
- **The window is 776 pixels,** so the stack with its padding is 800 wide.

### `reddit-api-pricing` (figure 3.1, "Enclosure")

Plan item 3-3: Reddit's 2023 price in Reddit's own words, from the archive.

- **The claim was checked first.** Wikipedia credits the first public figure
  to Apollo's developer, on 31 May 2023, and the chapter says "the company
  announced" it. u/spez's post of 9 June 2023 (created 17:44:13 UTC) states
  it: "Effective July 1, 2023, the rate for apps that require higher usage
  limits is $0.24 per 1K API calls". The text was read from the archive's
  copy of the thread's JSON (`20230610045457`,
  `…/comments/145bram/_/jnk45rr.json`).
- **Only the archive will do.** reddit.com's robots.txt disallows every path
  (`User-agent: *` / `Disallow: /`); web.archive.org's robots.txt answered
  404.
- **old.reddit.com, not www.** The www captures are new Reddit's shell: the
  post arrives by a later request, which the archive doesn't replay.
  old.reddit.com draws the post on the server. Its first capture,
  `20230609174525`, came a minute after the post ("submitted 1 minute ago";
  the sidebar says "0 points (19% upvoted)").
- **Two crops of one capture:** the title through the byline, and the post's
  first list's third item, "Premium Enterprise API / Third-party apps", both
  in the post's column, leaving out the sidebar and the sign-up banner.
  The item's next line names Apollo, Reddit is Fun, and Sync, the apps the
  chapter's paragraph mentions.
- **Some files are lost on every load.** Reddit's archived stylesheets for
  tooltips and crosspost previews came back aborted on most loads, while the
  post looked right, so both parts accept it (`expect: {all_files: false}`).
  On the approved take, the second part lost one stylesheet,
  `crosspost-preview.De3P20Yb4PY.css`, which styles nothing in the crop.
- **The toolbar stays pinned as the page scrolls,** over the window's top 65
  pixels, so the second part scrolls its item to 96 pixels down. At 12, the
  toolbar covered the item's heading and its first line.
