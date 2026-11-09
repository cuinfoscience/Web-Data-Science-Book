# Images for ch-13

Figures in `ch-13-ai-apis.qmd`. `tools/shots` writes the table below from `provenance.json`
and rewrites only what is between the two markers. Notes below the table are
for people: what a figure shows that is easy to miss, and what a retake needs.

<!-- shots:begin: generated from provenance.json by tools/shots; edits between these markers are replaced -->
| File | Kind | Captured | Source | How |
|---|---|---|---|---|
| `datalab-keys.png` and `datalab-keys_annotated.png`, `.pdf` | capture | 2026-11-09 | https://www.datalab.to/app/keys | Brian C. Keegan: screenshot by hand in a desktop browser; imported by tools/shots, 1 area blacked out |
| `datalab-signin.png` and `datalab-signin_annotated.png`, `.pdf` | capture | 2026-11-09 | https://www.datalab.to/app/keys | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `openrouter-create-key.png` and `openrouter-create-key_annotated.png`, `.pdf` | capture | 2026-11-09 | https://openrouter.ai/settings/keys | Brian C. Keegan: screenshot by hand in a desktop browser; imported by tools/shots |
| `openrouter-home.png` and `openrouter-home_annotated.png`, `.pdf` | capture | 2026-11-09 | https://openrouter.ai/ | tools/shots: Google Chrome for Testing 154.0.8037.92, 800×600 at 2× |
| `openrouter-keys.png` and `openrouter-keys_annotated.png`, `.pdf` | capture | 2026-11-09 | https://openrouter.ai/settings/keys | Brian C. Keegan: screenshot by hand in a desktop browser; imported by tools/shots, 2 areas blacked out |
<!-- shots:end -->

## Notes

## Notes

- **datalab-signin** comes from `https://www.datalab.to/app/keys`, which sends a visitor who isn't signed in to Datalab's sign-in service at `auth.datalab.to`. The recipe waits for "Sign in to your Datalab account". The bottom of the card, with the terms links, is cropped off.
- **openrouter-home**: OpenRouter's header has a second, hidden "Sign Up" element, so marker 1 takes the visible one (`nth: 1`). The counts on the page (tokens, users, models) change, and they are below the crop.
- **datalab-keys, openrouter-keys, openrouter-create-key** are Brian C. Keegan's screenshots, signed in, taken on 2026-11-09 and imported with `tools/shots/run import`.
  - They are 1× screenshots (`scale: 1`), and their markers are placed by `xy`.
  - What's hidden:
    - On Datalab's page, the left menu is cropped off, and the key's visible characters are blacked out.
    - On OpenRouter's page, the header with the account's avatar and name is cropped off, and so is the row of another key; the `info4617` key's short ID is blacked out.
    - The create-key form shows nothing private.
  - Screenshots of a newly created key, with its value showing, couldn't be taken as planned, so the chapter describes that step in words.
