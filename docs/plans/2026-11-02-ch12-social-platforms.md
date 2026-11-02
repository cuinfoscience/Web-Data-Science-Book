# Plan: chapter 12 and week 12, social and media platform APIs

**Status:** Proposed 2026-11-02, the morning week 12 starts, from the instructor's answers to an AMA after the [course AAR of weeks 10–11](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/docs/aar/2026-11-01-weeks-10-11.md). The lab's Part 1 was built first, for today's class (course #156); this plan is for the chapter, and for Parts 2 and 3, which follow it.

## Where chapter 12 stands (audit, 2026-11-01)

- **Size and state.** 588 lines, about 2,650 words before the exercises; chapter 10 has 5,884 and chapter 11 10,202. None of its code has been run for the book. It has no figures, no tour, and no key management. One output (lines 162–166) looks invented.
- **Three of its four platforms don't work as written for a student starting this week** (all checked 2026-11-01 or 11-02):
  - **Reddit** closed self-service API access on 2025-11-11 (the Responsible Builder Policy): a new app needs approval.
  - **Spotify** has required, since 2026-02-11, that a development app's owner have Premium. It removed top tracks, `followers`, `popularity` and batch fetches, and capped search at 10 ([migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide)).
  - **Mastodon** removed the password login the chapter uses (4.4, July 2025).
- **Bluesky's public AppView** answers `getProfile` and `getAuthorFeed` with no login.

## Decisions (instructor, 2026-11-01 and 11-02)

| Question | Decision |
|---|---|
| Platforms | **Bluesky, YouTube, Reddit, Spotify**. Mastodon comes out. |
| The lab | Bluesky Monday and Wednesday; YouTube Friday. Reddit and Spotify are in the chapter only. |
| Reddit | Evaluate the successors to Pushshift: PullPush, Arctic Shift and others (findings below). |
| Spotify | A case study only, with no live code. |
| The case | Federal agencies' public accounts: on Bluesky, the five with a `.gov` handle (`noaa.gov`, `nws.noaa.gov`, `climate.noaa.gov`, `noaacomms.noaa.gov`, `federalreserve.gov`), plus verified official `.bsky.social` accounts (the Library of Congress, the St. Louis Fed); on YouTube, the same agencies' channels. |
| YouTube key | `YOUTUBE_KEY`, from a personal Google account, set with chapter 11's three safe ways. |
| Friday's last 15 minutes | The week's portfolio checkpoint (course `AGENTS.md`, since 2026-11-02). |

## The chapter, after this plan

Section order follows chapters 10 and 11.

1. **Learning Objectives; Companion Notebook.**
2. **Platforms, Data, and Power.** Platforms share data at their discretion, unlike chapter 11's agencies. The dated changes at Reddit, Spotify and X go here. "Social data is people data" stays, extended:
   - public institutions as the running case;
   - never print a private person's handle;
   - deleted posts;
   - terms of service;
   - research access through the DSA's Article 40 (cross-referenced to chapter 3).
3. **A Tour: From the Website to the API**, with `tools/shots` captures:
   - an agency's Bluesky profile (`bsky.app/profile/nws.noaa.gov`): its domain handle, its check and its counts;
   - an agency's YouTube channel page;
   - a table pairing each feature on the page with its request.
4. **Bluesky's Public API.** Raw `requests` against `public.api.bsky.app`, with a User-Agent, a timeout and `raise_for_status()`:
   - `getProfile`, and how to tell the agency from an impostor (domain handle, verification);
   - `getProfiles` for several accounts;
   - `getAuthorFeed`, with reposts set aside;
   - paging with `cursor`, set against chapter 10's `continue` and chapter 11's `offset`;
   - followers, counted and never listed.
   - An optional closing section on `atproto` and app passwords, as chapter 10 adds mwclient.
