# Limitations

What Confam does not do, or does not do well yet, as of the last commit. Read this before any
demo, application or claim. Where a number is mentioned it comes from `docs/EVAL.md`, which is
built on synthetic fictional fixtures.

## 1. Translations are unreviewed drafts

- Nigerian Pidgin, Hausa, Yoruba and Igbo were written by an AI assistant, **not by native
  speakers**. Every one is marked as a draft in the code (`localeStatus` in `packages/i18n`) and
  every non-English screen shows a "Draft translation" label in the page header.
- Hausa (hooked letters), Yoruba (dotted letters and tone marks) and Igbo (dotted letters and ṅ)
  render correctly in the interface font. That says nothing about whether the words, grammar,
  register or tone are right. Some may be wrong, awkward, or mean something else.
- Do not ship or demo these as reviewed. A native speaker must sign off each language before the
  label is removed (CLAUDE.md). The verdict words ("Altered", "Not official", "Cannot confirm")
  are the highest-risk strings: a wrong word changes what a voter does.
- Dates in the interface follow each language's formatting where the browser supports it; official
  notice text is never translated and keeps its own language.
- The engine's word lists (month names, weekdays, negations) are English only. A notice in Hausa,
  Yoruba, Igbo or Pidgin would not have its dates or negations recognised as facts.

## 2. Everything was tested on synthetic, fictional data

- All notices, replacements, signatures, rumours and pictures come from the invented "Simulated
  Electoral Commission". Nothing here has been tried on a real notice from a real body.
- The pictures are rendered by a script with one built-in font. **Real letterheads, stamps, seals,
  signatures, logos, tables, multi-column layouts and real photographs are untested.** A stamp
  over text, a coloured background or a decorative font will probably make reading worse.
- The earlier engine and its 165-case and 150-case suites mentioned in the project documents are
  **not in this repository** and were not ported. The engine in `services/engine` is a first
  rule-based one written from the written rules. Its behaviour is not the legacy engine's.
- There is no measured real-world accuracy and none may be claimed. The evaluation numbers
  (`docs/EVAL.md`) describe how the engine behaves on invented fixtures built to exercise it.
- The suites cannot cover an adversary who has read the code and designs a copy to slip past it.

## 3. "Not official" depends on the record being current

- `not_official` is returned when a copy states a different date, amount of money or web address
  for the same thing a **current** notice in the record talks about. It is only as right as the
  record.
- A genuine new notice that is not yet in the record, and that changes one of those facts, can
  be called `not_official`. A newer genuine notice that has not yet been signed into the record
  is exactly this case. The product rule is that an unknown notice is `cannot_confirm` /
  `not_in_record` (never "fake"), but a notice that contradicts a recorded fact is treated as
  contradicting it.
- The record in this repository is a JSON fixture. The two-person signing flow, the signed
  append-only log with hash chaining, and the database permissions (CLAUDE.md rules 5 and 6) are
  **not built**. The fixture loader refuses a notice that is not signed by two different people,
  which is a check on test data, not the real control. No watch loop exists to draft new entries.
- The conflict finder is conservative on purpose and will usually say `not_in_record` instead.

## 4. How copies are matched and compared (engine limits)

