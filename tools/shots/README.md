# tools/shots

Capture, check, and record the book's screenshots, so that every figure can
be made again the same way and says where it came from. The plan and the
after-action report behind it are in this repo's `docs/`:
[`docs/plans/2026-09-24-screenshot-toolkit.md`](../../docs/plans/2026-09-24-screenshot-toolkit.md) and
[`docs/aar/2026-09-24-screenshots.md`](../../docs/aar/2026-09-24-screenshots.md).

Done so far:

- **M1:** headless captures, guards, retries, provenance, and `check`.
- **M2:** headed captures of browser UI (DevTools, View Source), with real input on a virtual display.
- **M3:** numbered markers placed from what the browser measured, a legibility check at each size a figure is shown, side-by-side composites, and contact sheets.
- **M4:** engines for the two ch-08 figures whose subject is a tool itself: the window Selenium opens, and Playwright's recorder (see Engines); evidence queries, the queries behind the numbers and claims in captions (see Evidence); `sync`, which copies figures into the course repo with a record of each (see Sync to the course repo); `import`, which makes a person's screenshot of a page behind a login a take like any other (see Hand captures); and `check` in CI, on pull requests that change images or the toolkit (see Checks).

## Quick start

```bash
bash tools/shots/bootstrap.sh --headed --tex      # once per container; safe to re-run
tools/shots/run doctor ch-07                      # every time, first: can this session capture?
tools/shots/run capture ch-07                     # takes go to tools/shots/out/ch-07/<figure>/
tools/shots/run sheet ch-07                       # look at every take at the size it will be shown
tools/shots/run compare ch-07 wayback-calendar    # same picture as the approved image?
tools/shots/run promote ch-07 wayback-calendar    # copy the take into images/ch-07/, record it
tools/shots/run evidence ch-07                    # run the queries behind the captions' claims
tools/shots/run check                             # before a PR
tools/shots/run sync ch-07 about-this-capture --to slides/week-07/img --as about_capture.png
                                                  # copy an approved figure into the course repo
tools/shots/run synced                            # every course copy against its record and source
tools/shots/run import ch-NN ID --file screenshot.png --by NAME --date YYYY-MM-DD
                                                  # a person's screenshot of a page behind a login
```

- **`bootstrap.sh`** does five things, plus two optional ones:
  - installs what is missing;
  - creates `tools/shots/.venv` with the pinned packages in `requirements.txt`;
  - fetches Chrome for Testing at a pinned major version (154) through Selenium Manager;
  - makes sure Chrome trusts the session proxy's certificate;
  - installs fonts, so pages in other scripts render as text and labels have a face;
  - with `--headed`, it adds the virtual display (Xvfb), real input (xdotool), and screen grabs (ImageMagick) that headed figures need;
  - with `--tex`, it adds pdflatex with TikZ and pdftocairo, which draw markers.

  It never runs `playwright install` and never turns off certificate checks.
- **`doctor`** answers whether capture works in this session. Do not reuse an earlier session's answer:
  - it checks the proxy, the browser, a real headless capture of example.com, and a real headed one with DevTools open;
  - it checks for TeX, and fails if a recipe has markers and TeX is missing;
  - with a chapter, it makes one request to each host that chapter's recipes use, a composite's parts included, and reads that host's robots.txt for the capture's User-Agent, noting any group addressed to Claude's agents (see "Field notes"). A disallowed page is a warning, unless its figure is an API's response marked `api_client: true`, which is a note. It warns when a host's `Crawl-delay` is longer than the pause its figures start at, and when robots.txt answers with something other than the file (EUR-Lex's browser check once answered 202 and an empty page). A server on this machine (`localhost`), such as chapter 1's Jupyter, is asked at the figure's own address instead: robots.txt doesn't apply to it;
  - it reports a proxy refusal as a policy block, which you report rather than route around. A host that a figure expects not to answer (`expect: {error: ...}`) is checked against public DNS instead, as `capture` does (see "Refusals and dead hosts").

## The rules

These come from `slides/common/AUTHORING.md` in the course repo and from the AAR:

- **Real or labeled.** A screenshot is a real capture of a real page. Diagrams and renders are welcome, marked with their `kind`. Never rebuild a real site's interface with invented content.
- **One honest User-Agent** for every request (`Web Data Science/v1 brian.keegan@colorado.edu`, the one the handouts teach). It goes to Chrome as Chrome's own `--user-agent` flag, so the User-Agent Client Hints (`Sec-CH-UA-Platform` and the rest) name the system the capture runs on. Playwright's `user_agent` option rewrites them too, and for a string that names no system it claims Windows. Page loads on one host are 8–30 seconds apart.
- **Retries:** a 5xx or a dropped connection is retried three times, 30, 60, then 120 seconds apart. A block page, a 403, or a proxy refusal is not retried.
- **No logins, no credentials, no student names or work.** A page behind a login is captured by the instructor by hand and brought in with `import`, which blacks out what the recipe's `redact:` boxes cover (see Hand captures).
- **No infobars.** Chrome for Testing puts a notice under the address bar: "Chrome for Testing … is only for automated testing". It is 55 pixels of browser chrome that says nothing about the page. Headed captures pass `--disable-infobars`, which keeps it off. `capture` fails a headed take whose bars above the page are taller than the tab strip and address bar (88 pixels), unless the figure's subject is the bar (`expect: {infobar: true}`, as for ch-08's Selenium window). The figures made before the toolkit ran Chrome without the switch and carried the notice.
- **Dated captions.** A figure that shows things that change (counts, versions, live pages) says in its caption when it was captured.
- **800×600 of the screen, or up to 1024×768 when that is clearer.** A figure shows 800×600 CSS pixels of the screen by default (1600×1200 image pixels at scale 2). In the book's 778-pixel column its text then stays about the size it had on screen; a whole 1680-pixel window shrinks it to less than half. To show DevTools, zoom DevTools and crop to what the text discusses, rather than widening the window. A figure may relax to 1024×768 when two things are true:
  - the extra room removes clutter: rows that wrap, columns cut short with "…", panels squeezed together;
  - its text still passes the legibility check everywhere it is shown. At 1024 pixels wide the book's column shows text at 76% of its size on screen (97% at 800), so on-screen text needs about 14.5 CSS pixels: zoom DevTools to about 150%.

  The recipe says what the room removes, in `oversize:`. This is the first check, and a soft one: going over is a warning. Beyond 1024×768, a recipe needs a reason too.

## What the chapter 5 pilot settled

The back-fill plan made the chapter 5 pilot (#138, 2026-09-24) a gate before
chapters 1–4. These are the conventions it settled for later figures. The
dated record is in §9 of [the screenshot AAR](../../docs/aar/2026-09-24-screenshots.md).

- **Pick what a page or DevTools can show.** Native context menus (Copy
  selector, Copy as cURL) are drawn outside both, where steps and anchors
  can't reach, so the pilot skipped them. A few figures of what the prose
  asks the reader to find beat many: four of the eight candidates were enough.
- **Scope, then zoom.** Without these settings, the first takes under the
  800×600 cap came out crammed.
  - Zoom DevTools to 125%.
  - `layout: stacked, sidebar: 1` gives the Elements tree the full width.
  - `columns:` and `overview: false` hide what the text doesn't discuss.
  - A taller window cropped to DevTools (`crop: {devtools: true}`) gives the
    Network panel room.
- **Thresholds held.** The pilot's figures measure 12.8–14.6 pixels in the
  book. On slides, DevTools captures need 0.56–0.58 of the text width.
- **Markers.**
  - Numbered markers sit on measured anchors.
  - A brace marks a block of rows, and a box marks a control.
  - Nothing can mark an overlay Chrome draws itself, such as the picker's
    size label, so the caption names it.
  - Markers are drawn at the book's scale. On a slide at 0.75 of the text
    width they come out about half size, and a marker size per target is
    still to do.
- **Captions and alt text.**
  - Date the caption ("in September 2026").
  - Say what the capture setup changes that a reader would see: a first visit
    (`first_visit: true`), or HTTP/1.1 through the proxy.
  - Don't claim a route the capture didn't take.
  - The pilot's alt text ran 400–433 characters, transcribing what a reader
    needs from the figure.
- **Review.** The pull request's review table, one row per figure, is where
  figures are kept or cut. Its columns are section, what it shows, region,
  text size, markers, and notes. Copy anything a retake needs into
  `IMAGES.md`, because the pull request's text isn't in the repository.

## Field notes

What later captures taught, in chapters 1, 2, 3, 4, 7, and 8 (2026-09-22 to 24): each
note is a practice and the case behind it. Read the notes for the kind of page
you're about to capture before writing its recipe. When a capture teaches you
something the next agent would otherwise find out again, add a note here.

### Before the recipe

- **Read robots.txt for the course's User-Agent.** Captures send
  `Web Data Science/v1 brian.keegan@colorado.edu`, and robots.txt is read for
  it: the `*` group, unless a group names it. A group addressed only to
  Claude's agents (`Claude-User`, `ClaudeBot`, `Claude-SearchBot`,
  `Claude-Web`, `anthropic-ai`) doesn't govern captures (`docs/decisions.md`,
  2026-09-24). `doctor ch-NN` warns when the course's User-Agent is
  disallowed, and lists groups for Claude's agents as a note (`lib/robots.py`).
  The Guardian and www.bbc.co.uk have such groups; chapter 4's back-fill,
  captured before the decision, took no figure from either.
- **robots.txt is per host.** feeds.bbci.co.uk allows what
  www.bbc.co.uk forbids, and feeds.npr.org has no robots.txt at all (404).
  Check the host in the figure's own URL.
- **An API's response is captured as an API client.** api.open-meteo.com
  and api.twitter.com disallow every path. The maintainer decided on
  2026-09-24 that a figure of the request a chapter's own code makes is
  captured anyway, one request per take, as chapter 2's distinction between
  crawlers and API clients allows (`docs/decisions.md`). Mark it
  `api_client: true`, on the figure or on a composite's part, and `doctor`
  reports the disallow as a note. robots.txt still governs every other page:
  leave such a figure out and ask.
