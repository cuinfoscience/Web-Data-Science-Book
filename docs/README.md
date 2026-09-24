# Project records

The records behind the book: what was decided, what was planned, what was reviewed, and where work stands. None of it is book content, and Quarto does not render it.

Read [`handoff.md`](handoff.md) and [`decisions.md`](decisions.md) before starting work. `AGENTS.md` at the repository root says the same for agents.

| Path | What it holds | How it is kept |
|---|---|---|
| [`handoff.md`](handoff.md) | Where work stands: what is done, paused, waiting on a decision, or known to be broken | Rewritten, not appended, when a session stops or the state changes. It describes the present. History lives in git and in the other records. |
| [`decisions.md`](decisions.md) | Standing decisions, with the reason for each and where it is enforced | Newest first. A decision is never deleted. When one is replaced, mark it *superseded* and link the entry that replaces it. |
| `aar/` | After-action reports: what the written rules said should happen, what happened, why the two differed, and the revisions that follow | One file per review. Newer reports are named `AAR_<repo>_<YYYY-MM-DD>.md`, the pattern the review skill's collector searches for. A report is not rewritten after the fact. When one of its actions is resolved, update the report's tracking table and add a dated note. |
| `plans/` | Plans for larger pieces of work, usually recommended by an AAR | Named `YYYY-MM-DD-<topic>.md`. A plan records a proposal and the decisions behind it. Once work starts, progress goes in `handoff.md` and the AAR's tracking table, not in the plan. |

## Current contents

| File | What it is |
|---|---|
| [`aar/2026-09-24-screenshots.md`](aar/2026-09-24-screenshots.md) | The first screenshot AAR. It covers the screenshots, editing, and annotation in chapters 7–8, course weeks 7–8, and the week-6 handout, before the toolkit existed. It moved here from the course repository. |
| [`aar/AAR_Web-Data-Science-Book_2026-09-24.md`](aar/AAR_Web-Data-Science-Book_2026-09-24.md) | The `tools/shots` sprint for chapters 5, 7, and 8. It is written for agents on other books who copy the toolkit, and it includes a design sketch and a porting checklist. |
| [`plans/2026-09-24-screenshot-toolkit.md`](plans/2026-09-24-screenshot-toolkit.md) | The screenshot toolkit, `tools/shots` (milestones M1–M3 done). |
| [`plans/2026-09-24-screenshot-backfill-ch01-05.md`](plans/2026-09-24-screenshot-backfill-ch01-05.md) | Back-filling real screenshots in chapters 1–5, their slides, and handouts. The chapter 5 pilot is done; the rest is paused. |
| [`plans/2026-09-24-computed-outputs.md`](plans/2026-09-24-computed-outputs.md) | Computed figures and DataFrame tables on the website, with notebooks kept free of outputs and code re-run only when code changes. Proposed. |

The course repository ([cuinfoscience/INFO4617-Fall2026](https://github.com/cuinfoscience/INFO4617-Fall2026)) keeps its own `docs/` for course-only reviews, such as the week-6 slides AAR. Its README points here for everything about screenshots and the book.
