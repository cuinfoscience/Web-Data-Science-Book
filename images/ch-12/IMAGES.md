# Images for ch-12

Figures in `ch-12-social.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `bsky-profile.png` and `bsky-profile_annotated.png`, `.pdf` | capture | 2026-11-02 | https://bsky.app/profile/nws.noaa.gov | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `youtube-channel.png` and `youtube-channel_annotated.png`, `.pdf` | capture | 2026-11-02 | https://www.youtube.com/@NOAA | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
<!-- shots:end -->

## Notes

- **bsky-profile** is the logged-out page, 800 pixels wide at scale 2. The crop runs from the foot of the banner to the end of the first post's text, which changes daily; a retake will show another post, and the counts will have moved. Marker 2 points at the blue check, not the name: two elements read "National Weather Service" (the heading and the post's byline), so the recipe's pattern matches the heading's text with its trailing check (`'^\s*National Weather Service\W*$'`, `nth: 0`). The page rounds to 63K and 1.3K; the chapter's `getProfile` output, from the same day, has 63,022 and 1,394.
- **youtube-channel** is logged out, 800 pixels wide at scale 2, cropped from the banner to the tab row, below YouTube's search bar. The recipe waits for `@NOAA`. The description is cut off by the page itself ("...more"). Marker 3 sits left of "noaa.gov", past the link icon (`side: left, gap: 12`), because "and 3 more links" fills the right. The chapter says this link proves nothing alone: the proof is a link from the agency's site to the channel. YouTube shows 51.8K: `subscriberCount` from the API is rounded to three significant figures as well, so the two should agree.
- Both pages redesign often (`drifts: true`). Check the markers after any retake; the text patterns, not positions, place them.
