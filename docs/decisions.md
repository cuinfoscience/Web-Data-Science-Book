# Decision log

Standing decisions for the book and its tools, newest first. Each entry gives the decision, the reason, and where the decision is written or enforced. Entries are never deleted. When a decision is replaced, it is marked *superseded*, with a link to the entry that replaces it. Proposals that nobody has decided yet are listed in [`handoff.md`](handoff.md), not here.

## 2026-10-05 · Earlier chapters point to the examples that later chapters add

**Decision.** When a later chapter, or an open issue, adds an example that an earlier chapter's discussion would benefit from, the same pull request updates the earlier chapter: a cross-reference, and a sentence that says what the later example adds. The edit keeps to lines that students' open pull requests don't touch, and the description names any overlap.

**Why.** The maintainer: "Always update earlier chapters as examples in late chapters or current issues would benefit from references and discussion." Without the pointer, a reader of chapter 2's court cases or chapter 3's API prices doesn't learn that chapter 8 puts them to work.

**Where.** `AGENTS.md` ("Extending the Book", item 7). First applied with chapter 8's logins and credentials, below: chapters 1, 2, 3, and 5 now point to it.

## 2026-10-05 · Chapter 8 teaches logging in by hand, headless browsing, and keeping credentials out of code

**Decision.**
- Chapter 8 shows a browser logging in to a practice site, quotes.toscrape.com, which accepts any username and password. The reader logs in by hand while the cell waits on `input()`, so the book's code never holds a password. Where code must log in by itself, the password comes from an environment variable or `getpass()`. The session is kept in a Chrome profile folder outside the project, treated like a password.
- The chapter says what logging in changes: the Terms of Service bind the reader, what the account sees isn't public, and the account is the reader's to lose. It names the routes that ask first: an API, a researcher program, data donation, and the site's permission.
- Headless mode is a section of its own. A screenshot shows what the browser drew, and the chapter says what a site still sees: `HeadlessChrome` in the User-Agent, and `navigator.webdriver`. `--no-sandbox` is for containers that run Chrome as root, not for a reader's computer.
- With conda-forge's `selenium`, Selenium Manager is a package of its own, and activating `webdata` sets `SE_MANAGER_PATH` to it. Step 1 sets the variable from `sys.prefix` when Jupyter started without it, and the chapter tells readers who add `selenium` to restart Jupyter from an activated `webdata`, since restarting the kernel isn't enough.
- The toolkit still never signs in (2026-09-23).

**Why.** The maintainer asked for logging in to be taught as the cheaper alternative to a paid API, with its real ethical costs, and for headless browsing and the worst and best practices with credentials to be covered. Chapter 3's API prices make the logged-in route the one students are most likely to try. The `SE_MANAGER_PATH` change comes from a test on 2026-10-05: conda-forge's `selenium` 4.50 depends on `selenium-manager` 4.50, which installs `bin/selenium-manager` (`Scripts\selenium-manager.exe` on Windows) with activation scripts that set the variable. A Python that hadn't been activated raised `NoSuchDriverException: Unable to obtain driver for chrome`, caused by `Unable to obtain working Selenium Manager binary`; setting the variable in the notebook fixed it. conda's shell wrapper re-activates the environment after `conda install`, but a Jupyter that was already running keeps its old environment, and so does every kernel it restarts.

**Where.** `ch-08-dynamic-pages.qmd` ("Setting Up Selenium", "Headless Mode", "Pages Behind a Login", "Choosing a Tool", "Common Issues to Debug"); `ch-01-introduction.qmd` ("Common Issues to Debug"); in the course repository, week 8's deck and handout, and week 1's setup handout.

## 2026-10-02 · Chapter 5 drops scapy for the operating system's own tools

**Decision.**
- Chapter 5 no longer uses scapy. Its traceroute and packet-sniffing code needed `sudo jupyter notebook` (or an Administrator prompt on Windows) and Npcap, which ran the whole notebook with root privileges.
- `ping`, `traceroute` (`tracert` on Windows), and `curl -v` take their place. They run from notebook cells with Jupyter's `!`, which needs no install and no administrator rights. Each cell picks the right command for the reader's system with `platform.system()`.
- The book has readers sniff no packets. Chapter 5 explains packets and the TCP handshake with `curl -v`'s account of a connection, and points to Wireshark, on a computer the reader owns, for anyone who wants to see the packets.