5. **YouTube Data API.**
   - Key management: a short pointer to chapter 11, then `YOUTUBE_KEY`.
   - `channels.list` by handle; `playlistItems.list` on a channel's uploads playlist; `videos.list` for statistics.
   - The quota: 10,000 units a day, most reads costing 1 unit, and searches capped separately at 100 calls a day ([getting started](https://developers.google.com/youtube/v3/getting-started), checked 2026-11-02; the cost of a search changed, so the chapter says when it was checked). Read channels and uploads rather than searching.
6. **Reddit After Pushshift** (evaluation, checked 2026-11-02; details in the table below).
   - **One runnable example:** an Arctic Shift search on r/boulder, `limit=5`, with `fields=` leaving out `author`, a User-Agent and a timeout. The example teaches `removed_by_category` and `retrieved_on`: the archive keeps what users deleted.
   - **A committed snapshot of the response**, so the chapter reads correctly when the service is down.
   - **History:** Pushshift (2015–2023), PullPush, Arctic Shift, Reddit's closing of the unauthenticated `.json` endpoints (announced 2026-05-28), the Responsible Builder Policy, and Watchful1's torrents, taken down in 2026.
   - **What the Responsible Builder Policy asks of researchers:** an accredited university, non-commercial use, re-running queries so deletions are reflected, and no re-identification. All of these conflict with using an archive.
   - **Disclosure:** the instructor is a co-author of the Pushshift dataset paper (Baumgartner et al. 2020), and the chapter says so where it cites it.
7. **Spotify: An Enclosure Case Study.** The 2024 removal of audio features and recommendations, and the 2026 rules for development apps, with dates and sources. No code.
8. **Comparing Platforms.** A table, one row per platform: who can read; what it costs; key or approval; what happens to deleted content.
9. **Recommended Exercises.** Keep the six-step Bluesky comparison of two accounts, but on the public API with no login (Step 1 becomes "check your User-Agent", not "log in"), comparing two federal accounts over a fixed past window.
10. **Additional Exercises.**
    - Replace the Reddit and Spotify items: a YouTube channel comparison by quota cost; an Arctic Shift study of deletion rates in a subreddit, reported as counts.
    - The graduate extension: research access under the DSA's Article 40.
11. **Social History and Public Interest.** Sources (all resolve in OpenAlex):
    - Baumgartner et al. 2020, *ICWSM*, [doi:10.1609/icwsm.v14i1.7347](https://doi.org/10.1609/icwsm.v14i1.7347) (disclosed);
    - Gaffney & Matias 2018, *PLOS ONE*, [doi:10.1371/journal.pone.0200162](https://doi.org/10.1371/journal.pone.0200162);
    - Proferes et al. 2021, *Social Media + Society*, [doi:10.1177/20563051211019004](https://doi.org/10.1177/20563051211019004);
    - Fiesler & Proferes 2018, [doi:10.1177/2056305118763366](https://doi.org/10.1177/2056305118763366);
    - Fiesler et al. 2024, *PACM HCI*, [doi:10.1145/3633070](https://doi.org/10.1145/3633070);
    - Ayers et al. 2018, *npj Digital Medicine*, [doi:10.1038/s41746-018-0036-2](https://doi.org/10.1038/s41746-018-0036-2);
    - Freelon 2018, [doi:10.1080/10584609.2018.1477506](https://doi.org/10.1080/10584609.2018.1477506).
12. **Common Issues to Debug; Key Takeaways; Further Reading.**

### Reddit after Pushshift: what each successor offers (checked 2026-11-02 from a cloud machine)

| Service | Access | Live test | Chapter code? |
|---|---|---|---|
| Arctic Shift API (Arthur Heitmann, donations) | No key; limits vary with load; 429 with `X-RateLimit-Reset`; `limit` ≤ 100; no uptime guarantee | 200; 5 r/boulder posts with about 100 fields; newest about 20 minutes old | Yes, with a snapshot |
| Arctic Shift monthly dumps (Academic Torrents) | Torrent | Through 2026-09; one month is 74 GB | History |
| PullPush | No key, Pushshift-style | 522: the server was down | No |
| Watchful1's per-subreddit torrents | Was a torrent | "No torrent exists"; taken down in 2026 | History |
| Pushshift | Moderators only | 403 | History |
| Reddit Data API, Reddit for Researchers | Approval; an accredited university; non-commercial use | Not tested | Only for students who already hold credentials |
| Reddit's `.json` pages | Closed to logged-out users (r/modnews, 2026-05-28) | 403 | No |
| ConvoKit Reddit corpora (Cornell) | `pip install`, then download | Docs 200; data runs to October 2018 | A stable offline alternative |

**Risks:**
- Arctic Shift is one maintainer with no service guarantee.
- Redistributing Reddit's data sits against Reddit's Data API Terms and User Agreement.
- Reddit has sued commercial scrapers (2025), though no academic archive.
- Some claims are secondary only: the reason the torrents came down, and who runs PullPush. The chapter says so, or leaves them out.

## How the work runs

Follow the course AAR's P0-3: settle the lab's scope first, which this plan does, and plan each part for the pace a class reaches.

| When | What |
|---|---|
| Mon Nov 2 | Lab Part 1 (Bluesky, no account) and Monday's frames. Done: course #156. |
| Mon–Tue | **PR A:** sections 1–4 and 9 (Bluesky), the tour's Bluesky captures, outputs from live runs. |
| Tue | Lab Part 2 (Bluesky: `cursor` paging, an agency's rhythm) after PR A merges, then Wednesday's frames. |
| Wed–Thu | **PR B:** sections 5–8, 10–12 (YouTube, Reddit after Pushshift, Spotify, comparison, history), and the YouTube capture. |
| Thu | Lab Part 3 (YouTube) after PR B merges, then Friday's frames. The lab ends with the portfolio checkpoint. |
| Fri | Part 1 revised to match the merged chapter, if it changed. |

Each lab key and deck records the chapter commit it follows. When the chapter changes, they are checked against it in the same sitting (AAR P1-1, P1-2).
