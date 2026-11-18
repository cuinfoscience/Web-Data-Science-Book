# Plan: chapter 14 and week 14, automating data collection

**Status:** Decided 2026-11-13 in an AMA with the instructor (four rounds). Week 14 has two class days for automation, Wednesday, November 18, and Friday, November 20 (its last 15 minutes go to portfolio checkpoint 4). Monday, November 16 finishes week 13's lab (Wednesday, November 11's class was cancelled). The chapter, the lab and the deck are built before Wednesday.

## Decisions (instructor, 2026-11-13)

| Question | Decision |
|---|---|
| Chapter | **Full rewrite**, in chapters 10–13's shape. The Rotten Tomatoes scraper, Selenium in Actions, and the old exercises go. |
| Case | The **National Weather Service's hourly forecast for Boulder**: `https://api.weather.gov/gridpoints/BOU/54,75/forecast/hourly`, found from `https://api.weather.gov/points/40.015,-105.2705`. No key. |
| What each run saves | The **hourly forecast only**, appended to a **CSV**: one row per forecast hour, about 156 a run. |
| Schedule | **Hourly** (minute 17, UTC), and **stops itself after December 11, 2026**, so a copy left running doesn't keep asking the NWS. |
| Where students' jobs run | A **template** kept in a folder of the course repository (`labs/week-14/template/`), handed out as a **zip file on Canvas**. Each student makes a new public repository of their own and puts the template in it. |
| Days | **Cloud first.** Wednesday: one request by hand, then each student's workflow running in GitHub Actions, so it collects all week. Friday: read what it gathered, then failures and monitoring. |
| cron | **In the chapter only**: crontab on a student's own computer, and that Actions' `schedule` uses the same syntax. Not in the lab. |
| Other services | **A table, in the chapter and on the slides**, of other hosted schedulers and their free tiers (checked against each provider's current pages). No treatment in the lab. |
| History | **Git scraping in journalism; NWS data as a public good; what scheduled bots cost the servers they ask.** |
| Chapter's data | The course repository runs the collector every hour from 2026-11-13 (`.github/workflows/collect-boulder-forecast.yml`), writing `labs/week-14/data/forecasts.csv`. The chapter reads that series and saves a frozen copy in `data/ch-14/` for reproducibility. |

## The shared contract

**The collector** is `labs/week-14/template/collector.py` in the course repository. The chapter shows it whole and builds it up from a notebook first. Columns of `forecasts.csv`: `collected_at` (UTC, when the run asked), `update_time` (the NWS's `updateTime`, UTC), `start_time` (the hour forecast, Mountain time with offset), `temperature` (°F), `precip_chance` (percent), `wind_speed`, `wind_direction`, `short_forecast`.

**The workflow** is `labs/week-14/template/.github/workflows/collect.yml`: `schedule` cron `"17 * * * *"`, `workflow_dispatch`, `permissions: contents: write`, checkout@v4, setup-python@v5 (Python 3.12), `pip install requests`, `python collector.py`, then commit `forecasts.csv` (`git diff --staged --quiet || git commit`), `git pull --rebase`, `git push`.

**What the first live checks found** (2026-11-13, from a cloud machine):
- `/points/40.015,-105.2705` → `gridId` BOU, 54, 75; `relativeLocation` Boulder, CO.
- The hourly forecast: 156 periods (6.5 days). `updateTime` 2026-11-12T18:46:17Z while `generatedAt` was 01:16:52Z the next hour: **the forecast itself changes a few times a day, not every hour**. The response headers say so too: `Last-Modified`, and `Cache-Control: public, max-age=1136, s-maxage=3600`. This is the chapter's way into "what bots cost servers": an hourly collector asks for the same forecast many times.
- The NWS asks every client to send a User-Agent that names the program and a contact.

## What each part teaches

**Chapter 14** (full rewrite; sections in order, adjust as the writing needs):
1. Learning Objectives; Companion Notebook.
2. Why schedule a collector: one request is a snapshot; a forecast keeps changing, and so do the sources of earlier chapters.
3. A tour: the NWS's forecast page for Boulder (weather.gov), then the API's two requests. Screenshots through `tools/shots`.
4. One request by hand: `/points`, then `forecastHourly`; the headers (`Last-Modified`, `Cache-Control`); `updateTime` vs `generatedAt`.
5. From a notebook to a script: `collector.py` built up step by step: constants, append with the header once, `raise_for_status()`, `main()` and the `__main__` guard, the stop date.
6. Scheduling on your own computer: cron and crontab (five fields, UTC vs local time, a laptop that sleeps); Windows Task Scheduler and macOS launchd in a sentence each.
7. Scheduling in the cloud with GitHub Actions: the workflow file line by line; delays to scheduled runs; `workflow_dispatch`; `permissions`; committing data back (git scraping); GitHub's 60-day pause for inactive repositories; minutes on public repositories.
8. Reading what it collected: load the course's series; how many distinct `update_time`s; how the forecast for one hour changed as it approached (lead time); a figure.
9. Failures and monitoring: a red run and its log; what fails loudly (HTTP errors) and what fails silently (a renamed field, an empty list, a stale forecast); a freshness check.
10. Other places to run a schedule: the table of hosted schedulers and their free tiers, each checked against its provider's current pages.
11. Recommended Exercises (rewritten for the companion notebook: a different NWS grid point or product, a freshness check, a workflow they write), Additional Exercises, Social History and Public Interest, Common Issues to Debug, Key Takeaways, Further Reading.

**Lab 14** (course repository, `labs/week-14/`; key, students' copy, PDF; `labs/AUTHORING.md`):
- **Wednesday, Part 1 (50 minutes):** set up; one request by hand to `/points`, then the hourly forecast; read `collector.py`; make a public repository and put the template in it from the Canvas zip; press "Run workflow"; watch the run's log; see the commit; read the new rows from the repository's raw URL.
- **Friday, Part 2 (35 minutes, then 15 on checkpoint 4):** read the course's longer series; the forecast for one hour across runs; how often the forecast actually changed; a freshness check; a broken run on purpose (a mistyped URL), and its red X and log.

**Deck 14** (course repository, `slides/week-14/`): built to `slides/common/AUTHORING.md`'s "Layout and density": one short code block per frame, narration on the left, no printed outputs. Includes the other-services table.

## Standing constraints

- No keys are needed. Never print a key if one appears.
- User-Agent: `WebDataScience/1.0 (your-email@colorado.edu)` in the chapter and the students' copies; the instructor's address only in the course's own workflow.
- Don't print private individuals' names; NWS forecasts have none.
- Don't mention writing tools or skills in commits or pull requests.
