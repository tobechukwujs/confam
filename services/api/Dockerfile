# Confam API with photo checks. Build context is the REPO ROOT:
#   docker build -f services/api/Dockerfile -t confam-api .
# UNTESTED here (no Docker on the dev machine). Check the first Render build log.
FROM python:3.12-slim

# Tesseract reads the photos. English data is enough: the notices are in English.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/contract packages/contract
COPY services/engine services/engine
COPY services/api services/api
COPY fixtures/sec-sim/notices.json fixtures/sec-sim/sample-verdicts.json fixtures/sec-sim/

RUN uv sync --frozen --no-dev --package confam-api

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# One photo at a time keeps memory small. Render sets $PORT.
ENV CONFAM_PHOTO_WORKERS=1
EXPOSE 8000
CMD ["sh", "-c", "uvicorn --app-dir services/api main:app --host 0.0.0.0 --port ${PORT:-8000}"]
