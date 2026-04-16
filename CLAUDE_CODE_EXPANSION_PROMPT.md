# Claude Code Prompt: Expand Web Data Science Chapters

## Task

Expand each chapter of the Quarto book in this repository to approximately 3,000 words. The current chapters range from 1,292 to 2,415 words. Each chapter needs additional narrative prose, tutorial examples, and exercises while preserving the existing structure, voice, and content.

## How to Execute

Work through chapters one at a time. For each chapter:

1. Read the current `.qmd` file
2. Read the corresponding expansion instructions below
3. Read `claude.md` for editorial voice and style guidelines
4. Expand the chapter by adding the specified content at the specified locations
5. Verify the word count approaches 3,000 (±300 words)
6. Move to the next chapter

Do NOT rewrite existing content unless it contains errors. ADD to what exists. Preserve all existing code blocks, cross-references (`@sec-`), callout blocks, and citation keys (`@author2024`).

## Voice and Style Reminders

- Second person ("you"), formal but approachable
- Narrative code blocks with comments (`eval: false` globally)
- Include expected output as comments where helpful
- 4–5 exercises per chapter, graduated from guided to open-ended
- At least 1 Missing Manual callout per chapter using `::: {.callout-tip}`
- At least 1 public interest callout using `::: {.callout-note}` referencing openness, oversight, or ownership
- Dry humor welcome but sparingly

---

## Chapter-by-Chapter Expansion Instructions

### Chapter 1: Introduction to Web Data Science
**File:** `ch-01-introduction.qmd`
**Current:** 2,020 words, 7 code blocks, 3 exercises
**Target:** 3,000 words, 9+ code blocks, 5 exercises

**Add the following:**

1. **After "Your First Request" section:** Add a subsection called "From Response to DataFrame" that takes the Wikimedia pageviews JSON response and walks through converting `data["items"]` to a DataFrame, renaming columns, converting the timestamp, and making a basic line plot with matplotlib. Show the full code with 2–3 paragraphs of narrative explaining each step. This previews the workflow used in every subsequent chapter.

2. **After the matplotlib plot:** Add a subsection called "Saving Your Work" that demonstrates saving the DataFrame to CSV with `df.to_csv()` and reloading it with `pd.read_csv()`. Explain why serialization matters: you should not re-scrape data you have already collected. Connect forward to Chapter 7's serialization discussion.

3. **Expand exercises to 5:** Add Exercise 4: "Explore the `requests` library documentation and find the method for making a POST request. In a Markdown cell, explain in your own words how POST differs from GET and when you would use each." Add Exercise 5: "Create a notebook that retrieves pageview data for three Wikipedia articles of your choice, saves each to a separate CSV file, and creates a single plot with all three time series on the same axes."

4. **Expand "Social History and Public Interest" section:** Add 2 paragraphs on the specific contributions of data journalism (ProPublica's "Machine Bias", The Markup's "Citizen Browser") and computational social science (Lazer et al. 2009 manifesto, the rise of "digital trace data" as a concept) to motivate why web data fluency matters for the public interest.

---

### Chapter 2: Ethics, Law, and Responsible Data Collection
**File:** `ch-02-ethics.qmd`
**Current:** 1,827 words, 4 code blocks, 4 exercises (numbered to 4)
**Target:** 3,000 words, 6+ code blocks, 5 exercises

**Add the following:**

1. **After the `robots.txt` section:** Add a subsection called "Comparing robots.txt Across Platforms" with a code block that retrieves and prints `robots.txt` for Wikipedia, Reddit, and a major news site. Add 2 paragraphs of narrative comparing what each site allows and restricts, and what the differences reveal about their stance toward automated access.

2. **After "Rate Limiting":** Add a subsection called "Building a Responsible Scraper Function" that wraps `requests.get()` in a function with built-in rate limiting, User-Agent headers, error handling, and logging. Show the complete function (~15 lines) with narrative explaining each design choice. This function template should be referenced in later chapters.

3. **After the ethical decision framework:** Add a subsection called "IRBs and Web Data" with 2 paragraphs explaining when web data collection constitutes human subjects research, when IRB review may be required, and how the distinction between public data and research data applies. Reference the Belmont Report principles (respect for persons, beneficence, justice) briefly.

4. **Add Exercise 5:** "Retrieve the `robots.txt` file for a website that you use daily but have never scraped. Read the Disallow rules carefully. Then read the site's Terms of Service. Write a 300-word analysis: if you wanted to collect data from this site for a research project, what would the `robots.txt`, the ToS, and the ethical framework from this chapter permit and restrict?"

