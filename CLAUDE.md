# Confam

Confam checks a forwarded "official" election notice against a signed record of
public notices and replies, in the sender's language, with what is true, what
changed and where the original is. It marks a notice the way a teacher marks a
script: the wrong figure is ringed in red and the right one is written beside it.

Built for the #AI4Elections Hackathon (Track 1, provenance for official
communications). Applications close 12 Nov 2026, 11:59 pm WAT. Build sprint ends
13 Dec 2026. Demo day is 15–16 Dec 2026.

## Read these first

| File | What it is | When to read |
| --- | --- | --- |
| `PRODUCT.md` | Users, purpose, verdicts, red lines | Before any product or copy change |
| `DESIGN.md` | Tokens, type, layout, marks, motion, do's and don'ts | Before any UI change |
| `docs/ARCHITECTURE.md` | System diagram, contract, data model, pipeline | Before any backend change |
| `confam-ui/screens.html` | The static prototype, every screen and state | When building a screen |
| `docs/ui-demo/` | Phone and desktop artboards (Home, Altered, Replaced, Spread) | When building a screen |

If these files disagree, PRODUCT.md wins on behaviour and DESIGN.md wins on look.
Ask before resolving a conflict that changes what a user sees.

## Stack

- `apps/web`: Next.js 15, App Router, TypeScript (`strict: true`), plain CSS with
  tokens. No UI kit, no Tailwind, no CSS-in-JS.
- `services/api`: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic.
- `services/engine`: the Python verification engine (already tested; keep its behaviour).
- `services/worker`: RQ worker for OCR jobs, verdict images and the watch loop.
- PostgreSQL 16, Redis 7.
- `packages/contract`: verdict JSON Schema. It generates TypeScript types and Pydantic models.
- `packages/i18n`: reply and UI strings in English, Pidgin, Hausa, Yoruba, Igbo.
- Package managers: pnpm (TypeScript), uv (Python).

## Commands

```bash
docker compose up                  # postgres, redis, api, worker, web
pnpm --filter web dev              # web only, http://localhost:3000
uv run uvicorn --app-dir services/api main:app --reload   # API, http://localhost:8000
uv run rq worker checks            # OCR and verdict-image jobs
pnpm contract:gen                  # regenerate TS + Pydantic from the schema
pnpm contract:check                # fail if generated files are stale or hand-edited
pnpm contract:tsc                  # type-check the generated TS against a sample
pnpm test                          # web unit tests (Vitest)
pnpm e2e                           # Playwright, phone viewport 360x640
uv run pytest                      # api, engine, worker
uv run python eval/run.py          # benchmark: 165-case and 150-case suites
uv run alembic upgrade head
```

If a command here does not exist yet, create it as part of the task that needs it
and update this section.

## Repo layout

```
apps/web/
  app/(public)/page.tsx            Home: check a notice
  app/(public)/check/[job]/        Reading screen (follows real engine progress)
  app/(public)/v/[code]/           Verdict page (public, shareable, verifies a reply)
  app/(public)/record/             Public official record
  app/(public)/simulation/         WhatsApp simulation for judges
  app/desk/                        Marking desk (login required)
  components/marks/                Mark, Ring, Strike, Caret, Tick, Cross, Pencil, Bracket
  components/sheet/                Sheet, Pin, CopySwitch, Receipt
  components/verdict/              VerdictLayout and one view per verdict
  lib/api.ts                       Typed client from packages/contract
  styles/tokens.css                DESIGN.md tokens as CSS custom properties
services/api/      routers/, channels/, record/
services/engine/   ocr/, compare/, explain/
services/worker/
packages/contract/ packages/i18n/
fixtures/sec-sim/  Fictional commission notices and attack cases
eval/              Benchmark runner and results
infra/             docker-compose, deploy config
```

## Rules that must never break

Each rule has a test. Never weaken or delete one of these tests to make a build pass.

1. **"Not in our record" is never "fake".** No match and no conflicting official
   fact returns `cannot_confirm` with reason `not_in_record`. Never `not_official`.
2. **Replaced notices are flagged.** A match to a superseded notice sets
   `superseded_by`, including on cache hits. The UI shows "Real, but replaced",
   never a plain green tick.
3. **Rules decide verdicts.** A language model may only extract text or a claim
   from a typed rumour. Its output goes back through the rule-based comparison.
   No model-written fact ever reaches a user.
4. **No confidence scores.** No percentages, grades or probability numbers
   anywhere in the UI, replies, images or API responses.
5. **Two people sign every record entry.** The same reviewer cannot sign a notice
   twice. Enforce it in the API and with a database unique constraint.
6. **The record log is append-only.** Each row hashes the previous one. The app's
   database role has no UPDATE or DELETE on `record_log`.
