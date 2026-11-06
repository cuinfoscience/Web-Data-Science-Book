# Images for ch-12

Figures in `ch-12-social.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `bsky-profile.png` and `bsky-profile_annotated.png`, `.pdf` | capture | 2026-11-02 | https://bsky.app/profile/nws.noaa.gov | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `youtube-channel.png` and `youtube-channel_annotated.png`, `.pdf` | capture | 2026-11-02 | https://www.youtube.com/@NOAA | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `yt-create-credentials.png` and `yt-create-credentials_annotated.png`, `.pdf` | capture | 2026-11-06 | https://console.cloud.google.com/apis/api/youtube.googleapis.com/credentials | Brian C. Keegan: screenshot by hand in Firefox; imported by tools/shots |
| `yt-create-key.png` and `yt-create-key_annotated.png`, `.pdf` | capture | 2026-11-06 | https://console.cloud.google.com/apis/credentials | Brian C. Keegan: screenshot by hand in Firefox; imported by tools/shots |
| `yt-enabled.png` and `yt-enabled_annotated.png`, `.pdf` | capture | 2026-11-06 | https://console.cloud.google.com/apis/api/youtube.googleapis.com | Brian C. Keegan: screenshot by hand in Firefox; imported by tools/shots |
| `yt-library.png` and `yt-library_annotated.png`, `.pdf` | capture | 2026-11-06 | https://console.cloud.google.com/apis/library/youtube.googleapis.com | Brian C. Keegan: screenshot by hand in Firefox; imported by tools/shots |
<!-- shots:end -->

## Notes

- **bsky-profile** is the logged-out page, 800 pixels wide at scale 2. The crop runs from the foot of the banner to the end of the first post's text, which changes daily; a retake will show another post, and the counts will have moved. Marker 2 points at the blue check, not the name: two elements read "National Weather Service" (the heading and the post's byline), so the recipe's pattern matches the heading's text with its trailing check (`'^\s*National Weather Service\W*$'`, `nth: 0`). The page rounds to 63K and 1.3K; the chapter's `getProfile` output, from the same day, has 63,022 and 1,394.
- **youtube-channel** is logged out, 800 pixels wide at scale 2, cropped from the banner to the tab row, below YouTube's search bar. The recipe waits for `@NOAA`. The description is cut off by the page itself ("...more"). Marker 3 sits left of "noaa.gov", past the link icon (`side: left, gap: 12`), because "and 3 more links" fills the right. The chapter says this link proves nothing alone: the proof is a link from the agency's site to the channel. YouTube shows 51.8K: `subscriberCount` from the API is rounded to three significant figures as well, so the two should agree.
- Both pages redesign often (`drifts: true`). Check the markers after any retake; the text patterns, not positions, place them.
- **yt-library, yt-enabled, yt-create-credentials, yt-create-key** are Brian C. Keegan's screenshots of the Google Cloud console, signed in, taken in Firefox on 2026-11-06 in the console's dark theme and imported with `tools/shots/run import`. They are 1× screenshots (`scale: 1`); a retake at 2× would be sharper on a projector. No account name, avatar, project ID or key value appears in any of them, so nothing is blacked out. Their markers are placed by `xy`, so check each one after a retake. **yt-create-key** is cropped 12 pixels on the left and at the top, where the page behind the dialog showed through, and is over 768 pixels tall because the dialog is one form (its `oversize:`). Its blue "Service account required" note is about Gemini; the chapter tells readers to skip it. The console changes often (`drifts: true`): if the menus move, the library URL in the chapter still opens the first page.