---

### Chapter 3: The Post-API Age
**File:** `ch-03-post-api.qmd`
**Current:** 1,409 words, 0 code blocks, 4 exercises
**DO NOT EXPAND.** This chapter has `[TO FILL]` markers for the author. Leave it as-is.

---

### Chapter 4: Data Formats: XML and JSON
**File:** `ch-04-data-formats.qmd`
**Current:** 1,741 words, 14 code blocks, 3 exercises
**Target:** 3,000 words, 16+ code blocks, 5 exercises

**Add the following:**

1. **After "Working with Real XML":** Add a subsection called "From XML to DataFrame" that demonstrates the full pipeline: retrieve the Congressional member XML, loop through all `<member>` tags, extract fields into a list of dictionaries, convert to DataFrame, and do a simple analysis (party counts by state). Include 2 code blocks and 2–3 paragraphs of narrative. Emphasize that this pattern — find_all → extract → list of dicts → DataFrame — is the fundamental pattern of the book.

2. **After "Working with a Real JSON Object":** Add a subsection called "Handling Deeply Nested JSON" with a more complex example — use a real API response such as the Open-Meteo weather API (free, no auth) to demonstrate navigating 3+ levels of nesting. Show how to use `.get()` with default values for safe access, and how to flatten nested structures for DataFrame conversion.

3. **Expand exercises to 5:** Add Exercise 4: "Write a function called `xml_to_dataframe(soup, tag_name, fields)` that takes a BeautifulSoup object, a tag name to search for, and a list of child tag names to extract, and returns a pandas DataFrame. Test it on the Congressional XML data." Add Exercise 5: "The Open-Meteo API returns weather forecast data in nested JSON. Retrieve a 7-day forecast for Boulder, CO (latitude 40.01, longitude -105.27) and convert the daily temperature data into a DataFrame. Plot the daily high and low temperatures."

4. **Expand "Social History and Public Interest":** Add 1 paragraph on RSS feeds as an early open data format that enabled the blogosphere and early computational journalism, and note how RSS usage has declined as platforms moved toward proprietary APIs and algorithmic feeds — an early form of the enclosure described in Chapter 3.

---

### Chapter 5: Web Architecture and Protocols
**File:** `ch-05-protocols.qmd`
**Current:** 1,817 words, 8 code blocks, 3 exercises
**Target:** 3,000 words, 10+ code blocks, 5 exercises

**Add the following:**

1. **After the DNS section:** Add a subsection called "The Structure of Domain Names" with a diagram-style explanation (using a Markdown table or formatted text) showing how `en.wikipedia.org` decomposes into subdomain, domain, and TLD. Explain what ICANN controls vs. what domain owners control. 2 paragraphs.

2. **After the Wikimedia pageviews API example:** Add a subsection called "Diagnosing HTTP Errors" that walks through common status codes (200, 301, 403, 404, 429, 500) with a practical example of each. For 403, demonstrate the Wikimedia User-Agent fix. For 429, demonstrate a retry-with-backoff pattern. Include 2 code blocks and 2–3 paragraphs of narrative.

3. **After the URL parsing section:** Add a subsection called "Building URLs Programmatically" that demonstrates using `urllib.parse.urlencode()` to construct query strings from dictionaries, and `urllib.parse.urljoin()` to combine base URLs with paths. Show how this is cleaner than f-string URL construction. 1 code block, 2 paragraphs.

4. **Expand exercises to 5:** Add Exercise 4: "Use the browser Network tab to analyze a page load for a website of your choice. Count how many requests are made and categorize them by type (HTML, CSS, JS, images, fonts, tracking/analytics). What percentage of requests are for the actual content vs. tracking?" Add Exercise 5: "Write a function called `diagnose_url(url)` that takes a URL and prints a diagnostic report: the HTTP status code, the Content-Type header, the server name (from headers), the response size, and the redirect chain if any. Test it on 5 different URLs."

---

### Chapter 6: Parsing Static Web Pages
**File:** `ch-06-static-pages.qmd`
**Current:** 1,718 words, 11 code blocks, 3 exercises
**Target:** 3,000 words, 14+ code blocks, 5 exercises

**Add the following:**

