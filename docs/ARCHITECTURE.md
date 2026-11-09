# Confam — System Architecture

Nov 7, 2026 · @Tobechukwu

## Overview

Confam is a Next.js (TypeScript) web app in front of two FastAPI services: a public API and a Python verification engine. The split keeps the slow, CPU-heavy OCR work off the request path and lets the engine you already tested stay in Python.

The architecture enforces the product rules in code, not just in the interface:

- **Rules decide verdicts.** The engine returns one of five verdicts from deterministic comparison. Language models only extract text or claims; they never write a fact a user sees.
- **"Not in our record" is never "fake".** A notice with no match and no conflicting fact returns `cannot_confirm` with reason `not_in_record`. This is a server-side invariant with its own test.
- **Two people sign every record entry.** The API refuses a second signature from the first signer, and every change is appended to a hash-chained log.
- **Replaced notices are flagged.** A genuine notice that has since been superseded returns `confirmed` with `superseded_by` set, never a plain green tick.
- **Nothing personal is kept.** Images are processed in memory and dropped; phone numbers are stored only as salted hashes; checks keep notice-level facts only.
- **Public data only.** Confam reads public official notices. It never touches BVAS, IReV, the voter register or any INEC system.

## System diagram

Text description of the components and what calls what (the exported diagram did not survive).

- **Channels** (five): the web checker, WhatsApp (Cloud API webhook), Telegram (bot webhook), the partner API (API key) and voice notes (transcribed, then sent through one of the other channels). Each one calls the same public API, `POST /v1/checks`.
- **Public API** (FastAPI, `services/api`): receives every check, rate-limits per hashed sender and per IP, serves the public verification page data (`GET /v1/verdicts/{code}`), the signed record and the marking-desk endpoints. For text it returns a verdict directly; for images it returns a `job_id` and the caller polls.
- **Redis**: holds the job queue, the result cache and rate-limit counters. The API writes jobs to it and reads cached results from it.
- **Worker** (RQ, `services/worker`): takes jobs from Redis and runs the slow work off the request path: OCR, verdict images and the watch loop. It calls the engine.
- **Engine** (Python, `services/engine`): rule-based comparison. It reads signed notices from PostgreSQL and returns one of five verdicts. A language model may be used only to extract a claim from a typed rumour, and its output goes back through the rule-based comparison.
- **PostgreSQL**: holds notices, signatures, the append-only `record_log`, checks and reviewers. Only signed notices can produce a verdict.
- **Marking desk** (`apps/web/app/desk`, login required): reviewers call the API to sign draft record entries. The watch loop in the worker also proposes drafts through the API; a person signs them, twice, before the engine can use them.

Every channel calls the same API, the worker runs the slow OCR off the request path, and only signed notices in PostgreSQL can produce a verdict.

## Repo layout

One monorepo with pnpm workspaces for TypeScript and uv for Python, so Claude Code can see the whole system at once.

```
confam/
  apps/
    web/                 Next.js 15 (App Router, TypeScript)
      app/(public)/      check, verdict/[code], record, simulation
      app/desk/          marking desk (auth required)
      components/marks/  Ink marks: ring, strike, caret, tick, cross, pencil
      lib/api.ts         typed client generated from OpenAPI
      styles/tokens.css  DESIGN.md tokens
  services/
    api/                 FastAPI: public API, record, desk, webhooks
      routers/           checks, record, desk, channels, verify_page
      channels/          whatsapp.py, telegram.py, templates/
      record/            models, signing, hash-chained log
    engine/              Python verification engine (your tested code)
      ocr/               two independent OCR passes
      compare/           diff, meaning rules, supersession
      explain/           conflict finder for invented notices
    worker/              RQ worker: OCR jobs, verdict images, watch loop
  packages/
    contract/            verdict JSON Schema -> TS types + Pydantic models
    i18n/                reply templates in 5 languages (reviewed drafts)
  fixtures/sec-sim/      fictional commission notices and attack cases
  eval/                  benchmark runner (165-case + 150-case suites)
  infra/                 docker-compose: postgres, redis, api, worker, web
  CLAUDE.md
```

