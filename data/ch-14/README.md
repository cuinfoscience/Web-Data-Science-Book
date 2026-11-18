# Boulder's hourly forecast, collected on a schedule (chapter 14)

`forecasts.csv` is the series that chapter 14's "Reading What It Collected" and "Failures and
Monitoring" read: the National Weather Service's hourly forecast for Boulder, Colorado
(`https://api.weather.gov/gridpoints/BOU/54,75/forecast/hourly`), saved by `collector.py`
from the course repository's `labs/week-14/template/`, one row per forecast hour, about 156
rows a run.

**This copy is frozen.** It is the course repository's `labs/week-14/data/forecasts.csv`, byte
for byte, as of commit `acd392a1e33ac8f7d45b5e7f1a3ebcf2df3726d8` of
`cuinfoscience/INFO4617-Fall2026` (the run of 2026-11-17T20:59Z), copied on 2026-11-17 at
23:34 UTC: 2,808 rows from 18 runs, 2026-11-13T02:23Z to 2026-11-17T20:59Z, holding 13 versions
of the forecast (`update_time` from 2026-11-12T18:46:17Z to 2026-11-17T18:45:49Z). The course's
own file keeps growing until December 11, 2026; the chapter's printed outputs, its chart, and
the numbers in its text come from this copy.

**The runs are sparse, and the chapter reports that.** The course's workflow,
`.github/workflows/collect-boulder-forecast.yml`, is scheduled for minute 17 of every hour (UTC).
The first run (02:23Z on November 13) was made by hand before the workflow was merged, and the
second (04:30Z) with the workflow's "Run workflow" button. GitHub started the other 16 on the
schedule, the first at 13:10Z on November 13, and they came 4.0 to 10.6 hours apart (median 6.9),
three or four a day. The instructor decided on 2026-11-13 to keep the series as GitHub's schedule
makes it, with no outside trigger; "When Did the Runs Actually Run?" measures the gaps.

**One version is known to be missing.** An earlier, interim copy of this file (in this
repository's history until 2026-11-17) held the first run above and five runs made by the same
`collector.py` at minute 17 of each hour, 03:17 to 07:17 UTC on 2026-11-13, from the computer
the chapter was drafted on. Its 07:17 run saved a forecast updated at 2026-11-13T06:46:19Z. The
course's file has no run between 04:30Z and 13:10Z that day, and so no row of that version; the
chapter's "How Often Did the Forecast Change?" says so.

| Column | Meaning |
|---|---|
| `collected_at` | When the run asked for the forecast (UTC) |
| `update_time` | When the NWS last updated the forecast (`updateTime`; UTC) |
| `start_time` | The hour the row forecasts (Mountain time, with its offset) |
| `temperature` | Degrees Fahrenheit |
| `precip_chance` | Probability of precipitation, percent; empty where the NWS gave `null` |
| `wind_speed`, `wind_direction` | As the NWS prints them, such as `5 mph` and `W` |
| `short_forecast` | Such as `Clear` or `Chance Snow Showers` |

NWS data is a work of the U.S. government; the NWS calls the API's contents "open data, free to
use for any purpose" (https://www.weather.gov/documentation/services-web-api, checked
2026-11-13).