1. **After Strategy 2 (`read_html`):** Add a subsection called "Cleaning Up `read_html` Results" that takes a Wikipedia table extracted with `read_html` and demonstrates common cleanup steps: renaming columns, dropping rows that are actually sub-headers, converting strings to numeric types, and handling merged cells that result in NaN values. 2 code blocks, 2 paragraphs.

2. **After the Oscars custom parser:** Add a subsection called "A Second Parser: Colorado Legislators" that demonstrates scraping legislator biographical data from `https://leg.colorado.gov/legislators`. Walk through inspecting the page, identifying the container for each legislator, extracting name, party, district, and contact info, and building a DataFrame. This connects to the course's module assignment. 3 code blocks, 3 paragraphs. Note that the page structure may have changed since writing and encourage students to re-inspect.

3. **After "Abstracting into Functions":** Add a subsection called "Error Handling Patterns" with a brief discussion (2 paragraphs) of the three most common scraping errors — network failures (`requests.exceptions.ConnectionError`), missing elements (`AttributeError` when `.find()` returns None), and unexpected page structure — and show a code block demonstrating a robust scraping function with `try/except` blocks for each.

4. **Expand exercises to 5:** Add Exercise 4: "Scrape a table from a non-English Wikipedia edition (e.g., French, Spanish, Japanese). Does `read_html` handle non-ASCII characters correctly? What cleanup steps are needed?" Add Exercise 5: "Write a scraper that retrieves data from multiple pages of the same site (e.g., multiple years of Oscars, multiple pages of search results). Include rate limiting, error handling, and progress reporting (`print(f'Processing page {i} of {n}...')`)."

---

### Chapter 7: Archived Web Pages and the Wayback Machine
**File:** `ch-07-archives.qmd`
**Current:** 1,429 words, 9 code blocks, 3 exercises
**Target:** 3,000 words, 12+ code blocks, 5 exercises

**Add the following:**