The verdict contract lives once, in `packages/contract` as JSON Schema, and generates both the TypeScript types and the Pydantic models. That stops the front end and engine drifting apart.

## Verdict contract and API

The contract extends the handoff's shape with three fields: `superseded_by`, a longer check code, and `record_as_of`. The check code is stored and sent as 8 characters with no hyphen; `XXXX-XXXX` is presentation only. The authoritative schema is `packages/contract/verdict.schema.json`.

```json
{
  "code": "K7Q2M9XA",
  "verdict": "confirmed | altered | not_official | partial | cannot_confirm",
  "reason": "unclear | not_in_record | no_fact | line_missing | null",
  "lang": "en | pcm | ha | yo | ig",
  "checked_at": "2026-11-05T14:02:00+01:00",
  "record_as_of": "2026-11-05T13:40:00+01:00",
  "notice": { "id": "SEC-2026-114", "title": "...", "published": "2026-09-03", "url": "..." },
  "superseded_by": {
    "id": "SEC-2026-140", "published": "2026-10-09", "url": "...", "title": "...",
    "changes": [ { "op": "replace", "kind": "date", "official": "28th November", "copy": "14th November" } ]
  },
  "changes": [ { "op": "replace", "kind": "date", "official": "14th", "copy": "15th", "box": [0.21, 0.46, 0.08, 0.03] } ],
  "conflicts": []
}
```

| Method | Path | Purpose | Auth |
| --- | --- | --- | --- |
| POST | /v1/checks | Submit text or an image; returns `{job_id}` for images, a verdict for text | Rate-limited |
| GET | /v1/checks/{job\_id} | Poll a job; streams OCR stage for the reading screen | Rate-limited |
| GET | /v1/verdicts/{code} | Public verification page data | Public |
| GET | /v1/record | Search the signed official record | Public |
| POST | /v1/record/drafts | Watch loop or reviewer proposes an entry | Reviewer, worker |
| POST | /v1/record/drafts/{id}/sign | First or second signature; same person refused | Reviewer |
| POST | /v1/channels/whatsapp | WhatsApp Cloud API webhook | Signature check |
| POST | /v1/channels/telegram | Telegram bot webhook | Secret token |
| POST | /v1/partner/checks | Tipline partners (CDD, Dubawa, Run-Am) | API key |

Check codes are 8 characters from a 31-symbol alphabet with no look-alikes (no 0/O, 1/I/L), about 850 billion combinations, so they cannot be enumerated.

## Data model

PostgreSQL holds five tables; Redis holds the job queue, the result cache and rate limits.

| Table | Key fields | Notes |
| --- | --- | --- |
| notices | id, title, body\_text, facts (jsonb: dates, money, links, phones), published, source\_url, superseded\_by, status | Only `status = signed` entries are used by the engine |
| signatures | notice\_id, reviewer\_id, role (first, second), signed\_at | Unique on (notice\_id, reviewer\_id): one person cannot sign twice |
| record\_log | seq, entry (jsonb), prev\_hash, hash, signed\_by | Append-only; each row hashes the previous one; no UPDATE or DELETE grants |
| checks | code, verdict, reason, notice\_id, changes, lang, content\_hash, checked\_at, expires\_at | No image, no phone number; content\_hash serves the cache and the spread monitor |
| reviewers | id, name, role, auth\_id | Desk logins only |

The spread monitor counts `checks` by `content_hash` and hour. It has no location field, because Nigerian mobile numbers carry no region and inferring one would breach the privacy rules.

Channel sessions (chosen language per user) live in Redis, keyed by a salted hash of the phone number, with a 30-day expiry.

## Verification pipeline

Each check runs these steps in the worker, and the first one to decide ends the run.

