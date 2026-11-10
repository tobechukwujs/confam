# Demo set

Six checks for a live demo, all built from the **fictional** "Simulated Electoral Commission"
notice `SEC-2026-140` (the current voter registration deadline). Nothing here is a real notice.
Every picture was kept only because it gives the intended answer through the real pipeline
(Tesseract, two readings, the confidence gate at its default of 95). Check that they still do:

```bash
uv run python eval/make_demo.py --check     # needs Tesseract
```

Regenerate them (only if the engine changes) with `uv run python eval/make_demo.py`.

**How to use.** Open the home page. For a picture: use "Choose a photo", drag it onto the box, or
paste it with Ctrl+V (photo checks are labelled Beta). For the text file: paste its contents into
the notice box. The API must be running with Tesseract available, and the record must be the
fictional fixture record (`fixtures/sec-sim/notices.json`).

| File | What it is | What the screen should show |
|---|---|---|
| `01_honest_confirmed.png` | The genuine notice in a chat screenshot ("Forwarded", a sender, a time) | **Confirmed**: a large green tick, "This matches the official notice.", no changes listed, the receipt naming notice `SEC-2026-140`. The chat lines around the notice are ignored. |
| `02_altered_date.png` | The same screenshot with the date changed from 28th to **29th** November | **Altered**: `29th` as the big red-ringed figure with `28th November` handwritten above it, one row in "What changed" ("Date. Your copy says 29th November. The official notice says 28th November."), and "Your photo, marked" with the ring on the date. |
| `03_altered_link_PASTE.txt` | The notice text with its web address changed to `register-sec.example` | **Altered** with the changed address marked and the official one (`register.sec.example`) written beside it. **This one is pasted text, not a photo: see below.** |
| `04_not_official.png` | An invented "URGENT" message that sends people to a look-alike address | **Not official**: a large red cross over the claim, the official address handwritten, and the official sentence quoted ("Register only at https://register.sec.example."). |
| `05_partial_crop.png` | The genuine notice with its last lines cut off | **Partial**: a pencil bracket around what is visible, "Part of the notice is missing, so we checked only what is visible", and the action "See the whole notice". |
| `06_cannot_confirm_blurry.png` | The genuine notice, out of focus | **Cannot confirm**: a pencil ring and question mark. It is never Confirmed and never Altered. The engine reports the reason as "nothing it can check" (no readable facts), so the sentence reads "We found nothing in this message that we can check against the record" rather than "send a clearer photo". |

`expected.json` records the exact verdict, notice, changes and conflicts each one produced when
the set was made.

## Why the changed web address is not a photo

At the default confidence gate (95) a changed web address on a **photo** is never called Altered.
Tesseract gives web addresses a confidence of about 84 to 91 at every picture size we tried, so
the gate withholds them: the photo of a changed address comes out **Cannot confirm** (never
Confirmed). The same is true of phone numbers. Pasted text has no reading step and no gate, so
`03_altered_link_PASTE.txt` shows the Altered address correctly. If you show the changed-address
edit on a photo, expect "Cannot confirm". See `docs/EVAL.md` and `docs/LIMITATIONS.md`.

## Other things worth knowing before a demo

- These are crisp, synthetic pictures. Real phone photos of real screens are harder: expect many
  more "Cannot confirm" answers (see `docs/EVAL.md`).
- Photo checks need Tesseract on the server. Without it the home page says photo checks are not
  available and text checks keep working.
- The sample verdict pages (`/v/…`, when `CONFAM_SEED_SAMPLES=1`) show every screen without any
  photo and are labelled as samples.