- **Design against a stand-in to keep to one request.** Chrome lays out a
  JSON or XML file the same way whatever serves it, so a local server that
  returns a copy of the response's shape is enough to work out the steps,
  crop, and marks (`tools/shots/.venv/bin/python -m http.server`, or a few
  lines of `http.server`). Then point the recipe at the real address and
  capture once, as figure 4-2 was made.
- **Keep to a host's `Crawl-delay`.** EUR-Lex's robots.txt asks for 10
  seconds between requests, so its figure sets `pause: [12, 30]`; `doctor`
  warns when a figure's pause starts below a host's delay.
- **Check the content type before choosing what Chrome will draw:**
  `curl -sI URL | grep -i content-type`. Chrome's XML viewer draws a foldable
  tree only for `text/xml` and `application/xml`. PBS NewsHour's feed
  (`application/rss+xml`) and Data Skeptic's (`text/plain`) show as raw text.
- **Pick content that won't pull attention from the lesson.** A live page
  carries that day's news. Chapter 4's feed figure uses the BBC's science
  section, not the front page, whose headlines that day were political. Say
  why in `IMAGES.md`.
- **Probe the page before writing its crop.** A short script prints where
  things are, and a clip shows what a crop would hold; the window and crop
  are then a few minutes' work, and `capture` confirms them:

  ```bash
  tools/shots/.venv/bin/python - <<'EOF'
  import sys; sys.path.insert(0, "tools/shots")
  from lib.env import chrome_path
  from playwright.sync_api import sync_playwright

  URL = "https://clerk.house.gov/xml/lists/MemberData.xml"
  with sync_playwright() as p:
      browser = p.chromium.launch(executable_path=chrome_path(),
                                  args=["--user-agent=Web Data Science/v1 brian.keegan@colorado.edu"])
      page = browser.new_page(viewport={"width": 800, "height": 700}, device_scale_factor=2)
      page.goto(URL, wait_until="load")
      for line in page.locator(".pretty-print .line").all()[:40]:    # what you might crop or mark
          print(round(line.bounding_box()["y"]), line.text_content()[:70])
      page.screenshot(path="tools/shots/out/probe.png", clip={"x": 0, "y": 42, "width": 800, "height": 600})
      browser.close()
  EOF
  ```

### Chrome's XML viewer (chapter 4)

- **What it draws.** `div.header` holds the note that the file has no style
  information, and `div.pretty-print` holds the tree. Each element with
  children is a `div.folder` whose first line has a fold triangle
  (`span.folder-button`) and the opening tag (`span.html-tag`). The text is
  13-pixel monospace, 15 CSS pixels a line.
- **Anchor the crop to the tree.** `crop: {selector:
  'div.pretty-print', pad: [6, 0, 0, 20], width: 800, height: 591}` leaves
  the note out, and still fits if the note's height changes.
- **Fold what the text ignores with Chrome's own triangles, and say so in the
  caption.** A folded element keeps three lines (its tags and "..."), so
  folding saves lines only for an element longer than that. Folding a
  one-line CDATA block saves nothing, but hides a line that would run past
  the edge.
- **Find a fold triangle by its tag's exact text:** `click: {selector:
  'text="<title-info>" >> xpath=preceding-sibling::*[1]'}`. CSS `:has()`
  with `:text-is()` ran for over a minute on the House roster's 18,000 lines
  and timed out; this takes about a second. In an XML file the viewer's
  elements are in the XHTML namespace, so an XPath step such as `//span`
  matches nothing: write `*`.
- **Text anchors count one match per tag:** `{text: '^<item>$', nth: 1}` is
  the second `<item>`. A tag that wraps, such as `<rss>` with its namespace
  declarations, takes `box: first-line`, or its marker lands past the right
  edge.
- **CDATA doesn't wrap** (`white-space: pre`), so a long description runs
  past the window's edge. Fold what the text doesn't need, and say so in the
  caption.

### View Source and the find bar (chapters 4 and 8)

- **Browser UI takes real input.** The find bar opens with `key: 'ctrl+f'` and
  fills with `type:`; page steps can't reach it.
- **Chrome centers the match, so scroll after searching, not before:** a
  `scroll: {selector: 'td.line-number[value="32"]', offset: 60}` step after
  `type:`.
- **The find bar covers the page's top right,** to about 47 CSS pixels below
  the toolbar. Put the line you're showing below it.
- **The bars are about 42 pixels of tab strip and 46 of toolbar.** A band crop
  from `top: 42` keeps the address bar, with its `view-source:` prefix, and
  leaves the tabs out.
- **Make the window 816 wide and crop 800,** so the page's 16-pixel scrollbar
  falls outside. Tick Line wrap (`click: {selector:
  'input[type="checkbox"]'}`) so long lines wrap rather than run off; a long
  URL with no break points can still run past the edge. A wrapped row is 15
  CSS pixels, and a new line about 17.
- **A `between` crop needs both of its lines in the window.** The page area is
  the window's height less 88. Make the window tall enough, and scroll the
  first line to a small offset: ch-08's `view-source-js` is 720 pixels tall,
  with line 11 at offset 4.
- **Mark a source line at its end.** A box around the line covers its line
  number. Anchor a marker to the line's cell with `box: first-line`
  (`td.line-number[value="33"] + td`); anchored to the link inside it, the
  marker sits on the closing quote.
- **Line numbers move when the site changes.** Before a retake, confirm the
  line the recipe names: `curl -s URL | grep -n 'application/rss+xml'`.

### Sizes and markers

- **Count lines before choosing a size.** At 15 pixels a line, 600 pixels
  hold 40. End a crop at the bottom of a line, or a sliver of the next one
  shows.
- **Keep 13-pixel text at 800 pixels wide.** It comes to 12.6 pixels in the
  book. At 1024 wide it would be 9.9, under the 11-pixel floor, so the relaxed
  limit suits DevTools zoomed to about 150%, not the XML viewer or View
  Source at 100%.