1. **After the Availability API section:** Add a subsection called "Comparing Multiple Snapshots" that retrieves snapshots of the same URL at three different dates (e.g., CNN's homepage in 2000, 2010, and 2020) and compares the number of links, the page size, and the text content length. This demonstrates the longitudinal research design that the Wayback Machine enables. 2 code blocks, 2 paragraphs.

2. **After the CDX Server section:** Add a subsection called "Filtering and Analyzing CDX Data" that demonstrates filtering CDX results by status code (keep only 200s), resampling by time period, and computing basic statistics (mean page size per year, number of snapshots per quarter). 2 code blocks, 2 paragraphs.

3. **After the document similarity section:** Add a subsection called "Visualizing Document Change Over Time" that computes pairwise similarity between consecutive versions and plots a "change timeline" — a line chart where the y-axis is the similarity between version N and version N+1, showing periods of stability and periods of major revision. 1 code block, 2 paragraphs explaining interpretation.

4. **Expand exercises to 5:** Add Exercise 4: "Choose a government website and use the CDX Server to answer: how frequently has the site been captured? Has capture frequency changed over time? Are there periods with no captures? What might explain these patterns?" Add Exercise 5: "Retrieve the earliest and most recent snapshots of a website you use regularly. Using the bag-of-words similarity technique from this chapter, compute the similarity between the two versions. What has changed? Write a brief analysis."

5. **Expand "Social History and Public Interest":** Add 2 paragraphs on specific examples of how journalists and lawyers have used the Wayback Machine for accountability (e.g., archived corporate promises, deleted government web pages, evolving Terms of Service used as evidence in litigation).

---

### Chapter 8: Dynamic Web Pages with Selenium
**File:** `ch-08-dynamic-pages.qmd`
**Current:** 1,713 words, 11 code blocks, 3 exercises (numbered oddly due to subsections)
**Target:** 3,000 words, 13+ code blocks, 5 exercises

**Add the following:**

1. **After "Simulating Interactions" → "Typing and Searching":** Add a subsection called "Waiting for Dynamic Content" that introduces `WebDriverWait` and `expected_conditions` as a better alternative to `time.sleep()`. Show a code block that waits for a specific element to appear (up to 10 seconds) before proceeding, and explain why this is more robust than fixed delays. 1 code block, 2 paragraphs.

2. **After "Passing to BeautifulSoup":** Add a subsection called "Scraping an Infinite Scroll Page" that demonstrates a complete workflow: navigate to a page with infinite scroll (suggest a public example like a government document listing or a news archive), scroll down in a loop until no new content appears, then extract all the loaded items. 2 code blocks (scroll loop + extraction), 2 paragraphs.

3. **After "The Fragility Problem":** Add a subsection called "Headless Mode" that introduces `Options().add_argument('--headless')` as a way to run Selenium without a visible browser window. Explain why this matters for automation (Chapter 14) and server-side execution. Show the setup code. 1 code block, 1 paragraph. Forward-reference Chapter 14.

4. **Renumber and expand exercises to 5.** The current exercises are embedded in subsections awkwardly. Consolidate them into a dedicated Exercises section and add: Exercise 4: "Use Selenium to scrape a page that loads data after clicking a 'Load More' button. Write a loop that clicks the button until it disappears, then extract all the loaded data." Exercise 5: "Compare the time it takes to retrieve data from the same source using (a) `requests.get()`, (b) Selenium in headed mode, and (c) Selenium in headless mode. Use `time.time()` to measure each. What is the performance cost of browser automation?"

---

### Chapter 9: Extracting Data from PDFs
**File:** `ch-09-pdfs.qmd`
**Current:** 1,650 words, 8 code blocks, 3 exercises
**Target:** 3,000 words, 11+ code blocks, 5 exercises

**Add the following:**

1. **After "Cleanup Strategies":** Add a subsection called "Regular Expressions for PDF Text" that covers the 5 most useful regex patterns for PDF cleanup: matching dates (`\d{1,2}/\d{1,2}/\d{4}`), extracting numbers with commas and dollar signs, removing page headers/footers that repeat on every page, splitting on section headings, and extracting email addresses or phone numbers. Show 1 code block with all 5 patterns and 2 paragraphs of narrative.

2. **After "Measuring Council Attendance":** Add a subsection called "Measuring Public Comment Frequency" that extends the Boulder City Council example to count how many public commenters spoke at each meeting. Walk through identifying the "Open Comment" or "Public Comment" section in the text, counting speaker names or numbered items, and tracking the count over time. 2 code blocks, 2 paragraphs.

3. **Expand exercises to 5:** Add Exercise 4: "Download at least 5 PDFs from a single government source (meeting agendas, inspection reports, budget documents). Write a pipeline that extracts a consistent data element from each and produces a DataFrame with one row per document. Visualize how this element changes over time." Add Exercise 5: "Compare text extraction between `pypdf` and `pdfplumber` on the same PDF document. Which produces cleaner output? For a PDF with tables, does `pdfplumber.extract_table()` produce usable results where `pypdf.extract_text()` does not?"

4. **Expand "Social History and Public Interest":** Add 2 paragraphs on the PDF liberation movement — DocumentCloud's role in investigative journalism (used by ProPublica, NYT, Washington Post), MuckRock's FOIA request platform and how it automates the process of prying documents from government agencies, and the Sunlight Foundation's work on making government data machine-readable.

---

### Chapter 10: Introduction to APIs: Wikipedia
**File:** `ch-10-wikipedia.qmd`
**Current:** 2,415 words, 11 code blocks, 5 exercises
**Target:** 3,000 words, 13+ code blocks, 5 exercises (already has 5)

**Add the following:**

1. **After "Getting Links and Categories":** Add a subsection called "Interlanguage Links" that retrieves the list of language editions for an article and analyzes how many languages cover the topic. Show the API call, the DataFrame conversion, and a brief analysis of which articles exist in many languages vs. few. 1 code block, 2 paragraphs. This demonstrates a research question about the global coverage of knowledge.

2. **After "A Second Case Study: World War II":** Add a subsection called "Combining Endpoints for Richer Analysis" that takes one article, retrieves both its revision history and its pageviews, and creates a dual-axis plot showing editing activity and reader interest over the same time period. Discuss what the relationship between editing and viewing reveals. 1 code block, 3 paragraphs of interpretive narrative.

3. **Expand "Social History and Public Interest":** Add 1 paragraph on Wikipedia's "knowledge equity" initiatives and the tension between open access and representativeness. Cite the gender gap research and the WikiProject Women in Red.

---

### Chapter 11: Government Data APIs
**File:** `ch-11-government.qmd`
**Current:** 1,918 words, 10 code blocks, 4 exercises
**Target:** 3,000 words, 12+ code blocks, 5 exercises

**Add the following:**

1. **After "Comparing Multiple Locations" (Census):** Add a subsection called "Reading the Census API Documentation" with 2 paragraphs walking through how to find a variable you need when you do not know the group code. Demonstrate the process: start at the groups index page, search for a keyword, browse the variable list, and identify the right variable code. This teaches the *process* of navigating complex documentation, not just the result.

2. **After the FRED "Server-Side Transformations" section:** Add a subsection called "Comparing CPI Across Locations" that retrieves CPI data for two metropolitan areas (e.g., Denver-Aurora-Lakewood vs. national average) and plots them on the same axes. 1 code block, 2 paragraphs of narrative about what the comparison reveals about regional cost-of-living differences.

3. **After the FEC section:** Add a subsection called "Combining Census and FRED Data" that merges the housing data (Census) with mortgage rate data (FRED) into a single DataFrame and creates a multi-panel figure showing housing construction by decade alongside interest rate trends. 1 code block, 2 paragraphs explaining the analytical value of multi-source integration.

4. **Add Exercise 5:** "Using the Census API, retrieve a demographic variable for all counties in Colorado (use `for=county:*&in=state:08`). Create a ranked bar chart of the top 20 counties. Write a brief analysis of what the ranking reveals."

---

### Chapter 12: Social and Media Platform APIs
**File:** `ch-12-social.qmd`
**Current:** 1,682 words, 11 code blocks, 3 exercises (listed as 4 but only 3 numbered)
**Target:** 3,000 words, 14+ code blocks, 5 exercises

**Add the following:**

1. **After "Comment Trees" (Reddit):** Add a subsection called "Analyzing Comment Engagement Patterns" that takes the extracted comment DataFrame and creates two visualizations: (a) a scatter plot of comment depth vs. score, and (b) a histogram of comment lengths. Add 2 paragraphs of narrative interpreting whether deeper comments receive less engagement and whether there is a "sweet spot" for comment length. 2 code blocks.

2. **After "Audio Features" (Spotify):** Add a subsection called "Comparing Artists by Audio Profile" that retrieves audio features for the top tracks of two contrasting artists (e.g., a classical pianist vs. a hip-hop artist) and creates a radar chart or grouped bar chart comparing their average danceability, energy, valence, and tempo. 2 code blocks, 2 paragraphs.

3. **Expand exercises to 5:** Renumber existing exercises clearly. Add Exercise 4: "Using spotipy, retrieve the full track listing and audio features for two playlists in different genres. Compute the mean and standard deviation of danceability, energy, and tempo for each playlist. Are the genres distinguishable by audio features alone?" Add Exercise 5: "Using the AT Protocol SDK, retrieve the 50 most recent posts from a Bluesky user of your choice. Compute basic statistics: average post length, posting frequency (posts per day), and the fraction of posts that are replies vs. original posts. How does this compare to what you would expect from the same user on Twitter/X or Reddit?"

4. **Expand "Social History and Public Interest":** Add 2 paragraphs on the Fediverse as an architectural alternative to platform enclosure. Explain that ActivityPub (Mastodon's protocol) and the AT Protocol (Bluesky's protocol) take different approaches to the same problem — distributing control — and briefly describe how each works. Connect to the ownership value from Chapter 3.

---

### Chapter 13: AI and Language Model APIs
**File:** `ch-13-ai-apis.qmd`
**Current:** 1,841 words, 11 code blocks, 3 exercises
**Target:** 3,000 words, 14+ code blocks, 5 exercises

**Add the following:**

1. **After "The Anthropic API" section:** Add a subsection called "Comparing Model Outputs" that sends the same classification prompt to both OpenAI and Anthropic, and compares the results. Discuss the implications for reproducibility: if two models give different classifications for the same input, which do you trust? 1 code block, 2 paragraphs.

2. **After "Cost Management":** Add a subsection called "Reproducibility and Documentation" that discusses the unique challenges of LLM-based research: non-deterministic outputs even at temperature=0, model version deprecation, and the difficulty of sharing proprietary API-based results. Propose a documentation template: model name and version, prompt text, temperature and other parameters, date of API calls, validation strategy. 3 paragraphs, no code.

3. **Expand exercises to 5:** Add Exercise 4: "Design a prompt for a content coding task relevant to a web-scraped dataset you have collected in an earlier chapter. Apply it to 20 documents. Then manually code the same 20 documents yourself. Compute the agreement rate. Where does the LLM disagree with you? Are its disagreements reasonable?" Add Exercise 5: "Using the embeddings API, compute embeddings for the titles of 30 Wikipedia articles on related topics. Use `scipy.cluster.hierarchy.linkage` and `dendrogram` to create a hierarchical clustering visualization. Do the clusters match your intuition about which topics are related?"

4. **Expand "Social History and Public Interest":** Add 2 paragraphs on the cost dimension of LLM-based research. Who can afford to run 10,000 API calls for a classification study? How does API pricing create new inequalities in computational research capacity? Connect to Chapter 3's point about access asymmetry.

---

### Chapter 14: Automating Data Collection
**File:** `ch-14-automation.qmd`
**Current:** 1,292 words, 2 code blocks (main script blocks, not counting inline YAML)
**Target:** 3,000 words, 5+ code blocks, 5 exercises

**This chapter needs the most expansion.** The YAML blocks are substantial but wc undercounts them.

**Add the following:**

1. **Before "Step 1: Notebook to Script":** Add a subsection called "Why Automate?" with 2–3 paragraphs explaining the research value of temporal data — how tracking a metric over time reveals dynamics that a single snapshot cannot. Give examples: Rotten Tomatoes scores changing as more reviews come in, Wikipedia's top pages reflecting current events, playlist composition reflecting seasonal trends. This motivates the technical material that follows.

2. **After the Rotten Tomatoes script:** Add a subsection called "Testing Your Script Locally" that shows how to run the script from the command line (`python scraper.py`), check that the CSV was created, and inspect its contents. Include terminal commands and expected output. 1 code block, 2 paragraphs.

3. **After the Wikipedia YAML example:** Add a subsection called "Understanding Cron Syntax" with a table or formatted explanation of the five cron fields (minute, hour, day-of-month, month, day-of-week) with examples: `"0 */6 * * *"` (every 6 hours), `"0 12 * * 1-5"` (weekdays at noon), `"0 0 1 * *"` (monthly). Reference crontab.guru. 1 paragraph of narrative.

4. **After "Secrets Management":** Add a subsection called "Monitoring and Debugging Actions" with 2 paragraphs explaining how to check if your Action is running (GitHub Actions tab), how to read the log output when it fails, and common failure modes (expired secrets, package version conflicts, rate limiting). Include a code block showing a simple data validation step added to the workflow.

5. **Expand exercises to 5:** Add Exercise 4: "Set up a GitHub Action that runs daily and collects a piece of data from a government API (weather, air quality, or a similar public source). Let it run for a week, then pull the accumulated data and create a visualization showing the daily values." Add Exercise 5: "Write a monitoring script that checks whether your scraper's output file was updated in the last 24 hours. If not, it should print a warning message. Add this check as a step in your GitHub Actions workflow."

---

### Chapter 15: Research Design with Web Data
**File:** `ch-15-research-design.qmd`
**Current:** 2,151 words, 1 code block, 3 exercises (listed as 3)
**Target:** 3,000 words, 3+ code blocks, 5 exercises

**Add the following:**

1. **After "Communicating Findings":** Add a subsection called "Visualization as Argument" with 2 paragraphs and 1 code block demonstrating a well-designed matplotlib figure with proper labels, titles, annotations, and a color scheme appropriate for the data. Contrast it with a poorly-designed version of the same figure (described in prose, not shown). Emphasize that every axis label, color choice, and title should serve the analytical purpose.

2. **After "Public Interest Framing":** Add a subsection called "Data Journalism as a Model" with 3 paragraphs discussing how data journalists at outlets like ProPublica, The Markup, and the Colorado Sun structure their investigations — from question to data to story — and what academic researchers can learn from their emphasis on narrative, accountability, and audience. Reference the guest speakers from the course (without naming them explicitly) as practitioners who integrate data fluency with domain expertise.

3. **Expand exercises to 5:** Add Exercise 4: "For a dataset you collected in an earlier chapter, write a 'data limitations' section (500 words) that honestly describes what the data can and cannot tell you. Address sampling bias, measurement validity, temporal scope, and platform-specific constraints." Add Exercise 5: "Design a multi-method research project that combines at least three techniques from this book (e.g., web scraping + API access + LLM analysis, or PDF extraction + Census data + automated collection). Write a 1-page methods section describing your data collection pipeline."

---

## After All Expansions

Run `wc -w ch-*.qmd` and verify each chapter is in the range of 2,700–3,300 words. Chapters with many code blocks may be at the lower end of word count but higher in line count — that is acceptable as long as the narrative prose between code blocks is substantial and explanatory.

Run `quarto render --to html` to verify the build succeeds and all cross-references resolve.