**Why.** The maintainer: scapy's install and its `sudo` launch were disruptive and confusing, and running a notebook with `sudo` sets a bad example. Every system ships these tools, and they show the same path and the same handshake without elevated privileges. Students' #106, #111, and #112 edit the scapy text this removes.

**Where.** `ch-05-protocols.qmd` ("TCP/IP: The Transport Layer", "Common Issues to Debug", the graduate extension, "Further Reading"), and week 5's deck in the course repository.

## 2026-10-02 · `webdata` comes from conda-forge with every library the chapters import; the stopword list is a text file

**Decision.**
- Chapter 1 and the course's setup handout create `webdata` in one command: `conda create -n webdata --override-channels -c conda-forge python=3.14 notebook requests beautifulsoup4 lxml pandas matplotlib seaborn gensim dnspython selenium playwright-python pypdf pdfplumber praw spotipy atproto mastodon.py openai anthropic`. It replaces `conda create -n webdata python=3.14` followed by `pip install notebook requests beautifulsoup4 pandas matplotlib seaborn`.
- Chapters no longer install their own libraries. Where a chapter used to say `pip install X`, it says that X is in `webdata`, and gives `conda install -c conda-forge X` for an environment made before this change. A chapter that needs a new library adds it to chapter 1's command.
- Chapter 7 reads its stopwords from `data/stopwords-en.txt` in this repository, fetched with `requests`, in place of NLTK's `stopwords` corpus. The file is NLTK's English list, unchanged. NLTK is no longer a dependency of the book's code.
- Two steps stay in their chapters because they aren't packages: Playwright's browsers (chapter 8) and API keys (chapters 11 to 13).

**Why.** The maintainer asked for every chapter's libraries to be installed in week 1. An audit of the chapters' imports found three that week 1's environment lacked and no chapter installed: `lxml`, which chapter 6's `pd.read_html()` needs, `dnspython` (chapter 5), and `scipy` (chapter 13). Chapter 7 also needed gensim, which has no Python 3.14 build on PyPI, and NLTK, whose corpus download it left commented out. Everything in the new command solves together on conda-forge for Python 3.14, checked on 2026-10-02. All 22 modules the chapters import load in the environment it builds. The same packages, added to a copy of an environment made the old way, load too. conda-forge's `playwright` package is the Node.js command-line tool; the Python library there is `playwright-python`, a release behind PyPI.

**Where.** `ch-01-introduction.qmd` ("Setting Up Your Environment", "Core Libraries", "Common Issues to Debug"), the install notes in chapters 4, 7, 8, 9, 12, and 13, `data/`, `README.md`, `AGENTS.md`, and, in the course repository, `handouts/week-01/setup.md` and the decks that showed installs.

## 2026-09-25 · The course's User-Agent takes the form the chapters teach

**Decision.**
- The book's tools and captures send `WebDataScience/1.0 (brian.keegan@colorado.edu)`: a name and version, then contact information in parentheses, the form chapter 1 teaches. It replaces `Web Data Science/v1 brian.keegan@colorado.edu`, and names the same project and contact.
- Examples keep `WebDataScience/1.0 (your-email@colorado.edu)`, with the reader's own address.
- An image captured before this keeps its record, which names the old string. A retake sends the new one.

**Why.** Wikimedia's API gateway gives a request with no identifying User-Agent 10 requests a minute, shared by every such request from its address, and "a compliant User-Agent header" 200 (mediawiki.org, "Wikimedia APIs/Rate limits"). The old string wasn't in that form. The pageviews API answered it with 429 on the first request, four times on 2026-09-24, and figure 1-4 was put down to the session's network. On 2026-09-25 the same session got 200 with the new string. The maintainer diagnosed it and approved the change.