7. **No personal data kept.** Images are processed in memory and dropped. Phone
   numbers are stored only as salted hashes. Checks expire after 30 days.
8. **Public data only.** Never call, scrape or probe INEC systems (BVAS, IReV,
   the voter register) or any non-public endpoint.
9. **Safe fixtures.** Test and demo notices come only from the fictional
   "Simulated Electoral Commission". Never create a realistic fake INEC document.
10. **Never look like INEC or a party.** No INEC logo, colours or seal. The line
    "Independent checker. Not INEC or any party." appears on every public page
    and every verdict image.
11. **Never invent numbers.** Only quote benchmark figures produced by
    `eval/run.py` in the same session. Do not invent users, partners, endorsements
    or accuracy figures in code, copy or docs.

## Verdict contract

The schema lives in `packages/contract/verdict.schema.json`. Change it there,
then run `pnpm contract:gen`. Never hand-edit the generated types.

```json
{
  "code": "K7Q2M9XA",
  "verdict": "confirmed | altered | not_official | partial | cannot_confirm",
  "reason": "unclear | not_in_record | no_fact | line_missing | null",
  "lang": "en | pcm | ha | yo | ig",
  "checked_at": "2026-11-05T14:02:00+01:00",
  "record_as_of": "2026-11-05T13:40:00+01:00",
  "notice": { "id": "SEC-2026-114", "title": "...", "published": "2026-09-03", "url": "..." },
  "superseded_by": { "id": "SEC-2026-140", "published": "2026-10-09" },
  "changes": [
    { "op": "replace", "kind": "date", "official": "14th", "copy": "15th",
      "box": [0.21, 0.46, 0.08, 0.03] }
  ],
  "conflicts": []
}
```

- `code`: 8 characters, alphabet `23456789ABCDEFGHJKMNPQRSTUVWXYZ` (no 0, O, 1, I, L). Stored and sent as 8 characters with no hyphen; `XXXX-XXXX` is presentation only.
- `superseded_by`: only on `confirmed`; `null` otherwise.
- `changes[].box`: x, y, width, height from OCR, each 0–1. Needed to place a mark on a photo.
- `conflicts[]`: only on `not_official`: `kind` (date, link, money), `copy`, `official`, `quote`.

### Verdict to screen

| Result | Verdict word | Mark (DESIGN.md) | Main action |
| --- | --- | --- | --- |
| `confirmed` | Confirmed | Large green tick | Share it with this check |
| `confirmed` + `superseded_by` | Real, but replaced | Pencil brackets, new value in pencil hand | Send the current notice |
| `altered` / replace | Altered | Red ring, official value handwritten above | Send the correct one |
| `altered` / insert | Altered | Red strike through added words | Send the correct one |
| `altered` / delete | Altered | Red caret, missing word handwritten | Send the correct one |
| `not_official` | Not official | Red cross, claim struck, official fact handwritten | Send the correct one |
| `partial` | Partial | Pencil bracket around what is visible | See the whole notice |
| `cannot_confirm` | Cannot confirm | Pencil ring and question mark, or none | Send a clearer photo / Check again later |

## Frontend

### Design system

Tokens go in `apps/web/styles/tokens.css` as custom properties, named after DESIGN.md:

```css
:root {
  --biro-blue: #1b2e96; --cover-deep: #14226f; --cover-line: #5766c2; --cover-text: #e9ecfb;
  --red-biro: #c40d23; --green-biro: #0a6b42; --pencil: #555b65;
  --print-black: #14171c; --soft-print: #4a525e;
  --page: #f6f9fb; --sheet-white: #ffffff; --feint-rule: #d3deea; --page-edge: #a9bcd2;
  --wash: #e6edf4; --selected-tint: #dfe5f6;
  --line: 30px; --double-line: 60px;
  --margin-phone: 38px; --gutter-phone: 14px; --margin-wide: 60px; --gutter-wide: 40px;
  --radius-sm: 3px;
}
```

- **Fonts:** Andika (400, 700) for all interface text. Playwrite NG Modern only for
  handwritten corrections; it lacks Hausa and some Igbo letters, so never use it
  for interface copy. Arial for the forwarded notice. Self-host with `next/font`.
- **Grid:** every vertical measure is a multiple of the 30px line. Body is 18/30.
  Controls are 60px tall. Text baselines sit on the rules.
- **Layout:** one page below 900px, left margin 38px for marks and pins. From
  900px a two-page spread up to 1280px: answer left, proof right, two staples at the fold.
- **Colour:** red only where a copy differs from the record. Form errors are bold
  print-black, never red. Green only for a match. Pencil only when unsure.
- **Flat:** no gradients, grain, embossing, curled corners, stamps, shields,
  scanners or AI sparkles. Only the notice sheet has a shadow.
