# Images for ch-13

Figures in `ch-13-ai-apis.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `datalab-signin.png` and `datalab-signin_annotated.png`, `.pdf` | capture | 2026-11-09 | https://www.datalab.to/app/keys | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `openrouter-home.png` and `openrouter-home_annotated.png`, `.pdf` | capture | 2026-11-09 | https://openrouter.ai/ | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
<!-- shots:end -->

## Notes

## Notes

- **datalab-signin** comes from `https://www.datalab.to/app/keys`, which sends a visitor who isn't signed in to Datalab's sign-in service at `auth.datalab.to`. The recipe waits for "Sign in to your Datalab account". The bottom of the card, with the terms links, is cropped off.
- **openrouter-home**: OpenRouter's header has a second, hidden "Sign Up" element, so marker 1 takes the visible one (`nth: 1`). The counts on the page (tokens, users, models) change, and they are below the crop.
- **The five hand captures** (`datalab-keys`, `datalab-key-created`, `openrouter-keys`, `openrouter-create-key`, `openrouter-key-created`) wait for the instructor's screenshots. Each recipe's `hand.steps` says what to capture. Every key value, and the account's name, email and avatar, must be covered by a `redact:` box before import. Any key shown in a screenshot is deleted afterwards.
