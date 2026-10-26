# Plan: week 11 after Monday's lab

**Status:** Proposed 2026-10-26, from the instructor's notes on Monday's live-coding lab. The textbook side is the pull request that adds this plan; the course side needs a session that can reach the course repository (`cuinfoscience/INFO4617-Fall2026`), which this one couldn't. It replaces the week in [`2026-10-25-ch11-four-apis.md`](2026-10-25-ch11-four-apis.md), §5, for Wednesday and Friday.

## What Monday showed

From the instructor's notes, 2026-10-26:

1. **Keys.** `os.environ['CENSUS_KEY']` raised `KeyError` for students who had run `export`.
2. **Start from the website and the documentation.** Students wanted a list or sample of groups and their variables first, and to go from the web interface to the same data from the API.
3. **Concrete examples throughout.** Part 1's step 2, the list of geographies, was a distraction: "what are students supposed to do with a list of geography ontologies?"
4. **Pace.** The class reached the start of step 4. Steps 4 and 5 move to Wednesday, before FRED.
5. **Scope.** Congress.gov is dropped. The rest of the week is Census, FRED, and perhaps the EIA. The instructor decided the same day to drop it from the chapter too.

## The chapter, after this plan's pull request

- **Keys:** three, `CENSUS_KEY`, `FRED_KEY`, and `EIA_KEY`. `DATAGOV_KEY` is gone. "When a Key Says `MISSING`" lists the causes of a `KeyError`: Jupyter started elsewhere or before the variable was set, `!export` in a cell, `export` on Windows, conda without reactivating, or a different name. A stopgap cell asks for a missing key with `getpass()`.
- **Census:** the section goes from table B19013 on data.census.gov to the same numbers from the API.
  - its group in `groups.json`, searched for "median household income";
  - the group's variables in `groups/B19013.json`;
  - Boulder County's request, which returns the website's \$103,994 ± 2,268;
  - the same variable for Colorado, Boulder County, and the city of Boulder: \$95,470 ± 578, \$103,994 ± 2,268, and \$87,493 ± 6,221.
  - `variables.json` and `geography.json` are gone. The dataset's `geography.html` and `examples.html` pages are linked for other kinds of place.
- **FRED, the EIA, and the Census–EIA join** are unchanged.

## The lab: proposed changes, for a session with the course repository

Follow course `labs/AUTHORING.md` as before: run with `labs/tools/run_key.py`, compare the `not-run-live` cells, write the key note last, then make the students' copy and the PDF.

**Part 1 (Monday, already taught), revised so the key matches the chapter:**
- three keys, and the `MISSING` checklist with the `getpass()` stopgap in the setup step;
- step 2's geography listing replaced by the chapter's groups → variables → same numbers sequence;
- the three places (state, county, city) as the geography example.

**Part 2, Wednesday:**
1. **Step 0:** reload the keys, using the `getpass()` stopgap for anyone whose key is still `MISSING`.
2. **Part 1's steps 4 and 5**, which Monday didn't reach, as written after the revision above.
3. **FRED:** series metadata; observations with a fixed end date; `units`; `frequency` with `aggregation_method`, Denver against the nation.
4. **The EIA, if time allows:** routes that describe themselves; a facet's values; Colorado's residential price. Paging can wait for Friday.

**Part 3, Friday:** no Congress.gov.
- the EIA, from wherever Wednesday stopped, through paging with `offset` and `length`;
- if time allows, the Census–EIA join, which reuses Monday's Census and Wednesday's EIA;
- "What did we learn?";
- the Friday revision block, aimed at sections no pull request this week will touch again.

**Slides:** remove the Congress.gov frames, and rebuild Wednesday's and Friday's frames from the chapter. No gray blocks.

**Course facts:** the key names' row in course `docs/course-facts.md` drops `DATAGOV_KEY`. Update every copy it lists, the students' keys announcement among them, if it is to be reposted.

## Open questions for the instructor

- Does Friday include the join, or stop at the EIA?
- Should the students' copy of Part 1 be regenerated, given that students already have Monday's copy?
