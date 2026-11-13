# Boulder's hourly forecast, collected every hour (chapter 14)

`forecasts.csv` is the series that chapter 14's "Reading What It Collected" and "Failures and
Monitoring" read: the National Weather Service's hourly forecast for Boulder, Colorado
(`https://api.weather.gov/gridpoints/BOU/54,75/forecast/hourly`), saved by `collector.py`
from the course repository's `labs/week-14/template/`, one row per forecast hour, about 156
rows a run.

<!-- TODO(Tuesday refresh): replace this paragraph and the file. -->
**This copy is an interim one, for drafting.** Its first run (156 rows, collected
2026-11-13T02:23Z) is the course repository's own first run, made by hand; the runs after it
were made by the same `collector.py`, unchanged but for the User-Agent's address, run at minute
17 of each hour (UTC) from the machine the chapter was drafted on: five runs, 03:17 to 07:17 UTC
on 2026-11-13, for six in all (936 rows). Before
the chapter merges, it is replaced by a copy of the course repository's
`labs/week-14/data/forecasts.csv`, which `.github/workflows/collect-boulder-forecast.yml` writes
every hour, and this section then says when it was copied and from which commit.

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
