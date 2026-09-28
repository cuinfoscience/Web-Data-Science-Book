# Contributing to *Web Data Science*

Thank you for helping. This book gets better when readers say where it breaks,
where it leaves them stuck, and what would make it clearer. You don't need to
know git, and you don't need to know the fix: a clear report is a real
contribution.

If you are taking INFO 4617 or 5617, this is also how the weekly textbook
revisions work. The course's
[revision framework](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/handouts/common/revision-framework.md)
says how they are graded, and its
[pull request walkthrough](https://github.com/cuinfoscience/INFO4617-Fall2026/blob/main/handouts/common/pull-request-walkthrough.md)
shows every screen.

**On this page:**
[Pick what fits](#pick-what-fits) ·
[File an issue](#file-an-issue) ·
[Change the book with a pull request](#change-the-book-with-a-pull-request) ·
[After you open a pull request](#after-you-open-a-pull-request) ·
[Review a pull request](#review-a-pull-request) ·
[Figures and screenshots](#figures-and-screenshots) ·
[Style in brief](#style-in-brief) ·
[Ground rules](#ground-rules) ·
[Get help](#get-help) ·
[License](#license)

## Pick what fits

| What you found | What to do |
|---|---|
| Code that raises an error, a wrong result, a dead link, or a screenshot that no longer matches the page | File **Something is wrong** |
| Something missing or unclear that **stopped you** | File a **Gap report** |
| An idea that would make the book better but **didn't stop you** | File a **Suggestion** |
| A fix you can make yourself | [Open a pull request](#change-the-book-with-a-pull-request) |
| A larger idea: a new section, exercise, or chapter | [Start a discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions) first |

Two questions settle most cases:

- **Is the book wrong now?** File *Something is wrong*.
- **Did it stop you?** File a *Gap report*. If it only could be better, file a *Suggestion*.

*Something is wrong* and *Gap report* get attention first. If you can't tell
which form fits, pick the closest one. A report in the wrong form still helps,
and it can be relabeled.

## File an issue

An issue is a report on GitHub. It takes a few minutes, and you need a free
GitHub account.

1. **Search first.** Look through the
   [open issues](https://github.com/cuinfoscience/Web-Data-Science-Book/issues).
   If someone already reported your problem, add a comment with your own
   evidence instead of filing a new issue.
2. **Open a form.** Click **Report an issue** in the sidebar of any chapter
   page, or go to
   [New issue](https://github.com/cuinfoscience/Web-Data-Science-Book/issues/new/choose)
   and choose a form. Blank issues are turned off, so there is always a form.
3. **Finish the title.** The form starts it with `Broken: `, `Gap: `, or
   `Suggestion: `. Complete the sentence: say what, and where.

   | Too vague | Specific |
   |---|---|
   | `Gap:` | `Gap: Ch. 11 doesn't say where the Census API key goes` |
   | `Broken: error` | `Broken: Ch. 6 "Strategy 2" example raises KeyError` |
   | `Suggestion: more examples` | `Suggestion: Ch. 10 add a table comparing the Wikipedia APIs` |

4. **Say where.** Pick the chapter, and copy the nearest heading exactly, so
   anyone can find the spot.
5. **Show the evidence.** Paste the code you ran and the whole error message,
   as text, not as a screenshot of text. Say what you expected and what
   happened instead.
6. **Leave the fix blank if you don't know it.** Where you got stuck is the
   useful part.
7. **Submit.**

Use the forms on GitHub's website. An issue made another way, such as with the
`gh` command-line tool, can skip the form and arrive without its label.

If you want to fix the problem yourself, say so in a comment on the issue.
Then other people know that someone is working on it.

## Change the book with a pull request

A pull request proposes a change to the book's files. Someone reviews it
before it becomes part of the book.

### Before you start

- **Change one thing per pull request.** Two fixes are two pull requests.
- **Edit the chapter's `.qmd` file.** Each chapter is one file at the top of
  the repository, such as `ch-05-protocols.qmd`. Don't edit the files in
  `notebooks/`: a script makes them from the chapters, and it overwrites
  any direct edit. To fix a notebook, fix its chapter.
- **Don't replace image files.** See
  [Figures and screenshots](#figures-and-screenshots).
- **Claim the issue.** If an issue describes the problem, comment on it, so no
  one else starts the same fix.

### In your browser

This way needs no installs.

1. On the book's website, click **Edit this page** in the sidebar. You can also
   open the file on GitHub and click the pencil icon.
2. If GitHub asks you to fork the repository, accept. A fork is your own copy
   of the book's files. If you have write access, you edit the book's
   repository directly, and there is no fork.
3. Make your change. Check it on the **Preview** tab.
4. Click **Commit changes…**. Write a title that says what and where, such as
   `Ch. 4: link the Missing Manual chapter on version control`, and a
   description that says why.
5. Select **Create a new branch for this commit and start a pull request**.
   Don't commit directly to `main`: that skips every check and changes the
   live book at once. (In a fork, GitHub makes the branch for you.)
6. Click **Propose changes**, then **Create pull request**.

In the browser you can't regenerate the chapter's notebook, so the
**Notebook sync** check fails. That is expected. Write "notebooks not
regenerated (edited in the browser)" in your description; the maintainer can
regenerate them before merging.

### On your computer

You need Python 3.14 (3.13 also works) with Jupyter (`pip install jupyter`), and
[Quarto](https://quarto.org/docs/get-started/) 1.4 or later to build the book.
[GitHub Desktop](https://desktop.github.com/), the
[`gh` command-line tool](https://cli.github.com/), and plain `git` all work.

1. Get a copy of the repository. With write access:

   ```bash
   gh repo clone cuinfoscience/Web-Data-Science-Book
   ```

   Without it, fork and copy in one step:

   ```bash
   gh repo fork cuinfoscience/Web-Data-Science-Book --clone
   ```

   In GitHub Desktop, use **File > Clone repository**.
2. Make a branch for this one change. Name it after the change, and start with
   the issue number if there is one:

   ```bash
   git switch -c ch06-strategy-2-keyerror
   ```

   In GitHub Desktop, use **Branch > New branch**.
3. Edit the chapter's `.qmd` file.
4. From the repository's top folder, regenerate the notebooks:

   ```bash
   python tools/make_notebooks.py
   ```

5. Check your prose for phrases the book avoids:

   ```bash
   python tools/trope_lint.py ch-06-static-pages.qmd
   ```

   It lists sentences to reconsider and never fails. [AGENTS.md](AGENTS.md)
   explains what to do with them ("Prose safeguards").
6. Run `quarto preview` while you work. Before you open the pull request,
   build the whole book:

   ```bash
   quarto render
   ```

   Build the whole book, not one chapter: a chapter built alone shows
   cross-reference warnings that aren't real, and the **Render** check fails on
   any warning.
7. Commit the chapter and the regenerated notebooks together, push, and open
   the pull request:

   ```bash
   git add ch-06-static-pages.qmd notebooks/
   git commit -m "Ch. 6: fix the KeyError in Strategy 2"
   git push -u origin ch06-strategy-2-keyerror
   gh pr create --web
   ```

   In GitHub Desktop, click **Commit**, then **Push origin**, then
   **Create Pull Request**.

If `main` changes while your pull request is open, click **Update branch** on
the pull request page, or run `git pull --no-rebase origin main` and push.
Both merge `main` into your branch. Don't rebase or force-push a branch other
people have seen: the book merges with merge commits and keeps its history.

### Write the pull request

The pull request form starts with a template. Fill in each part:

- **Title:** what and where. Not `Update ch-05-protocols.qmd`, but
  `Ch. 5: explain why time.sleep() goes between requests`.
- **Closes #N:** the number of the issue it fixes. GitHub closes that issue
  when the pull request is merged.
- **Location, Problem, Why, Change:** the file and the heading; what you saw,
  with code and output; who it affects; and what you changed, and chose not
  to change. The course teaches these same four fields.
- **AI assistance:** if an AI tool helped, name it and say what it did. The
  course asks for this, and the book discloses its own use in
  [Appendix B](https://cuinfoscience.github.io/Web-Data-Science-Book/appendix-ai-disclosure.html).
- **Checks:** tick what you ran. If you couldn't run something, say why.

A draft pull request is fine when you want early feedback.

## After you open a pull request

### The automatic checks

| Check | Runs when your pull request changes | If it fails |
|---|---|---|
| **Render** | a `.qmd` file, `_quarto.yml`, or `references.bib` | The book didn't build, or it printed a warning. Click **Details** and find the first `ERROR` or `WARN` line. A broken cross-reference (`@sec-…`) or citation key (`@key`) is a common cause. |
| **Notebook sync** | a `.qmd` file or a notebook | A notebook doesn't match its chapter. Run `python tools/make_notebooks.py` and commit `notebooks/`. If you edited in the browser, say so in the description. |
| **Trope lint** | a `.qmd` file | It never fails. It lists phrases to reconsider. |
| **Screenshot check** | a file in `images/` or `tools/shots/` | An image doesn't match its record: it was replaced by hand, or its `IMAGES.md` table is out of date. Undo the change to `images/`, and report the figure instead (see [Figures and screenshots](#figures-and-screenshots)). |

A first pull request from a fork can wait until a maintainer approves its
checks. After that, a red check is almost always about your edit. Fix it on the
same branch, and the checks run again.

### Review and merge

- Someone reviews your pull request: the maintainer, and in the course, your
  classmates.
- Answer each comment in its thread. Push your fixes to the same branch. Don't
  open a new pull request.
- Students' pull requests are merged in class, after a code-review standup on a
  Friday: you present your change, a classmate reviews it, and the maintainer
  merges the approved ones with a merge commit. Other pull requests are merged
  by the maintainer the same way. Don't merge your own pull request or a
  classmate's, even if GitHub shows you the button.
- Not every pull request is merged. A closed one can still be a useful report,
  and in the course you are graded on the proposal and the review, not on the
  merge.
- After a merge, the live book updates within a few minutes.

## Review a pull request

1. Open the pull request, and click **Files changed**.
2. To comment on a line, move the pointer over it and click **+**. To propose
   exact wording, click **Add a suggestion** (the ± icon) in the comment box.
   The author can accept a suggestion with one click.
3. Click **Review changes**, and choose **Comment**, **Approve**, or
   **Request changes**.
4. Be kind, specific, and actionable. Say which points must be fixed and which
   would be nice, and end with a verdict.

## Figures and screenshots

Every image in `images/` comes from a recipe in `tools/shots/recipes/`. The
toolkit records where each image came from, and its `check` command, which runs
on every pull request that changes an image, flags an image that someone
replaced by hand. So:

- **A screenshot is out of date?** File *Something is wrong*, and attach a
  screenshot of what you see now.
- **A figure would help?** File a *Gap report* or a *Suggestion*. Describe the
  figure, and attach a sketch or an example if you have one.

The maintainer makes figures with the toolkit, which runs in a Linux container,
not on a laptop. Every figure has alt text that gives the words and numbers a
reader needs, and a caption that says when anything that changes was captured.
[`tools/shots/README.md`](tools/shots/README.md) has the details.

## Style in brief

[AGENTS.md](AGENTS.md) is the full style guide. It is written for people and
for AI assistants; its parts about `docs/` and merging are for maintainers. The
essentials:

- Write to the reader as "you", like an experienced mentor. Use plain words,
  and define a term the first time you use it.
- Keep each code comment on one line. Code blocks don't run when the book
  builds (`eval: false`); readers run them in the notebooks.
- In **Recommended Exercises**, a step's code cell holds only comment prompts,
  such as `# Your code here`, never a solution. **Additional Exercises** are
  open-ended, and the graduate extension (INFO 5617) comes last.
- Link other chapters with `@sec-` references. Cite sources from
  `references.bib` with `@key`.
- Give each data source's URL and the date you used it.
- Avoid sentences that only announce that something is important.
  `tools/trope_lint.py` flags them.

## Ground rules

- Be kind. Critique the text, not the person.
- Protect privacy: no classmate's name or work in an example or a screenshot,
  and no personal data.
- Never paste an API key, password, or token into an issue, a pull request, or
  the book. Use environment variables, as the book's API chapters do.
- The repository is public, so your GitHub username appears on what you post.
  If you are in INFO 4617 or 5617 and want to contribute under a pseudonym, ask
  the instructor.

## Get help

- **About one issue or pull request:** ask in its comments.
- **About something broader:**
  [start a discussion](https://github.com/cuinfoscience/Web-Data-Science-Book/discussions).
- **About git and GitHub:** see the *Missing Manual*'s
  [Chapter 31: Version Control](https://cuinfoscience.github.io/INFO-Missing-Manual/chapters/version-control.html).
- **In INFO 4617 or 5617:** bring it to class or office hours.

## License

The book is released under CC BY-NC-SA 4.0 ([LICENSE](LICENSE)). Under
[GitHub's Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service#6-contributions-under-repository-license),
what you contribute to this repository is licensed under the same terms.
