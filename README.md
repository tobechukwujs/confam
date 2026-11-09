# Confam

See [CLAUDE.md](CLAUDE.md), [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Status

- `packages/contract`: verdict JSON Schema, generated TypeScript and Pydantic types.
- `packages/i18n`: English strings only (other languages TODO, need native-speaker review).
- `services/engine`: a first rule-based comparison written from CLAUDE.md and ARCHITECTURE.md (NOT the legacy engine, which has not been ported). It finds the notice a copy belongs to, applies the meaning rules (dates, numbers, money, links, phones, negations), flags look-alike characters as unclear, detects crops as partial, checks links and phones against the record, flags replaced notices, and finds contradicted facts for not-official. No model is involved and no score is returned. English only. It has no measured accuracy: `eval/run.py` and the benchmark suites do not exist in this repo.
- `services/api`: `POST /v1/checks` (text), `GET /v1/verdicts/{code}`, in-memory store, fictional record from `fixtures/sec-sim`.
- `apps/web`: home, verdict page (`/v/[code]`) with all five verdicts plus "Real, but replaced", and the public record (`/record`, `/record/[id]`: exact signed text, who signed and when). "Open the original" links to our own record page, so it never breaks; "View source" shows only for a real https address.
- Languages: English, Nigerian Pidgin, Hausa, Yoruba, Igbo (`packages/i18n`). Everything except English is an **unreviewed AI draft** and shows a "Draft translation" label until a native speaker signs it off (`localeStatus`). The switch is in the cover; `?lang=` beats the `confam_lang` cookie; official notice text is never translated and keeps its own `lang`.
- Fixtures use only `*.example` addresses; a test fails the build if any government-style address appears anywhere in the repo.

## Run locally

```bash
pnpm install && uv sync
CONFAM_SEED_SAMPLES=1 uv run uvicorn --app-dir services/api main:app --reload
SHOW_SAMPLES=1 pnpm --filter web dev
uv run pytest && pnpm test && pnpm e2e
```

## Deploy (prepared, not deployed)

- Web: Vercel, Root Directory `apps/web`. Set `API_URL` (and `SHOW_SAMPLES` only for a labelled demo).
- API: Render, from `render.yaml`. Set `CONFAM_CORS_ORIGINS` to the Vercel URL.
- Variables are listed in `.env.example`.

## TODO

- Port the real Python engine into `services/engine`.
- `confam-ui/` prototype (not supplied): port `assets/marks.js` and `assets/engine.js`; marks here are first-pass shapes.
- Image checks (`{job_id}` flow), record and signing, marking desk, channels, worker, docker-compose, eval.
- `superseded_by` has no `url`, so "Send the current notice" shares the notice id and date only (contract change needed).
