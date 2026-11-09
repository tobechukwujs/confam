# Confam

See [CLAUDE.md](CLAUDE.md), [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Status

- `packages/contract`: verdict JSON Schema, generated TypeScript and Pydantic types.
- `packages/i18n`: English strings only (other languages TODO, need native-speaker review).
- `services/engine`: **stub**. Exact match gives `confirmed` (with `superseded_by` when replaced); anything else gives `cannot_confirm` / `not_in_record`. The real engine is not ported yet.
- `services/api`: `POST /v1/checks` (text), `GET /v1/verdicts/{code}`, in-memory store, fictional record from `fixtures/sec-sim`.
- `apps/web`: home, verdict page (`/v/[code]`) with all five verdicts plus "Real, but replaced".

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
