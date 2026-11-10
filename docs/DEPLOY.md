# Deploying Confam (GitHub, Render, Vercel)

Nothing has been pushed or deployed yet. This is the order to do it in. Free plans on all three.

## 0. Decide before the first push

- **Commit author is public.** Every commit is authored `EGBOH TOBECHUKWU <tobechukwuegboh@gmail.com>`. If that email should not be public, use GitHub's no-reply address and rewrite author history *before* the first push (afterwards it is awkward). Tell me and I will do it.
- **No LICENSE file.** Without one, the code is "all rights reserved" by default. Choose one (or none) before making the repo public.
- **Repo visibility.** The repo contains only fictional "Simulated Electoral Commission" fixtures and no secrets (checked). Private is fine for Render and Vercel too.

## 1. GitHub

Create an empty repo (no README, no licence, so history matches), then:

```bash
git remote add origin https://github.com/<you>/confam.git
git push -u origin main
```

## 2. Render (API)

1. New > Blueprint > pick the repo. It reads `render.yaml` and builds `services/api/Dockerfile` (Tesseract is installed in the image).
2. Set `CONFAM_CORS_ORIGINS` to your Vercel URL (no trailing slash, comma-separate several). You can set it after step 3 and redeploy.
3. Wait for the build; open `https://<service>.onrender.com/health`. Expect `{"status":"ok","photo_checks":true}`. `photo_checks:false` means Tesseract was not found.

Caveats:
- **The Dockerfile has never been built** (no Docker on the dev machine). Read the first build log; fix, don't assume.
- **Free plan sleeps** after about 15 minutes idle; the first request takes up to a minute.
- **512 MB memory.** Photos are shrunk before reading and one is read at a time (`CONFAM_PHOTO_WORKERS=1`). If you see out-of-memory restarts, that is the first suspect.
- **State is in memory.** A restart or spin-down loses every check, so a shared `/v/<code>` link dies after the service sleeps. A database is not built yet.

## 3. Vercel (web)

1. Add New Project > pick the repo. **Root Directory: `apps/web`**. Framework: Next.js (from `vercel.json`).
2. Environment variables:
   - `API_URL` = the Render URL (server-side calls).
   - `NEXT_PUBLIC_API_URL` = the same Render URL. **Build-time**: changing it needs a redeploy.
   - `SHOW_SAMPLES` = `1` only for a labelled demo, and only while the API has `CONFAM_SEED_SAMPLES=1`.
3. Deploy, then put the Vercel URL into the API's `CONFAM_CORS_ORIGINS` and redeploy the API.

Photos go from the browser straight to the API (Vercel functions cap request bodies near 4.5 MB), which is why CORS must list the web origin.

## 4. Check it

From the repository root:

```bash
python scripts/smoke.py --api https://<service>.onrender.com --web https://<project>.vercel.app
```

It runs text checks, the record, a forged code, CORS, the five demo pictures (when photo checks are on) and the web pages. Exit code 1 on any failure; skipped steps say SKIPPED. It was run locally against a production-style install (`uv sync --frozen --no-dev`, built web) and passed 35/35 there; that says nothing yet about Render or Vercel.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Photo upload fails in the browser, text works | `CONFAM_CORS_ORIGINS` missing the exact Vercel origin, or `NEXT_PUBLIC_API_URL` not set at build time |
| Home page says photo checks unavailable | `/health` shows `photo_checks:false`: Tesseract missing in the image |
| Record / verdict pages error on Vercel | `API_URL` wrong or the API is asleep (retry after a minute) |
| Shared verdict link says "No check with that code" | The API restarted; checks are not persisted yet |
| 429 responses | Per-IP rate limit (`CONFAM_RATE_LIMIT_PER_MINUTE`) |

Variables are listed in `.env.example`. The honest limits of the checker are in `docs/LIMITATIONS.md`; read them before any demo.
