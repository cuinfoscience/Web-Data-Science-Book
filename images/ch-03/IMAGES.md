# Images for ch-03

Figures in `ch-03-post-api.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `dead-endpoints.png` | capture | 2026-09-24 | https://api.pushshift.io/reddit/search/submission/?q=test&size=1; https://api.crowdtangle.com/posts; https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=nasa | tools/shots: Google Chrome for Testing 154.0.8037.57, 560×400 at 2× |
| `dsa-article-40.png` and `dsa-article-40_annotated.png`, `.pdf` | capture | 2026-09-24 | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065 | tools/shots: Google Chrome for Testing 154.0.8037.57, 800×700 at 2× |
<!-- shots:end -->

## Notes

The chapter 3 part of the screenshot back-fill
([plan](../../docs/plans/2026-09-24-screenshot-backfill-ch01-05.md), §4),
captured on 2026-09-24. Recipes: `tools/shots/recipes/ch-03.yml`.

### `dead-endpoints` (figure 3.2, "Dead-Endpoint Forensics")

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

### `dsa-article-40` (figure 3.1, "Exemption")

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

### Waiting for web.archive.org

web.archive.org reset every connection from this session on 2026-09-24,
still at 21:45 UTC, while archive.org's availability API answered. Two
candidates wait for it. Neither has been seen yet; check each against its
brief before promoting it.

- **3-2, CrowdTangle's last capture,** the one the chapter's
  `last_snapshot()` finds:

  ```yaml
  - id: crowdtangle-last-capture
    kind: capture
    section: "Dead-Endpoint Forensics"
    brief: >-
      Show the archive's last capture of CrowdTangle's site, the one
      last_snapshot() finds: www.crowdtangle.com on 14 August 2024, under the
      Wayback Machine's toolbar and its capture date.
    url: https://web.archive.org/web/20240814023608/https://www.crowdtangle.com/
    steps:
      - wait: {selector: '#wm-ipp-base'}
    expect:
      text: ['(?i)crowdtangle']
  ```

- **3-3, Reddit's 2023 price, in Reddit's own words.** reddit.com's
  robots.txt now disallows every path (`User-agent: *` / `Disallow: /`), so
  only an archived copy will do. The candidate is u/spez's r/reddit post of
  June 2023, "Addressing the community about changes to our API", archived
  on 15 June 2023 (`20230615235211`). Before capturing, confirm that the post
  states the price, $0.24 per 1,000 API calls. Wikipedia's article on the
  controversy credits the first public figure to Apollo's developer, on
  31 May 2023, and the chapter says "the company announced" it.
