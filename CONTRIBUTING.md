# Contributing to *Web Data Science*

Thank you for helping. This book gets better when readers say where it breaks, where it leaves them stuck, and what would make it clearer. You don't need to know git, and you don't need to know the fix: a clear report is a real contribution.

If you are taking INFO 4617 or 5617, this is also how the weekly textbook revisions work. The course's [revision framework](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/handouts/common/revision-framework.md) says how they are graded, and its [pull request walkthrough](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/handouts/common/pull-request-walkthrough.md) shows every screen. If you are an AI assistant, read [AGENTS.md](AGENTS.md) too.

This guide comes from what has gone wrong and what has worked: the project's after-action reviews (`docs/aar/`) and the reviews on its pull requests. Most of the advice below answers a problem that happened more than once.

**On this page:** [Pick what fits](#pick-what-fits) · [File an issue](#file-an-issue) · [Comment on an issue](#comment-on-an-issue) · [Three rules before you edit](#three-rules-before-you-edit) · [Edit in your browser](#edit-in-your-browser) · [Edit on your computer](#edit-on-your-computer) · [Write the pull request](#write-the-pull-request) · [Writing that passes review](#writing-that-passes-review) · [The automatic checks](#the-automatic-checks) · [After a review](#after-a-review) · [Review a pull request](#review-a-pull-request) · [Who merges](#who-merges) · [Figures and screenshots](#figures-and-screenshots) · [Ground rules](#ground-rules) · [Get help](#get-help) · [License](#license)

## Pick what fits

| What you found | What to do |
|---|---|
| Code that raises an error, a wrong result, a dead link, or a screenshot that no longer matches the page | File **Something is wrong** |
| Something missing or unclear that **stopped you** | File a **Gap report** |
| An idea that would make the book better but **didn't stop you** | File a **Suggestion** |
| A fix you can make yourself | [Open a pull request](#three-rules-before-you-edit) |
| A larger idea: a new section, exercise, or chapter | [Start a discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions) first |
| An open issue or pull request about the same thing | [Comment on it](#comment-on-an-issue) or [review it](#review-a-pull-request), instead of starting another |

Two questions settle most cases:

- **Is the book wrong now?** File *Something is wrong*.
- **Did it stop you?** File a *Gap report*. If it only could be better, file a *Suggestion*.

**Search before you start.** Look through the [open issues](https://github.com/cuinfoscience/Web-Data-Science-Book/issues) *and* the [open pull requests](https://github.com/cuinfoscience/Web-Data-Science-Book/pulls). At one point five open pull requests fixed the same Selenium install step, and four the same OCR paragraph; only one of each can be merged. If someone got there first, the most useful thing you can do is make their report or fix better.

## File an issue

An issue is a report on GitHub. It takes a few minutes, and you need a free GitHub account.

1. **Open a form.** Click **Report an issue** in the sidebar of any chapter page, or go to [New issue](https://github.com/cuinfoscience/Web-Data-Science-Book/issues/new/choose) and choose a form. Blank issues are turned off, so there is always a form.
2. **Finish the title.** The form starts it with `Broken: `, `Gap: `, or `Suggestion: `. Complete the sentence: say what, and where. A title left as `Suggestion:` can't be found again.

   | Too vague | Specific |
   |---|---|
   | `Gap:` | `Gap: Ch. 11 doesn't say where the Census API key goes` |
   | `Broken: error` | `Broken: Ch. 6 "Strategy 2" example raises KeyError` |
   | `Suggestion: more examples` | `Suggestion: Ch. 10 add a table comparing the Wikipedia APIs` |

3. **Say where.** Pick the chapter, and copy the nearest heading exactly, so anyone can find the spot.
4. **Show the evidence.** Paste the code you ran and the whole error message, as text, not as a screenshot of text. Say what you expected and what happened instead, and which Python you used.
5. **Leave the fix blank if you don't know it.** Where you got stuck is the useful part.
6. **Submit.**

Use the forms on GitHub's website. An issue made another way, such as with the `gh` command-line tool, can skip the form and arrive without its label.

## Comment on an issue

Most of an issue's value is added after it is filed. A comment does one of three things, and saying which helps everyone who reads it later:

- **Claim** it: "I'm fixing this: I'll replace the bare URL with a link and check the other two in that section." Then others know someone is on it. The maintainer assigns it to you.
- **Link** it to another issue or pull request about the same problem: "Same cause as #242." This keeps two conversations from splitting.
- **Sharpen** it: add what it's missing, such as the exact heading, the error you got, or the Python version where it fails.

If an issue is really a duplicate, say which one to keep. Don't close someone else's issue; the maintainer does that.

## Three rules before you edit

Most pull requests that stalled broke one of these.

1. **Edit the chapter's `.qmd` file, never `notebooks/` or `images/`.** Each chapter is one file at the top of the repository, such as `ch-05-protocols.qmd`. A script makes every notebook from its chapter and overwrites any edit made to the notebook itself. A notebook edited by hand has also broken the build for everyone: one edit left the file as invalid JSON, and every pull request after it failed. If you found the problem in a notebook, its first cell names the chapter; search the `.qmd` for the same code or sentence and change it there. For images, see [Figures and screenshots](#figures-and-screenshots).
2. **One change per pull request, on its own branch.** Two fixes are two pull requests. If you work in a fork, never open a pull request from your fork's `main` branch: every later commit you make to it joins the open pull request. One such pull request grew to 55 files and had to be closed.
3. **Check that no open pull request already changes those lines.** Two pull requests that change the same sentence can't both be merged, and the second one becomes a conflict.

## Edit in your browser

This way needs no installs, and it is how most of the book's contributors work.

1. On the book's website, click **Edit this page** in the sidebar. You can also open the file on GitHub and click the pencil icon.
2. If GitHub asks you to fork the repository, accept. A fork is your own copy of the book's files. If you have write access, you edit the book's repository directly, and there is no fork.
3. Make your change. Check it on the **Preview** tab. (The preview is GitHub's Markdown, not Quarto's, so callouts and cross-references won't look right there. That's expected.)
4. Click **Commit changes…**. Write a title that says what and where, such as `Ch. 4: link the Missing Manual chapter on version control`, and a description that says why.
5. Select **Create a new branch for this commit and start a pull request**. Don't commit directly to `main`: that skips every check and changes the live book at once. In a fork, GitHub makes the branch for you.
6. Click **Propose changes**, then **Create pull request**, and [fill in the template](#write-the-pull-request).

In the browser you can't regenerate the chapter's notebook, so the **Notebook sync** check fails. That is expected, and it isn't held against you. Write "Edited in the browser, so the notebooks aren't regenerated" under **Checks**. After your pull request is merged, a workflow regenerates the notebooks.

## Edit on your computer

You need Python 3.14 (3.13 also works) with Jupyter, and [Quarto](https://quarto.org/docs/get-started/) 1.4 or later to build the book. The book's own `webdata` environment (chapter 1) has everything but Quarto. [GitHub Desktop](https://desktop.github.com/), the [`gh` command-line tool](https://cli.github.com/), and plain `git` all work.

1. Get a copy of the repository. With write access:

   ```bash
   gh repo clone cuinfoscience/Web-Data-Science-Book
   ```

   Without it, fork and copy in one step:

   ```bash
   gh repo fork cuinfoscience/Web-Data-Science-Book --clone
   ```

   In GitHub Desktop, use **File > Clone repository**.
2. Start from an up-to-date `main`, and make a branch for this one change. Name it after the change, starting with the issue number if there is one:

   ```bash
   git switch main
   git pull origin main
   git switch -c 175-ch06-strategy-2-keyerror
   ```

   In GitHub Desktop, use **Branch > New branch**.
3. Edit the chapter's `.qmd` file.
4. **Run every code cell you changed**, in the chapter's notebook or a scratch notebook, and make any output comments in the chapter match what it printed. Seventeen errors once reached the book in code that had never been run, and a reviewer can tell. If a cell calls a live site, say in the pull request which cells you ran and when.
5. From the repository's top folder, regenerate the notebooks, check your prose, and build the whole book:

   ```bash
   python tools/make_notebooks.py
   python tools/trope_lint.py ch-06-static-pages.qmd
   quarto render
   ```

   `trope_lint.py` lists sentences to reconsider and never fails; [AGENTS.md](AGENTS.md) says what to do with them ("Prose safeguards"). Build the whole book, not one chapter: a chapter built alone shows cross-reference warnings that aren't real, and the **Render** check fails on any warning. Use `quarto preview` while you work.
6. Commit the chapter and the regenerated notebooks together, push, and open the pull request:

   ```bash
   git add ch-06-static-pages.qmd notebooks/
   git commit -m "Ch. 6: fix the KeyError in Strategy 2"
   git push -u origin 175-ch06-strategy-2-keyerror
   gh pr create --web
   ```

   In GitHub Desktop, click **Commit**, then **Push origin**, then **Create Pull Request**.

Don't rebase or force-push a branch once its pull request is open. The book merges with merge commits and keeps its history, and a reviewer may have your branch open.

## Write the pull request

The pull request form starts with a template. Replace every `[bracketed hint]`; a description that still has them reads as unfinished.

- **Title:** what and where, as `Ch. N: …`. Not `Update ch-05-protocols.qmd`, but `Ch. 5: explain why time.sleep() goes between requests`.
- **Closes #N:** the issue this pull request fixes, and only that one. GitHub closes an issue when a pull request or commit that says "Closes", "Fixes", or "Resolves" before its number is merged, wherever the words appear, even in a quotation. To mention an issue without closing it, write "See #N" or "Related to #N". If no issue fits, delete the line.
- **Location, Problem, Why, Change:** the file and the heading; what you saw, with code and output; who it affects; and what you changed, and chose not to change. The course teaches these same four fields.
- **AI assistance:** if an AI tool helped, name it and say what it did. The course requires this, and the book discloses its own use in [Appendix B](https://cuinfoscience.github.io/Web-Data-Science-Book/appendix-ai-disclosure.html). Write "none" if none did.
- **Checks:** tick only what you did. If you couldn't run something, say why. A box ticked for a step that wasn't done costs more trust than an empty one.

A draft pull request is fine when you want early feedback.

## Writing that passes review

[AGENTS.md](AGENTS.md) is the full style guide. It is written for people and for AI assistants; its parts about `docs/` and merging are for maintainers. These are the points reviews ask about most, in rough order of how often.

**Links and references**

- Link with `[descriptive text](https://…)`, never a bare URL.
- Link another chapter with an `@sec-` reference, such as `@sec-protocols`, not with a URL to the website. Cite a source from `references.bib` with `@key`.
- A *Missing Manual* reference goes in a `::: {.callout-tip}` block: "For a deeper introduction to [topic], see *Missing Manual* Chapter N: [Title]."
- Give each data source's URL and the date you used it. Anything that changes, such as a price, a count, or a page's layout, needs a date.

**Markdown and Quarto**

- Put a blank line before and after every heading, list, callout fence (`:::`), and code fence.
- Use the callout that fits: `.callout-tip` for practical tips and *Missing Manual* references, `.callout-warning` for ethical and legal cautions, `.callout-note` for a short note that fits nowhere else, and `.callout-important` for critical setup or debugging steps.
- A connection to the post-API age (openness, oversight, ownership), or a piece of history, goes in the chapter's "Social History and Public Interest" section, not in a callout. Link each fact there to its source, or cite it from `references.bib`.
- Put code, file names, function names, and HTML tags in backticks: `` `requests.get()` ``, `` `robots.txt` ``, `` `<div>` ``.
- Escape a dollar sign in prose as `\$`. Two unescaped dollar signs in one paragraph become math.
- In a figure caption, keep square brackets inside backticks. A bare `]` ends the caption early.

**Code**

- Every live request sends the book's User-Agent form, `WebDataScience/1.0 (your-email@colorado.edu)`, never the library default. Chapter 10 adds the library and its version after it, `python-requests/2.x`, the full form [Wikimedia's User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy) asks for. Wikipedia refuses the default with status 403, and Wikimedia's rate limits give an identified client 200 requests a minute and an unidentified one 10.
- Give live requests a `timeout`, and check the response before parsing it: `response.raise_for_status()` before `response.json()`. A rate-limited site answers with an HTML error page, and `.json()` on that raises a confusing `JSONDecodeError` instead of the real problem.
- Keep each code comment on one line. Code in the book doesn't run when the book builds; readers run it in the notebooks.
- In **Recommended Exercises**, a step's code cell holds only comment prompts, such as `# Your code here`, never a solution. **Additional Exercises** are open-ended, and the graduate extension (INFO 5617) comes last.

**Voice**

- Write to the reader as "you", like an experienced mentor. Use plain words, and define a term the first time you use it.
- Say what a thing does or what the reader should do, rather than that it is important, crucial, or powerful. `tools/trope_lint.py` flags these sentences.
- Write for the reader's real starting point: Anaconda as installed, often no terminal, and often the browser editor.

**Facts that live in more than one place**

Some facts, such as the `webdata` install command, are written in several files, here and in the course repository. If you change one, find the others (`git grep` helps) and change them in the same pull request.

## The automatic checks

| Check | Runs when your pull request changes | It fails when | What to do |
|---|---|---|---|
| **Render** | a `.qmd` file, `_quarto.yml`, or `references.bib` | The book doesn't build, or the build prints a warning. | Click **Details** and find the first `ERROR` or `WARN` line. Common causes: a broken `@sec-` reference or `@key`, an unclosed code fence, a `]` outside backticks in a caption, or an unescaped pair of `$`. |
| **Notebook sync** | a `.qmd` file or a notebook | Regenerating the notebooks would change them. | See below: this check fails for three different reasons. |
| **Trope lint** | a `.qmd` file | Never. | It lists phrases to reconsider. |
| **Screenshot check** | a file in `images/` or `tools/shots/` | An image doesn't match its record. | Undo your change to `images/` and report the figure instead (see [Figures and screenshots](#figures-and-screenshots)). |

**When Notebook sync is red**, find which case you're in:

- **You edited in the browser.** Expected. Say so under **Checks**.
- **You edited a notebook.** Undo it, and make the change in the chapter:

  ```bash
  git restore --source origin/main notebooks/ch-06-static-pages.ipynb
  ```

  If you edited in the browser, ask in the pull request, and the maintainer will restore the notebook.
- **You edited the `.qmd` on your computer** and forgot to regenerate. Run `python tools/make_notebooks.py`, then commit `notebooks/`.
- **None of these.** After each merge to `main`, a workflow opens a pull request titled "Regenerate notebooks after merges to main". Until the maintainer merges it, `main` itself is out of date, and every pull request that touches a chapter fails this check. Nothing is wrong with yours. Once that pull request is merged, click **Update branch** on yours, and the check passes.

A pull request from a fork waits for the maintainer to approve its checks before they run, so a new pull request may show no checks at first.

## After a review

Someone will review your pull request: the maintainer, and in the course, your classmates. Most pull requests get a "Changes requested" review the first time; that is the normal path, not a failure.

- **Answer each comment in its thread.** Say what you changed, or why you didn't.
- **Accept a suggestion** with **Commit suggestion** under it, or batch several with **Add suggestion to batch**.
- **Make other changes on the same branch.** In the browser, open **Files changed**, click **⋯** on the file, and choose **Edit file**. Check that the editor names your branch, not `main`, before you commit. If your commit opens a second pull request by mistake, close the new one and make the change again from **Files changed** on the first.
- **Never open a new pull request** for the same change. The conversation, and the review, belong to the first one.
- **Click Re-request review** (the circular arrows next to the reviewer's name) when you're done, so the reviewer knows.

**Conflicts.** If GitHub says your branch has conflicts, `main` has changed the same lines since you started. You can leave the conflict for the maintainer, unless a review asks you to resolve it. Then click **Resolve conflicts**, keep the text that should stay, delete the `<<<<<<<`, `=======`, and `>>>>>>>` lines, and click **Mark as resolved** and **Commit merge**. On your computer, run `git pull --no-rebase origin main`, fix the files, and commit. If `main` deleted the lines you changed, say so in the pull request: your change may no longer be needed.

## Review a pull request

A good review is as useful as a good fix. Check five things:

1. **The right file:** the `.qmd`, not `notebooks/` or `images/`.
2. **One change:** the title and the diff agree, and nothing unrelated is mixed in.
3. **Correct:** if it changes code, run it, or at least the changed lines, and compare the output with what the chapter says. Reviewers have caught claims that running the code disproved.
4. **Clear:** a reader at that point in the book would understand it.
5. **Markdown and style:** the points in [Writing that passes review](#writing-that-passes-review).

How to write it:

1. Open the pull request, and click **Files changed**.
2. To comment on a line, move the pointer over it and click **+**. To propose exact wording, click **Add a suggestion** (the ± icon) in the comment box.
3. Click **Review changes**, and write a summary in this shape:

   ```markdown
   **Verdict:** approve / request changes
   **Must fix:** at most two things, each with the line
   **Nice to have:** anything else
   ```

   Choose **Approve** or **Request changes** to match.
4. Be kind, specific, and actionable. Review the change, not the person, and assume good faith.

If two pull requests do the same thing, say so on both, and say which one does it better.

## Who merges

The maintainer merges pull requests, with a merge commit: students' pull requests in class or in a review pass, others when they are ready. **Don't merge your own pull request or a classmate's, even if GitHub shows you the button.** Changes merged without review have reached the book and had to be reverted.

Not every pull request is merged. Some are superseded by another, and some change lines that `main` has since rewritten. A closed pull request can still be a useful report, and in the course you are graded on the proposal and the review, not on the merge. After a merge, the live book updates within a few minutes.

## Figures and screenshots

Every image in `images/` comes from a recipe in `tools/shots/recipes/`. The toolkit records where each image came from, and its `check` command, which runs on every pull request that changes an image, flags an image that someone replaced by hand. So:

- **A screenshot is out of date?** File *Something is wrong*, and attach a screenshot of what you see now.
- **A figure would help?** File a *Gap report* or a *Suggestion*. Describe the figure, and attach a sketch or an example if you have one.

Every screenshot in the book is a real capture of a real page, never a page rebuilt to look real; a diagram is labeled as a diagram. Screenshots show no classmate's name or work, no one signed in, and no private person's contact details. Every figure has alt text that gives the words and numbers a reader needs, and a caption that says when anything that changes was captured. The maintainer makes figures with the toolkit, which runs in a Linux container, not on a laptop; [`tools/shots/README.md`](tools/shots/README.md) has the details.

## Ground rules

- **Be kind.** Critique the text, not the person.
- **Protect privacy.** No classmate's name or work in an example or a screenshot, and no personal data. Count private individuals in public records, such as council minutes, rather than naming them.
- **Keep secrets out.** Never paste an API key, password, or token into an issue, a pull request, or the book. Use environment variables, as the book's API chapters do.
- **Use AI tools in the open.** The course allows them on four conditions: say where and how they shaped your work; understand and be able to explain every line you submit; never use them to misrepresent data, sources, or effort; and check their output for accuracy before you trust it.
- **Your username is public.** The repository is public, so your GitHub username appears on what you post. If you are in INFO 4617 or 5617 and want to contribute under a pseudonym, ask the instructor.

## Get help

- **About one issue or pull request:** ask in its comments.
- **About something broader:** [start a discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions).
- **About git and GitHub:** see the *Missing Manual*'s [Chapter 31: Version Control](https://cuinfoscience.github.io/INFO-Missing-Manual/chapters/version-control.html).
- **In INFO 4617 or 5617:** bring it to class or office hours.

## License

The book is released under CC BY-NC-SA 4.0 ([LICENSE](LICENSE)). Under [GitHub's Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#6-contributions-under-repository-license), what you contribute to this repository is licensed under the same terms.