- **Wrapper text.** Text copied around a genuine notice (a "Forwarded" label, a sender, a
  timestamp, a caption above or below) is ignored when the notice's own first or last words line
  up next to it. Still counted: anything inside the notice, an edit to its first or last words,
  and any web address or money amount that is not in the record. A phone number that is not in
  the record counts only after the notice (a sender's number appears before it).
  Consequences: a trailing caption that comments on the notice ("Not valid.") is **not judged**,
  and a phone number placed before the notice is ignored.
- A cut-off notice followed by a caption cannot be told apart from an edited ending, so it is
  reported as altered or cannot-confirm, never partial and never confirmed. A notice cut off at
  the start, with extra words before the cut, has the same ambiguity.
- **Short paraphrases.** A short message built from common words, or quoting one sentence of a
  notice, can match a real notice and be reported as `altered` instead of `cannot_confirm`. The
  evaluation shows this. Fixing it means changing a match threshold, which has not been done.
- A rewrite of a real notice that shares too little wording is not recognised as related and
  comes back `cannot_confirm`.
- Look-alike characters (0/O, 1/l/I/i, 5/S, 8/B, 2/Z, 6/G, rn/m, vv/w, cl/d) give
  `cannot_confirm` with reason `unclear`. The set is generous on purpose: it withholds an answer
  rather than risk confirming a forgery, so a real one-letter change of that kind is not called
  `altered`.
- Equivalent forms are treated as the same fact (14th November and November 14, N500 and 500
  naira). Forms the tokenizer does not know are not: unusual date styles, amounts written in
  words, numbers written in words.
- Replacement is followed along a chain to the newest notice. The differences between the old and
  new notice are word-level; the label is the kind of fact ("Date"), not what it is about
  ("Registration deadline"), because the record has no such field.

## 5. Photo checks are weak and unproven on real photographs

- Photos need Tesseract. Without it the API says photo checks are unavailable and text checks
  keep working.
- **Two reading passes of the same engine make the same mistakes and then agree on them.** On the
  synthetic pictures only 5 of 64 honest pictures came out `confirmed`; most were called
  `altered` because both passes misread a word identically (for example "announces" read as
  "4nnounces"), and a digit inside a garbled word counts as a fact. Cropped pictures were
  mostly not recognised as partial (see `docs/EVAL.md` for the figures).
- The safe direction held in the evaluation: no edited picture was confirmed. But the list of
  changes shown with an `altered` picture can contain reading noise next to, or instead of, the
  real edit, so the marks can point at the wrong place.
- A second independent reader (for example Azure AI Vision Read) is a planned plug-in point and is
  **not implemented**. Reading thresholds were not tuned on purpose before the results were reviewed.
- A photo with no readable text returns `cannot_confirm` / `unclear` with no notice. A readable
  photo that matches nothing is `not_in_record`.
- Pictures are shrunk to 1600 pixels on the long side before reading, with the second pass
  enlarged to at most 2400. Memory on Render's free plan (512 MB) has **not been measured**.
- The marked photo is shown from the browser's own memory; after a reload or on a shared link the
  text sheet is shown instead. By design: the picture is never stored (rule 7).
- Image checks run one at a time in an in-process queue. Jobs are lost if the server restarts.
  The Redis and RQ worker in the architecture is not built.

## 6. Design rules that bend

- **Scale Rule** (the changed figure is the largest text on the screen). It holds for short
  figures, dates (the day is shown large and the month small) and amounts that fit. A long web
  address or a long value shrinks to 30 pixels so that it fits on one phone screen, which is
  **smaller than the verdict word**. The screen still shows the full value and the official
  correction.
- The pen marks (ring, strike, caret, tick, cross, brackets, question mark) are first-pass shapes
  drawn for this project. The prototype's `marks.js` and the `confam-ui` prototype were never
  supplied, so they were not ported.
- The "Copy switch" and the pen animation polish were cut for time. The pen draw animation is a
  simple stroke reveal.
- The One Screen Rule is checked at 360 by 640 for every verdict in all five languages. Phones
  that are smaller, or users who enlarge the system font, can push the action below the fold.

## 7. Operations

- Deploy files are prepared and **untested**: `render.yaml`, `services/api/Dockerfile` (there is
  no Docker on the development machine, so it has never been built) and `apps/web/vercel.json`.
- The check store, the rate limiter and the job queue are in memory in one process. Restarting
  the API loses checks, jobs and rate-limit counters. Rate limiting is per IP only.
- Samples at `/v/<code>` (fictional notices) are served when `CONFAM_SEED_SAMPLES=1`. They are
  labelled as samples on the page. Turn them off when a real record is loaded.
- No WhatsApp or Telegram channel, no verdict images, no marking desk, no partner API and no
  voice input exist yet. docker-compose, PostgreSQL and Redis are not set up.
- Domain, WhatsApp number, reviewer accounts and the name "Confam" (trademark unchecked) are
  placeholders.
