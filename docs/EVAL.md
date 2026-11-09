# Evaluation

**These numbers come from synthetic, fictional fixtures.** Every case is built from the invented
"Simulated Electoral Commission" notices in `eval/record.json`. They say nothing about real
notices, real letterheads, stamps or signatures, or real photographs. Do not quote them as
accuracy in any real-world sense (CLAUDE.md rule 11). They are only produced by
`uv run python eval/run.py`, and only figures from a run in the current session may be quoted.

## Run it

```bash
uv run python eval/run.py                 # everything; the picture suites need Tesseract
uv run python eval/run.py --no-images     # text suites only (about 5 seconds)
uv run python eval/run.py --suite edits_text honest_text
```

Exit code 1 if any edited or invented copy is confirmed as genuine. Results go to
`eval/results/latest.md` (summary and every case that missed) and `eval/results/latest.json`
(every case). The text suites also run in `uv run pytest` (`services/engine/tests/test_eval_cases.py`)
as a regression gate; the picture suites are slow and need Tesseract, so they only run here.

## What is measured

| Number | Meaning | Target |
|---|---|---|
| Correct verdicts | The verdict is one of the accepted answers for that case | as high as possible |
| **Forged copies confirmed as genuine** | An edited or invented copy that came out `confirmed` | **0, always** |
| False alarms on honest copies | An honest copy called `altered` or `not_official` | low |
| Honest copies not confirmed | An honest copy answered `cannot_confirm` or `partial` (safe, but unhelpful) | low |
| Crops confirmed as complete | A cut-off notice that came out `confirmed` | 0 |
| Replaced notice not flagged | An honest copy of the replaced notice confirmed without `superseded_by` (rule 2) | 0 |

## The suites

| Suite | Cases | What it is |
|---|---:|---|
| `honest_text` | 168 | Each of 8 notices copied unchanged: 6 harmless variants (upper/lower case, extra spaces, line breaks, dropped full stops) and inside each of 15 chat wrappers ("Forwarded", sender, timestamp, captions above and below, a Pidgin caption, numbers and negations in captions) |
| `edits_text` | 131 | One-detail edits of every kind: a date's day or month, a time, a weekday, a number, an amount of money, a phone number, a web address (host, scheme, path), a removed negation, a swapped word, a look-alike character, an inserted sentence, a dropped middle or last sentence, a link or phone number appended |
| `edits_text_wrapped` | 131 | The same edits, each inside a chat wrapper |
| `crops_text` | 24 | A notice cut off at the end or the start, with and without a header |
| `invented` | 15 | Invented notices from the fictional commission (wrong links, wrong dates, fees, bogus portals) |
| `modified_real` | 3 | Rewrites of a real notice (the right answer is `altered`) |
| `paraphrases` | 4 | True in spirit but not a copy ("I heard the commission will not announce results by phone") |
| `pidgin_rumours` | 20 | Rumours in Nigerian Pidgin about the fictional commission |
| `honest_image` | 64 | Each notice as a picture: clean, WhatsApp-compressed (60% size, JPEG 30), phone photo of a screen (tilt, perspective, blur, noise, uneven light, JPEG 55) and low resolution (480 px), with and without a chat wrapper |
| `edits_image` | 92 | One-detail edits (up to three kinds per notice) as pictures, in every degradation, in a chat wrapper |
| `crops_image` | 16 | Cut-off pictures, clean and WhatsApp-compressed |

All text is English except the Pidgin rumours. The pictures are rendered by `eval/images.py` with
a built-in font, so every machine produces the same ones.

## Results of the run documented here

Run `2026-11-09T09:19:41+00:00` on the working tree on top of commit `612354c` (Tesseract 5.4,
102.6 seconds on the development laptop). Re-run `eval/run.py` for current numbers.

| Suite | Cases | Correct | Forged confirmed | False alarms | Honest not confirmed |
|---|---:|---:|---:|---:|---:|
| honest_text | 168 | 168 | 0 | 0 | 0 |
| edits_text | 131 | 131 | 0 | - | - |
| edits_text_wrapped | 131 | 131 | 0 | - | - |
| crops_text | 24 | 24 | 0 | - | - |
| invented | 15 | 15 | 0 | - | - |
| modified_real | 3 | 2 | 0 | - | - |
| paraphrases | 4 | 2 | 0 | - | - |
| pidgin_rumours | 20 | 20 | 0 | - | - |
| honest_image | 64 | 5 | 0 | 41 | 18 |
| edits_image | 92 | 85 | 0 | - | - |
| crops_image | 16 | 1 | 0 | - | - |
| **Total** | **668** | **584** | **0** | **41** | **18** |

- **Forged or invented copies confirmed as genuine: 0.** This is the number that must stay 0.
- Crops confirmed as complete: 0. Replaced notice confirmed without `superseded_by`: 0.

### Reading these results honestly

- **Text is solid on these fixtures, pictures are not.** All 168 honest text copies, including
  every wrapper, are confirmed. Only 5 of 64 honest pictures came out `confirmed`: 41 were called
  `altered` (false alarms) and 18 `cannot_confirm`. Only 1 of 16 cropped pictures came out
  `partial`; the rest were `altered` or `cannot_confirm`.
- **Why pictures miss.** The two reading passes are both Tesseract, so they make the same
  mistakes and then agree on them. For example both read "announces" as "4nnounces" or
  "nnounces", and the stray digit counts as a fact. A second, independent reader (for example Azure
  AI Vision Read, not implemented) would address this. Thresholds were deliberately not tuned
  before these results were reviewed.
- **The safe direction holds.** No edited picture was confirmed. 85 of 92 edited pictures were
  called `altered`; the other 7 were `cannot_confirm` (mostly a web address that one pass misread).
  Even when `altered` is correct, the listed changes can include reading noise next to, or instead
  of, the real edit.
- **Misses in the text suites.** `modified_real` 02 (a rewrite that shares too little wording to be
  recognised) came out `cannot_confirm`. Two paraphrases built from common words, or quoting one
  sentence of a notice, came out `altered` against a real notice instead of `cannot_confirm`:
  matching accepts scattered shared words, and a quoted sentence with a header word reads as an
  edited start. Changing that means changing a match threshold, so it is reported, not changed.
- **What the suites do not cover.** Real letterheads, stamps, signatures, real photographs, other
  fonts, real chat apps, languages other than English (the engine's word lists are English only),
  long documents, tables, and adversaries who know how the engine works.

Suites and the wrapper library are code (`eval/cases.py`, `eval/mutate.py`, `eval/wrappers.py`):
adding a case is the way to record a new failure.
