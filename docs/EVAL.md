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

Run `2026-11-10T09:23:46+00:00` on the working tree on top of commit `5e6a6dc` (Tesseract 5.4,
engine as of the photo-slip, kind-ordering, placement-label and alignment changes; the
confidence gate is OFF). Re-run `eval/run.py` for current numbers.

| Suite | Cases | Correct | Forged confirmed | False alarms | Honest not confirmed |
|---|---:|---:|---:|---:|---:|
| honest_text | 168 | 168 | 0 | 0 | 0 |
| edits_text | 131 | 131 | 0 | - | - |
| edits_text_wrapped | 131 | 131 | 0 | - | - |
| crops_text | 24 | 24 | 0 | - | - |
| invented | 15 | 15 | 0 | - | - |
| modified_real | 3 | 1 | 0 | - | - |
| paraphrases | 4 | 4 | 0 | - | - |
| pidgin_rumours | 20 | 20 | 0 | - | - |
| honest_image | 64 | 8 | 0 | 30 | 26 |
| edits_image | 92 | 84 | 0 | - | - |
| crops_image | 16 | 3 | 0 | - | - |
| **Total** | **668** | **589** | **0** | **30** | **26** |

- **Forged or invented copies confirmed as genuine: 0.** This is the number that must stay 0.
- Crops confirmed as complete: 0. Replaced notice confirmed without `superseded_by`: 0.

Change since the previous documented run (same suites): honest pictures confirmed 5 to 8, false
alarms 41 to 30, not confirmed 18 to 26; edited pictures called `altered` 85 to 84 of 92 (none
confirmed); cropped pictures `partial` 1 to 3 of 16; paraphrases accepted 2 to 4 of 4; rewrites of
a real notice accepted 2 to 1 of 3 (the cost of the alignment rule below). Text honest copies
(168), edits (262) and crops (24) are unchanged.

### Photo false alarms: the confidence gate (not yet chosen)

`eval/confidence_table.py` reads every picture once and re-judges the same readings under a range
of thresholds. A change resting on a word that Tesseract read with less confidence than the
threshold (in either reading) becomes `cannot_confirm` / `unclear` instead of `altered`.
Confidence is kept inside the engine only: it is never returned, serialised or shown.

| Threshold | Honest confirmed | Honest false alarms | Honest withheld | Edits caught (altered) | Edits withheld | Forged confirmed |
|---|---:|---:|---:|---:|---:|---:|
| off | 8 | 30 | 26 | 84 | 8 | 0 |
| 30 | 8 | 23 | 33 | 82 | 10 | 0 |
| 40 | 8 | 20 | 36 | 80 | 12 | 0 |
| 50 | 8 | 18 | 38 | 77 | 15 | 0 |
| 60 | 8 | 16 | 40 | 73 | 19 | 0 |
| 65 | 8 | 14 | 42 | 69 | 23 | 0 |
| 70 | 8 | 11 | 45 | 69 | 23 | 0 |
| 75 | 8 | 8 | 48 | 68 | 24 | 0 |
| 80 | 8 | 6 | 50 | 67 | 25 | 0 |
| 85 | 8 | 6 | 50 | 62 | 30 | 0 |
| 90 | 8 | 6 | 50 | 61 | 31 | 0 |
| 95 | 8 | 0 | 56 | 32 | 60 | 0 |

(64 honest pictures, 92 edited pictures. "Withheld" means `cannot_confirm`. Forged confirmed is 0
at every threshold.) Confidence of the changes reported on honest pictures called `altered`:
median 65, highest 95. Confidence of the real-fact changes on edited pictures called `altered`:
median 93.5, highest 96.

How to read it:

- The gate never makes an honest picture `confirmed` (8 at every threshold); it only turns false
  alarms into `cannot_confirm`. More honest pictures confirmed needs better reading, not a gate.
- 6 false alarms survive any threshold up to 90: both passes read the same wrong word with high
  confidence. Only 95 removes them, and it also withholds 60 of 92 genuinely edited pictures
  (the real edits sit at a median 93.5, so 95 is right at their edge and fragile).
- 80 to 90 is the middle: 6 false alarms, 61 to 67 of 92 edits still caught.

The threshold is the product owner's choice and is not set. To choose, set
`CONFAM_MIN_WORD_CONFIDENCE` on the API (or change `DEFAULT_MIN_CONFIDENCE` in
`confam_engine/ocr/agree.py`).

### Paraphrases: how much of a notice a copy must line up with

`eval/alignment_sweep.py` shows how much of its notice each kind of case lines up with: real
edits 0.59 to 1.00 (median 0.97), rewrites of a real notice 0.36 to 0.58, paraphrases 0.22 to
0.33. A copy that lines up with less than **0.45** of a notice is no longer called `altered`.

| Threshold | Edits still altered | Paraphrases not altered | Rewrites accepted | Crops partial | Honest confirmed |
|---|---:|---:|---:|---:|---:|
| 0.0 (off) | 262 of 262 | 2 of 4 | 2 of 3 | 24 of 24 | 168 of 168 |
| 0.3 | 262 of 262 | 3 of 4 | 2 of 3 | 24 of 24 | 168 of 168 |
| 0.4 to 0.5 | 262 of 262 | 4 of 4 | 1 of 3 | 24 of 24 | 168 of 168 |
| 0.6 | 261 of 262 | 4 of 4 | 1 of 3 | 24 of 24 | 168 of 168 |
| 0.8 | 254 of 262 | 4 of 4 | 1 of 3 | 24 of 24 | 168 of 168 |

It has no effect on the picture suites. It costs one rewrite of a real notice (it lines up with
0.36 of it) and, above 0.5, begins to lose edits that drop a sentence.

### Reading these results honestly

- **Text is solid on these fixtures, pictures are not.** All 168 honest text copies, including
  every wrapper, are confirmed. Only 8 of 64 honest pictures came out `confirmed`: 30 were called
  `altered` (false alarms) and 26 `cannot_confirm`. Only 3 of 16 cropped pictures came out
  `partial`; the rest were `altered` or `cannot_confirm`.
- **Why pictures miss.** The two reading passes are both Tesseract, so they can make the same
  mistake and then agree on it. A second, independent reader (for example Azure AI Vision Read,
  not implemented) would address this. Look-alike slips inside words are now ignored on photos;
  other consistent misreads (for example "on" read as "0M" by both passes) still count.
- **The safe direction holds.** No edited picture was confirmed. 84 of 92 edited pictures were
  called `altered`; the other 8 were `cannot_confirm` (mostly a web address that one pass
  misread). Even when `altered` is right, the changes are now ordered link, money, phone, date,
  time, number, negation first, so the real edit is listed before reading noise.
- **Misses in the text suites.** One rewrite of a real notice lines up with too little of it and
  came back `cannot_confirm` (see the alignment table). No other text case missed.
- **What the suites do not cover.** Real letterheads, stamps, signatures, real photographs, other
  fonts, real chat apps, languages other than English (the engine's word lists are English only),
  long documents, tables, and adversaries who know how the engine works.

Suites and the wrapper library are code (`eval/cases.py`, `eval/mutate.py`, `eval/wrappers.py`):
adding a case is the way to record a new failure.