- **Motion:** only the pen moves, about 1.5 s when a verdict lands (ring or tick
  drawn, correction written left to right). Respect `prefers-reduced-motion`.
  All other transitions 160 ms.

### Components

- `Mark` draws each mark to fit its target (port `assets/marks.js` from the
  prototype). Marks ride above the notice and never edit its text.
- Every numbered `Pin` on the sheet pairs with a row in the "What changed" list,
  so screen readers get the same information.
- `CopySwitch` swaps only the differing words between Your copy and Official and
  removes the marks, so the eye sees nothing else moved.
- `Receipt` shows official notice id, published date, checked time, record as of,
  check code, "Open the original" and "Verify this check".

### Quality bar

- **One Screen Rule:** at 360×640 the verdict word, marked figure, sentence,
  instruction and main action fit without scrolling. Playwright checks this for
  every verdict.
- **Scale Rule:** the changed figure is the largest text on the verdict screen.
- First load under 200 KB compressed including fonts, so it works on slow 3G.
- WCAG 2.2 AA. Tap targets at least 44px. Real `<button>`, `<a>`, `<label>`.
  A verdict never relies on colour alone: the word and the shape carry it too.
- Set `lang` on quoted text whose language differs from the interface.
- Hausa ɓ ɗ ƙ, Yoruba ẹ ọ ṣ with tone marks, and Igbo ị ọ ụ ṅ must render correctly.
- Prefer Server Components. Add `"use client"` only for the switch, marks
  animation, uploads and voice.

### Strings

All user-facing text comes from `packages/i18n`. Never hard-code copy in
components. Non-English strings are unreviewed drafts until a native speaker signs
them off. Show a "draft translation" label on non-English web screens until then.
Official text is always quoted word for word in its own language.

## Backend

- Routers: `checks`, `verdicts`, `record`, `desk`, `channels` (WhatsApp, Telegram), `partner`.
- `POST /v1/checks` returns a verdict for text, or `{job_id}` for images. The web
  polls `GET /v1/checks/{job_id}` and shows real OCR progress.
- Every channel calls the same check service, so verdicts are identical everywhere.
- Webhooks verify signatures (WhatsApp) and secret tokens (Telegram).
- Rate-limit per hashed sender and per IP in Redis.
- Pipeline order: cache, two OCR passes, find notice, compare, meaning rules,
  link and phone allow-list, supersession, explain, render. The first step to
  decide ends the run. Details in `docs/ARCHITECTURE.md`.
- Verdict images are 1080×1350, rendered server-side from a card template with
  headless Chrome. Each carries the verdict, check code, checked time, record-as-of
  time, verification link and the independence line.
- WhatsApp: mark as read and show typing while the job runs; send one image plus
  caption per verdict. Typing indicators, image-plus-button layouts and the
  reported ₦14 reply charge are unverified. Check Meta's current docs before relying on them.
- First contact asks for a language with five buttons and stores it against the
  hashed number in Redis for 30 days. A typed message in another language overrides it.

## Testing and evaluation

- Write a failing test first for any engine, record or contract change.
- Engine changes must run `eval/run.py`. Report correct verdicts, forged notices
  confirmed as genuine (must stay 0) and false alarms on honest copies.
- Regression tests that must always exist:
  - no match and no conflict gives `cannot_confirm` / `not_in_record`
  - a replaced notice gives `superseded_by`, including from cache
  - a second signature by the same reviewer is refused
  - a tampered log row breaks the hash chain
  - no table has an image or raw phone column
  - every verdict passes the 360×640 One Screen check

## How to work in this repo

- Plan before editing anything that touches more than one package, and show the plan.
- Keep changes small and focused. One concern per commit.
- Ask before adding a dependency, changing the contract, or changing a rule above.
- Do not commit, push or open a PR unless asked.
- Never put secrets in code. Use `.env` (git-ignored) and document new variables in `.env.example`.
- If something in this file is out of date, say so and propose the edit.

## Current milestone

**Now to 12 Nov: application link.**
1. Monorepo, contract package, docker-compose.
2. Engine behind `POST /v1/checks` for pasted text.
3. Home and all verdict screens in Next.js with marks, deployed with a public URL.

Then: 13–27 Nov photo checks, signed record, marking desk, 50–100 public notices,
native-speaker review. 28 Nov–13 Dec WhatsApp and Telegram, verdict images, watch
loop, spread monitor, benchmark rerun, model card, 3-minute video.

If time runs short, cut voice input first, then the partner API. Keep the watch
loop and supersession.

## Placeholders to replace before going live

- `confam.example` domain, WhatsApp number, reviewer accounts.
- Fictional commission data in fixtures, replaced by real public notices through the two-person flow.
- Non-English strings, until native-speaker review.
- The name "Confam" is a working name; trademark not checked.