**Where.** `tools/shots/lib/recipes.py` (the default), `tools/shots/README.md`, and `AGENTS.md`. *Supersedes* the User-Agent string in "The course's User-Agent is the one robots.txt is read for" and "One honest identity for captures and examples", below; the rest of both stands. Chapter 6 and week 6's Oscars handout, which the maintainer keeps, still show the old string.

## 2026-09-24 · A figure of an API's response is captured as an API client

**Decision.**
- A figure that shows an API's response, the request a chapter's own code makes, is captured even where the API host's robots.txt disallows the path. It sends the course's User-Agent and makes one request per take, at the chapter's own address.
- robots.txt still governs every other page a figure loads. A recipe marks an API's response with `api_client: true`, and `doctor` then reports the disallow as a note instead of a warning.
- The first two: the Open-Meteo forecast in chapter 4 (figure 4-2), and Twitter API v1.1's part of chapter 3's figure on retired endpoints.

**Why.** api.open-meteo.com's robots.txt disallows every path, and api.twitter.com's disallows every path for all but Googlebot and Bingbot, so the back-fill had left both figures out and asked. Chapter 2 says robots.txt addresses crawlers, and that deliberate API clients follow the API's own terms; the chapters' code sends every reader to both endpoints.

**Where.** `tools/shots/lib/recipes.py` (`api_client`), `tools/shots/lib/robots.py` and `tools/shots/shots.py` (`doctor`), `tools/shots/README.md` ("Field notes"), and `AGENTS.md`. *Amends* "The course's User-Agent is the one robots.txt is read for", below.

## 2026-09-24 · Students' pull requests merge after a Friday code-review standup

**Decision.**
- Students' pull requests are merged in class, after a code-review standup on a Friday. Each author presents the change, a classmate reviews it, and the maintainer merges the approved ones with merge commits.
- Nobody merges a student's pull request at other times, and agents never merge one.
- The first session is on the course's roadmap: `docs/plans/2026-09-24-friday-code-review.md` in the course repository.

**Why.** About 40 student pull requests were open. Some overlapped, and four conflicted with `main` after the merges of #148–#152. Reviewing them together turns the backlog into the review practice the revision framework grades, and a merge in front of the class shows what happens next. Week 4's deck had told students they could merge their own, while `CONTRIBUTING.md` said the maintainer merges; this settles it.

**Where.** `CONTRIBUTING.md` ("Review and merge"), `AGENTS.md`, and, in the course repository, `handouts/common/revision-framework.md` and week 4's deck.

## 2026-09-24 · Recommend Python 3.14

**Decision.**
- The book recommends Python 3.14; 3.13 also works. Chapter 1's setup creates `webdata` with `python=3.14`.
- gensim, used in chapter 7, publishes no 3.14 wheels on PyPI as of September 2026. On 3.14 it comes from conda-forge (`conda install -c conda-forge gensim`), which builds it for 3.14.
- The CI workflows run 3.14 as well.