- **A marker on the bottom line can hang past the picture's edge.** The
  annotated image grows to hold it (by 3 pixels on ch-04's feed). To avoid
  that, end the crop a few pixels lower.
- **The narrowest legible width on a slide** is 16 × the image's width ÷
  (`p20` × 1920 × 0.875) of `\textwidth`, both in image pixels. Chapter 4's
  roster: 16 × 1602 ÷ (26 × 1920 × 0.875) = 0.59.

### Plain text and wiki pages (chapter 2)

- **A plain-text file is one text node.** Chrome shows robots.txt as one
  `<pre>`, so neither a selector nor a text pattern can pick out a line.
  `match:` searches the element's text with `^` and `$` at each line, and
  scrolls to or marks what it finds: `{match: '^User-agent: \*$', in: 'pre'}`.
  A multi-line pattern (`'^Allow: .*(?:\nAllow: .*)*'`) gives a brace the
  whole run of lines. End the pattern before a line's newline; a range that
  includes it can reach into the next line.
- **Plain text leaves the right side empty.** robots.txt's lines stop short
  of 600 pixels, so its figure is 600 wide, not 800, and the figure block's
  `width="78%"` shows it at its size on screen. A narrow crop with no width
  set fills the book's column: a 460-pixel crop of 16-pixel text would show
  at 27 pixels.
- **A page can move as it scrolls.** Scrolling Wikimedia's policy page past
  its header turned on the skin's sticky header, and the page's own header
  left the flow, lifting the content 40 pixels after the scroll step placed
  it. The `match` scroll measures again and corrects, up to three times.
- **Mark a block from its edge.** A marker aimed at a phrase that starts
  mid-line needs a leader line across the text. On the policy figure each
  marker sits at the left of its block (the paragraph, the example), and
  the caption names the sentence.
- **Crop to the text column.** At 800 pixels, the policy's text shares the
  width with a navigation box. The crop is the 460-pixel column, in a
  window 700 tall, so it starts below the page's floating contents button.

### Captions and notebooks

- **Brackets in a caption belong inside backticks.** `make_notebooks.py`
  once read a caption only up to its first `]`, so a chapter 4 caption that
  showed `<![CDATA[` left its figure unconverted in the notebook, with a
  relative image path and a raw `@fig-` reference. Since #151 it reads code
  spans and balanced brackets whole, and it exits with an error when a figure
  or reference is left unconverted. A stray `]` outside backticks still ends a
  caption, and the script says so.
- **Alt text that names what drifts is rewritten on a retake:** the first
  headline, the first member of the roster. `IMAGES.md` lists what to check.

### Jupyter and composites (chapter 1)

- **A figure of a local app needs the app running.** Chapter 1's Jupyter
  figures come from a real Jupyter server on this machine, set up with the
  chapter's own commands (`images/ch-01/IMAGES.md` has them). Run it with no
  token (`--IdentityProvider.token=''`), so the recipe's address carries no
  secret, and bind it to `127.0.0.1`. `doctor` asks a `localhost` figure's own
  address, since robots.txt doesn't apply.
- **Reset what a take changes.** Running a cell raises the kernel's execution
  count, so a retake would show `[2]:`. Close the notebook's kernel session
  first; Jupyter's API refuses the `DELETE` without its `_xsrf` cookie echoed
  in an `X-XSRFToken` header. Pre-answer first-run prompts the figure isn't
  about (Jupyter's news and update questions) with a settings override, and
  say so in `IMAGES.md`.
- **Capture the text as the reader will get it.** The companion notebook's
  Markdown cells are the chapter's own text, so a capture of the notebook
  follows edits to the chapter: regenerate the notebooks and copy the new one
  in before the take. Keep a figure's block out of the cells it captures;
  chapter 1 places both Jupyter figures after the code cell they show.
- **Some apps scroll a panel, not the window.** `scroll: {…, within:
  '.jp-WindowedPanel-outer'}` positions a cell in Jupyter's notebook panel.
- **Anchor to what is drawn.** In a rendered Markdown cell, a text pattern
  also matches the cell's hidden source editor, and `.first` picks the hidden
  one: anchor by selector (`.jp-RenderedMarkdown p:has-text(…)`). A text box
  measured over a wrapper includes the full-width boxes of the blocks inside
  it: anchor to the innermost element (`.jp-OutputArea-output pre`), or the
  marker lands at the far edge.
- **Chrome won't draw a normal window much under 500 pixels wide.** A headed
  take at 386 pixels came out about 500 wide and cropped, cutting the page's
  right side. For a narrow panel of browser UI, as in chapter 1's View Source
  half, make the window wider and crop the page; a headless take can be as
  narrow as the page allows.
- **Check the page's own width.** Wikipedia's layout wraps at 370 pixels in a
  headless take, so the article half of chapter 1's composite is 370 wide,
  and the pair fits 800×600 with its text at 12.7 pixels in the book.

### Refusals and dead hosts (chapter 3)

- **Show a refusal as the reader meets it.** A retired API that still runs
  answers with a status and a body. Pushshift's 403 is one line of JSON,
  `{"detail":"Not authenticated"}`, under Chrome's Pretty-print bar.
  `expect: {status: 403, text: ['Not authenticated']}` makes the refusal the
  take's subject.
- **A host that doesn't answer is shown as Chrome's own page.** `expect:
  {error: 'ERR_NAME_NOT_RESOLVED|ERR_TUNNEL_CONNECTION_FAILED'}` keeps the take
  when the page fails to load with that error, and fails it if the page loads.
  The error page arrives a moment after the failure, so `capture` waits for
  `chrome-error://` before it measures; an `evaluate` right after the failed
  `goto` meets "Execution context was destroyed".
- **Behind the proxy, a dead host looks like a refused one.** The session's
  proxy answers 502 to a tunnel it can't open, whether the host's name
  doesn't resolve or its policy refuses the host, and Chrome reports both as
  `ERR_TUNNEL_CONNECTION_FAILED`. So `capture` and `doctor` ask public DNS
  (Google's DNS over HTTPS). No address means a dead host, and the take is
  kept, with the answer in its log. An address means a policy block: it is
  reported, and the take is deleted. On 2026-09-24 api.crowdtangle.com's
  names answered SERVFAIL. The caption says the page names a failed tunnel
  because the capture went through a proxy; chapter 3 makes the same point
  about `ProxyError`.
- **Crop Chrome's error page from `.icon` to `.error-code`.** `#main-content`
  runs 40 pixels past the error's name, and the page is indented 24 pixels:
  `crop: {between: ['.icon', '.error-code'], left: 24}` lines it up with the
  part above it.
- **Stack parts that differ in height.** Side by side, a one-line JSON answer
  next to a 250-pixel error page leaves half the figure empty. `layout:
  {direction: column}` puts one above the other.
- **A site may check the browser before it answers.** EUR-Lex sometimes
  answers a first visit with 202 and a script that checks the browser, sets a
  cookie, and reloads. `capture` judges the page it shows (200) and keeps the
  first status as `first_status`. Its floating contents box (`#TOCSidebarSA`)
  covers the bottom quarter of the window until `click: {selector:
  '#tocHideBtnStandalone'}` closes it. Its paragraph ids start with a digit,
  so select them as `[id="040.004"]`; `#040.004` is not valid CSS.
- **reddit.com is only in the archive.** Its robots.txt disallows every path,
  so Reddit's 2023 pricing post (3-3) is the Wayback Machine's copy. See
  "Archived pages".

### Archived pages (chapters 3 and 7)

- **Check the claim in the archive before choosing the figure.** Chapter 3
  says Reddit announced $0.24 per 1,000 API calls. The archived JSON of the
  thread (`…/comments/145bram/_/jnk45rr.json`, 10 June 2023) holds u/spez's
  post: "the rate for apps that require higher usage limits is $0.24 per 1K
  API calls". That settled which page to show.
- **New Reddit's archived pages are shells.** The post arrives by a later
  request that the archive often lacks. old.reddit.com draws the post on the
  server, so its captures show it; the first came a minute after the post.
- **The availability API's "closest" is the last capture of the page
  itself.** CrowdTangle's address was captured until December 2024, but every
  capture after 14 August 2024 is a 301 redirect. The CDX API
  (`/cdx/search/cdx?url=…&fl=timestamp,statuscode`) shows which is which.
- **The toolbar covers a page's own pinned header.** The Wayback toolbar is
  pinned to the top of the window, and so is CrowdTangle's banner (Bootstrap's
  `navbar-fixed-top`), which announced the shutdown. The `if_` view
  (`/web/20240814023608if_/…`) replays the page without the toolbar. 3-2
  stacks the two views, and the labels say which is which.
- **A page can come back half drawn.** On 2026-09-25 the archive aborted some
  of a page's stylesheets, a different few on each load. Every text check
  passed, and the page showed without its styles. `capture` now fails a take
  when one of the page's own files fails before any answer, and retries it
  (see "How a capture works"). Reddit's archived pages lose their stylesheets
  for tooltips and crosspost previews on nearly every load, while the post
  looks right; that recipe accepts the loss (`expect: {all_files: false}`).
- **Scroll before a crop far down the page.** A `between` crop is cut from
  the window, so an element 1,100 pixels down needs a `scroll` step first,
  or a window tall enough to hold the whole crop (chapter 7's calendar:
  `window: [800, 1100]`). The window's height isn't what the figure shows;
  the crop is.
- **The toolbar is in a closed shadow root.** The playback script calls
  `attachShadow({mode: "closed"})`, so no selector, text wait, or hover
  reaches the toolbar's count or its **About this capture** panel. The M1
  recipe's hover by text never worked; its legacy image was clicked by
  position. `open_shadow: true` opens the root (see Recipes), and the
  toolbar's own ids work: `#wm-expand` is the About button, `#wm-capinfo`
  its panel.
- **The toolbar changes with the window.** Below 1,100 pixels wide it drops
  its logo and its strip chart of captures by year, and keeps the address,
  the capture count with its date range, and the capture's date with its
  arrows. From 1,100 the strip chart is back, over the count until about
  1,280, where the logo returns too. Chapter 7's figures keep under 800, so
  its text says what a narrow window leaves out.
- **The count is a second request.** The toolbar's "N captures" and its date
  range come from `/__wb/sparkline`. On 2026-09-25 that request failed on
  some loads while the page loaded, and the toolbar showed neither, which
  no guard noticed. The recipes wait for the count's text.
- **The calendar's summary line uses no-break spaces**:
  `Saved&nbsp;<strong>8,516,745 times</strong>&nbsp;<span>between …`. A
  plain space in a pattern doesn't match `&nbsp;`; `\s` does.
- **At 800 pixels wide the calendar sets three months to a row**, each 240
  by 210 pixels, and its histogram shows about 15 years around the selected
  one: 2004 to 2019 for 2005.

### Chrome's JSON viewer (chapters 3 and 4)

- **Pretty-print's checkbox can't be selected.** Chrome draws its bar in a
  closed shadow root, which no selector, Playwright's included, reaches. The
  recipe clicks where it is drawn, `click: {position: [104, 9]}`, and the next
  step, `wait: {text: '"daily": \{'}`, fails the take unless the text was
  reformatted. The bar shows the box ticked or not, so the figure says which
  view it is.
- **How Pretty-print lays JSON out.** A list of strings gets one item to a
  line; a list of numbers stays on one line, which wraps in a narrow window
  (figure 4-2 needs 600 pixels). It rewrites numbers, too: a whole number
  loses its `.0` (`1635.0` becomes `1635`), which Python keeps, so say so in
  the caption.
- **Crop from the bar, not the body.** The body's top edge sits 13 pixels
  down, where its margin and the `<pre>`'s collapse, so `between: ['body',
  'pre']` clips the bar. Start at `.json-formatter-container` (0 to 20
  pixels).
- **Mark lines with `match`.** The pretty-printed text is one `<pre>`, as a
  plain-text file is, so a line or a run of lines is a `match` anchor:
  `{match: '^\s*"time": \[(?:\n.*){8}', in: 'pre'}` is the `time` list,
  opening bracket to closing one.

### When a host is down

- **Tell an outage from a refusal.** On 2026-09-24,
  web.archive.org reset every connection after about 11 seconds while
  archive.org answered, and the proxy's status page (`curl -sS
  "$HTTPS_PROXY/__agentproxy/status"`) listed the relay failures. Work on
  another chapter and retry later. A 403, or a proxy refusal, is a policy:
  report it, and don't route around it. On 2026-09-25 it answered again, but
  not every time. The relay's log showed tunnels opened and closed 11 seconds
  later with no answer, and the CDX API answered one query with a 504. The
  30-, 60-, and 120-second retries got through. From about 01:30 UTC it
  reset connections again, and answered some page loads with its "Fail with
  status: 502" page and some of a page's images with 502; half an hour of
  retries got chapter 7's five figures through.
- **A 429 on the first request is the session's address, not your pace.**
  On 2026-09-24, Wikimedia's REST API answered the chapter 1 pageviews URL
  with 429 ("You are making too many requests") before any other request had
  gone to it: cloud sessions share addresses, and the limit counts everyone
  on them. Don't retry in a loop. Try once much later, or have the figure
  captured from another network. It answered 429 again that evening, through
  `capture`'s three retries: a limit counted over a shared address outlasts
  the backoff. One request on 2026-09-25 got the same answer.

## Making a figure, start to finish

One figure, from the request to the merged pull request. Each step names its
command or file; the table after the steps says where each part of a
figure's record is kept.

1. **Write the brief first.** Before any capture, write the figure's `brief:`
   in its recipe: what the reader should see, for which paragraph, and what
   the figure leaves out. Two to five plain sentences. It is the request the
   figure answers. A reviewer can judge a take against it, and so can
   whoever retakes the figure a year later, when the page has changed. The
   recipes here have one for every figure; `check` warns about a figure
   without one.
2. **Check the session and the page.** Run `tools/shots/run doctor ch-NN` in
   this session. The page must load signed out, and show no student names or
   work and no one's personal data. A page behind a login is the
   instructor's to capture by hand, and `import` brings the screenshot in
   (see Hand captures).
3. **Write the rest of the recipe.** Use the smallest window and crop that
   hold what the brief names: 800×600 CSS pixels by default, or up to
   1024×768 when the extra room removes clutter and the text still passes,
   with what it removes in `oversize:`. For browser UI, add `mode: headed` and a `devtools:` block
   that sets the dock, the zoom (125% in most chapter 5 figures), the panel,
   and the panes, columns, and sidebars to hide. Steps wait for a condition;
   none sleeps blindly. Add `annotate:` marks that point at elements or
   DevTools rows, `targets:` for each place the figure is shown, and
   `drifts: true` if it shows anything that changes. The "Field notes" above
   cover robots.txt, content types, Chrome's XML viewer, View Source, and
   crops; read the ones for your page first.
4. **Capture, and read what it says.** `tools/shots/run capture ch-NN --only
   <figure>`. A failed guard names the problem: an error page, missing text,
   an infobar. Read the warnings on a passing take too: a DevTools setting
   that DevTools did not honor, a figure over the soft limit, and the text
   size at each target.
5. **Look at the contact sheet.** `tools/shots/run sheet ch-NN` shows each
   take at the size its readers will see. Look for text too small to read; a
   wrapped row or a column cut short with "…", which means too much is in
   view; traces of the capture (the proxy's address, headers naming its IP
   address or location); and any bar under the address bar. Then hold the
   take against the brief: it should show what the brief asks for and
   nothing the brief leaves out. If not, change the recipe and capture again.
   `annotate` redraws markers without a new capture.
6. **Promote.** `tools/shots/run promote ch-NN <figure>` copies the take into
   `images/ch-NN/`, draws its markers once more, and records it in
   `provenance.json` and the `IMAGES.md` table. Outside the table, write in
   `IMAGES.md` what a retake needs to know: what the figure shows that is
   easy to miss, and why it looks the way it does.
7. **Write the figure block.** The caption says what to notice, gives the
   capture's month and year if the figure drifts, and names Chrome's own
   overlays, which get no marker. The `fig-alt` transcribes the text and
   numbers a reader needs, in 280–440 characters. Then run
   `tools/shots/run check`.
8. **Build.** Regenerate the notebooks (`python tools/make_notebooks.py`),
   run `python tools/trope_lint.py` on the changed chapter, and render it
   with Quarto.
9. **Make the course copies.** A slide or handout that uses the figure gets
   a copy in the course repo through `sync`, under the file name the deck
   uses: `tools/shots/run sync ch-NN <figure> --to slides/week-NN/img --as
   <name>.png`. It records the copy in `shots.json` and `IMAGES.md` and sets
   its size in `stubs.tsv`; say what the image shows in its `stubs.tsv` row,
   and write any notes outside the markers. A crop for a slide's column is a
   course recipe of its own (see Course-only figures). On a 1920-pixel slide
   its text must reach 16 pixels.
10. **Open the pull requests.** Open one in the textbook and one in the
    course repo, together, each on a new branch. The textbook PR's
    description has the review table: for each figure, its section, what it
    shows, kind, markers, alt text, capture date, and legibility result.
    Attach the contact sheet. Merge with a merge commit, when the maintainer
    asks.

### Where each piece lives

| Piece | Where |
|---|---|
| The request: what the reader should see, for which paragraph, and what the figure leaves out | the recipe's `brief:` |
| How to capture it: the page, window, DevTools, steps, and crop | the rest of the figure's recipe in `recipes/` |
| Markers | the recipe's `annotate:` |
| Where it is shown, and the reason for any exception | the recipe's `targets:`, `oversize:`, and `legibility: {skip: …}` |
| How an image made before the toolkit was made | the recipe's `legacy:` |
| What the reader is told | the chapter's figure block: the caption and `fig-alt` |
| What was captured, when, how, and the hashes that tie image to recipe | `images/ch-NN/provenance.json` |
| What a retake needs to know | `images/ch-NN/IMAGES.md`, outside the generated table |
| Every take, its log, and its markers | `tools/shots/out/ch-NN/<figure>/` (not committed) |
| Copies on slides and handouts | the course repo's `img/` folders, each with `stubs.tsv` and `IMAGES.md` |
| Which figures were accepted, and why | the PR's review table. It lives on GitHub, not in the repo, so copy anything a retake needs into `IMAGES.md`. |
| The plans, and the decisions behind these rules | `docs/plans/`, `docs/decisions.md`, and `docs/aar/` |

## How a capture works

`capture` runs each figure's recipe in a fresh browser context:

1. It paces the request.
2. It loads the page.
3. It runs the steps.
4. It checks the page and the image against the guards.
5. It crops.
6. It writes the take to `tools/shots/out/<chapter>/<figure>/<UTC time>.png`, with a `.json` log beside it.

A take fails its guards when:

- the status is unexpected;
- the page reads like an error or block page (a Cloudflare challenge, "Access denied," the Wayback Machine's "Fail with status");
- expected text is missing;
- one of the page's own files (a stylesheet, image, font, or script from the page's host) failed before any answer came back, which leaves the page half drawn with all its text in place. The take is retried, as for a dropped connection. A file the server answered, even with a 404, is the page as it is; so is an image or script the page aborted itself. A recipe whose page always loses a few files that don't show accepts them with `expect: {all_files: false}`: the take's log names them, and the contact sheet is where the take is judged;
- the image is nearly blank;
- in a headed take, an infobar sits above the page (see "No infobars");
- a page the recipe expects not to load (`expect: {error: ...}`) loads after all;
- the screenshot itself fails, as when a crop falls outside the window. The take is retried rather than ending the run.

The status judged is that of the page the take shows. A site that checks the browser with a script (EUR-Lex answers some first visits with 202, then reloads) is judged at the reloaded page's status, and the take keeps the first as `first_status`.

A failed take is named `<UTC time>.FAILED.png` and kept for inspection. `promote` refuses it. Nothing but `promote` writes to `images/`.

`compare` scores a take against the approved image with a difference hash: near 0 of 64 for the same region of the same page, about 32 for a different page. The score ignores scale, so a 2× take compares fairly with a 1× image, and live numbers that drift barely move it.

## Recipes

One YAML file per chapter in `recipes/`. A figure:

```yaml
- id: x-com-1999                 # the image is images/ch-07/x-com-1999.png
  kind: capture                  # capture | render | diagram | illustration
  section: "Broken and Missing Captures"
  brief: >-                      # the request the figure answers, in sentences
    Show a capture whose HTML was saved but whose images were not: x.com on
    November 14, 1999, with broken-image icons and their alt text above the
    signup form and the X.com Corporation footer, under the Wayback toolbar.
  url: https://web.archive.org/web/19991114081850/http://x.com/
  window: [700, 600]             # CSS pixels: the page and its toolbar, and no more
  open_shadow: true              # the toolbar's closed shadow root, opened (see Field notes)
  steps:                         # each step waits for a condition; none sleeps blindly
    - wait: {selector: '#wm-ipp-base'}
    - wait: {text: 'X\.com Corporation'}   # a regular expression; reaches into open shadow roots
    - wait: {text: '[0-9,]+ captures'}     # the toolbar's count, which a second request fetches
  expect:                        # guards beyond the defaults
    text: ['X\.com Corporation', '[0-9,]+ captures']
  crop: {window: true}           # or {top: 0, height: 610}, {selector: ..., pad: 8}, in CSS pixels
  drifts: true                   # shows things that change: the caption must say when
  legacy:                        # how an image made before tools/shots was made
    captured: 2026-09-22
    method: headless Playwright (Node), 1280×800 window at 1×, top 610 pixels
```

- **The brief** is for people: what the reader should see, for which paragraph, and what the figure leaves out (step 1 of "Making a figure"). The tool doesn't read it, and it stays out of the recipe's hash, so rewording it needs no new take.
- **Defaults:** an 800×600 window at scale 2, 8–30 second pauses, a 60-second limit on each wait, three retries, and JavaScript on. A chapter can change them under `defaults:`, and a figure can override any of them. (The ch-08 recipes set 1280×800, the window their first images were made in; each of its figures now sets its own.)
- **Steps:** `wait` (for `text`, `selector`, or `network_idle`), `hover`, `click` (by `selector`, `text`, or, as a last resort, `position`), `scroll`, `press`, and `settle` (seconds, for animation with no end signal). `scroll: {selector: …, offset: 175}` puts an element's top 175 pixels below the window's top; add `within: '.panel'` for a page that scrolls a panel rather than the window, as Jupyter does.
- **Crops around an element** take `pad` as one number or four (top, right, bottom, left, as in CSS), and `width` and `height` to fix the size: `{selector: '.card', pad: [13, 0, 0, 18.5], width: 560, height: 595}`. `{between: ['#art_40', '[id="040.004"]'], pad: [12, 0, 12, 0]}` is a band from the top of one element to the bottom of another; `left` and `width` default to the window.
- **Pages that lose files:** `expect: {all_files: false}` accepts a page whose own files fail on every load, when the ones lost don't show. Reddit's archived stylesheets for tooltips and crosspost previews came back aborted on most loads, while the post's own styles loaded (chapter 3's `reddit-api-pricing`).
- **Refusals as subjects:** `expect: {status: 403}` for a refusal with a body, `expect: {block: true}` for a block page, and `expect: {error: 'ERR_NAME_NOT_RESOLVED|…'}` for a host that doesn't answer, whose take is Chrome's own error page (see "Refusals and dead hosts" under Field notes).
- **Closed shadow roots:** `open_shadow: true` makes a shadow root that the page asks to have closed open instead, before any of the page's scripts run. A closed root is drawn like any other, but no selector reaches it, Playwright's included: no step can wait for its text or hover its buttons, and the text measure can't count it. The page looks the same; only its scripts could tell, since `element.shadowRoot` returns the root rather than `null`. The Wayback Machine's toolbar is one (chapter 7). Headless captures only: DevTools reaches closed roots on its own.
- **An API's response:** `api_client: true`, on the figure or on a composite's part, marks the request a chapter's own code makes, captured as an API client where robots.txt disallows it (see "Before the recipe" under Field notes). It changes what `doctor` says, not the capture, so it stays out of the recipe's hash.
- **Plain text:** `scroll: {match: '^User-agent: \*$', in: 'pre', offset: 130}` scrolls a line of a plain-text file to 130 pixels below the window's top; `match` anchors mark such lines (see Markers). The step measures again after scrolling and corrects, because a page can move as it scrolls.
- **Other modes:** `mode: headed` and `mode: composite` are below. `engine: selenium` and `engine: codegen` are for figures whose subject is the tool itself (see Engines). `mode: hand` is a screenshot a person takes (see Hand captures).
- **Patterns** are regular expressions. A leading `(?i)` ignores case; the tool turns it into JavaScript's `i` flag, because Playwright and DevTools evaluate patterns in JavaScript, which has no inline flags.
- **Quoting:** quote any YAML value that contains ` #`, or everything after it becomes a comment. In single quotes, a backslash is literal: write `'quotes\?page=2'`.

## Headed figures

A figure that shows browser UI (DevTools, View Source, a menu) sets `mode: headed`.
This one keeps DevTools readable inside the 800×600 soft limit: a small window,
DevTools docked at the bottom and zoomed to 125%, and the Styles pane beside the
Elements tree rather than under it. Captured on 2026-09-24, it puts DevTools'
text at 13.4 pixels in the book's column; the full 1680-pixel window of the
book's current `xkcd-inspect.png` puts it at 5.1.

```yaml
- id: xkcd-inspect
  kind: capture
  url: https://xkcd.com/
  mode: headed
  window: [800, 600]                # the whole browser window, in CSS pixels
  devtools: {dock: bottom, size: 340, zoom: 1.25, layout: side-by-side}
  steps:
    - wait: {selector: '#comic img'}
    - inspect: {selector: '#comic img', selects: '^<img'}
  crop: {window: true}
```

How a headed capture runs:

- **The window:** Chrome for Testing opens on a virtual display sized for the window at its scale. It gets a fresh profile, a debugging port, and no "controlled by automated test software" bar.
- **DevTools settings:** `devtools:` opens DevTools with the page, from settings written into the profile before launch:
  - `dock` (`right`, `bottom`, `left`);
  - `zoom` (1.25 keeps DevTools readable in the book inside 800×600, and about 1.5 inside 1024×768; 1.75 makes it large enough for print);
  - `size`: the pane's width, or its height when docked at the bottom;
  - `layout`: `side-by-side` puts the Styles pane beside the Elements tree. DevTools' default (`auto`) stacks Styles under the tree in a narrow window, where it can squeeze the tree out entirely;
  - `sidebar`: the Styles pane's size, its width beside the tree or its height under it (`layout: stacked`). In an 800-pixel window, `layout: stacked, sidebar: 1` gives the Elements tree DevTools' whole width, so its rows don't wrap, and leaves only Styles' tab bar below it for the crop to cut. DevTools 154 can't hide the pane. `hidden` puts it at its smallest, whichever layout DevTools uses: 97 DevTools pixels wide beside the tree, or 57 tall under it. Before the read-back existed, `hidden` set only one layout, so in a narrow pane that DevTools stacked, the Styles pane took most of the height and squeezed the tree;
  - `overview: false` hides the Network panel's timeline above the request list. `columns` shows or hides Network columns: `[waterfall]` adds Waterfall, which DevTools 154 hides by default, and `{waterfall: true, initiator: false}` also drops a column the text doesn't need.

  DevTools 154 ignores the stored `panel`, so the toolkit clicks that panel's tab. For `network`, it then reloads the page so the log is complete. That reload is a second visit: it sends the cookies the first load was given and revalidates what it cached. `first_visit: true` clears both before the reload, so the log shows what a first visit sends and receives: every request reaches the network, and none carries a cookie.

  Chrome keeps part of the page in view. Docked at the bottom of a 600-pixel window, DevTools gets at most about 360 pixels (about 70% of the area below the browser's bars), whatever `size` says. For a DevTools figure that needs more height, make the window taller and crop to DevTools: `window: [800, 1000]`, `size: 600`, and `crop: {devtools: true}` show 800×600 of DevTools alone, within the soft limit (ch-05's `network-headers`).
- **Every setting is read back.** A key DevTools doesn't know is ignored without an error. The pilot found two such failures: a Styles-pane key DevTools 154 no longer reads, and a User-Agent option that also rewrote the Client Hints. So before the grab, each headed take reads DevTools' own page for what it drew, and records it in the take's log as `devtools_seen`. The browser's bar height is recorded as `bars`. `capture` then reports each difference from the recipe as a warning beside the take, such as "DevTools: the pane is 463 pixels tall, not 650; Chrome keeps part of the page in view".

  | Setting | Read back from | Selftest |
  |---|---|---|
  | `zoom` | DevTools' device pixel ratio over the capture's scale | 125% |
  | `dock`, `size` | where DevTools leaves room for the page | bottom 400, right 450, left 380; 650 asked in a 700-pixel window is reported |
  | `layout`, `sidebar` | the Elements panel's tree and Styles boxes | stacked at 120, side by side at 200, `hidden` at its smallest |
  | `overview`, `columns` | the Network panel's timeline and column headings | timeline off, Waterfall on, Initiator off; DevTools' defaults as the control |
  | "What's new" marked as seen | no "What's new" panel | shut |
  | `panel` | the selected tab (a step may change it, so a difference is a note) | the Network figures |
  | `--disable-infobars` | the browser's bars above the page | 88 pixels; `expect: {infobar: true}` fails without a bar |
  | `--user-agent`, `first_visit` | the requests a local server receives | since the chapter 5 pilot |

  A new setting gets a row here and a selftest check that reads it back.
- **Finding DevTools controls:** docked DevTools is itself a web page. The toolkit reads that page over the debugging port to find where a tab, button, request row, or header name is drawn, then clicks it for real with xdotool. No pixel positions are typed into recipes.
- **Before any step:** it waits for the page's `load` event and for DevTools to draw its Elements tree. DevTools undoes a selection made before then.
- **The screen grab:** the pointer is parked in the page's bottom-left corner, so hover styles and DevTools' node highlight clear. Then the screen is grabbed.

Headed steps, in addition to the ones above:

- `inspect: {selector: …}` (or `text:`) selects the element in DevTools. By default it clicks DevTools' "Select an element" button, checks the button switched on, then clicks the element. `via: menu` right-clicks and chooses Inspect instead, which can't confirm the menu opened. `selects:` is a pattern the selected node must match; one retry is made if it doesn't.
- `tree: {keys: [Left], until: '^<center', max: 24}` clicks the empty right-hand end of the selected row, so the Elements tree has keyboard focus, and checks that it does. Clicking the node's own text could start editing its tag, which would swallow the keys. Then it presses keys until the selected node matches.
- `devtools_click: {text: '^Fetch/XHR$'}` and `devtools_wait: {text: 'quotes\?page=4'}` click or wait for something in DevTools, found by its text (a pattern) or `css:`. DevTools may break a row into pieces ("quotes", ":", a value), so match with `\s*` between them. `button: 3` right-clicks; buttons 4 and 5 turn the wheel up and down over the thing found, `repeat` times: `{text: '^200$', button: 4, repeat: 30}` scrolls a request list back to its first row.
- `key: 'ctrl+f'`, `type: 'var data'`, and `pointer: {selector: …}` are real keys, real typing, and the real pointer resting on an element, for tooltips. `pointer: {devtools: {css: 'li[role="treeitem"].selected'}}` rests it on something in DevTools instead: on a tree row, DevTools highlights that element on the page.

Crops for headed figures are in window coordinates:

- `{window: true}`: the whole window;
- `{devtools: true}`: the docked DevTools pane alone;
- `{content: true, height: 760}`: below the browser's own bars;
- `{top: 0, height: 680}`: a band of the window;
- `{between: ['body', 'td.line-number[value="43"]']}`: from the top of one element to the bottom of another, which is how View Source is cut at a line;
- `{selector: …, pad: 8}`: one element.

## Engines

A figure whose subject is a tool rather than a page is made by that tool:
`engine: selenium` for the window `webdriver.Chrome()` opens, and `engine:
codegen` for Playwright's recorder. Both need `mode: headed`, crop the screen
by `top`, `left`, `width`, and `height`, run only their own steps, and are in
the selftest.

**`engine: selenium`** (`lib/engine_selenium.py`) drives Chrome through
Selenium alone, so a caption can say "driven by Selenium". Selenium Manager
resolves Chrome for Testing at the pinned version and its ChromeDriver, as
chapter 8 describes. The toolkit adds nothing to the window, so Chrome for
Testing's "only for automated testing" bar stays: it is the point of the
figure (`expect: {infobar: true}`). ChromeDriver passes `--test-type`, so
`--no-sandbox`, which Chrome needs as root, adds no warning of its own.

- **Steps:** `wait` (for `text` or `selector`), `scroll`, `pointer` (the real
  pointer, for a tooltip), and `settle`.
- **The record:** the take records Chrome's and ChromeDriver's versions, and
  the HTTP status from the page's Navigation Timing, which WebDriver doesn't
  report.
- **Text:** Chrome's own bars aren't in the page, so the text measure counts
  the page's text alone. The bar's text is about 14 pixels (a capital is 10
  tall); a recipe that crops to the bar says so.

**`engine: codegen`** (`lib/engine_codegen.py`) shows codegen's recorder
and the Playwright Inspector. The `playwright codegen` command can't run
here: it launches Playwright's own Chromium build, which the toolkit never
installs. So the engine does what the command does, in Chrome for Testing:
it launches the browser, turns on the same recorder (the driver's
`enableRecorder`: Python, recording), and opens the page. Clicks are real
(xdotool), so the recorder writes a line for each, as it would for a person.
The first figure taught six things:

- **The Inspector takes no switches.** Playwright opens it in a browser of
  its own, which `--force-device-scale-factor` can't reach. The engine runs
  in a child process whose display sets `GDK_SCALE`, which both windows
  follow.
- **The recorder writes its script when the browser closes.** `expect:
  {code: [...]}` checks that file, and the take keeps it as `recorded`.
- **Open the page after the recorder starts**, as the command does, or the
  script lacks `page = context.new_page()`.
- **The Inspector's text is out of every client's reach.** Its sizes come
  from its own stylesheet (code at 14 pixels, the toolbar at 13), counted
  with the script's characters.
- **HTTPS-Upgrades.** Playwright turns off Chrome's upgrade of plain-http
  links and redirects. quotes.toscrape.com redirects its author pages to
  http, which the session's proxy doesn't carry. `https_upgrades: true` turns
  the upgrade back on, as in regular Chrome, by replacing Playwright 1.63's
  own `--disable-features` switch; a new Playwright version needs the list
  in `lib/engine_codegen.py` checked. (Playwright's routes can't help: they
  don't see a request a redirect makes.)
- **Stack the windows.** `window` is the browser's window, and `inspector:
  {window: [800, 595], at: below}` puts the Inspector under it (or `right`).
  Side by side, two windows fill 1,600 pixels and their text shrinks to half
  in the book; stacked at 800, it reaches 13.6 pixels. A crop can stop after
  the code the text discusses.

Its steps: `wait` (for `text`, `selector`, or `url`), `click` (a real click,
by `role` and `name`, by `selector` and `text`, or by `text`; it waits until
`pause[0]` seconds have passed since the last page load), `scroll` (not
recorded, as a wheel isn't), `pointer` (the recorder highlights the element
and shows its locator), and `settle`.

## Hand captures

A page behind a login is the one kind of figure a person takes: the toolkit
never signs in. The recipe says so with `mode: hand`, and `import` turns the
person's screenshot into a take, which `sheet`, `promote`, and `sync` treat
like any other.

```yaml
- id: issue-form
  kind: capture
  mode: hand
  url: https://github.com/OWNER/REPO/issues/new?template=revision.yml
  hand:
    why: the form needs a signed-in GitHub account, and the toolkit never signs in
    steps: >-
      Sign in, open the URL in a window whose page is 800 CSS pixels wide, and take
      a screenshot of the window. Read window.devicePixelRatio in DevTools' console.
    text_px: 14                  # the form's text, from DevTools' Computed pane
  scale: 2                       # the screenshot's pixels per CSS pixel: that devicePixelRatio
  crop: {top: 86, left: 0, width: 800, height: 480}
  redact:
    - {box: [700, 90, 100, 40], why: the signed-in account's avatar and menu}
```

```bash
tools/shots/run import course issue-form --file issue.png --by "A. Person" --date 2026-09-28 \
    --browser "Chrome 141 on macOS 15"
```

- **Coordinates:** `crop` and each `redact` box are in the screenshot's CSS
  pixels, counted from its top-left corner: the pixels an image viewer shows,
  divided by `scale`. Both use that one frame, so a box stays on what it hides
  when the crop changes. A crop past the screenshot's edge is refused, with a
  question: is `scale` the page's `devicePixelRatio`? A page zoomed to 125% on
  a 2× display has 2.5.
- **Finding the numbers:** in a screenshot of the whole window, the page
  starts below the browser's bars, whose height the console gives as
  `outerHeight - innerHeight`; that is the crop's `top`. An element's box
  in the screenshot is its `getBoundingClientRect()` with that height added
  to `y`. On a real Chrome window at scale 2 (2026-09-25), a box found this way
  blacked out an avatar and a user name exactly, with the header's own color
  one pixel outside it. A Mac's window screenshot adds a shadow around the
  window, which moves every coordinate, unless you hold Option as you click.
- **Redaction** comes first: each box is filled black, and then the image is
  cropped. A box outside the crop is reported, since it hides nothing there.
- **Metadata stays behind.** The take is a new PNG of the pixels alone,
  converted to sRGB from the screenshot's own color profile (a Mac's is
  Display P3). The screenshot's PNG text and EXIF, where a computer's name can
  hide, aren't copied. The screenshot itself isn't kept; the record holds its
  SHA-256 and size.
- **Text size:** no page is left to measure, so the recipe declares the size
  of the text a reader needs, `hand: {text_px: 14}`, read from DevTools'
  Computed pane. The take records it as declared, and the legibility check
  judges it as it judges a measured figure's.
- **Marks** can only be placed by `xy`, in the take's pixels. Moving one needs
  no new take, for any figure: a spot typed in isn't measured.
- **The record:** who took the screenshot (`--by`), on what day (`--date`), in
  what browser (`--browser`), when it was imported, the screenshot's hash, and
  each box blacked out, with its reason. `IMAGES.md` shows it as "A. Person:
  screenshot by hand in Chrome 141 on macOS 15; imported by tools/shots, 1
  area blacked out".
- **What no check can do:** nothing reads a screenshot's text, so nothing
  finds a name, an avatar, or an address that the boxes missed. Look at the
  take on the contact sheet before promoting it.
- **Elsewhere:** `capture` skips a hand figure and says how to import it.
  `doctor` doesn't read robots.txt for it, because a person's browser loads the
  page, as a person.

No recipe uses it yet. Its first candidate is week 1's issue form
(`issue_form.png`), if the maintainer chooses a hand capture over a public
issue (see "Waiting on the maintainer" in `docs/handoff.md`).

## Markers

A figure with numbered markers lists them under `annotate:`. Each mark points
`at` something, and the browser measures where that is at the moment of
capture, so a retake moves the markers with the page. Nothing is placed by
typing in pixel positions.

```yaml
annotate:
  width_in: 2.625        # the whole figure's printed width; sets the markers' scale
  size: small            # 11-point markers, or small ones (8.5 points)
  marks:
    - {n: 3, at: {selector: '.field--name-field-award-category-oscars', box: text}}
    - {n: 5, at: {selector: '.field--name-field-honoree-type', box: text}, column: honoree}
    - {n: 4, shape: brace, at: {selector: '.paragraph--type--award-honoree'}, x: 202.5}
    - {n: 1, shape: bracket, at: {selector: '.field--name-field-award-categories'}, x: -1}
    - {n: 2, at: {devtools: {row: 'paragraph--type--award-category'}}, side: left, x: 30, gap: 7}
    - {label: '← you clicked', at: {devtools: {selected: true}}, x: -4}
```

What a mark can point `at`:

- a page element: `selector:` or `text:` (a pattern). `box: element` (the default for a selector) is the element's box; `box: text` (the default for text) is the box of its words, and `box: first-line` of their first line;
- a match inside an element's text: `match:` (a pattern; `^` and `$` match at each line) with `in:` (a selector, the page's body by default). It is the box of the matched characters, across line breaks. A plain-text file, such as a robots.txt, is one `<pre>` with one text node, so no element stands for one of its lines: `{match: '^User-agent: \*$', in: 'pre'}` does;
- something in DevTools: `devtools: {row: …}` is an Elements-tree row, from its disclosure triangle to the end of its first line; `{selected: true}` is the selected row; `{text: …}` or `{css: …}` is anything else DevTools draws;
- `nth: 2` picks a match (from 0), `nth: [0, 3]` joins a run of matches into one box, and `all: true` joins them all;
- `xy: [x, y]` in image pixels, as a last resort. The tool flags it, because it will not follow the page.

A mark's `shape`:

- `marker` (the default with a number `n`): a numbered circle on the thing's `side` (right, left, above, or below), `gap` CSS pixels away (4 by default). A dotted leader line joins the circle to its thing whenever they end up apart.
- `brace`: a curly brace along the thing's side, spanning it. Its number, or its `label`, sits just past the brace's tip.
- `bracket`: an open bracket. When the thing runs past the picture's edge, the bracket runs past it too and ends in an arrow.
- `box`: a rounded box around the thing, with its number beside it.
- `label` (the default without a number): text beside the thing. With a number as well, the marker follows the text: "4 more honorees ④".

Placement:

- `x` and `y` pin a mark to a place in the crop, in CSS pixels, counted from the right or bottom edge when negative. Pins are for choices about the figure's own empty space, such as a column of markers in DevTools' margin. They are not a way to reach the thing.
- Markers with the same `column` share one line, just past the widest of their things.
- Markers on one line that would overlap spread apart evenly, keep their order, and get leader lines.
- A marker that would touch another mark's brace or bracket moves back toward its own thing.
- A label over the picture gets a white backing.

`capture` draws the markers on every passing take, beside it:
`<UTC time>.annotated.pdf` for slides and handouts (vector), and `.png` for the
book, at one pixel per pixel of the screenshot. `annotate` redraws them from
an existing take after you change the marks, with no new capture; changing
what a mark points at does need a new capture. `promote` draws them once more,
from the recipe as it is then, and copies both files into `images/` as
`<figure>_annotated.png` and `.pdf`. The styles are the course handouts'
(`styles/shotmarkers.sty` copies `handoutmarkers.sty` from the course repo),
so a marker drawn here looks like one in a handout.

## Legibility

**First, a soft limit on size.** A figure shows 800×600 CSS pixels of the
screen by default: its image size over its scale. It may relax to 1024×768
when the extra room removes clutter and its text still passes at every target.
`capture`, `annotate`, `sheet`, and `check` report a figure over 800×600, and
say how small the book's column will make its text:

| What the figure shows | What the tools say |
|---|---|
| up to 800×600 | nothing |
| up to 1024×768, with a reason in `oversize:` and text that passes at every target | a note |
| up to 1024×768, without a reason | a warning: say what clutter the room removes, or crop to 800×600 |
| up to 1024×768, with text too small somewhere it is shown (reason or not) | a warning: go back to 800×600, or zoom the page or DevTools |
| more than 1024×768, with a reason in `oversize:` | a note |
| more than 1024×768, without a reason | a warning |

Within 1024×768, the reason is the clutter the extra room removes:

```yaml
window: [1024, 768]
devtools: {dock: bottom, size: 460, zoom: 1.5, panel: network}
oversize: "at 800 pixels wide the Network list cuts Name and Type short with …"
```

Beyond it, the reason says why the text still reads, as for the week-06 handout's
DevTools figure:

```yaml
oversize: "DevTools is zoomed to 175%, so its text reads as a 594×471 capture's would"
```

An image made before the toolkit measured text can't show that its text passes,
so it gets a warning inside 1024×768 until it is retaken.

**Then, the text itself.** Every take records the size of the text inside its
crop, counted by character, from the page and from DevTools. The legibility
check works out how tall that text will be where the figure is shown:

| Target | Recipe | Shown at | Threshold |
|---|---|---|---|
| book | on for every chapter figure; `targets: {book: false}` turns it off | the HTML book's column, 778 pixels in a 1280-pixel-wide window, or the image's own width if narrower | 11 px |
| slides | `targets: {slides: {width: 0.8}}`, the share of a course slide's text width | a slide 1920 pixels wide | 16 px |
| handout | `targets: {handout: {width_in: 5.04}}` | print | 6 pt |

The size judged is the one that four in five characters reach or exceed, so a
footer does not fail a figure but small main text does. `capture` reports it
for every take. `check` fails a promoted image under a threshold, unless its
recipe says why the words don't matter: `legibility: {skip: "the lesson is
the empty page"}`. The thresholds began as the plan's starting values, and the
chapter 5 pilot kept them (see "What the chapter 5 pilot settled").

Known cases, measured or computed from the images:

- Week 08's `infinite_scroll.png`, dropped because it could not be read on its slide: DevTools text at 11 pixels, in a 555-pixel crop, on 35% of the slide's text width. That is 11.7 pixels on a 1920-pixel slide, under 16. The selftest checks this case.
- Week 08's `xkcd_inspect.png` read well: the same text on half the text width comes to 16.7 pixels.
- The week-06 handout's DevTools figure measures 6.7 points in print. Its card figure measures 5.2 points, which is readable at the edge; at 3 inches wide it would pass.
- Before their retakes, every ch-07 and ch-08 figure showed 1100–1858 CSS pixels across, so the book's column showed its text at 42–71% of its size on screen; in the full-window DevTools captures (`network-tab-json`, `xkcd-inspect`), DevTools' text came to about 5 pixels. Retaken within the limit, chapter 7's five measure 11–13.4 pixels in the book (2026-09-25), and chapter 8's two tool windows, taken by the engines, 19.4 (the Selenium window's page) and 13.6 (the Inspector's code).

## Composites

`mode: composite` captures each of its `parts` as a figure of its own, then
joins them side by side on white, each labeled below, inside a thin frame:

```yaml
- id: javascript-off-on
  url: https://quotes.toscrape.com/js/
  mode: composite
  window: [900, 695]
  parts:
    - {label: JavaScript off, javascript: false, steps: [{wait: {text: 'Quotes to Scrape'}}]}
    - {label: JavaScript on, steps: [{wait: {text: 'Albert Einstein'}}]}
  layout: {gap: 28, pad: 15, label_px: 28}     # CSS pixels
```

A part can set its own `url`, `steps`, `expect`, `crop`, `javascript`,
`window`, `scale`, `mode` (headless or headed), and `devtools`. Each part is
paced, guarded, and retried like any take, and the joined take lists its parts.
A composite whose parts each load their own page needs no `url` of its own;
`IMAGES.md` then lists every part's. `layout: {direction: column}` stacks the
parts one above the other, each labeled below, for parts of different
heights (chapter 3's `dead-endpoints`).

## Contact sheets

`sheet ch-NN` draws each figure's newest take, with its markers if it has
any, at the size each of its targets shows it: the book's column, its share
of a 1920-pixel slide, a handout at 96 pixels per inch. The measured text size
and the verdict are written above each one. Look at the sheet before a pull
request, and attach it to the pull request, so a reviewer sees what readers
will see.

## Course-only figures

`recipes/course.yml` holds figures made for the course repo rather than a
chapter. `capture`, `annotate`, and `sheet` work on them. `promote` refuses
them, because their images live in the course repo, where `sync` copies their
newest passing take (see Sync to the course repo), and `check` only validates
their recipes. The two figures there
rebuild the week-06 Oscars handout's annotated screenshots and are the
regression test for markers. Every mark lands within 10 image pixels (5 CSS
pixels) of where it was placed by hand. In the DevTools figure, markers, the
label, and the brace are within 2.5 pixels, and leader lines within 6: the hand
version stopped leaders closer to a triangle than to text. On the 2× card
figure the largest difference, 9.6 pixels, is where the hand version bent its
column of markers.

The eleven `week07-*` figures remake week 7's slide screenshots (2026-09-25),
which the deck's frames show at 35–100% of the text width. They taught four
things about slides:

- **Crop for the column, not the page.** A frame's column sets the crop:
  text at p20 CSS pixels reaches 16 on a 1920-pixel slide only in a crop
  narrower than `width × 1680 × p20 / 16`. x.com's 1999 page, in a 35%
  column, is its top 560 pixels; AboutFace's two quoted lines, in a 44%
  column, are two small crops stacked, 271 pixels wide.
- **Height is the other limit.** A slide's text area is about 200 points
  tall, so a tall image in a narrow column runs off it: April and August
  stacked whole were 265 points. `latexmk` reports it as an overfull vbox;
  each crop keeps only the weeks where the color changes.
- **Accept lost files that don't show.** A crop of the toolbar alone doesn't
  show the page's own images and stylesheets, which the archive failed on
  every load on 2026-09-25, so those recipes set `expect: {all_files: false}`.
  So do x.com's, whose images are broken whatever the archive answers.
- **Some small text can't reach 16.** The toolbar's date range under its
  count is 9 pixels at any width, and the strip of bars needs the toolbar
  1,100 pixels wide or more, so on a full-width slide it comes to 14.5. The
  recipe says why in `legibility: {skip: …}`: the count and the date the
  frame discusses read at 19.

The four `week08-*` figures remake week 8's JavaScript off/on pair,
JavaScript off alone, playwright.dev, and the window Selenium opens
(2026-09-25). The last crops to the bar's first sentence, 445 pixels, for a
35% column. They add a fifth lesson:

- **Or load the page narrow.** A live site reflows for a narrow window, so a
  page loaded 480 pixels wide fills a 35% column without a sideways crop.
  playwright.dev folds its menu into a button and wraps its headline to four
  lines; its menu bar and hero read at 19.6 pixels. The same pages in 900-
  and 1,280-pixel windows had shown their text at about 7 to 11.

## Sync to the course repo

`sync` copies a figure into a folder of the course repository and records
where the copy came from; `synced` checks every copy against its record.

```bash
tools/shots/run sync ch-08 playwright-codegen --to slides/week-08/img --as codegen.png
tools/shots/run sync course week08-js-off --to slides/week-08/img --as js_off.png
tools/shots/run sync ch-01 jupyter-cells --to handouts/week-01/img --annotated
tools/shots/run synced
```

- **What it copies:** a chapter figure as approved in `images/`, with its
  marked-up PNG and PDF when it has markers (`--annotated` copies the
  marked-up PNG alone, for a Markdown handout); a course-only figure from its
  newest passing take in `out/course/`, or the one `--take` names.
- **A committed source:** a chapter figure must be committed as it is, so
  the record can name the commit it came from. A course figure's take isn't
  committed; its record names the textbook's commit and the take.
- **The record:** `shots.json` beside the copy holds, per file, the figure,
  the source file and its commit, both hashes, and the capture's page, date,
  browser, User-Agent, and engine. `IMAGES.md` gets a table generated from
  it, between `<!-- shots:begin -->` and `<!-- shots:end -->`, placed before
  the stubs table; everything else in the file is for people, and
  `make_stubs.py` keeps to its own markers.
- **stubs.tsv:** when the file has a row, `sync` sets its size and redraws
  the stubs table. The row stays: `stubs.tsv` lists every image a deck
  includes, not only placeholders.
- **What it says:** each copy is "new", "the same as the file already
  there", or "replacing a different file", so a sync meant to refresh a
  record can't silently change a slide.
- **`synced`** reads every `shots.json` under the course repo's `slides/`
  and `handouts/`. A copy changed by hand fails; a copy whose source changed
  since, or whose take was cleaned from `out/`, is a warning.
- **Where:** the course repository is `--course`, `$SHOTS_COURSE`, or
  `INFO4617-Fall2026` beside this one.

The first run (2026-09-25) recorded the 25 copies then in the course repo,
all of them exact: weeks 3, 5, 7, and 8's slides and weeks 1 and 4's
handouts. It reproduced each file byte for byte, which is the plan's test for
this step.

## Provenance

- **`images/<chapter>/provenance.json`** records, for each image:
  - its kind and source URL;
  - when it was captured, and by whom (the tool, a hand-run script before it, or a person, for an import);
  - the browser, User-Agent, window, scale, and crop;
  - a hash of the recipe and of the image;
  - the sizes of its text, which `check` judges;
  - for a composite, its parts;
  - for an image with markers, hashes of the annotated PNG and PDF, the printed width they were drawn for, and a hash of the marks.
- **The recipe's hash** covers what decides the capture. The brief, `notes:`, `legacy:`, marks, targets, `oversize:`, and legibility settings are left out, so changing them needs no new take.
- **Existing images:** `adopt` records ones made before the toolkit, from their recipe's `legacy:` block.
- **`images/<chapter>/IMAGES.md`** gets a table generated from `provenance.json`, between `<!-- shots:begin -->` and `<!-- shots:end -->`. Everything outside the markers is for people, and the tool never touches it: what a figure shows that is easy to miss, and what a retake needs.

## Evidence

A count, a date, or a claim a figure's caption or paragraph rests on comes
from a query whose limit and paging are recorded beside the figure (AAR P1-2).
The recipe lists the queries under `evidence:`, each with the claim it backs:

```yaml
evidence:
  - id: facebook-2005-statuses
    claim: >-
      facebook.com's captures were 200s until April 8, 2005, 403s from April 10,
      and 200s again from August 6.
    url: https://web.archive.org/cdx/search/cdx
    params: {url: facebook.com, from: '20050301', to: '20050831', output: json,
             fl: 'timestamp,statuscode', limit: 1000, showResumeKey: 'true'}
    page: resume_key          # follow the CDX resume key until the API stops returning one
    summary: {runs: statuscode}
```

- **`evidence ch-NN`** runs each query as captures load pages: with the
  course User-Agent, 8–30 seconds between requests to one host, and retries
  after a 5xx or a dropped connection. It saves every response under `out/`.
- **Complete, or it fails.** A query is complete only when its last page says
  so: a CDX page without a resume key, or, without paging, fewer rows than
  `limit`. A page that returns exactly its limit and can't page fails, and so
  does one whose resume key the query doesn't follow. That is the check that
  would have caught week 7's first account of x.com's images: a 25-row answer
  to a query with more (course PR #44).
- **The record:** a complete run goes into `provenance.json`, under
  `evidence`: each request with its URL and rows, the total, the date, and a
  summary. `IMAGES.md` lists each query and its claim under the figures.
- **Summaries:** `{group_by: urlkey, count: statuscode}` counts each group's
  values and gives its first and last timestamps; `{runs: statuscode}` gives
  each stretch of one value, in the API's order, with its first and last
  timestamps and its rows.
- **`check`** warns about a figure whose evidence was never run to its end, or
  whose query or claim changed after it ran, so the claim on record is the one
  the data was read against. Reading the summary against the claim is still a
  person's job; `evidence` prints it.
- **Robots.txt:** `doctor` reads it for each query's host too, as for an API a
  chapter's code calls (`api_client`).

The first two, in chapter 7 (2026-09-25), confirmed the calendar paragraph's
dates and corrected one of the x.com paragraph's: the spacer image was saved
twice, on April 29 and May 5, 2000, not only in April. The x.com query also
showed that "captured only as 404s", in the figure's notes, was wrong: the six
images' later captures are redirects. Their first captures were 404s, and none
was ever a 200.

## Checks

`check` reports **errors**, which exit 1:

- a recipe that does not validate;
- an image without provenance;
- an image changed after its provenance was recorded (replaced by hand);
- a kind that disagrees with the recipe;
- an annotated PNG or PDF that is missing, or changed after it was drawn;
- text too small to read at one of the figure's targets (see Legibility);
- a figure block with no `fig-alt`;
- an out-of-date `IMAGES.md` table.

It reports **warnings** for:

- a figure whose recipe has no `brief:`;
- a figure not used in its chapter (a figure may use either `<figure>.png` or `<figure>_annotated.png`);
- short alt text;
- a drifting figure whose caption does not give the capture year;
- marks changed in the recipe since the annotated image was drawn (promote again);
- a figure showing more than 800×600 CSS pixels whose recipe does not say why (`oversize:`), or, within 1024×768, whose text is too small somewhere it is shown or was never measured (see Legibility);
- evidence never run to its end, or whose query or claim changed after it ran (see Evidence).

With no chapter named, `check` covers every chapter and `course.yml`. So does
CI: `.github/workflows/shots-check.yml` runs it on each pull request that
changes `images/`, `tools/shots/`, or the workflow itself, and on no other
(AAR P1-1; the maintainer asked for image pull requests only). `check` loads no
page and starts no browser, so the job installs just PyYAML, Pillow, and
websockets, at the pins in `requirements.txt`, and `check` itself takes about a
second. An image replaced by hand, or an `IMAGES.md` table left behind, fails
it, so the reviewer's look can go to what the figure shows.

`selftest` runs 142 offline checks against a local web server. It needs the browser but no network. It covers:

- the guards, retries, `promote`, and `check`;
- a stylesheet whose connection drops, which fails a take whose text is all there and is retried, beside one answered with a 404, which passes, and a recipe that accepts lost files, whose log names them; an aborted stylesheet counts, an aborted image or script doesn't;
- text in a closed shadow root, which no step or guard can find, and `open_shadow: true`, which opens the root for steps, guards, and the text measure;
- robots.txt: groups for Claude's agents, and a disallowed API response marked `api_client` reported as a note while a disallowed page stays a warning;
- refusals: a host that doesn't answer shown as Chrome's error page, and a failure when that page loads after all; behind a stand-in proxy that opens no tunnels, public DNS (a stand-in too) telling a dead host from a policy block in `capture` and `doctor`, and an unexpected tunnel failure still a policy block; a script check's 202 and reload; robots.txt's `Crawl-delay`;
- a `scroll` step that scrolls a panel (`within`), not the window;
- anchors measured at capture, at scale 1 and 2; markers, braces, brackets, and hand-placed marks drawn to PDF and PNG, the PNG keeping the screenshot's pixels unchanged; `annotate` without a new capture;
- the size limits: 800×600; the relaxed 1024×768, which needs a reason and text that passes; beyond it; and `check`;
- `match`: a line of a plain-text file scrolled to its offset, and a match's box across line breaks;
- legibility, with week 08's `infinite_scroll.png` as the failing case; composites side by side and stacked; a `between` crop in a headless take; `sheet`;
- headed capture: Inspect through the element picker, the tree walked by keyboard, a request found and clicked in the Network panel, View Source cut at a line, and anchors in DevTools and on the page in one take;
- the User-Agent and its Client Hints, and a first visit's reload, read back from what the local server receives;
- every DevTools setting read back from what DevTools drew (the table under "Headed figures"), with DevTools' defaults as a control, and a setting DevTools won't honor reported at capture;
- the infobar guard: no bar above the page, and a recipe that expects one fails without it;
- the engines' recipe rules (`mode: headed`, their own steps, window crops, `inspector` for codegen alone);
- the Selenium engine: the window `webdriver.Chrome()` opens, with Chrome for Testing's bar and the versions recorded;
- the codegen engine: a real click written as a line of the recorder's script, both windows grabbed, and the Inspector's code counted at its stylesheet's size;
- evidence, against a stand-in CDX server: a query paged to its end, its summaries and its listing in `IMAGES.md`, a page that returns exactly its limit and one whose resume key is left unfollowed failing, and `check` on evidence never run, a changed query, and a reworded claim;
- sync, into a stand-in course repo: an approved figure copied with its record, table, and stubs size, a person's notes kept; `synced` finding it, then a copy changed by hand; `--annotated` without markers and an uncommitted source refused;
- import, of a made-up screenshot: `capture` leaving it to a person; the take cropped at scale 2, its avatar blacked out, its note and color profile left behind, and who, when, the screenshot's hash, and the redaction recorded; a declared text size judged, and one too small warned about; a crop past the edge, a future date, and a figure the toolkit captures refused; the recipe rules for `mode: hand`; `promote` with markers, `check`, and a mark moved by `xy` redrawn without a new take.

It skips the marker checks if TeX is missing and the headed checks if the virtual display is.

## Files

| Path | What it is |
|---|---|
| `bootstrap.sh`, `requirements.txt`, `run` | setup, pinned packages, and a wrapper that uses the toolkit's own Python |
| `shots.py` | the commands |
| `lib/env.py` | paths, the proxy, and the pinned browser |
| `lib/recipes.py` | loading and validating recipes |
| `lib/browser.py`, `lib/steps.py`, `lib/crop.py` | launching Chrome for Testing, running steps, and cropping |
| `lib/display.py` | the virtual display, real input, and screen grabs |
| `lib/devtools.py` | DevTools settings, reading them back from what DevTools drew, and reading the DevTools page to find things on screen |
| `lib/headed.py` | one headed attempt: window, DevTools, headed steps, and the crop |
| `lib/engine_selenium.py` | one attempt at the window `webdriver.Chrome()` opens, driven by Selenium |
| `lib/engine_codegen.py` | one attempt at codegen's recorder and Inspector, in a child process, with real clicks |
| `lib/measure.py` | at capture: anchors' boxes and the text's sizes, in the take's pixels |
| `lib/annotate.py`, `styles/shotmarkers.sty` | markers laid out from anchors, drawn with TikZ to PDF and PNG |
| `lib/legibility.py` | text size at each target, against the thresholds |
| `lib/sheet.py` | contact sheets |
| `lib/guards.py` | error and block pages, retries, policy blocks, and public DNS for a host that doesn't answer |
| `lib/robots.py` | what a host's robots.txt says to the capture's User-Agent and to Claude's agents, for `doctor` |
| `lib/capture.py` | one figure, start to finish, composites, and the take log |
| `lib/compare.py` | take against approved image |
| `lib/provenance.py` | `provenance.json` and the `IMAGES.md` table |
| `lib/evidence.py` | the queries behind captions' claims: paging, the complete-or-fail rule, summaries, and staleness |
| `lib/sync.py` | copies into the course repo: `shots.json`, the `IMAGES.md` table, `stubs.tsv` sizes, and `synced` |
| `lib/hand.py` | a person's screenshot made a take: the recipe rules for `mode: hand`, redaction, the crop, and the record |
| `selftest.py` | the offline test |
| `recipes/` | one YAML file per chapter, and `course.yml` for course-only figures |
| `out/`, `.venv/` | takes, markers, contact sheets, and the virtual environment (git-ignored) |
