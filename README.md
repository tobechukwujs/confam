# Confam

See [CLAUDE.md](CLAUDE.md), [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Status

- `packages/contract`: verdict JSON Schema, generated TypeScript and Pydantic types.
- `packages/i18n`: English plus four unreviewed draft languages (see Languages below).
- `services/engine`: a first rule-based comparison written from CLAUDE.md and ARCHITECTURE.md (NOT the legacy engine, which has not been ported). It finds the notice a copy belongs to, applies the meaning rules (dates, numbers, money, links, phones, negations), flags look-alike characters as unclear, detects crops as partial, checks links and phones against the record, flags replaced notices, and finds contradicted facts for not-official. No model is involved and no score is returned. English only. It has no measured accuracy: `eval/run.py` and the benchmark suites do not exist in this repo.
- `services/api`: `POST /v1/checks` (JSON text, or a raw image body for photos which returns `{job_id}`), `GET /v1/checks/{job_id}`, `GET /v1/verdicts/{code}`, `GET /v1/record[/{id}]`, in-memory store, fictional record from `fixtures/sec-sim`.
- Photo checks: the browser shrinks the picture and sends it straight to the API; the server reads it in memory only (never written to disk, dropped when the job ends), twice with different preparations of Tesseract, and a change counts only if both readings show it at the same spot. A disagreement on a fact or a look-alike character gives Cannot confirm, never Confirmed or Altered. The marked photo is shown from the browser's own memory; after a reload or on a shared link the text sheet is shown instead. A second engine (for example Azure AI Vision Read) can be plugged in as the second reader (`confam_engine.ocr.types.Reader`); that is not implemented.
- `apps/web`: home, verdict page (`/v/[code]`) with all five verdicts plus "Real, but replaced", and the public record (`/record`, `/record/[id]`: exact signed text, who signed and when). "Open the original" links to our own record page, so it never breaks; "View source" shows only for a real https address.
- Languages: English, Nigerian Pidgin, Hausa, Yoruba, Igbo (`packages/i18n`). Everything except English is an **unreviewed AI draft** and shows a "Draft translation" label until a native speaker signs it off (`localeStatus`). The switch is in the cover; `?lang=` beats the `confam_lang` cookie; official notice text is never translated and keeps its own `lang`.
- **Limitations: read [docs/LIMITATIONS.md](docs/LIMITATIONS.md) before any demo or claim.**
- Evaluation: `uv run python eval/run.py` runs synthetic fictional suites (honest copies, wrapped forwards, one-detail edits, crops, invented notices, Pidgin rumours, and pictures). Read [docs/EVAL.md](docs/EVAL.md) before quoting any number: it is synthetic and says nothing about real notices. a test fails the build if any government-style address appears anywhere in the repo.

## Run locally

```bash
pnpm install && uv sync
CONFAM_SEED_SAMPLES=1 uv run uvicorn --app-dir services/api main:app --reload
SHOW_SAMPLES=1 pnpm --filter web dev
uv run pytest && pnpm test && pnpm e2e
```

## Photo checks on Windows: install Tesseract

Photo checks need the Tesseract program. Text checks work without it, and the API reports
`"photo_checks": false` on `/health` until it is found. In PowerShell:

```powershell
winget install --id UB-Mannheim.TesseractOCR -e   # verify the package id with: winget search tesseract
tesseract --version                              # open a NEW terminal first so PATH refreshes
```

If `tesseract` is not found, either add `C:\Program Files\Tesseract-OCR` to PATH or set
`TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe` (the default install path is also
tried automatically). English data is included. No Docker is needed locally.
Then `uv run pytest -rs` runs the picture tests that are skipped without Tesseract.

## Deploy (prepared, not deployed)

- Web: Vercel, Root Directory `apps/web`. Set `API_URL` (and `SHOW_SAMPLES` only for a labelled demo).
- API: Render, from `render.yaml`, which now builds `services/api/Dockerfile` (Tesseract is installed in the image; untested because there is no Docker on the dev machine). Set `CONFAM_CORS_ORIGINS` to the Vercel URL: photos go from the browser straight to the API (set `NEXT_PUBLIC_API_URL` in Vercel to the Render URL).
- Variables are listed in `.env.example`.

## TODO

- Port the real Python engine into `services/engine`.
- `confam-ui/` prototype (not supplied): port `assets/marks.js` and `assets/engine.js`; marks here are first-pass shapes.
- Record and signing, marking desk, channels, a worker queue (Redis/RQ) instead of the in-process job runner, docker-compose, eval.
- Photo checks have only been run against fake readers and rendered fixture pictures so far; the Tesseract tests are skipped until it is installed, and the reading thresholds have not been tuned on real photos.
- A photo the engine cannot read at all returns `no_fact` (the contract does not allow `unclear` without a notice); propose allowing `notice: null` for `unclear`.
- `superseded_by` has no `url`, so "Send the current notice" shares the notice id and date only (contract change needed).
