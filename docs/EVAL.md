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

Run `2026-11-10T09:33:58+00:00` on the working tree on top of commit `c91d503` (Tesseract 5.4, the
confidence gate **ON at 95**, the default). Re-run `eval/run.py` for current numbers.

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
| honest_image | 64 | 8 | 0 | 0 | 56 |
| edits_image | 92 | 32 | 0 | - | - |
| crops_image | 16 | 3 | 0 | - | - |
| **Total** | **668** | **537** | **0** | **0** | **56** |

- **Forged or invented copies confirmed as genuine: 0.** This is the number that must stay 0.
- **False alarms on honest copies: 0** (text and pictures).
- Crops confirmed as complete: 0. Replaced notice confirmed without `superseded_by`: 0.

### The decision: confidence gate at 95, and what it costs

Decision (product owner): a false "altered" on a genuine notice is the worst error we can make; a
missed edit becomes `cannot_confirm` and is never confirmed. So a change on a word that the
reader was less than 95 sure of, in either reading, is `cannot_confirm`, never `altered`.
Confidence is kept inside the engine only: it is never returned, serialised or shown.

| | Gate off | Gate 95 |
|---|---:|---:|
| Honest pictures confirmed | 8 of 64 | 8 of 64 |
| Honest pictures called `altered` (false alarms) | 30 | **0** |
| Honest pictures `cannot_confirm` | 26 | 56 |
| Edited pictures called `altered` | 84 of 92 | **32 of 92** |
| Edited pictures `cannot_confirm` | 8 | 60 |
| Edited pictures confirmed (forged) | 0 | 0 |
| Cropped pictures `partial` | 3 of 16 | 3 of 16 |

Edited pictures called `altered` at 95, by kind of edit:

| Edit | Altered | Withheld |
|---|---:|---:|
| a date's day | 7 of 20 | 13 |
| a date's month | 13 of 20 | 7 |
| a number | 3 of 4 | 1 |
| a removed negation | 7 of 12 | 5 |
| a time | 2 of 12 | 10 |
| **a web address** | **0 of 16** | 16 |
| **a phone number** | **0 of 8** | 8 |

**At 95, a changed web address or phone number on a photo is never called altered.** Tesseract
gives web addresses a confidence of about 84 to 91 at every picture size we tried (22 to 72 point
text, three picture widths), so they never pass a gate of 95. Those photos come out "Cannot
confirm", never "Confirmed". The same edit pasted as text is reported correctly.

How the gate behaves at other thresholds (`eval/confidence_table.py`, 64 honest and 92 edited
pictures; forged confirmed is 0 in every row):

| Threshold | Honest false alarms | Honest withheld | Edits altered | Edits withheld |
|---|---:|---:|---:|---:|
| off | 30 | 26 | 84 | 8 |
| 70 | 11 | 45 | 69 | 23 |
| 80 | 6 | 50 | 67 | 25 |
| 90 | 6 | 50 | 61 | 31 |
| **95** | **0** | 56 | **32** | 60 |

The gate never makes an honest picture `confirmed`; it only turns false alarms into
`cannot_confirm`. 95 sits right at the edge of the real edits (their median confidence is 93.5,
highest 96), which is why it removes the false alarms and also most of the catches.

### The six honest pictures that still false-alarm at 90

`eval/false_alarm_report.py` (full output in `eval/results/false_alarms_gate90.txt`). All of them
vanish at 95. Both passes read the same thing, with confidence 90 to 95:

| Picture | Official | Both passes read | Pattern |
|---|---|---|---|
| E-003 phone | `2:00 pm` | `2:00` and a lone `P` | the `m` was lost, leaving a time with no am/pm and a stray letter |
| E-005 phone + wrapper | `4:00 pm` | `4:00` | the `pm` was lost |
| E-006 clean | `or`, and `on` | `OF`, and nothing | `r` read as `F`; a short word dropped |
| E-006 clean + wrapper | `or`, and `on` | `OF`, and nothing | same |
| E-006 WhatsApp | `on` | nothing | a short word dropped |
| E-006 WhatsApp + wrapper | `or` | `OF` | `r` read as `F` |

None of them is a look-alike pattern. The pairs already in the slip rule (rn/m, cl/d, 0/O, 1/l/I,
5/S, 8/B and so on) do not apply. Trying extra pairs (M/N, u/v, e/c, h/b) against the stored
readings removed no false alarm, and a/o made it worse (6 to 9); forged confirmed stayed 0.

**Proposals (not applied; each needs your decision):**

1. *Dropped short words.* Ignore, on photos, a word of one or two letters (other than a negation)
   that both passes omitted. On its own this would clear 1 of the 6 (the E-006 WhatsApp picture,
   which only misses `on`); the two E-006 clean pictures would still have the `OF` misread.
2. *am/pm fragments.* On photos, treat a lone `A`, `P`, `AM` or `PM` next to a time as that
   time's meridiem. This would clear the two time pictures (E-003 and E-005): 2 of the 6.
3. *`r` read as `F` in two-letter words* is a single observed case; not worth a rule.
4. *A lower floor for web addresses and phone numbers.* Keep 95 for everything else but use a lower
   floor for these two kinds. Measured on the stored readings, with the gate at 95 for the rest:

| Link/phone floor | Honest false alarms | Link + phone edits caught (of 24) | Edits altered (of 92) | Forged confirmed |
|---|---:|---:|---:|---:|
| none (today) | 0 | 0 | 32 | 0 |
| 90 | 0 | 4 | 36 | 0 |
| 85 | 0 | 5 | 37 | 0 |
| 80 | 0 | 9 | 41 | 0 |

None of these changes the contract.

### Paraphrases: how much of a notice a copy must line up with

`eval/alignment_sweep.py` shows how much of its notice each kind of case lines up with: real
edits 0.59 to 1.00 (median 0.97), rewrites of a real notice 0.36 to 0.58, paraphrases 0.22 to
0.33. A copy that lines up with less than **0.45** of a notice is not called `altered`.

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

- **Text is solid on these fixtures, pictures are cautious.** All 168 honest text copies, including
  every wrapper, are confirmed. With the gate at 95 no honest picture is called altered, but only 8
  of 64 are confirmed and only 32 of 92 edited pictures are called altered (60 are "Cannot
  confirm"). Only 3 of 16 cropped pictures came out `partial`.
- **Why pictures miss.** The two reading passes are both Tesseract, so they can make the same
  mistake and then agree on it. A second, independent reader (for example Azure AI Vision Read,
  not implemented) would address this.
- **The safe direction holds.** No edited picture was confirmed. A missed edit is a
  `cannot_confirm`.
- **Misses in the text suites.** One rewrite of a real notice lines up with too little of it and
  came back `cannot_confirm`. No other text case missed.
- **What the suites do not cover.** Real letterheads, stamps, signatures, real photographs, other
  fonts, real chat apps, languages other than English (the engine's word lists are English only),
  long documents, tables, and adversaries who know how the engine works.

Suites and the wrapper library are code (`eval/cases.py`, `eval/mutate.py`, `eval/wrappers.py`):
adding a case is the way to record a new failure.