1. **Cache.** Hash the image (perceptual) and the text. A hit returns the stored verdict at once, re-checked only for supersession.
2. **Read twice.** Two independent OCR passes produce two readings with word boxes.
3. **Find the notice.** Retrieve candidate notices from the signed record by title and key facts.
4. **Compare.** Diff each reading against the official text. A difference counts only when both readings show it at the same spot.
5. **Apply meaning rules.** Digits, dates, links, money and negations always count. A single look-alike character returns `cannot_confirm` with reason `unclear`.
6. **Check links and numbers.** Any web address or phone number not on the record's allow-list is reported as a change.
7. **Check supersession.** A match to a replaced notice sets `superseded_by`.
8. **Explain.** With no match, look for an official fact that contradicts the copy. A conflict gives `not_official`; no conflict gives `cannot_confirm` with `not_in_record`.
9. **Render.** Fill the reviewed template in the user's language and generate the 1080×1350 verdict image with the code, check time and independence line.

An LLM may be used in step 8 only to pull a claim out of a typed rumour. Its output goes back through steps 4 to 7, so it never decides the verdict.

## Channels

Every channel calls the same `/v1/checks` endpoint, so the verdict is identical wherever the question comes from.

| Channel | How it connects | Notes |
| --- | --- | --- |
| Web checker | Next.js server actions call the API | Works on slow 3G; first load under 200 KB |
| WhatsApp | Cloud API webhook into FastAPI | Mark as read and show typing while the job runs; one image plus caption per verdict |
| Telegram | Bot API webhook | Free fallback; same templates |
| Partner API | API key, JSON verdict | For tiplines; unmatched items go on to their fact-checkers |

On first contact the bot asks for a language with five buttons and remembers the choice. Any typed message in another language overrides it, because a forwarded notice is usually English and says nothing about the reader.

Voice notes are transcribed, read back with Yes and No buttons, and checked only after a Yes.

WhatsApp typing indicators, image-plus-button layouts and the reported ₦14 reply charge are unverified. Confirm them against Meta's current documentation before the build sprint.

## Security, privacy and safeguards

Each risk maps to a control that lives in code and a test that proves it.

| Risk | Control | Test |
| --- | --- | --- |
| Someone poisons the record | Two signatures from different reviewers; hash-chained log; database role with no UPDATE or DELETE on the log | Second signature by first signer is refused; tampered log row breaks the chain |
| A genuine new notice is called fake | No match and no conflict always returns `cannot_confirm` / `not_in_record` | Dedicated regression test |
| An old notice gets a green tick | `superseded_by` checked on every match, including cache hits | Replaced fixture returns the replaced variant |
| A Confam reply is forged | Verdict image carries the code, check time and verification link; codes are 8 characters | Unknown code returns 404 |
| Personal data leaks | Images held in memory only; salted phone hashes; checks expire after 30 days | No image or phone field in any table |
| Abuse and flooding | Rate limits per hashed sender and per IP; webhook signature checks | Load test on the worker queue |
| Impersonating INEC | Independence line on every page and image; no INEC colours or logo | Visual review checklist |

All attack fixtures come from the fictional Simulated Electoral Commission. The repo never contains a realistic fake INEC document.

## Build order

Ship a hosted, working text checker before applications close on 12 November, then grow it in the order that protects the demo.

1. **Now to 12 Nov: application link.**
   - Monorepo, contract package, docker-compose.
   - Engine behind `POST /v1/checks` for pasted text.
   - Next.js check page and the five verdict screens with marks, deployed.
2. **13 to 27 Nov: real record.**
   - OCR jobs with word boxes; photo checks on the web.
   - Notices, signatures and log tables; marking desk with logins.
   - Load 50 to 100 public INEC notices through the two-person flow; native-speaker review of templates.
3. **28 Nov to 13 Dec: channels and proof.**
   - WhatsApp and Telegram bots; verdict image generation.
   - Watch loop drafting record entries; spread monitor.
   - Benchmark rerun, model card, safety documents, 3-minute video.
4. **15 to 16 Dec: demo day.** QR code on the table so judges can forward samples from their own phones.

If time runs short, cut voice input first, then the partner API. Keep the watch loop and supersession: without them, real notices get wrong answers.
