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
from confam_engine import OfficialNotice, latest_successor

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


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class SupersededRef(BaseModel):
    id: str
    published: str


class SignatureOut(BaseModel):
    reviewer: str
    role: Literal["first", "second"]
    signed_at: str


class RecordSummary(BaseModel):
    id: str
    title: str
    published: str
    lang: str
    superseded_by: SupersededRef | None


class RecordList(BaseModel):
    record_as_of: str
    notices: list[RecordSummary]


class RecordEntry(RecordSummary):
    url: str
    text: str
    signatures: list[SignatureOut]


def _summary(notice: OfficialNotice, notices: list[OfficialNotice]) -> dict:
    newest = latest_successor(notice, notices)
    return {
        "id": notice.id,
        "title": notice.title,
        "published": notice.published,
        "lang": notice.lang,
        "superseded_by": {"id": newest.id, "published": newest.published} if newest else None,
    }


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

    @app.get("/v1/record", response_model=RecordList)
    def list_record() -> dict:
        rec = holder.record
        return {
            "record_as_of": rec.record_as_of.isoformat(),
            "notices": [_summary(n, rec.notices) for n in rec.notices],
        }

    @app.get("/v1/record/{notice_id}", response_model=RecordEntry)
    def get_record_entry(notice_id: str) -> dict:
        rec = holder.record
        notice = rec.get(notice_id) if ID_RE.match(notice_id) else None
        if notice is None:
            raise HTTPException(status_code=404, detail="No such notice in the record.")
        return {
            **_summary(notice, rec.notices),
            "url": notice.url,
            "text": notice.text,  # exact signed text, never reworded
            "signatures": [
                {"reviewer": s.reviewer, "role": s.role, "signed_at": s.signed_at} for s in notice.signatures
            ],
        }

    return app
