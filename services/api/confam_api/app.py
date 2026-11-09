from __future__ import annotations

import json
import re
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from confam_contract.serialize import verdict_to_json
from confam_contract.verdict import Verdict

from .ratelimit import RateLimiter
from .record import Record, RecordHolder, load_record
from .service import CheckService
from .settings import Settings
from .store import CheckStore

CODE_RE = re.compile(r"^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$")


class CheckRequest(BaseModel):
    """Text checks only for now. TODO(ARCHITECTURE.md): images return {job_id}."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(max_length=5000)
    lang: Literal["en", "pcm", "ha", "yo", "ig"] = "en"

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Paste the notice text to check it.")
        return value


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _seed_samples(store: CheckStore, settings: Settings) -> None:
    path = settings.record_path.parent / "sample-verdicts.json"
    samples = json.loads(path.read_text(encoding="utf-8"))
    for name, payload in samples.items():
        if name.startswith("_"):
            continue
        store.put(Verdict.model_validate(payload), permanent=True)


def create_app(settings: Settings | None = None, record: Record | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    holder = RecordHolder(record or load_record(settings.record_path))
    store = CheckStore()
    service = CheckService(holder, store)
    limiter = RateLimiter(settings.rate_limit_per_minute, settings.ip_salt)
    if settings.seed_samples:
        _seed_samples(store, settings)

    app = FastAPI(title="Confam API", version="0.0.0")
    app.state.holder, app.state.store, app.state.service = holder, store, service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/checks")
    def create_check(body: CheckRequest, request: Request) -> JSONResponse:
        if not limiter.allow(_client_ip(request)):
            raise HTTPException(status_code=429, detail="Too many checks. Please try again in a minute.")
        verdict = service.check_text(body.text, body.lang)
        return JSONResponse(verdict_to_json(verdict))

    @app.get("/v1/verdicts/{code}")
    def get_verdict(code: str) -> JSONResponse:
        normal = code.replace("-", "").upper()
        verdict = store.get(normal) if CODE_RE.match(normal) else None
        if verdict is None:
            raise HTTPException(status_code=404, detail="No check with that code.")
        return JSONResponse(verdict_to_json(service.refreshed(verdict)))

    return app