**Why.** The book named four versions (3.10 or later, 3.11 or later, 3.12 or later, and 3.12 in chapter 1's setup), and a student asked which one to use (#31). Every other library the book installs publishes 3.14 builds on PyPI, checked on 2026-09-24.

**Where.** `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, the preface (`index.qmd`), chapter 1's setup, chapter 7's gensim note, `.github/workflows/`, and the course's `handouts/week-01/setup.md`.

## 2026-09-24 · The course's User-Agent is the one robots.txt is read for

*The User-Agent string here is superseded by [2026-09-25 · The course's User-Agent takes the form the chapters teach](#2026-09-25--the-courses-user-agent-takes-the-form-the-chapters-teach); the rest stands.*

**Decision.**
- Every request the book's tools and scripts make for the maintainer sends the course's User-Agent, `Web Data Science/v1 brian.keegan@colorado.edu` (see the 2026-09-23 entry). None goes out with a library default, such as `python-requests/2.34`, or with a Claude agent's string.
- robots.txt is read for that User-Agent. A group addressed only to Claude's agents (`ClaudeBot`, `Claude-User`, and the rest) doesn't govern the book's captures; `doctor` lists such groups as a note, so they stay visible.
- Code examples send a User-Agent of the same form with the reader's own address, `WebDataScience/1.0 (your-email@colorado.edu)`, as chapter 1 does. The chapters' other strings are aligned once students' open pull requests on the same lines are reviewed.

**Why.** Wikipedia refuses the library default with a 403 (#5), so an example without a User-Agent fails as written. The chapter 4 back-fill had treated robots.txt groups for Claude's agents as binding on captures that send the course's User-Agent. The maintainer decided that the course's User-Agent, which names the project and a contact, is the identity robots.txt is read for.

**Where.** `tools/shots/lib/recipes.py` (`DEFAULTS`), `tools/shots/shots.py` (`doctor`), `tools/shots/README.md` ("Field notes"), and `AGENTS.md`. *Amends* "One honest identity for captures and examples", below.

## 2026-09-24 · A screenshot may relax to 1024×768 when that is clearer and still legible

**Decision.**
- 800×600 CSS pixels stays the default for what a screenshot shows.
- A screenshot may show up to 1024×768 when both of these hold:
  - the extra room removes clutter: rows that wrap, columns cut short with "…", panels squeezed together;
  - its text still passes `tools/shots/run check` everywhere it is shown: 11 pixels in the book, 16 on a 1920-pixel slide, 6 points in print.
- The recipe says what the room removes, in `oversize:`. The tools warn about a figure in that range that has no reason, has text too small at any target, or has text that was never measured.
- Beyond 1024×768, a recipe still needs a reason, such as DevTools zoomed to 175% for print.

**Why.** The 800×600 cap fixed tiny text, but under the cap alone some figures came out crammed (see "Figures are readable at both ends", below). The maintainer asked to allow 1024×768 when it keeps text legible and reduces clutter. At 1024 pixels wide, the book's column shows text at 76% of its size on screen, against 97% at 800. So the legibility check, not the size, stays the test: on-screen text needs about 14.5 CSS pixels, which for DevTools means zooming to about 150%.

**Where.** `tools/shots/lib/legibility.py` (`SOFT_LIMIT`, `RELAXED_LIMIT`, and `size_verdict`), `tools/shots/run check`, `tools/shots/README.md` ("The rules" and "Legibility"), `AGENTS.md`, and the course's `slides/common/AUTHORING.md`. *Amends* "A screenshot shows at most 800×600 CSS pixels of the screen", below.

## 2026-09-24 · No browser banners in figures

**Decision.**
- Figures don't show Chrome for Testing's "only for automated testing" notice, or any other infobar.
- Headed captures launch Chrome with `--disable-infobars`. `tools/shots` fails a headed take whose bars above the page are taller than the tab strip and address bar.
- The one exception is a figure whose subject is the bar: ch-08's window opened by Selenium, whose caption points at it. Its recipe says `expect: {infobar: true}`.

**Why.**
- The notice is 55 pixels of browser chrome that says nothing about the page, and it repeats in every capture that has it.
- It was in figures made by scripts before the toolkit, which ran Chrome without the switch: ch-08's `network-tab-json` and `xkcd-inspect`, and week 08's `network_json.png`.
- The toolkit's own captures had it off only because Playwright passes the switch by default.

**Where.** `tools/shots/lib/headed.py` (the switch and the guard), `tools/shots/README.md` ("No infobars"), `AGENTS.md` ("Figures and screenshots"), and the course's `slides/common/AUTHORING.md`.

## 2026-09-24 · Chapter work resumes

**Decision.** The maintainer lifted the pause set after the chapter 5 pilot. The order of work:
- The screenshot back-fill of chapters 1–4 comes first, in the plan's order: ch-04, ch-01, ch-02, ch-03. Each chapter gets one textbook PR and one course PR.
- Two gates come before it: the pilot's resolution note, and effect tests for the DevTools preferences (AAR P0-3).
- The chapter 7–8 and slide retakes (AAR P2-1) follow the back-fill.
- Computed outputs wait on their plan's §9 decisions, not on the pause.

**Why.** The pause existed to review the toolkit and the process before scaling them. That review is done: the AAR, its P0 text (#140, course #53), and the pilot gate, closed on 2026-09-24.

**Where.** [`handoff.md`](handoff.md), and [`plans/2026-09-24-screenshot-backfill-ch01-05.md`](plans/2026-09-24-screenshot-backfill-ch01-05.md). *Supersedes* "Pause chapter work after the chapter 5 pilot", below.

## 2026-09-24 · Figures are readable at both ends

**Decision.**
- A figure is scoped to what its paragraph discusses, then enlarged. Text too small and a figure too crammed both fail the reader.
- Crop to the subject, and hide the panels, columns, and sidebars the text doesn't mention.
- Enlarge by zooming the application, not by widening the window.
- `tools/shots/run check` is the one place that judges text size: 11 pixels in the book's column, 16 on a 1920-pixel slide, 6 points in print.
- The 800×600 cap stays, as a soft limit inside this rule.

**Why.** The 800×600 cap fixed the tiny text of whole-window captures. The chapter 5 pilot then squeezed DevTools into the cap, and the figures came out crammed: the Styles pane took 40% of the width, rows wrapped, and columns were cut short. Separately, the slide rule in `AUTHORING.md` (W/1680 of the text width) was too small for DevTools text by the toolkit's slide threshold. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.1, P0-1.)

**Where.** `AGENTS.md` ("Figures and screenshots"), the course's `slides/common/AUTHORING.md` ("How much a screenshot shows"), and `tools/shots/lib/legibility.py`. *The cap was relaxed the same day: a figure may show up to 1024×768 when its text still passes (entry above).*

## 2026-09-24 · Pull requests merge with merge commits; history is never rewritten

**Decision.**
- Merge pull requests with merge commits. Do not squash or rebase.
- Never force-push a branch someone may have seen.
- Open a new branch for each pull request, and don't base one pull request on another's unmerged branch.
- A session given one fixed branch restarts it from `main` after each merge. With merge commits, that is a fast-forward, not a force-push.
- Agents merge only when the maintainer asks, and never merge a student's pull request.

**Why.** Squash merges left the session's branch behind `main` after every merge. It had to be reset and force-pushed, about six times in one day, and one stacked pull request had to be rebased. The review history became hard to follow, and the maintainer asked why. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.3.)

**Where.** This log, and `AGENTS.md` ("Git and Pull Requests"). A permission rule that denies force-pushes is proposed and untested (P0-2). *Supersedes* the squash merges used up to #138.

## 2026-09-24 · Pause chapter work after the chapter 5 pilot

*Superseded the same day by "Chapter work resumes", above.*

**Decision.** After the chapter 5 screenshot pilot merged (#138 here, #51 in the course repo), stop implementation on other chapters until the maintainer resumes it. That covers the back-fill of chapters 1–4, the retakes for chapters 7–8 and the slides, and computed outputs.

**Why.** Review the toolkit and the process before scaling them. The pilot found five toolkit bugs, plus figures that were too crammed to read.

**Where.** [`handoff.md`](handoff.md) lists what is paused.

## 2026-09-24 · One instructions file, `AGENTS.md`; records in `docs/`

**Decision.**
- The agent instructions live in `AGENTS.md`, renamed from `claude.md`. `CLAUDE.md` only imports it. An agent that looks for another file (`GEMINI.md`, `.cursorrules`) is pointed at `AGENTS.md` by the README.
- Project records live in this repository's `docs/`: AARs, plans, this log, and the hand-off note. The screenshot AAR and plans moved here from the course repository, which keeps pointers.

**Why.** Agents and their tools look for these names. The lowercase `claude.md` was not found by the AAR's own collector. Records sit beside the code they govern: `tools/shots` is here. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.5.)

**Where.** `AGENTS.md`, `README.md` ("For AI Agents"), [`README.md`](README.md) in this folder.

## 2026-09-24 · A screenshot shows at most 800×600 CSS pixels of the screen

**Decision.** A screenshot figure shows at most 800×600 CSS pixels of the screen. A recipe that needs more says why in `oversize:`.

**Why.** Whole-window captures shrank text to 42–71% of its on-screen size in the book's 778-pixel column. DevTools' text came out near 5 pixels.

**Status.** Standing, as the soft limit inside the entry above, "Figures are readable at both ends". The cap is a heuristic that serves that aim. Under the cap alone, the chapter 5 pilot produced crammed figures. ([AAR](aar/AAR_Web-Data-Science-Book_2026-09-24.md) §5.1.) *Amended the same day: 800×600 is the default, and a figure may relax to 1024×768 when the room removes clutter and its text still passes. See "A screenshot may relax to 1024×768 when that is clearer and still legible", at the top.*

**Where.** `tools/shots/lib/legibility.py` (`SOFT_LIMIT`), `tools/shots/run check`, the course's `slides/common/AUTHORING.md`, and `AGENTS.md`.

## 2026-09-24 · Screenshots come from a toolkit, and one chapter goes first

**Decision.** Screenshots are made with `tools/shots`. Each figure has a recipe, guarded capture, provenance, measured markers, and a check, so it can be made again. A new use of the toolkit is piloted on one chapter before it rolls out.

**Why.** Scripts in a scratchpad made figures that no one could remake or trace. ([Screenshot AAR](aar/2026-09-24-screenshots.md), P0-2 and P1-4.)

**Status.** Milestones M1–M3 done (#135–#137). The chapter 5 pilot is done (#138).

**Where.** [`plans/2026-09-24-screenshot-toolkit.md`](plans/2026-09-24-screenshot-toolkit.md), `tools/shots/README.md`.

## 2026-09-24 · Real captures, or diagrams labeled as diagrams

**Decision.**
- A screenshot is a real capture of a real page, with its URL, date, and method recorded.
- Diagrams, charts, and renders drawn from live data are welcome, labeled as what they are. A render drawn to look like a browser window says so in its caption.
- Never rebuild a real site's interface by hand and fill it with invented content. If a page can't be captured, keep the placeholder, or show a real page that makes the same point.
- A count or date printed in a caption comes from a recorded query.

**Why.** Look-alikes of GitHub pages, filled with invented content such as a made-up pull request, sat among real screenshots. Only a commit message disclosed them. ([Screenshot AAR](aar/2026-09-24-screenshots.md), P0-3.)

**Where.** The course's `slides/common/AUTHORING.md` ("What counts as a screenshot"), and the toolkit's provenance and `check`. `check` matches each image against its recorded capture.

## 2026-09-23 · One honest identity for captures and examples

*The User-Agent string here is superseded by [2026-09-25 · The course's User-Agent takes the form the chapters teach](#2026-09-25--the-courses-user-agent-takes-the-form-the-chapters-teach); the rest stands.*

**Decision.**
- Captures and the book's request examples identify themselves with one User-Agent: `Web Data Science/v1 brian.keegan@colorado.edu`.
- They wait 8–30 seconds between page loads on a host.
- No logins, and no student names or student work in any image.
- Traces of the capture setup stay out of frame: the proxy's address, the egress IP, and location cookies.

**Why.** Sites can see who is asking and can refuse. The book teaches identifying yourself, so its own tools do too.

**Where.**
- The identity and pacing are set in one place, `tools/shots/lib/recipes.py` (`DEFAULTS`). The toolkit's selftest reads the identity back from a local server, Client Hints included.
- The rule on capture traces is in `AGENTS.md`, under "Figures and screenshots".

## Before 2026-09 · Code in the book is narrative

**Decision.** Code blocks do not run when the book is built (`execute: eval: false` in `_quarto.yml`), and the companion notebooks ship without outputs.

**Why.** "Running code, seeing it fail, and debugging it is where the learning happens" (`index.qmd`).

**Status.** Standing. Showing computed figures and tables is proposed in [`plans/2026-09-24-computed-outputs.md`](plans/2026-09-24-computed-outputs.md). That plan keeps the notebooks free of outputs.
